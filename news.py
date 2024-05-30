# -*- coding: utf-8 -*-
import sqlite3
import logging










from config import Config

NEWS_DATABASE = Config.NEWS_DATABASE

def get_db():
    db = sqlite3.connect(NEWS_DATABASE)
    db.row_factory = sqlite3.Row 
    return db

    
def get_latest_news(permissions, page=1, page_size=Config.PAGE_SIZE):

    db = get_db()
    offset = (page - 1) * page_size 

    if permissions:
        if not isinstance(permissions, list): 
            permissions = [permissions]

        like_clauses = " OR ".join("permissions LIKE ?" for perm in permissions) 

        query = f'SELECT * FROM news WHERE {like_clauses} ORDER BY timestamp DESC LIMIT ? OFFSET ?' 

        
        like_params = [f'%{permission}%' for permission in permissions] 
        
        cur = db.execute(query, like_params + [page_size, offset]) 
    else:
        query = 'SELECT * FROM news WHERE permissions LIKE ? ORDER BY timestamp DESC LIMIT ? OFFSET ?' 
        cur = db.execute(query, ['%Public%', page_size, offset])

    news_items = cur.fetchall() 
    return news_items


def validate_input(title, content, author, permissions, timestamp):
    if not isinstance(title, str) or not (1 <= len(title) <= 100): 
        raise ValueError("Title must be a string between 1 and 100 characters") 
    if not isinstance(content, str) or not (1 <= len(content) <= 2000):
        raise ValueError("Content must be a string between 1 and 2000 characters")
    if not isinstance(author, str) or not author:
        raise ValueError("Author must be a non-empty string")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("Timestamp must be a non-empty string")
    
    
    if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
        raise ValueError("Permissions skal være en liste af strenge")
    return True 

def add_post_to_database(title, content, author, permissions, timestamp):
    try:
        validate_input(title, content, author, permissions, timestamp) 
        conn = get_db()
        
        with conn: 

            cur = conn.cursor()

            if permissions is None or not permissions:
                permissions = ['Public']
            
            permissions_str = ", ".join(permissions) 

            cur.execute('INSERT INTO news (title, content, author, permissions, timestamp) VALUES (?, ?, ?, ?, ?)',
                        (title, content, author, permissions_str, timestamp))
            
        logging.info(f"Post by {author} added to the database successfully on {timestamp}.") 

    except sqlite3.DatabaseError as db_err:
        logging.error(f"Database error occurred: {db_err}")
        raise
    
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")
        raise

    finally:
        if conn:
            conn.close() 