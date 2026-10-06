# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import re

with open('backend/tests/test_vulnerabilities.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'    @pytest\.mark\.parametrize\(\n        \("status", "encerrada"\),\n        "status, encerrada",\n        \[',
    r'    @pytest.mark.parametrize(\n        "status, encerrada",\n        [',
    text
)

text = re.sub(
    r'            pytest\.param\(\n                StatusVulnerabilidade\.FALSO_POSITIVO, True, id="AC-STATUS-12-falso-positivo"\n            \),\n            pytest\.param\(StatusVulnerabilidade\.FALSO_POSITIVO, True, id="AC-STATUS-12-falso-positivo"\),',
    r'            pytest.param(StatusVulnerabilidade.FALSO_POSITIVO, True, id="AC-STATUS-12-falso-positivo"),',
    text
)

text = re.sub(
    r'        """Corrigida e Falso positivo saem da fila de trabalho; os demais permanecem\."""\n        """Corrigida, Falso positivo, Aceito como Risco e Duplicado saem da fila de trabalho\."""\n        assert status\.encerrada is encerrada',
    r'        """Corrigida, Falso positivo, Aceito como Risco e Duplicado saem da fila de trabalho."""\n        assert status.encerrada is encerrada',
    text
)


with open('backend/tests/test_vulnerabilities.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("fixed vulnerabilities tests duplicates")

