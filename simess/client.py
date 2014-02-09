import sys
import socket
from simess.assets import client_strings


class SiMessClient():

    def __init__(self, host="localhost", port=5000, buffer_size=4096):
        self.host, self.port = host, port
        self.buffer_size = buffer_size

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(2)

        self.connection_list = [sys.stdin, self.s]

        self.nickname = str(input("Nickname: "))

        try:
            self.s.connect((host, port))
            self.s.send(self.nickname.encode())
        except socket.error:
            print(client_strings.client_error_str["Unable to connect"])
            sys.exit()
        else:
            print(client_strings.client_success_str["Connection Successful"].format(self.nickname))

    def __del__(self):
        self.close()

    def prompt(self, symbol="@", text=""):
        sys.stdout.write(client_strings.prompt_str.format(str(symbol), str(text)))
        sys.stdout.flush()

    def functions(self, function):
        functions_list = {
            "/q": "self.close",
            "/spam": "self.spam"
        }

        f = str(function).lower()

        if f in functions_list.keys():
            functions_list[f]()
        else:
            print(client_strings.client_error_str["Unknown Command"])

    def spam(self):
        for i in range(0, 10):
            self.data_send(str(i).encode())

    def message_send(self):
        data = str(sys.stdin.readline()).strip()
        if data[0] == '/':
            self.functions(data)
        else:
            self.data_send(data.encode())

        self.prompt()

    def data_send(self, message):
        self.s.send(message)

    def data_receive(self):
        try:
            data = bytes(self.s.recv(self.buffer_size)).decode()
        except socket.error:
            print(client_strings.client_error_str["Disconnected from server"])
            self.close()
        else:
            if not data:
                print(client_strings.client_error_str["Disconnected from server"])
                self.close()
            else:
                if data[0] == '/':
                    self.functions(data)
                else:
                    print(data)
                    self.prompt('+')

    def close(self):
        del self.host, \
            self.port, \
            self.buffer_size, \
            self.connection_list, \
            self.nickname

        self.s.close()
        print("Goodbye!")
        sys.exit()