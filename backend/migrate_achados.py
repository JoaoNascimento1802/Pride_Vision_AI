# Copyright (c) 2024, Equipe PRIDE Vision AI. All rights reserved.
# Licensed under the BSD 3-Clause License. See LICENSE.md in the project root for license information.

import sqlite3

try:
    conn = sqlite3.connect('backend/pride_vision.db')
    cursor = conn.cursor()

    columns = [
        "process_name VARCHAR",
        "pid INTEGER",
        "syscall VARCHAR",
        "container_id VARCHAR",
        "cloud_provider VARCHAR",
        "region VARCHAR",
        "compliance_control VARCHAR",
        "hit_count INTEGER",
        "last_seen_at DATETIME"
    ]
    
    for col in columns:
        try:
            cursor.execute(f"ALTER TABLE achados ADD COLUMN {col}")
        except sqlite3.OperationalError as e:
            pass

    conn.commit()
    conn.close()
    print('Database migration for achados applied successfully!')
except Exception as e:
    print('Failed to migrate database:', e)