# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿with open(r"C:\Users\Joaoe\.gemini\antigravity\brain\92dae92a-4968-4a2f-a75b-76ccca570fb5\.system_generated\tasks\task-8655.log", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "FAILURES" in line or "ERRORS" in line:
        print("".join(lines[i:i+40]))
        break
