import re

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """def criar_tabelas():
    # Run alembic migrations
    import os
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    Base.metadata.create_all(bind=engine)"""

text = re.sub(r'def criar_tabelas\(\):[\s\S]*?Base\.metadata\.create_all\(bind=engine\)', replacement, text)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
