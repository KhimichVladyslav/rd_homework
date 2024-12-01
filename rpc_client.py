import socket
import select
import sys


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('0.0.0.0', 53554))
    print("Connected to the server at 0.0.0.0:53554")

    while True:
        try:
            read_sockets, _, _ = select.select([client_socket, sys.stdin], [], [])
            for notified_socket in read_sockets:
                if notified_socket == client_socket:
                    message = client_socket.recv(1024).decode('utf-8').strip()
                    if not message:
                        print("Server disconnected.")
                        client_socket.close()
                        return
                    print(message)
                else:
                    message = input().strip()
                    if message:
                        client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            return


start_client()
