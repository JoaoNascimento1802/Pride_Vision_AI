with open('backend/app/routers/observability.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('@router.get("/metrics")\nfrom app.models.user import User\ndef get_metrics', 'from app.models.user import User\n@router.get("/metrics")\ndef get_metrics')

with open('backend/app/routers/observability.py', 'w', encoding='utf-8') as f:
    f.write(text)
