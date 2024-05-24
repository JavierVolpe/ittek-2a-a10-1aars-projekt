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
        if not isinstance(permissions, list):
            permissions = [permissions]

        # Construct the WHERE clause using LIKE for each permission
        like_clauses = " OR ".join("permissions LIKE ?" for _ in permissions)
        query = f'SELECT * FROM news WHERE {like_clauses} ORDER BY timestamp DESC LIMIT 5'
        # Prepare the parameters for the LIKE clause
        like_params = [f'%{permission}%' for permission in permissions]
        cur = db.execute(query, like_params)
    else:
        # Default to 'Public' if no permissions specified
        query = 'SELECT * FROM news WHERE permissions LIKE ? ORDER BY timestamp DESC LIMIT 5'
        cur = db.execute(query, ['%Public%'])

    news_items = cur.fetchall()
    return news_items


def add_post_to_database(title, content, author, permissions, timestamp):
    conn = get_db()
    cur = conn.cursor()
    
    # Join the list of permissions with a comma
    permissions_str = ", ".join(permissions)  # Ensure permissions is a list of full strings
    print("Permissions list:", permissions)  # Debugging line to check the format of permissions
    print("Permissions_str list:", permissions_str)  # Debugging line to check the format of permissions

    # Insert into the database
    cur.execute('INSERT INTO news (title, content, author, permissions, timestamp) VALUES (?, ?, ?, ?, ?)',
                (title, content, author, permissions_str, timestamp))
    conn.commit()
    conn.close()
