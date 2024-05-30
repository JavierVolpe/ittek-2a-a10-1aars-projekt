# -*- coding: utf-8 -*-
from flask_login import UserMixin
import ldap3
import logging
from config import Config

logging.basicConfig(level=logging.DEBUG)
domain = Config.LDAP_DOMAIN
server_uri = Config.LDAP_SERVER_URI

class User(UserMixin):
    def __init__(self, username, groups=None):
        self.username = username
        self.groups = groups if groups is not None else []

    def get_id(self):
        return self.username
        
    def get_groups(self):
        return self.groups

def authenticate(server_uri, domain, username, password):
    user_dn = f"{username}@{domain}"
    logging.debug(f"User DN: {user_dn}")

    try:
        server = ldap3.Server(server_uri, get_info=ldap3.ALL)
        connection = ldap3.Connection(server, user=user_dn, password=password)

        if not connection.bind():
            logging.error("Failed to bind to the server. Invalid credentials.")
            raise ValueError("Invalid credentials")
        else:
            logging.debug("Successfully authenticated.")

        return User(username)

    except ldap3.core.exceptions.LDAPException as e:
        logging.error(f"LDAP exception: {e}")
        raise ValueError("LDAP authentication failed")
    
def get_user_groups(username):
    user_dn = f"{username}@{domain}"
    logging.debug(f"Fetching groups for user DN: {user_dn}")

    try:
        server = ldap3.Server(server_uri, get_info=ldap3.ALL)
        service_account_username = Config.LDAP_SERVICE_USERNAME
        service_account_password = Config.LDAP_SERVICE_PASSWORD
        connection = ldap3.Connection(server, user=f"{service_account_username}@{domain}", password=service_account_password)

        if not connection.bind():
            logging.error("Failed to bind to the server with the service account.")
            raise ValueError("Failed to connect to LDAP server")

        connection.search(
            search_base=f"dc={domain.split('.')[0]},dc={domain.split('.')[1]}",
            search_filter=f"(sAMAccountName={username})",
            attributes=['memberOf']
        )

        if len(connection.entries) == 0:
            logging.error("No entries found for the user.")
            return []

        groups = [group.split(',')[0].split('=')[1] for group in connection.entries[0]['memberOf']]
        logging.debug(f"User groups: {groups}")
        return groups

    except ldap3.core.exceptions.LDAPException as e:
        logging.error(f"LDAP exception: {e}")
        raise ValueError("Failed to fetch user groups")
