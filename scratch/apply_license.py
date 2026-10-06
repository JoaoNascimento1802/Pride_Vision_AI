import os

license_text = """Copyright (c) 2024, Equipe PRIDE Vision AI (João Emanuel Pessoa do Nascimento, Karina Aparecida Bezerra, Davi Freire de França, Thales Samuel Paulino, Yanuska Monalisa Antunes Yabiku).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

with open('LICENSE.md', 'w', encoding='utf-8') as f:
    f.write(license_text)

py_header = """# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""

ts_header = """// Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
// Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

"""

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', 'venv', '__pycache__', 'scratch', '.gemini', '.pytest_cache', 'dist', 'build']]
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            print(f"Processing {path}", flush=True)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if 'Copyright' not in content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(py_header + content)
        elif file.endswith('.ts') or file.endswith('.tsx'):
            path = os.path.join(root, file)
            print(f"Processing {path}", flush=True)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if 'Copyright' not in content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(ts_header + content)

print('Licença BSD 3-Clause aplicada a todos os arquivos.')
