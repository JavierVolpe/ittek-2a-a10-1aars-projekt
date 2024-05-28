# -*- coding: utf-8 -*-
import sqlite3
import logging
from config import Config

NEWS_DATABASE = Config.NEWS_DATABASE

def get_db():
    db = sqlite3.connect(NEWS_DATABASE)
    db.row_factory = sqlite3.Row # Tillader os at tilgå kolonner med navn
    return db

    
def get_latest_news(permissions, page=1, page_size=Config.PAGE_SIZE):
    # Connect to the database
    db = get_db()

    # Calculate the offset for the SQL query. This is used for pagination.
    # If we're on page 1, the offset is 0. If we're on page 2, the offset is the page size, etc.
    offset = (page - 1) * page_size

    # Check if permissions are specified
    if permissions:
        # If permissions is not a list (i.e., it's a single permission), convert it to a list
        if not isinstance(permissions, list):
            permissions = [permissions]

        # Construct the WHERE clause of the SQL query. We want to select news items where the permissions
        # column contains any of the specified permissions. We use the LIKE operator for this.
        # The underscore "_" is a convention in Python meaning that we don't care about the actual value
        # from the permissions list in each iteration of the loop. We just want to repeat 
        # "permissions LIKE ?" for the number of permissions we have. Hence, "_" is a throwaway variable.
        like_clauses = " OR ".join("permissions LIKE ?" for _ in permissions)

        # Construct the SQL query string. We order the results by timestamp in descending order,
        # and limit the results to the page size, skipping past the results for previous pages.
        query = f'SELECT * FROM news WHERE {like_clauses} ORDER BY timestamp DESC LIMIT ? OFFSET ?'

        # Prepare the parameters for the LIKE clause. We surround each permission with '%' characters
        # to match any permissions that contain the permission string anywhere within them.
        like_params = [f'%{permission}%' for permission in permissions]

        # Execute the SQL query, passing in the parameters for the LIKE clause, and the limit and offset.
        cur = db.execute(query, like_params + [page_size, offset])
    else:
        # If no permissions are specified, we default to selecting news items where the permissions
        # column contains 'Public'. We still order by timestamp and limit the results for pagination.
        query = 'SELECT * FROM news WHERE permissions LIKE ? ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        cur = db.execute(query, ['%Public%', page_size, offset])

    # Fetch all the rows returned by the query
    news_items = cur.fetchall()

    # Return the fetched rows
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
    
    # Validate timestamp
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("Timestamp must be a non-empty string")
    
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