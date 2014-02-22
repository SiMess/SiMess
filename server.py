import socket
import select
from simess.server import SiMessServer


if __name__ == "__main__":

    server = SiMessServer()

    print("[ SiMess server started on port {0} ]\n".format(str(server.port)))

    running = True

    while running:

        try:
            read_ready, write_ready, error_ready = select.select(server.connection_list, [], [])

            try:
                for sock in read_ready:
                    if sock == server.s:
                        server.add_connection()
                    else:
                        try:
                            data = server.message_receive(sock)
                            if data:
                                server.message_broadcast(sock, data)
                        except socket.error:
                            server.remove_connection(sock)
                            continue
            except KeyboardInterrupt:
                break

        except KeyboardInterrupt:
            break

    server.close()
    exit()
