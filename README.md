1. set up DB_ENGINE_PATH in common/vars.py
2. set up CLIENT_DB_ENGINE_PATH in common/vars.py
3. Run model.py and client_db_model to create database.

launcher.py - starts server and several clients

server.py - starts server in terminal. 

runServerUi.py - run Server with GUI

client.py - starts client in terminal

runClientUi.py - starts chat client with GUI

After client is started, it tries to add new contact with login "alex".
Then requests all contacts.
After that deletes added contact "alex" and again requests all contacts.

Server db Structure.

Table clients:
    contains information about each client whenever connected to server

Table clients history: info about messages to other clients

Table contacts: links between clients
________________
Client db structure.

Contacts: list of contacts of this particular client

contacts_history: history of messages of this client to contacts
____

When client sends add/del contact rq to server, the contact also added/removed from local db

After this client sends a message, it is stored to local db also.
