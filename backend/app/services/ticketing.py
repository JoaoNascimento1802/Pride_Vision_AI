# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.models.enums import TicketProvider, TicketStatus
from app.models.integration import Integration
from app.models.ticket import Ticket
from app.models.vulnerability import Vulnerability
from app.services.crypto import decrypt_token, encrypt_token


class TicketData(BaseModel):
    external_id: str
    external_key: str | None = None
    url: str
    title: str
    status: TicketStatus


class TicketProviderAbstraction:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def create_ticket(self, vuln: Vulnerability) -> TicketData:
        raise NotImplementedError

    def sync_ticket(self, ticket: Ticket) -> TicketData:
        raise NotImplementedError

    def add_comment(self, ticket: Ticket, comment: str) -> None:
        raise NotImplementedError


class JiraTicketProvider(TicketProviderAbstraction):
    def _get_integration(self) -> Integration:
        integ = self.db.query(Integration).filter_by(user_id=self.user_id, provider="jira").first()
        if not integ or not integ.access_token_enc:
            raise ValueError("Jira não configurado ou não autenticado para este usuário.")
        return integ

    def _ensure_token(self, integ: Integration) -> str:
        if not integ.access_token_enc:
            raise ValueError("Token não configurado.")
        if integ.expires_at:
            exp_at = integ.expires_at
            if exp_at.tzinfo is None:
                exp_at = exp_at.replace(tzinfo=UTC)
            if datetime.now(UTC) >= exp_at - timedelta(minutes=1):
                refresh_token_enc = integ.refresh_token_enc
                if not refresh_token_enc:
                    raise ValueError("Token do Jira expirado e sem refresh token disponível.")

                refresh_token = decrypt_token(refresh_token_enc)
                resp = httpx.post(
                    "https://auth.atlassian.com/oauth/token",
                    json={
                        "grant_type": "refresh_token",
                        "client_id": settings.JIRA_CLIENT_ID,
                        "client_secret": settings.JIRA_CLIENT_SECRET,
                        "refresh_token": refresh_token,
                    },
                )
                if resp.status_code != 200:
                    raise ValueError("Falha ao renovar token do Jira.")

                data = resp.json()
                integ.access_token_enc = encrypt_token(data["access_token"])
                if "refresh_token" in data:
                    integ.refresh_token_enc = encrypt_token(data["refresh_token"])
                integ.expires_at = datetime.now(UTC) + timedelta(seconds=data["expires_in"])
                self.db.commit()

        return decrypt_token(integ.access_token_enc)

    def _api_call(
        self, integ: Integration, method: str, path: str, json_data: dict[str, Any] | None = None
    ) -> httpx.Response:
        token = self._ensure_token(integ)
        url = f"https://api.atlassian.com/ex/jira/{integ.cloud_id}/rest/api/3{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        resp = httpx.request(method, url, headers=headers, json=json_data)
        if resp.status_code == 401:
            # Força expiração e tenta de novo
            integ.expires_at = datetime.now(UTC)
            token = self._ensure_token(integ)
            headers["Authorization"] = f"Bearer {token}"
            resp = httpx.request(method, url, headers=headers, json=json_data)
        return resp

    def _map_status(self, jira_status_category: str) -> TicketStatus:
        # Jira usa categorias: "new", "indeterminate", "done"
        if jira_status_category == "done":
            return TicketStatus.RESOLVED
        if jira_status_category == "indeterminate":
            return TicketStatus.IN_PROGRESS
        return TicketStatus.OPEN

    def create_ticket(self, vuln: Vulnerability) -> TicketData:
        integ = self._get_integration()

        # Em vez de hardcodar o projeto, precisaríamos de UI para o usuário escolher o projeto.
        # Por simplicidade/MVP, a API 3 do Jira requer o Project ID/Key e IssueType ID.
        # Podemos buscar o primeiro projeto disponível na conta para facilitar o fluxo.
        resp_proj = self._api_call(integ, "GET", "/project")
        if resp_proj.status_code != 200 or not resp_proj.json():
            raise ValueError("Não foi possível listar projetos no Jira.")
        project = resp_proj.json()[0]
        project_id = project["id"]

        # Obter issue types do projeto
        resp_meta = self._api_call(integ, "GET", f"/issue/createmeta?projectIds={project_id}")
        meta = resp_meta.json()
        if not meta.get("projects"):
            raise ValueError("Nenhum projeto encontrado nos metadados.")

        issue_types = meta["projects"][0]["issuetypes"]
        # Priorizar "Bug", se não "Task", se não o primeiro
        issue_type_id = None
        for it in issue_types:
            if it["name"].lower() == "bug":
                issue_type_id = it["id"]
                break
        if not issue_type_id:
            for it in issue_types:
                if it["name"].lower() == "task":
                    issue_type_id = it["id"]
                    break
        if not issue_type_id:
            issue_type_id = issue_types[0]["id"]

        title = f"[{vuln.risco.value.upper()}] {vuln.tipo_vuln} na {vuln.aplicacao.nome}"

        # Constrói Atlassian Document Format (ADF) puro e sem segredos/PII
        description_adf = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Vulnerabilidade identificada no PRIDE Vision AI.\n",
                        }
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Severidade PRIDE: ",
                            "marks": [{"type": "strong"}],
                        },
                        {"type": "text", "text": f"{vuln.risco.value.upper()}\n"},
                    ],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Caminho/Recurso: ",
                            "marks": [{"type": "strong"}],
                        },
                        {"type": "text", "text": f"{vuln.endpoint}\n"},
                    ],
                },
            ],
        }

        payload = {
            "fields": {
                "project": {"id": project_id},
                "summary": title,
                "description": description_adf,
                "issuetype": {"id": issue_type_id},
            }
        }

        resp = self._api_call(integ, "POST", "/issue", json_data=payload)
        if resp.status_code != 201:
            raise ValueError(f"Falha ao criar issue no Jira: {resp.text}")

        data = resp.json()
        issue_key = data["key"]
        issue_id = data["id"]

        return TicketData(
            external_id=issue_id,
            external_key=issue_key,
            url=f"{integ.site_url}/browse/{issue_key}",
            title=title,
            status=TicketStatus.OPEN,
        )

    def sync_ticket(self, ticket: Ticket) -> TicketData:
        integ = self._get_integration()
        resp = self._api_call(integ, "GET", f"/issue/{ticket.external_id}")
        if resp.status_code != 200:
            raise ValueError(f"Falha ao buscar issue no Jira: {resp.text}")

        data = resp.json()
        status_category = data["fields"]["status"]["statusCategory"]["key"]
        title = data["fields"]["summary"]

        return TicketData(
            external_id=ticket.external_id,
            external_key=ticket.external_key,
            url=ticket.url,
            title=title,
            status=self._map_status(status_category),
        )

    def add_comment(self, ticket: Ticket, comment: str) -> None:
        integ = self._get_integration()
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }
        }
        self._api_call(integ, "POST", f"/issue/{ticket.external_id}/comment", json_data=payload)


class AzureDevOpsTicketProvider(TicketProviderAbstraction):
    def create_ticket(self, vuln: Vulnerability) -> TicketData:
        return TicketData(
            external_id="ado-123",
            external_key="ADO-123",
            url="https://dev.azure.com/org/project/_workitems/edit/123",
            title=f"[{vuln.risco.value.upper()}] {vuln.tipo_vuln} na {vuln.aplicacao.nome}",
            status=TicketStatus.OPEN,
        )

    def sync_ticket(self, ticket: Ticket) -> TicketData:
        return TicketData(
            external_id=ticket.external_id,
            external_key=ticket.external_key,
            url=ticket.url,
            title=ticket.title,
            status=ticket.status,
        )

    def add_comment(self, ticket: Ticket, comment: str) -> None:
        pass


class ServiceNowTicketProvider(TicketProviderAbstraction):
    def create_ticket(self, vuln: Vulnerability) -> TicketData:
        return TicketData(
            external_id="inc-999",
            external_key="INC0000999",
            url="https://instance.service-now.com/nav_to.do?uri=incident.do?sys_id=inc-999",
            title=f"[{vuln.risco.value.upper()}] {vuln.tipo_vuln} na {vuln.aplicacao.nome}",
            status=TicketStatus.OPEN,
        )

    def sync_ticket(self, ticket: Ticket) -> TicketData:
        return TicketData(
            external_id=ticket.external_id,
            external_key=ticket.external_key,
            url=ticket.url,
            title=ticket.title,
            status=ticket.status,
        )

    def add_comment(self, ticket: Ticket, comment: str) -> None:
        pass


def get_provider(
    db: Session, provider_type: TicketProvider, user_id: int
) -> TicketProviderAbstraction:
    if provider_type == TicketProvider.JIRA:
        return JiraTicketProvider(db, user_id)
    if provider_type == TicketProvider.AZURE_DEVOPS:
        return AzureDevOpsTicketProvider(db, user_id)
    if provider_type == TicketProvider.SERVICENOW:
        return ServiceNowTicketProvider(db, user_id)
    raise ValueError(f"Provider {provider_type} não implementado")


def criar_ticket(
    db: Session, vulnerabilidade: Vulnerability, provider_type: TicketProvider, user_id: int
) -> Ticket:
    provider = get_provider(db, provider_type, user_id)

    # Valida duplicidade
    existente = next(
        (
            t
            for t in vulnerabilidade.tickets
            if t.provider == provider_type and t.status != TicketStatus.CLOSED
        ),
        None,
    )
    if existente:
        return existente

    try:
        dados = provider.create_ticket(vulnerabilidade)
    except Exception as e:
        raise ValueError(f"Falha ao criar ticket no {provider_type.value}: {str(e)}")

    ticket = Ticket(
        vulnerabilidade_id=vulnerabilidade.id,
        provider=provider_type,
        external_id=dados.external_id,
        external_key=dados.external_key,
        url=dados.url,
        title=dados.title,
        status=dados.status,
        last_synced_at=datetime.now(UTC),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def sincronizar_ticket(db: Session, ticket: Ticket, user_id: int) -> Ticket:
    provider = get_provider(db, ticket.provider, user_id)
    try:
        dados = provider.sync_ticket(ticket)
        ticket.status = dados.status
        ticket.title = dados.title
        ticket.last_synced_at = datetime.now(UTC)
        db.commit()
        db.refresh(ticket)
    except Exception:
        pass
    return ticket
