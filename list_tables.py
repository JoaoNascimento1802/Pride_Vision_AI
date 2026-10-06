# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

﻿import sqlite3
conn = sqlite3.connect('backend/pride_vision.db')
print([t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
