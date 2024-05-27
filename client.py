import socket
import threading

message_received_event = threading.Event()
console_lock = threading.Lock()

def connect_to_server(host='127.0.0.1', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    return client_socket

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            with console_lock:
                print(f"\nReceived: {message}")
            message_received_event.set()
        except:
            break

def send_message(client_socket, message):
    client_socket.send(message.encode())

def get_channels(client_socket):
    send_message(client_socket, "GET_CHANNELS")

def publish_channel(client_socket, name, desc):
    send_message(client_socket, f"PUBLISH|{name}|{desc}")

def delete_channel(client_socket, name):
    send_message(client_socket, f"DELETE|{name}")

def subscribe_channel(client_socket, name):
    send_message(client_socket, f"SUBSCRIBE|{name}")

def unsubscribe_channel(client_socket, name):
    send_message(client_socket, f"UNSUBSCRIBE|{name}")

def post_news(client_socket, channel, news):
    send_message(client_socket, f"NEWS|{channel}|{news}")

def print_menu():
    with console_lock:
        print("\nOptions:")
        print("1. GET_CHANNELS")
        print("2. PUBLISH")
        print("3. DELETE")
        print("4. SUBSCRIBE")
        print("5. UNSUBSCRIBE")
        print("6. POST NEWS")
        print("7. EXIT")

def main():
    global message_received_event
    client_socket = connect_to_server()
    while True:
        print_menu()
        choice = input("Enter choice: ").strip()
        if choice == "1":
            get_channels(client_socket)
            message_received_event.wait()
            message_received_event.clear()
        elif choice == "2":
            name = input("Enter channel name: ").strip()
            desc = input("Enter channel description: ").strip()
            publish_channel(client_socket, name, desc)
        elif choice == "3":
            name = input("Enter channel name: ").strip()
            delete_channel(client_socket, name)
        elif choice == "4":
            name = input("Enter channel name: ").strip()
            subscribe_channel(client_socket, name)
        elif choice == "5":
            name = input("Enter channel name: ").strip()
            unsubscribe_channel(client_socket, name)
        elif choice == "6":
            channel = input("Enter channel name: ").strip()
            news = input("Enter news content: ").strip()
            post_news(client_socket, channel, news)
        elif choice == "7":
            client_socket.close()
            break
        else:
            with console_lock:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
