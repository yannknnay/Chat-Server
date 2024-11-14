import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

client_sockets = []


def send_massage(text_area, text_input):
    massage = text_input.get()
    if massage:
        for client_socket in client_sockets:
            try:
                client_socket.send(massage.encode())
            except Exception as e:
                print(f"Error sending message to a client: {e}")
                client_sockets.remove(client_socket)
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, 'You: ' + massage + '\n')
        text_area.config(state=tk.DISABLED)
        text_input.delete(0, tk.END)


def receive_massage(client_socket, text_area):
    while True:
        try:
            massage = client_socket.recv(1500).decode()
            if massage.lower() == 'exit':
                client_socket.close()
                client_sockets.remove(client_socket)
                break
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, 'Client: ' + massage + '\n')
            text_area.config(state=tk.DISABLED)
            text_area.yview(tk.END)
        except Exception as e:
            print(f"Error receiving message from a client: {e}")
            client_sockets.remove(client_socket)
            break


def start_server(text_area, host='127.0.0.1', port=8080):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f'Server started on {host}:{port} and waiting for connections...')

    while True:
        client_socket, client_address = server_socket.accept()
        client_sockets.append(client_socket)
        print(f'Connection from {client_address}')

        thread = Thread(target=receive_massage, args=(client_socket, text_area))
        thread.daemon = True
        thread.start()


# Graphical Interface
window = tk.Tk()
window.title("Fala Aí")
window.geometry("400x400")

text_area = tk.Text(window, height=5, width=50, state="disabled")
text_area.pack(pady=10)

text_input = tk.Entry(window, width=50)
text_input.pack(pady=10)

send_button = tk.Button(window, text="Send", width=20,
                        command=lambda: send_massage(text_area, text_input))
send_button.pack(pady=10)

# Start server in a new thread
server_thread = Thread(target=start_server, args=(text_area,))
server_thread.daemon = True
server_thread.start()

window.mainloop()
