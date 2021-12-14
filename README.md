1. set up DB_ENGINE_PATH in common/vars.py
2. Run model.py to create database.

launcher.py - starts server and several clients

server.py - starts server. 

client.py - starts client

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
