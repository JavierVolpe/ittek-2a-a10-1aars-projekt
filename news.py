# -*- coding: utf-8 -*-
import sqlite3
import logging
"""
Logging levels: 
NOTSET=0
DEBUG=10
INFO=20
WARN=30
ERROR=40
CRITICAL=50
"""
from config import Config

NEWS_DATABASE = Config.NEWS_DATABASE

def get_db():
    db = sqlite3.connect(NEWS_DATABASE)
    db.row_factory = sqlite3.Row # Tillader os at tilgå kolonner med navn
    return db

    
def get_latest_news(permissions, page=1, page_size=Config.PAGE_SIZE):

    db = get_db()
    offset = (page - 1) * page_size # Hvis page er 1, vil offset være 0. Hvis page er 2, vil offset være page_size, osv.

    if permissions:
        if not isinstance(permissions, list): # Hvis permissions ikke er en liste, laver vi den om til en liste
            permissions = [permissions]

        like_clauses = " OR ".join("permissions LIKE ?" for perm in permissions) # "permissions LIKE ? OR permissions LIKE ? OR permissions LIKE ?"

        query = f'SELECT * FROM news WHERE {like_clauses} ORDER BY timestamp DESC LIMIT ? OFFSET ?' # "SELECT * FROM news WHERE permissions LIKE ? OR permissions LIKE ? OR permissions LIKE ? ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        # Vi bruger offset og page_size til at bestemme, hvor mange rækker vi vil have fra databasen, og hvor vi vil starte fra. F.eks. hvis page_size er 5 og offset er 10, vil vi få rækkerne 11-15 fra databasen.
        
        like_params = [f'%{permission}%' for permission in permissions] # Vi laver en liste af strengene, hvor vi tilføjer % foran og bagved hver streng i listen. F.eks. 
        # ["%permission1%", "%permission2%", "%permission3%"]
        cur = db.execute(query, like_params + [page_size, offset]) # Vi tilføjer de nødvendige parametre til query'en, og udfører den
    else:
        query = 'SELECT * FROM news WHERE permissions LIKE ? ORDER BY timestamp DESC LIMIT ? OFFSET ?' # Hvis der ikke er nogen tilladelser, henter vi kun rækker, hvor permissions er 'Public'
        cur = db.execute(query, ['%Public%', page_size, offset])

    news_items = cur.fetchall() # Henter alle rækkerne fra cur, og gemmer dem i en liste
    return news_items


def validate_input(title, content, author, permissions, timestamp):
    if not isinstance(title, str) or not (1 <= len(title) <= 100): # Vi bruger isinstance til at tjekke, om title er en streng, og om længden af strengen er mellem 1 og 100 tegn
        raise ValueError("Title must be a string between 1 and 100 characters") # Hvis valideringen fejler, kastes en ValueError, og programmet stopper
    if not isinstance(content, str) or not (1 <= len(content) <= 2000):
        raise ValueError("Content must be a string between 1 and 2000 characters")
    if not isinstance(author, str) or not author:
        raise ValueError("Author must be a non-empty string")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("Timestamp must be a non-empty string")
    
    # Tjekker om 'permissions' ikke er en liste, eller om ikke alle elementer i 'permissions' er strenge
    if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
        raise ValueError("Permissions skal være en liste af strenge")
    return True # Returnerer True, hvis alle valideringerne er gået igennem, ellers kastes en ValueError og stopper programmet

def add_post_to_database(title, content, author, permissions, timestamp):
    try:
        validate_input(title, content, author, permissions, timestamp) # Hvis valideringen fejler, kastes en ValueError, og programmet stopper
        conn = get_db()
        
        with conn: # Når du bruger with conn:, sørger Python for, at forbindelsen lukkes korrekt efter udførelsen af koden inden for with-blokken, selvom der opstår en fejl.

            cur = conn.cursor()

            if permissions is None or not permissions:
                permissions = ['Public']
            
            permissions_str = ", ".join(permissions) # Tager listen af tilladelser og samler dem til en enkelt streng, hvor de er adskilt af kommaer

            cur.execute('INSERT INTO news (title, content, author, permissions, timestamp) VALUES (?, ?, ?, ?, ?)',
                        (title, content, author, permissions_str, timestamp))
            
        logging.info(f"Post by {author} added to the database successfully on {timestamp}.") # Log the successful insertion of the post

    except sqlite3.DatabaseError as db_err:
        logging.error(f"Database error occurred: {db_err}")
        raise
    
    except Exception as ex:
        logging.error(f"An error occurred: {ex}")
        raise

    finally:
        if conn:
            conn.close() # Ensure the connection is closed even if an exception occurs