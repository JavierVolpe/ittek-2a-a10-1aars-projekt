import sqlite3
from flask import g

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
    return db
    


def get_latest_news(permissions):
    db = get_db()
    if permissions:
        # Ensure permissions is a list, even if a single permission is provided
        if not isinstance(permissions, list):
            permissions = [permissions]
        # Use the SQL IN clause for multiple permissions
        query = 'SELECT * FROM news WHERE permissions IN ({}) ORDER BY timestamp DESC LIMIT 5'.format(', '.join(['?']*len(permissions)))
        cur = db.execute(query, permissions)
    else:
        # Default to 'Public' if no permissions specified
        permissions = ['Public']
        query = 'SELECT * FROM news WHERE permissions IN (?) ORDER BY timestamp DESC LIMIT 5'
        cur = db.execute(query, permissions)

    news_items = cur.fetchall()
    return news_items

    
    news_items = cur.fetchall()
    return news_items