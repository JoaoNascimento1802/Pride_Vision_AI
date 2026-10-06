# Copyright (c) 2026, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import sqlite3

try:
    conn = sqlite3.connect('backend/pride_vision.db')
    cursor = conn.cursor()
    
    # 1. Update the 'prod' enum to 'producao' in 'aplicacoes' table
    cursor.execute("UPDATE aplicacoes SET ambiente = 'producao' WHERE ambiente = 'prod'")
    cursor.execute("UPDATE aplicacoes SET ambiente = 'homologacao' WHERE ambiente = 'homolog'")
    cursor.execute("UPDATE aplicacoes SET ambiente = 'teste' WHERE ambiente = 'test'")
    
    # 2. Add the missing columns to the 'policies' table
    try:
        cursor.execute("ALTER TABLE policies ADD COLUMN require_signature BOOLEAN NOT NULL DEFAULT 0")
    except sqlite3.OperationalError as e:
        pass

    try:
        cursor.execute("ALTER TABLE policies ADD COLUMN require_provenance BOOLEAN NOT NULL DEFAULT 0")
    except sqlite3.OperationalError as e:
        pass

    try:
        cursor.execute("ALTER TABLE policies ADD COLUMN trusted_builder BOOLEAN NOT NULL DEFAULT 0")
    except sqlite3.OperationalError as e:
        pass

    conn.commit()
    conn.close()
    print('Database migration applied successfully!')
except Exception as e:
    print('Failed to migrate database:', e)