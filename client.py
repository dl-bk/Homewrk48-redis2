import socket
import threading

HOST = "localhost"
PORT = 8080

def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            print('\n', message)
    except Exception as e:
        print(f"ERROR Exception in receive_messages: {str(e)}")

def send_messages(client_socket):
    try:
        while True:
            message = input("Enter your message: ")
            client_socket.send(message.encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] Exception in send_messages: {str(e)}")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((HOST, PORT))
    print("Connected to the server")

    username = input("Enter your name: ")
    client_socket.send(username.encode('utf-8'))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))

    receive_thread.start()

    try:
        while True:
            message = input("Enter your message: ")
            client_socket.send(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("Disconnected from server")
    except Exception as e:
        print(f"[ERROR] Exception in send_messages: {str(e)}")


except Exception as e:
    print(f"ERROR: Exception in main: {str(e)}")

finally:
    client_socket.close()
