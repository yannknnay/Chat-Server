import tkinter as tk
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


def send_massage(client_socket, text_area, text_input):
    massage = text_input.get()

    if massage:
        client_socket.send(massage.encode())
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, 'You:' + massage + '\n')
        text_area.config(state=tk.DISABLED)
        text_area.delete(0, tk.END)


def receive_massage(client_socket, text_area):
    while True:
        massage = client_socket.recv(1500).decode()

        if massage.lower() == 'exit':
            client_socket.close()
            break

        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, 'Server:' + massage + '\n')
        text_area.config(state=tk.DISABLED)
        text_area.yview(tk.END)


# Creating a socket and connecting to a server
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect('127.0.0.1,8080')

# Graphical Interface
window = tk.Tk()
window.title("Fala Aí")
window.geometry("400x400")

text_area = tk.Text(window, height=5, width=50, state="disabled")
text_area.pack(pady=10)

text_input = tk.Entry(window, width=50)
text_input.pack(pady=10)

send_button = tk.Button(window, text="Send", width=20,
                        command=lambda: send_massage(client_socket, text_area, text_input))
send_button.pack(pady=10)

# Threads for receiving massages
thread = Thread(target=receive_massage, args=(client_socket, text_area))
thread.daemon = True
thread.start()

window.mainloop()
