import socket
import threading

clients = []
channels = {}
subscriptions = {}
restricted_words = ["badword1", "badword2"]

def start_server(host='127.0.0.1', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Client connected from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            handle_message(client_socket, message)
        except:
            break
    clients.remove(client_socket)
    client_socket.close()

def handle_message(client_socket, message):
    parts = message.split("|")
    command = parts[0]

    if command == "GET_CHANNELS":
        send_channels(client_socket)
    elif command == "PUBLISH":
        publish_channel(client_socket, parts[1], parts[2])
    elif command == "DELETE":
        delete_channel(client_socket, parts[1])
    elif command == "SUBSCRIBE":
        subscribe_channel(client_socket, parts[1])
    elif command == "UNSUBSCRIBE":
        unsubscribe_channel(client_socket, parts[1])
    elif command == "NEWS":
        post_news(client_socket, parts[1], parts[2])

def send_channels(client_socket):
    if channels:
        response = "Channels:\n" + "\n".join([f"{name}: {desc}" for name, desc in channels.items()])
    else:
        response = "No channels available"
    client_socket.send(response.encode())

def publish_channel(client_socket, name, desc):
    if name in channels:
        client_socket.send(f"Channel already exists: {name}".encode())
        return
    channels[name] = desc
    subscriptions[name] = []
    notify_clients(f"New channel: {name}: {desc}")

def delete_channel(client_socket, name):
    if name in channels:
        del channels[name]
        del subscriptions[name]
        notify_clients(f"Deleted channel: {name}")

def subscribe_channel(client_socket, name):
    if name in channels:
        if client_socket not in subscriptions[name]:
            subscriptions[name].append(client_socket)
            client_socket.send(f"Subscribed to channel: {name}".encode())
        else:
            client_socket.send(f"Already subscribed to channel: {name}".encode())
    else:
        client_socket.send(f"Channel not found: {name}".encode())

def unsubscribe_channel(client_socket, name):
    if name in channels and client_socket in subscriptions[name]:
        subscriptions[name].remove(client_socket)
        client_socket.send(f"Unsubscribed from channel: {name}".encode())
    else:
        client_socket.send(f"Not subscribed to channel: {name}".encode())

def post_news(client_socket, channel, news):
    if channel in subscriptions:
        if any(word in news for word in restricted_words):
            client_socket.send("Your news contains restricted words and cannot be posted.".encode())
            return
        for subscriber in subscriptions[channel]:
            try:
                subscriber.send(f"News in {channel}: {news}".encode())
            except:
                subscriptions[channel].remove(subscriber)
        client_socket.send("News posted successfully.".encode())
    else:
        client_socket.send("Channel not found or no subscribers.".encode())

def notify_clients(message):
    for client in clients:
        try:
            client.send(message.encode())
        except:
            clients.remove(client)

if __name__ == "__main__":
    start_server()
