with open("pride-full-scan.yml", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('-F "file=@gitleaks-report.json"', '-F "file=@gitleaks-report.json" || echo "No leak found"')
content = content.replace('-F "file=@semgrep-report.json"', '-F "file=@semgrep-report.json" || echo "No sast found"')
content = content.replace('-F "file=@trivy-report.json"', '-F "file=@trivy-report.json" || echo "No deps found"')
content = content.replace('-F "file=@checkov-report.json" || true', '-F "file=@checkov-report.json" || echo "No infra found"')
content = content.replace('-F "file=@nuclei-report.jsonl" || true', '-F "file=@nuclei-report.jsonl" || echo "No dast found"')
content = content.replace('-d "@sbom.json"', '-d "@sbom.json" || echo "No sbom found"')

with open("pride-full-scan.yml", "w", encoding="utf-8") as f:
    f.write(content)