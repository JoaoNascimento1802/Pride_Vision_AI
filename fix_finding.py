import re

with open('backend/app/models/ingestion.py', 'r', encoding='utf-8') as f:
    text = f.read()

cloud_fields = """
    # --- Somente Cloud CSPM ---
    cloud_provider: Mapped[str | None] = mapped_column(String(50), default=None)
    region: Mapped[str | None] = mapped_column(String(50), default=None)
    compliance_control: Mapped[str | None] = mapped_column(String(200), default=None)
"""
if "cloud_provider" not in text:
    text = text.replace("    hit_count:", cloud_fields + "\n    hit_count:")
    with open('backend/app/models/ingestion.py', 'w', encoding='utf-8') as f:
        f.write(text)

with open('backend/app/services/dominio.py', 'r', encoding='utf-8') as f:
    text = f.read()

cloud_dom = """
    # Presentes apenas no Cloud CSPM
    cloud_provider: str | None = None
    region: str | None = None
    compliance_control: str | None = None
"""
if "cloud_provider" not in text:
    text = text.replace("    # Presentes apenas no Runtime", cloud_dom + "\n    # Presentes apenas no Runtime")
    with open('backend/app/services/dominio.py', 'w', encoding='utf-8') as f:
        f.write(text)

with open('backend/app/schemas/vulnerability.py', 'r', encoding='utf-8') as f:
    text = f.read()

if "cloud_provider" not in text:
    text = text.replace("process_name: str | None = None", "cloud_provider: str | None = None\n    region: str | None = None\n    compliance_control: str | None = None\n\n    process_name: str | None = None")
    with open('backend/app/schemas/vulnerability.py', 'w', encoding='utf-8') as f:
        f.write(text)
