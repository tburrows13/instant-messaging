import socket

from BaseClass import ProtocolObject

with open("address.txt") as file:
    file = file.readlines()
    host = file[0].strip()[5:]
    port = int(file[1].strip()[5:])


print(host, port)


class Client(ProtocolObject):
    def __init__(self):
        conn = socket.socket()
        super().__init__(conn)
        # '81.135.254.250'
        self.conn.connect((host, port))

        # Check that we are connected correctly
        self.send_command("1")
        init = self.get_command()
        if init == "9":
            print("Successfully connected")
        else:
            raise ConnectionError("Unexpected return value from server")

    def start(self):
        print("Would you like to:")
        print("1 Log in")
        print("2 Register")
        print("3 Quit")
        while True:
            inp = input("- ")
            if inp in ("1", "2", "3"):
                break
            else:
                print("The input is not valid\n")
        if inp == "3":
            return True
        elif inp == "2":
            self.register()
        elif inp == "1":
            self.log_in()
        # Register calls log_in(), so we will always be logged in at this point
        while True:
            self.check_for_messages()

            print("Would you like to:")
            print("1 Read the oldest message")
            print("2 Send a message")
            print("3 Check for new messages")
            print("4 Log out")
            print("5 Quit")
            while True:
                inp = input("- ")
                if inp in ("1", "2", "3", "4", "5"):
                    break
                else:
                    print("Invalid input\n")
            print()
            if inp == "1":
                self.read_message()
            elif inp == "2":
                self.send_message()
            # We don't check for 3, as we just go back, and it calls
            # check_for_messages() anyway
            elif inp == "4":
                print("\nLogging out...\n\n\n")
                return False
            elif inp == "5":
                print("\nQuitting...\n\n\n")
                return True

    def log_in(self):
        while True:
            username = input("Username: ")
            password = input("Password: ")

            # Validation here
            con = False
            for name in (username, password):
                if name.find(",") != -1:
                    print("Username or password must not contain commas\n")
                    con = True
                    break
                if len(name) < 2:
                    print("Username or password must be greater than 1 character\n")
                    con = True
                    break
            if con:
                continue

            self.send_command("&" + username + "," + password)
            confirm = self.get_command()
            if confirm == "=":
                break
            else:
                print("\nIncorrect credentials, press enter to try again")
                print("or press 1 to register")
                a = input()
                if a == 1:
                    print("Registering...\n")
                    self.register()
        print("Successful login!\n\n")

    def register(self):
        while True:
            username = input("Username: ")
            password = input("Password: ")
            # Validation here
            con = False
            for name in (username, password):
                if name.find(",") != -1:
                    print("Username or password must not contain commas\n")
                    con = True
                    break
                if len(name) < 2:
                    print("Username or password must be greater than 1 character\n")
                    con = True
                    break
            if con:
                continue
            self.send_command("$" + username + "," + password)
            confirm = self.get_command()
            if confirm == "=":
                break
            else:
                print("Username already taken, please try again\n")
        print("Successfully registered!\n\nNow please log in:")
        self.log_in()

    def check_for_messages(self):
        print("Checking for new messages...")
        self.send_command("+")
        reply = self.get_command()
        assert reply[0] == "-"
        new_messages = int(reply[1:])
        if new_messages > 1:
            print("You have " + str(new_messages) + " unread messages!\n")
        elif new_messages == 1:
            print("You have 1 unread message!\n")
        else:
            print("You have no new messages\n")
        return new_messages

    def read_message(self):
        print("Getting oldest unread message...\n")
        self.send_command("*")
        reply = self.get_command()
        assert reply[0] == "*"
        if reply[1] == ",":
            print("There are no new messages to display")
        else:
            # Split the reply into the user its from, and the message
            _, message = reply[0], reply[1:]
            split_index = message.find(",")
            userfrom, message = message[:split_index], message[split_index+1:]
            # Now we have removed the dividing comma
            print("From: " + userfrom)
            print(message)
            print("\n1 - Reply")
            print("2 - Continue")
            inp = input("- ")
            if inp == "1":
                self.send_message(userfrom)
        print()

    def send_message(self, user=None):
        self.send_command("%")
        if user is None:
            while True:
                user = input("Send to: ")
                self.send_command(user)
                reply = self.get_command()
                if reply == "=":
                    break
                else:
                    print("Invalid username, please select another one\n")
        else:
            print("Replying to " + user)
            self.send_command(user)
            reply = self.get_command()
            assert reply == "="
        print("Input message: ")
        message = input()
        self.send_command("~" + message)
        print("\nMessage sent!\n")


if __name__ == "__main__":
    done = False
    while not done:
        done = Client().start()
