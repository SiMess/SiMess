import socket
import select
import time
# import curses

buffer_size = 4096  # Advisable to keep it as an exponent of 2
host, port = "", 5000
waiting_list = 10

# List to keep track of socket descriptors
connection_list = []

# Dictionary for nicknames
nick_dict = {}


class SiMess():

    def __init__(self):
        pass

    def add_client(self, sock_source):
        # Handle the case in which there is a new connection received through server_socket
        sock_new, addr = sock_source.accept()
        connection_list.append(sock_new)

        nickname_new = bytes(sock_new.recv(buffer_size)).decode()
        peer_name_new = str(sock_new.getpeername()[0]) + ':' + str(sock_new.getpeername()[1])
        nick_dict.update({peer_name_new: nickname_new})

        print("[ Action: Connected\n  Nickname: {0}\n  IP: {1} Port: {2}\n  Timestamp: {3} ]\n".format(
            nickname_new, peer_name_new.split(':')[0], peer_name_new.split(':')[1], time.ctime(time.time())
        ))

        new_client_msg = str("#> [ {0} ({1}:{2}) Entered room ]".format(
            nickname_new, peer_name_new.split(':')[0], peer_name_new.split(':')[1]
        )).encode()

        self.broadcast_data(sock_new, new_client_msg)

    def remove_client(self, sock_source):
        peer_name = str(sock_source.getpeername()[0]) + ':' + str(sock.getpeername()[1])
        nickname = str(nick_dict[peer_name])

        print("[ Action: Disconnected\n  Nickname: {0}\n  IP: {1} Port: {2}\n  Timestamp: {3} ]\n".format(
            nickname, peer_name.split(':')[0], peer_name.split(':')[1], time.ctime(time.time())
        ))

        offline_msg = str("#> [ {0} ({1}:{2}) Leaved room ]".format(
            nickname, peer_name.split(':')[0], peer_name.split(':')[1]
        )).encode()
        self.broadcast_data(sock_source, offline_msg)

        del nick_dict[peer_name]
        sock.close()
        connection_list.remove(sock)

    # Function to broadcast chat messages to all connected clients
    def broadcast_data(self, sock_source, message):
        # Do not send the message to master socket and the client who has send us the message
        for sk in connection_list:
            if sk != server and sk != sock_source:
                try:
                    sk.send(message)
                except socket.error:
                    # Broken socket connection may be, chat client pressed ctrl+c for example
                    sk.close()
                    connection_list.remove(sk)

    def broadcast_msg(self, sock_source, message):
        peer_name = str(sock_source.getpeername()[0]) + ':' + str(sock.getpeername()[1])
        nickname = str(nick_dict[peer_name])
        broadcast_msg = str("\t{1} <{0}".format(nickname, message)).encode()
        self.broadcast_data(sock_source, broadcast_msg)


if __name__ == "__main__":

    server_simess = SiMess()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(waiting_list)

    # Add server socket to the list of readable connections
    connection_list.append(server)

    # Add nickname for the server
    nick_dict.update({"127.0.0.1" + ':' + str(port): "Server"})

    running = True

    # std_scr = curses.initscr()
    # std_scr.clear()

    print("[ SiMess server started on port {0} ]\n".format(str(port)))

    while running:
        # Get the list sockets which are ready to be read through select
        read_ready, write_ready, error_ready = select.select(connection_list, [], [])

        for sock in read_ready:
            #New connection
            if sock == server:
                server_simess.add_client(sock)
            #Some incoming message from a client
            else:
                # Data received from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = bytes(sock.recv(buffer_size)).decode()
                    if data == "/q" or not data:
                        raise socket.error
                    elif data:
                        server_simess.broadcast_msg(sock, data)
                except socket.error:
                    server_simess.remove_client(sock)
                    continue

    server.close()