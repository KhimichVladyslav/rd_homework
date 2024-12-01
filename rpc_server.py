import socket
import select
from collections import defaultdict


def processing_data(dct: dict, command):
    parts = command.split(' ')
    comm = parts[0]

    if comm == 'get':
        key = parts[1]
        return f'Result: {dct[key]}' if dct[key] else 'Error: empty value'

    elif comm == 'set':
        key, value = parts[-2:]

        try:
            dct[key] = int(value)
            return b''
        except ValueError:
            return 'Error: not a number'

    elif comm == 'getkeys':
        return " ".join(list(dct.keys()))

    return 'Error: invalid command format'


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 53554))
    server_socket.listen(1)
    print("Server is listening on port 53554...")

    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    data = defaultdict(int)

    while True:
        try:
            read_sockets, _, _ = select.select([client_socket], [], [])
            for notified_socket in read_sockets:
                message = notified_socket.recv(1024).decode('utf-8').strip()

                if not message:
                    print("Client disconnected.")
                    client_socket.close()
                    server_socket.close()
                    return

                print(f"Received: {message}")
                response = processing_data(data, message)
                client_socket.sendall(response.encode('utf-8') if response else b'')

        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()
            server_socket.close()
            return


start_server()
