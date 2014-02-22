import socket
from time import gmtime, strftime
from simess.assets import server_strings


class SiMessServer():

    def __init__(self, host="127.0.0.1", port=5000, buffer_size=4096, waiting_list=10):

        self.host, self.port = host, port
        self.buffer_size = buffer_size
        self.waiting_list = waiting_list

        self.connection_list = []
        self.nick_dict = {}

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.s.listen(self.waiting_list)

        self.connection_list.append(self.s)

    def add_connection(self, sock=None, report=True, nick=None):

        if not sock:
            sock, addr = self.s.accept()

        peername = [sock.getpeername()[0], sock.getpeername()[1]]

        if nick:
            nickname = nick
        else:
            nickname = bytes(sock.recv(self.buffer_size)).decode()

        self.connection_list.append(sock)
        self.nick_dict.update({sock.getpeername(): nickname})

        if report:
            timestamp = gmtime()

            kwargs = {
                "sock": sock,
                "event": server_strings.client_status_str[1],
                "nick": nickname,
                "peer": peername,
                "timestamp": timestamp,
                "share": True
            }

            self.event_report(**kwargs)

    def remove_connection(self, sock):

        peername = [sock.getpeername()[0], sock.getpeername()[1]]
        nickname = str(self.nick_dict[sock.getpeername()])
        timestamp = gmtime()

        kwargs = {
            "sock": sock,
            "event": server_strings.client_status_str[0],
            "nick": nickname,
            "peer": peername,
            "timestamp": timestamp,
            "share": True
        }

        self.event_report(**kwargs)

        del self.nick_dict[sock.getpeername()]
        self.connection_list.remove(sock)
        sock.close()

    def event_report(self, sock, event, nick, peer, timestamp, share=False):

        kwargs = {
            "sock": sock,
            "event": event,
            "nick": nick,
            "peer": peer,
            "timestamp": timestamp
        }

        self.event_print(**kwargs)

        if share:
            self.event_share(**kwargs)

    def event_print(self, sock, event, nick, peer, timestamp):

        print(server_strings.server_events_str["Server Event Print"].format(
            event, nick, peer[0], peer[1], strftime("%d-%b-%Y %I:%M:%S %p", timestamp)
        ))

    def event_share(self, sock, event, nick, peer, timestamp):

        data = str(server_strings.server_events_str["Server Event Share"].format(
            nick, peer[0], peer[1], event, strftime("%I:%M:%S %p", timestamp)
        )).encode()

        self.data_broadcast(sock, data)

    def client_functions(self, func, sock):

        functions = dict()

        f = functions.get(func)

        if f == "":
            pass
        else:
            sock.send(server_strings.server_error_str["Unknown Command"].strip().encode())
            print(server_strings.server_error_str["Unknown Command"])

    def server_functions(self, func, sock):

        functions = {
            "//q": "shutdown"
        }

        f = functions.get(func)

        if f == "shutdown":
            raise KeyboardInterrupt
        else:
            sock.send(server_strings.server_error_str["Unknown Command"].strip().encode())
            print(server_strings.server_error_str["Unknown Command"])

    def message_receive(self, sock):

        data = bytes(sock.recv(self.buffer_size)).decode()

        if data:
            if data[0] == '/' and data[1] != '/':
                self.client_functions(data, sock)
            elif data[0] == '/' and data[1] == '/':
                self.server_functions(data, sock)
            else:
                return data
        else:
            self.remove_connection(sock)
            return None

    def message_broadcast(self, sock, message):

        nickname = self.nick_dict[sock.getpeername()]
        timestamp = gmtime()

        data = str(server_strings.client_message_broadcast_str.format(
            message, nickname, strftime("%I:%M:%S %p", timestamp)
        )).encode()

        self.data_broadcast(sock, data, True)

    def data_broadcast(self, sock, message, client_message=False):

        for sk in self.connection_list:
            if sk != self.s and sk != sock:
                try:
                    sk.send(message)
                except socket.error:
                    self.remove_connection(sk)
            elif sk == sock and client_message:
                try:
                    sk.send(server_strings.server_success_reply_str["Sent"].encode())
                except socket.error:
                    self.remove_connection(sk)

    def close(self):

        print(server_strings.server_events_str["Server Shutting Down"])

        del self.host, \
            self.port, \
            self.buffer_size, \
            self.waiting_list, \
            self.connection_list, \
            self.nick_dict

        self.s.close()
