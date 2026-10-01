from pathlib import Path

content = Path('backend/app/routers/uploads.py').read_text(encoding='utf-8')

new_func = '''
@router.post(
    "/uploads/trivy",
    response_model=ResultadoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def enviar_trivy(
    aplicacao_id: int,
    arquivo: UploadFile = File(..., description="Relatório JSON gerado pelo Trivy"),
    db: Session = Depends(get_db),
) -> ResultadoUploadResponse:
    """
    Recebe o relatório JSON do Trivy (SCA).
    """
    return await _processar(db, aplicacao_id, Ferramenta.TRIVY, arquivo)
'''

target_str = '@router.get("/uploads", response_model=list[UploadResumo])'
content = content.replace(target_str, new_func + '\n\n' + target_str)
Path('backend/app/routers/uploads.py').write_text(content, encoding='utf-8')

