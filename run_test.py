# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿from app.database import Base, criar_engine, sessionmaker, current_tenant_id
from app.models.application import Application
from app.models.enums import Exposicao, Ambiente, Importancia

engine = criar_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

app1 = Application(nome="App T1", responsavel="TI", url="http://", tenant_id=1, exposicao=Exposicao.INTERNA, ambiente=Ambiente.TESTE, importancia=Importancia.BAIXA)
app2 = Application(nome="App T2", responsavel="TI", url="http://", tenant_id=2, exposicao=Exposicao.INTERNA, ambiente=Ambiente.TESTE, importancia=Importancia.BAIXA)

db.add_all([app1, app2])
db.commit()
db.expunge_all()

current_tenant_id.set(1)

apps = db.query(Application).all()
print("Tenant 1 got:", [a.nome for a in apps])

current_tenant_id.set(2)
apps2 = db.query(Application).all()
print("Tenant 2 got:", [a.nome for a in apps2])
