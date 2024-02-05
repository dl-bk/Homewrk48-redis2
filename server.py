import redis 
import socket
import threading
import time

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def handle_client(client_socket, username):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"{username}: {message}")
            store_message(username, message)
            broadcast_message(username, message)
    
    except Exception as e:
        print(f"ERROR: Exception in handle_client: {str(e)}")
    
    finally:
        remove_user(username)
        client_socket.close()

def store_message(username, message):
    message_id = f'message:{username}_{time.time()}'
    redis_client.set(message_id, message)

def broadcast_message(sender, message):
    active_users = get_active_users()
    for user in active_users:
        if user != sender:
            current_socket = active_sockets[user]
            current_socket.send(f'{sender}: {message}'.encode('utf-8'))

def remove_user(username):
    active_sockets.pop(username)
    redis_client.delete(f'user_info:{username}')
    redis_client.srem('active_users', username)

def get_active_users():
    return redis_client.smembers('active_users')

try:
    redis_client.ping()
except redis.ConnectionError:
    print("ERROR Unable to connect to Redis. Make sure Redis is running.")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8080))
server.listen(5)
print('INFO: Server listening on port 8080')
active_sockets = {}
try:
    while True:
        client_socket, address = server.accept()
        print(f"Connected with: {address}")
        username = client_socket.recv(1024).decode('utf-8')

        active_sockets[username] = client_socket

        redis_client.sadd('active_users', username)

        client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
        client_thread.start()

except KeyboardInterrupt:
    print("Server shut down")
except Exception as e:
    print(f"ERROR: Exception in main: {str(e)}")
finally:
    server.close()