from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter as tk

clients = {}


def broadcast_message(sender_socket, message):
    for client_socket, username in clients.items():
        if client_socket != sender_socket:
            try:
                client_socket.send(f"[Broadcast]{message}".encode())
            except Exception as e:
                print(f"Error sending message to {username}: {e}")
                client_socket.close()
                del clients[client_socket]
                update_user_list()


def route_message(sender_socket, message):
    try:
        if ':' in message:
            target_user, actual_message = message.split(':', 1)
            target_user = target_user.strip()
            actual_message = actual_message.strip()

            for client_socket, username in clients.items():
                if username == target_user:
                    # Send to the target user
                    client_socket.send(f"[Private from {clients[sender_socket]}]: {actual_message}".encode())
                    # Confirm back to the sender
                    sender_socket.send(f"[Private to {target_user}]: {actual_message}".encode())
                    return
            # Notify sender if the target user is not found
            sender_socket.send(f"[Server] User '{target_user}' not found.".encode())
        else:
            # Broadcast if no target user specified
            broadcast_message(sender_socket, f"{clients[sender_socket]}: {message}")
    except Exception as e:
        print(f"Error routing message: {e}")


def handle_client(client_socket):
    try:
        username = client_socket.recv(1500).decode().strip()
        if not username or username in clients.values():
            client_socket.send("[Server] Invalid or duplicate username.".encode())
            client_socket.close()
            return

        clients[client_socket] = username
        log_message(f"[Server] User '{username}' connected.")
        broadcast_message(client_socket, f"[Server] User '{username}' has joined the chat.")

        while True:
            message = client_socket.recv(1500).decode()
            if message.lower() == 'exit':
                break
            route_message(client_socket, message)
    except Exception as e:
        print(f"Error handling client: {e}")

    log_message(f"[Server] User '{clients[client_socket]}' disconnected.")
    broadcast_message(client_socket, f"[Server] User '{clients[client_socket]}' has left the chat.")
    del clients[client_socket]
    client_socket.close()
    update_user_list()


def start_server():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8080))
    server_socket.listen()
    log_message("[Server] Server started on 127.0.0.1:8080...")

    while True:
        client_socket, client_address = server_socket.accept()
        log_message(f"[Server] Connection from {client_address}")
        Thread(target=handle_client, args=(client_socket,)).start()
        update_user_list()


def update_user_list():
    user_list = ",".join(clients.values())
    for client_socket in clients:
        try:
            client_socket.send(f"[UserList]{user_list}".encode())
        except Exception as e:
            print(f"Error updating user list: {e}")


def log_message(message):
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, f'{message}\n')
    log_area.config(state=tk.DISABLED)
    log_area.yview(tk.END)


# GUI
window = tk.Tk()
window.title("Server")
window.geometry("300x200")

log_area = tk.Text(window, state='disabled')
log_area.pack(expand=True, fill='both')

server_thread = Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

window.mainloop()
