from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

def send_message(client_socket, text_area, text_input, target_user=None):
    message = text_input.get()
    if not message:
        return

    if target_user:
        message = f"{target_user}: {message}"

    try:
        client_socket.send(message.encode())
        text_area.config(state=tk.NORMAL)
        text_area.insert(tk.END, f'You: {message}\n')
        text_area.config(state=tk.DISABLED)
        text_input.delete(0, tk.END)
    except Exception as e:
        print(f"Error sending message: {e}")

def receive_message(client_socket, text_area, user_list):
    while True:
        try:
            message = client_socket.recv(1500).decode()
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, f'{message}\n')
            text_area.config(state=tk.DISABLED)
            text_area.yview(tk.END)

            # Update user list when a new list is received from the server
            if "Online Users" in message:
                users = message.split(":")[1].strip()
                update_user_list(user_list, users.split(","))
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

def update_user_list(user_list, users):
    user_list.delete(0, tk.END)
    for user in users:
        user_list.insert(tk.END, user)

def get_username():
    username = ""
    while not username:
        username = simpledialog.askstring("Username", "Enter your username:")
        if not username:
            messagebox.showerror("Error", "Username cannot be empty.")
    return username

window = tk.Tk()
window.title("Chat Client")
window.geometry("500x500")

notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill='both')

broadcast_frame = tk.Frame(notebook)
notebook.add(broadcast_frame, text="Broadcast")

private_frame = tk.Frame(notebook)
notebook.add(private_frame, text="Private")

text_area_broadcast = tk.Text(broadcast_frame, state='disabled')
text_area_broadcast.grid(row=0, column=0, sticky='nsew')

text_input_broadcast = tk.Entry(broadcast_frame)
text_input_broadcast.grid(row=1, column=0, sticky='ew', pady=5)

text_area_private = tk.Text(private_frame, state='disabled')
text_area_private.grid(row=0, column=0, rowspan=4, sticky='nsew')

text_input_private = tk.Entry(private_frame)
text_input_private.grid(row=4, column=0, sticky='ew', pady=5)

user_list = tk.Listbox(private_frame)
user_list.grid(row=0, column=1, rowspan=4, sticky='ns', padx=5)

send_button_private = tk.Button(private_frame, text="Send", command=lambda: send_message(client_socket, text_area_private, text_input_private, target_user=user_list.get(tk.ACTIVE)))
send_button_private.grid(row=5, column=1, sticky='ew', pady=5)

username = get_username()

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8080))
client_socket.send(username.encode())

send_button_broadcast = tk.Button(broadcast_frame, text="Send", command=lambda: send_message(client_socket, text_area_broadcast, text_input_broadcast))
send_button_broadcast.grid(row=2, column=0, pady=5)

Thread(target=receive_message, args=(client_socket, text_area_broadcast, user_list), daemon=True).start()

# Configure grid layout for both frames to expand correctly
broadcast_frame.grid_rowconfigure(0, weight=1)
broadcast_frame.grid_columnconfigure(0, weight=1)

private_frame.grid_rowconfigure(0, weight=3)
private_frame.grid_rowconfigure(4, weight=1)
private_frame.grid_columnconfigure(0, weight=3)
private_frame.grid_columnconfigure(1, weight=1)

window.mainloop()
