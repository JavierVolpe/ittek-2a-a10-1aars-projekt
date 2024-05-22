# auth.py
import ldap3
import logging

logging.basicConfig(level=logging.DEBUG)

def authenticate(server_uri, domain, username, password):
    # Use user principal name (UPN) format for AD authentication
    user_dn = f"{username}@{domain}"
    logging.debug(f"User DN: {user_dn}")

    try:
        # Create the server object without SSL
        server = ldap3.Server(server_uri, get_info=ldap3.ALL)
        # Create the connection object
        connection = ldap3.Connection(server, user=user_dn, password=password)

        # Attempt to bind to the server
        if not connection.bind():
            logging.error("Failed to bind to the server. Invalid credentials.")
            raise ValueError("Invalid credentials")
        else:
            logging.debug("Successfully authenticated.")
        
    except ldap3.core.exceptions.LDAPException as e:
        logging.error(f"LDAP exception: {e}")
        raise ValueError("LDAP authentication failed")

    return connection
