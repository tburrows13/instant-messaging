import socket
from threading import Thread, Lock
from datetime import datetime

from BaseClass import ProtocolObject
from access_database import store, load


host = ""
port = 10002
storage_name = "data.json"

lock = Lock()


class ThreadedClient(ProtocolObject):
    def __init__(self, conn):
        super().__init__(conn)
        self.buffer = ""
        self.username = None
        self.lock = lock

        initial = self.get_command()
        if initial != "1":
            print("Unexpected initialisation value received. "
                  "Closing connection.")
            self.conn.close()
            return
        
        self.send_command("9")
        while True:
            command = self.get_command()
            if not command:
                break
            # Split command into control byte and the rest of the information
            if len(command) > 1:
                control, command = command[0], command[1:]
            else:
                control = command

            # Do stuff with command
            if control == "&":
                self.log_in(command)
            elif control == "$":
                self.register(command)
            elif control == "+":
                self.check_for_messages()
            elif control == "*":
                self.read_message()
            elif control == "%":
                self.send_message()

        self.conn.close()

    def log_in(self, creds):
        username, password = creds.split(",")
        users = load(self.lock)
        if username in users and users[username][0] == password:
            print("Logged in with " + username + " : " + password)
            self.username = username
            self.send_command("=")
        else:
            print("Failed login with " + username + " : " + password)
            self.send_command("!")

    def register(self, creds):
        username, password = creds.split(",")
        users = load(self.lock)
        if username not in users:
            users[username] = [password, ["server", "Thank you for using this mail application"]]
            store(users, self.lock)
            print("Successfully registered " + username + " : " + password)
            self.send_command("=")

        else:
            print("Failed to register " + username + " : " + password)
            self.send_command("!")

    def check_for_messages(self):
        # Get the number of messages that the user hasn't read
        data = load(self.lock)
        messages = data[self.username]

        # -1 because the first item is the users password
        new_messages = str(len(messages) - 1)
        self.send_command("-" + new_messages)

    def read_message(self):
        data = load(self.lock)
        # First check if there is a message to send:
        messages = data[self.username]
        if len(messages) - 1 == 0:
            # There are no messages
            self.send_command("*,")
        else:
            message = messages[1]
            self.send_command("*" + message[0] + "," + message[1])

            # Now we need to delete it from our database
            del data[self.username][1]
            store(data, self.lock)

    def send_message(self):
        # First check if the user exists
        while True:
            user = self.get_command()
            users = load(self.lock)
            if user in users:
                self.send_command("=")
                break
            else:
                self.send_command("!")
        message = self.get_command()
        assert message[0] == "~"
        message = message[1:]
        users[user].append([self.username, message])
        store(users, self.lock)


def create_threaded_client(conn, address):
    _ = ThreadedClient(conn)
    print(str(datetime.now()) + ": Lost connection with: " + address[0] + " : " + str(address[1]))


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))
# except socket.error as e:
#    raise SystemError("Connection not made")

s.listen(5)

print(str(datetime.now()) + ": Waiting for connection...")

while True:
    connection, addr = s.accept()
    print(str(datetime.now()) + ": Connected to: " + addr[0] + " : " + str(addr[1]))
    t = Thread(target=create_threaded_client, args=(connection, addr))
    t.start()
