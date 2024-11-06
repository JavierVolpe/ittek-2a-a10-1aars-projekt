Det Bedste Intranet
===================

**Gruppe 10 - 2A - E023 - ITTEK - KEA**

-   Emil Fabricius Schlosser
-   Javier Alejandro Volpe
-   Morten Hamborg Johansen

* * * * *

Det Bedste Intranet is a secure and feature-rich intranet platform developed as part of our first-year project for the IT Technology program at KEA. The application is built using Flask, Flask-Login, Flask-SocketIO, and SQLAlchemy, providing an internal communication and collaboration tool for organizations. It features LDAP authentication, news posting, group-based chat rooms, and message boards tailored to user groups.

Table of Contents
-----------------

-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [Configuration](#configuration)
-   [Running the Application](#running-the-application)
-   [Usage](#usage)
    -   [Authentication](#authentication)
    -   [News Feed](#news-feed)
    -   [Message Boards](#message-boards)
    -   [Real-Time Chat](#real-time-chat)
    -   [Admin Panel](#admin-panel)
-   [Security Considerations](#security-considerations)
-   [Acknowledgements](#acknowledgements)
-   [License](#license)

Features
--------

-   **LDAP Authentication**: Secure login using LDAP credentials.
-   **Group-Based Access Control**: Access control based on LDAP group memberships (e.g., IT, HR, Manager).
-   **News Feed**: Users can view and create news posts with specific permissions.
-   **Message Boards**: Post and view message cards in group-specific message boards.
-   **Real-Time Chat**: Group-specific chat rooms using SocketIO for real-time communication.
-   **Admin Panel**: Admin users can manage posts and perform administrative tasks.
-   **Profile Page**: Users can view their profile and group memberships.


Prerequisites
-------------

-   **Python 3.7 or higher**
-   **Virtual Environment**: Recommended to isolate dependencies.
-   **LDAP Server**: Access to an LDAP server for authentication.
-   **SSL Certificates**: `cert.pem` and `key.pem` for HTTPS (can be self-signed for development).
-   **SQLite Database**: Default database or configure another database in `config.py`.

Installation
------------

1.  **Clone the Repository**


    `git clone https://github.com/JavierVolpe/ittek-2a-a10-1aars-projekt.git
    cd ittek-2a-a10-1aars-projekt`

2.  **Create a Virtual Environment**


    `python3 -m venv venv
    source venv/bin/activate  # On Windows use 'venv\Scripts\activate'`

3.  **Install Dependencies**

    bash

    Copy code

    `pip install -r requirements.txt`

4.  **Set Up the Database**

    The necessary tables will be created automatically when you run the application for the first time.

5.  **Obtain SSL Certificates**

    Place your `cert.pem` and `key.pem` files in the root directory of the project.

Configuration
-------------

The `config.py` file contains all the configuration variables needed to run the application. Review and update it with your specific settings.

### Important Configuration Variables

-   **SECRET_KEY**: A secret key for securely signing the session cookie. Keep this value secret.
-   **LDAP_SERVER_URI**: The URI of your LDAP server.
-   **LDAP_DOMAIN**: Your organization's LDAP domain.
-   **DATABASE_URI**: The URI for your database. By default, it uses SQLite.
-   **NEWS_DATABASE**: The path to your news database file.

Running the Application
-----------------------

1.  **Activate the Virtual Environment**


    `source venv/bin/activate  # On Windows use 'venv\Scripts\activate'`

2.  **Start the Application**

    `python app.py`

    Or, if you prefer to use Flask's development server:

    `flask run --cert=cert.pem --key=key.pem --host=0.0.0.0 --port=5000`

3.  **Access the Application**

    Open your web browser and navigate to:

    `https://localhost:5000/`

Usage
-----

### Authentication

-   **Login**: Navigate to `/login` and enter your LDAP credentials.
-   **Logout**: Click on the logout button or navigate to `/logout`.
-   **Profile**: View your username and group memberships at `/profile`.

### News Feed

-   **View News**: Navigate to `/news` to see the latest news posts.
-   **Create News Post**: Go to `/create` to add a new news post (must be logged in).
-   **Pagination**: Use the page navigation to view older posts.

### Message Boards

-   **Post a Message**: Navigate to `/message-poster` to post a new message card.
-   **View Messages**: View existing message cards relevant to your groups.

### Real-Time Chat

-   **IT Chat**: `/it-chat` (accessible to users in the 'IT' group)
-   **HR Chat**: `/hr-chat` (accessible to users in the 'HR' group)
-   **Manager Chat**: `/manager-chat` (accessible to users in the 'Manager' group)

Engage in real-time conversations with group members.

### Admin Panel

-   **Access**: Available at `/admin-panel` for users in the 'Enterprise Admins' group.
-   **Manage Posts**: View and delete posts from all users.

Security Considerations
-----------------------

-   **SSL Encryption**: The application runs over HTTPS using SSL certificates.
-   **LDAP Authentication**: Users are authenticated against an LDAP server.
-   **Group-Based Access Control**: Access to routes and features is restricted based on LDAP group membership.
-   **Input Validation**: User inputs are validated to prevent SQL injection and XSS attacks.
-   **Session Management**: Secure session handling using Flask-Login.
-   **No Hardcoded Credentials**: Ensure that no credentials are hardcoded in the codebase.

Acknowledgements
----------------

This project was developed as part of the first-year project for the ITTEK program at KEA.

-   **Emil Fabricius Schlosser**
-   **Javier Alejandro Volpe**
-   **Morten Hamborg Johansen**

We would like to thank our instructors and classmates for their support and guidance throughout the development of this project.

License
-------

This project is licensed under the MIT License. See the LICENSE file for details.
