class Config:
    # Database konfiguration
    DATABASE_URI = "sqlite:///app.db"
    PAGE_SIZE = 5
    SECRET_KEY = "your_secret_key_is_not_thisone"
    DEBUG = True
    DATABASE = 'database.db'

    # LDAP server konfiguration
    LDAP_SERVER_URI = "ldap://10.0.0.4:389"
    LDAP_DOMAIN = "A10.dk"



