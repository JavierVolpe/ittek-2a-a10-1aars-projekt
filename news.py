import sqlite3
from flask import g
import logging


DATABASE = 'database.db'

def get_db():
    # 'g' is a global object in Flask which is used to store data during an application context.
    # The 'getattr' function tries to get the '_database' attribute from the 'g' object. 
    # If it doesn't exist, it returns 'None'.
    db = getattr(g, '_database', None)

    # If 'db' is 'None', this means the database connection has not been established yet.
    if db is None:
        # So, we connect to the database and store this connection in 'g._database'.
        db = g._database = sqlite3.connect(DATABASE)

        # The 'row_factory' attribute decides how rows will be returned from the cursor.
        # Here we set it to 'sqlite3.Row' which allows us to access the columns in a row by name.
        db.row_factory = sqlite3.Row

    # Finally, we return the 'db' object which now represents our database connection.
    return db
    
def get_latest_news(permissions, page=1, page_size=5):
    db = get_db()
    offset = (page - 1) * page_size

    if permissions:
        if not isinstance(permissions, list):
            permissions = [permissions]

        # Construct the WHERE clause using LIKE for each permission
        like_clauses = " OR ".join("permissions LIKE ?" for _ in permissions)
        query = f'SELECT * FROM news WHERE {like_clauses} ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        # Prepare the parameters for the LIKE clause
        like_params = [f'%{permission}%' for permission in permissions]
        cur = db.execute(query, like_params + [page_size, offset])
    else:
        # Default to 'Public' if no permissions specified
        query = 'SELECT * FROM news WHERE permissions LIKE ? ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        cur = db.execute(query, ['%Public%', page_size, offset])

    news_items = cur.fetchall()
    return news_items



def validate_input(title, content, author, permissions, timestamp):
    # Validate title
    if not isinstance(title, str) or not (1 <= len(title) <= 100):
        raise ValueError("Title must be a string between 1 and 100 characters")
    
    # Validate content
    if not isinstance(content, str) or not (1 <= len(content) <= 2000):
        raise ValueError("Content must be a string between 1 and 2000 characters")
    
    # Validate author
    if not isinstance(author, str) or not author:
        raise ValueError("Author must be a non-empty string")
    
    # Validate permissions
    if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
        raise ValueError("Permissions must be a list of strings")
    
    # If all validations pass, return True
    return True

def add_post_to_database(title, content, author, permissions, timestamp):
    conn = None
    try:
        # Validate inputs
        validate_input(title, content, author, permissions, timestamp)

        # Get a connection to the database
        conn = get_db()
        
        with conn:
            # Get a cursor object
            cur = conn.cursor()

            if permissions is None or not permissions:
                permissions = ['Public']
            
            # Join the list of permissions with a comma
            permissions_str = ", ".join(permissions)
            
            # Insert the post into the database
            cur.execute('INSERT INTO news (title, content, author, permissions, timestamp) VALUES (?, ?, ?, ?, ?)',
                        (title, content, author, permissions_str, timestamp))
            
            # Commit the changes (handled by the context manager)
            
        # Log the successful insertion
        logging.info(f"Post by {author} added to the database successfully on {timestamp}.")

    except sqlite3.DatabaseError as db_err:
        logging.error(f"Database error occurred: {db_err}")
        raise
    
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")
        raise

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()