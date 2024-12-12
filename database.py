import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('build_buddy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS builds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            build_type TEXT NOT NULL,
            version TEXT NOT NULL,
            customer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed'
        )
    ''')
    
    conn.commit()
    conn.close()

def log_build(build_type, version, customer, status):
    conn = sqlite3.connect('build_buddy.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO builds (build_type, version, customer, status)
        VALUES (?, ?, ?, ?)
    ''', (build_type, version, customer, status))
    conn.commit()
    conn.close()

def get_build_stats():
    conn = sqlite3.connect('build_buddy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT build_type, COUNT(*) as count
        FROM builds
        GROUP BY build_type
    ''')
    
    results = cursor.fetchall()
    stats = {
        'kompass': 0,
        'nagare': 0
    }
    
    for build_type, count in results:
        stats[build_type.lower()] = count
    
    conn.close()
    return stats
