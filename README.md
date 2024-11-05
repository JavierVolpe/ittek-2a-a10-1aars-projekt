Det Bedste Intranet
===================

**Gruppe 10 - 2A - E023 - ITTEK - KEA**

-   Emil Fabricius Schlosser
-   Javier Alejandro Volpe
-   Morten Hamborg Johansen

* * * * *

Det Bedste Intranet is a secure and feature-rich intranet platform built using Flask, Flask-Login, Flask-SocketIO, and SQLAlchemy. It provides an internal communication and collaboration tool for organizations, featuring authentication via LDAP, news posting, chat rooms, and message boards tailored to user groups.

Table of Contents
-----------------

-   [Features](#features)
-   [Architecture Overview](#architecture-overview)
-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [Configuration](#configuration)
-   [Running the Application](#running-the-application)
-   [Usage](#usage)
-   [Security Considerations](#security-considerations)
-   [Acknowledgements](#acknowledgements)
-   [License](#license)

Features
--------

-   **User Authentication**: Secure login using LDAP authentication.
-   **Group-Based Access Control**: Access to specific features and chat rooms based on LDAP groups (e.g., IT, HR, Manager).
-   **News Feed**: Users can view and create news posts with permissions.
-   **Message Boards**: Post and view message cards in group-specific message boards.
-   **Real-Time Chat**: Group-specific chat rooms using SocketIO for real-time communication.
-   **Admin Panel**: Admin users can manage posts and perform administrative tasks.
-   **Profile Page**: Users can view their profile and group memberships.

Architecture Overview
---------------------

The application is structured using the Flask framework and utilizes:

-   **Flask-Login**: For managing user sessions and authentication.
-   **Flask-SocketIO**: Enables real-time communication for chat rooms.
-   **Flask-SQLAlchemy**: ORM for database interactions.
-   **LDAP**: For authenticating users against an LDAP server.
-   **SQLite**: Used for storing news posts and message cards.

Prerequisites
-------------

-   **Python 3.7+**
-   **Virtual Environment**: Recommended to isolate dependencies.
-   **LDAP Server**: Access to an LDAP server for authentication.
-   **Certificates**: SSL certificates (`cert.pem` and `key.pem`) for HTTPS.
-   **SQLite Database**: Default database or configure another database in `config.py`.

Installation
------------

1.  **Clone the Repository**

    bash

    Copy code

    `git clone https://github.com/JavierVolpe/ittek-2a-a10-1aars-projekt/ittek-2a-a10-1aars-projekt.git
    cd ittek-2a-a10-1aars-projekt`

2.  **Create a Virtual Environment**

    bash

    Copy code

    `python3 -m venv venv
    source venv/bin/activate  # On Windows use 'venv\Scripts\activate'`

3.  **Install Dependencies**

    bash

    Copy code

    `pip install -r requirements.txt`

4.  **Set Up the Database**

    The application uses SQLite by default. The necessary tables will be created automatically when you run the application for the first time.

5.  **Obtain SSL Certificates**

    Place your `cert.pem` and `key.pem` files in the root directory of the project.

Configuration
-------------

1.  **Create a `config.py` File**

    Create a `config.py` file in the project root with the following content:

    python

    Copy code

    `class Config:
        SECRET_KEY = 'your_secret_key'
        LDAP_SERVER_URI = 'ldap://your-ldap-server'
        LDAP_DOMAIN = 'yourdomain.com'
        DATABASE_URI = 'sqlite:///your-database.db'
        NEWS_DATABASE = 'news.db'
        PAGE_SIZE = 5  # Number of news items per page
        SERVER_PORT = 5000  # Port to run the server
        DEBUG = False  # Set to True for debug mode`

    Replace the placeholders with your actual configuration values.

2.  **Configure LDAP Authentication**

    -   **LDAP_SERVER_URI**: The URI of your LDAP server.
    -   **LDAP_DOMAIN**: Your organization's LDAP domain.
3.  **Configure the Database**

    -   **DATABASE_URI**: The URI for your database. By default, it uses SQLite.
    -   **NEWS_DATABASE**: The path to your news database file.
4.  **Set Secret Key**

    -   **SECRET_KEY**: A secret key for securely signing the session cookie. Keep this value secret.

Running the Application
-----------------------

1.  **Start the Application**

    bash

    Copy code

    `python app.py`

    Or with Flask's development server:

    bash

    Copy code

    `flask run --cert=cert.pem --key=key.pem --host=0.0.0.0 --port=5000`

2.  **Access the Application**

    Open your web browser and navigate to:

    arduino

    Copy code

    `https://localhost:5000/`

Usage
-----

### Login

-   Navigate to the `/login` route.
-   Enter your LDAP credentials to log in.

### News Feed

-   View the latest news posts on the `/news` route.
-   Create a new post on the `/create` route (must be logged in).
-   Posts can be assigned permissions to control visibility.

### Message Boards

-   Access message boards specific to your groups.
-   Post new messages or view existing ones.

### Real-Time Chat

-   Join group-specific chat rooms:
    -   IT Chat: `/it-chat`
    -   HR Chat: `/hr-chat`
    -   Manager Chat: `/manager-chat`
-   Real-time messaging powered by SocketIO.

### Admin Panel

-   Admin users (members of the `Enterprise Admins` group) can access the admin panel at `/admin-panel`.
-   Delete posts and manage content.

Security Considerations
-----------------------

-   **SSL Encryption**: The application runs over HTTPS using SSL certificates.
-   **LDAP Authentication**: Users are authenticated against an LDAP server.
-   **Group-Based Access Control**: Access to routes and features is restricted based on LDAP group membership.
-   **Input Validation**: User inputs are validated to prevent SQL injection and XSS attacks.
-   **Session Management**: Secure session handling using Flask-Login.

Acknowledgements
----------------

This project was developed as part of the coursework for the ITTEK program at KEA.

-   **Emil Fabricius Schlosser**
-   **Javier Alejandro Volpe**
-   **Morten Hamborg Johansen**

Special thanks to the instructors and peers who supported this project.

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.
