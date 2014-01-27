import socket
import select
import sys
# import unicurses

host = None
port = None
nickname = None


def prompt():
    sys.stdout.write('@> ')
    sys.stdout.flush()

# Main function
if __name__ == "__main__":

    # stdscr = unicurses.initscr()
    # unicurses.endwin()

    if len(sys.argv) == 1:
        host = str(input("Host: "))
        port = int(input("Port: "))
        nickname = str(input("Nickname: "))
    elif len(sys.argv) == 2:
        host = sys.argv[1]
        port = int(input("Port: "))
        nickname = str(input("Nickname: "))
    elif len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
        nickname = str(input("Nickname: "))
    elif len(sys.argv) == 4:
        host = sys.argv[1]
        port = int(sys.argv[2])
        nickname = str(sys.argv[3])
    else:
        sys.exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # Connect to remote host
    try:
        s.connect((host, port))
        s.send(nickname.encode())
    except ConnectionRefusedError:
        print("\t[ Unable to connect ]")
        sys.exit()

    running = True

    print("[ Hello, {0}! You are connected to the SiMess chat server... ]".format(nickname))
    print("[ -------{0}------------------------------------------------ ]".format('-' * len(nickname)))
    prompt()

    while running:
        socket_list = [sys.stdin, s]  # sys.stdin only in Linux

        # Get the list sockets which are readable
        read_ready, write_ready, error_ready = select.select(socket_list, [], [])

        for sock in read_ready:
            # Incoming message from remote server
            if sock == s:
                try:
                    data = sock.recv(4096)
                except ConnectionResetError:
                    print("\n\t[ Disconnected from server ]")
                    s.close()
                    sys.exit()
                if not data:
                    print("\n\t[ Disconnected from server ]")
                    s.close()
                    sys.exit()
                else:
                    # Print data
                    sys.stdout.write("\n\t{0}\n".format(data.decode()))
                    prompt()

            # User entered a message
            else:
                msg = str(sys.stdin.readline()).strip()
                if msg == "/q":
                    print("Goodbye!")
                    s.close()
                    sys.exit()
                else:
                    s.send(msg.encode())
                    prompt()
