# auth.py
import ldap3
import logging

logging.basicConfig(level=logging.DEBUG)

def authenticate(server_uri, domain, username, password):
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

        # Search for the user's groups
        connection.search(
            search_base=f"dc={domain.split('.')[0]},dc={domain.split('.')[1]}",
            search_filter=f"(sAMAccountName={username})",
            attributes=['memberOf']
        )

        # Get the list of groups
        groups = connection.entries[0]['memberOf']
        group_names = [group.split(',')[0].split('=')[1] for group in groups]
        logging.debug(f"User groups: {group_names}")

    except ldap3.core.exceptions.LDAPException as e:
        logging.error(f"LDAP exception: {e}")
        raise ValueError("LDAP authentication failed")

    return connection, group_names
