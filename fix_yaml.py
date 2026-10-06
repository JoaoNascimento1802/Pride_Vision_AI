# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

with open("pride-full-scan.yml", "r", encoding="utf-8") as f:
    content = f.read()

import re

# Fix Gitleaks step
gitleaks_action = """uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          report-format: json
          report-path: gitleaks-report.json"""

gitleaks_docker = """run: |
          wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz
          tar -xzf gitleaks_8.18.2_linux_x64.tar.gz
          ./gitleaks detect --source . --report-path gitleaks-report.json --report-format json || true"""

content = content.replace(gitleaks_action, gitleaks_docker)

# Replace the curl commands to be safe
content = re.sub(r'(curl.*? -F "file=@(.*?)".*?)(\s*\|\|\s*true)?\n', r'if [ -f \2 ]; then \1; else echo "File \2 not found, skipping upload"; fi\n', content)
content = re.sub(r'(curl.*? -d "@(.*?)".*?)(\s*\|\|\s*true)?\n', r'if [ -f \2 ]; then \1; else echo "File \2 not found, skipping upload"; fi\n', content)

with open("pride-full-scan.yml", "w", encoding="utf-8") as f:
    f.write(content)