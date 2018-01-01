class ProtocolObject:
    def __init__(self, conn):
        self.buffer = ""
        self.conn = conn

    def get_command(self):
        # Set command length to 2 which is default
        command_length = 2

        while True:
            data = self.conn.recv(command_length).decode("utf-8")
            if not data:
                return ""

            self.buffer += data

            if not self.buffer[0] in ["#", ":"]:
                # If the buffer doesn't begin with ":" or "#",
                # then we have received an invalid command
                print("Unexpected command received...")
                print("Closing connection...")
                return ""

            if self.buffer[0] == "#":
                # We have a variable length buffer, so we need to get the
                # length of the command
                for i in range(len(self.buffer)):
                    # We check for the ":" because the number in between the
                    # "#" and ":" is the length of the command
                    if self.buffer[i] == ":":
                        # Remove the variable command length bit
                        _, command_length, self.buffer = \
                            self.buffer[0], int(self.buffer[1:i]), self.buffer[i:]
                        break

            if self.buffer[0] == ":":
                if len(self.buffer) >= command_length:
                    # Split the buffer into the first 8 chars (the command),
                    # leaving the rest in the buffer, also binning the first `:`
                    _, command, self.buffer = \
                        self.buffer[0], self.buffer[1:command_length], \
                        self.buffer[command_length:]
                    return command
                    # Ignore if not true, as it will just check again next time

    def send_command(self, command):
        if len(command) == 1:
            # Fixed length command
            to_send = ":" + command
        else:
            # Variable length command
            to_send = "#" + str(len(command) + 1) + ":" + command
        self.conn.sendall(to_send.encode("utf-8"))
