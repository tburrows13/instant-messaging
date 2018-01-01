# instant-messaging
A command-line chat application written in Python using the `sockets` module

#### Usage

Run `server.py` on the host machine, and edit `HOST` in `address.txt` to whatever IP address the server machine has.  Then run `client.py` on any client machine, and it will interface with the server to exchange messages.  The server listens by default on port 10002.  If running the server and client on different networks, you will probably need to [set up port forwarding](https://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/) from your router.

#### Server machine requires
- `server.py`
- `access_database.py`
- `BaseClass.py`
- `database.json`

#### Client machine requires
- `client.py`
- `BaseClass.py`
- `address.txt`

All users, passwords, and unread messages are stored **in plaintext** in `database.json`.  Run `access_database.py` to reset this database.
