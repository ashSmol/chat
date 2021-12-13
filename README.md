1. set up DB_ENGINE_PATH in common/vars.py
2. Run model.py to create database.

After client is started, it tries to add new contact with login "alex".
Then requests all contacts.
After that deletes added contact "alex" and again requests all contacts.