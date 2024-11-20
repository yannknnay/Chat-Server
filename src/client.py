from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk


def send_message(client_socket, target_user, text_input, text_area):
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


def receive_message(client_socket, frames, notebook):
    while True:
        try:
            message = client_socket.recv(1500).decode()

            if message.startswith("[UserList]"):
                user_list = message.replace("[UserList]", "").split(",")
                update_user_frames(frames, notebook, user_list)
            elif message.startswith("[Broadcast]"):
                broadcast_message = message.replace("[Broadcast]", "").strip()
                update_broadcast_frame(frames, broadcast_message)
            elif message.startswith("[Private from "):
                sender = message.split(']')[0].replace("[Private from ", "").strip()
                private_message = message.split(']:', 1)[1].strip()
                update_private_frame(frames, notebook, sender, f"{sender}: {private_message}")
            elif message.startswith("[Private to "):
                target_user = message.split(']')[0].replace("[Private to ", "").strip()
                private_message = message.split(']:', 1)[1].strip()
                update_private_frame(frames, notebook, target_user, f"You: {private_message}")
            else:
                print(f"Unhandled message: {message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def update_broadcast_frame(frames, message):
    text_area = frames["Broadcast"]["text_area"]
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, f'{message}\n')
    text_area.config(state=tk.DISABLED)
    text_area.yview(tk.END)


def update_private_frame(frames, notebook, user, message):
    if user not in frames:
        create_private_frame(frames, notebook, user)
    text_area = frames[user]["text_area"]
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, f'{message}\n')
    text_area.config(state=tk.DISABLED)
    text_area.yview(tk.END)


def create_private_frame(frames, notebook, user):
    private_frame = tk.Frame(notebook)
    notebook.add(private_frame, text=user)

    text_area = tk.Text(private_frame, state='disabled')
    text_area.pack(expand=True, fill='both')

    text_input = tk.Entry(private_frame)
    text_input.pack(fill='x', pady=5)

    send_button = tk.Button(private_frame, text="Send",
                            command=lambda: send_message(client_socket, user, text_input, text_area))
    send_button.pack(pady=5)

    frames[user] = {"frame": private_frame, "text_area": text_area, "text_input": text_input}


def get_username():
    username = ""
    while not username:
        username = simpledialog.askstring("Username", "Enter your username:")
        if not username:
            messagebox.showerror("Error", "Username cannot be empty.")
    return username


def update_user_frames(frames, notebook, user_list):
    for user in user_list:
        if user not in frames and user != username:  # Evita criar frame para si mesmo
            create_private_frame(frames, notebook, user)

    # Remover frames de usuários que saíram
    existing_users = list(frames.keys())
    for user in existing_users:
        if user not in user_list and user != "Broadcast":
            notebook.forget(frames[user]["frame"])
            del frames[user]


# GUI
window = tk.Tk()
window.title("Chat Client")
window.geometry("500x500")

notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill='both')

frames = {}

broadcast_frame = tk.Frame(notebook)
notebook.add(broadcast_frame, text="Broadcast")

text_area_broadcast = tk.Text(broadcast_frame, state='disabled')
text_area_broadcast.pack(expand=True, fill='both')

text_input_broadcast = tk.Entry(broadcast_frame)
text_input_broadcast.pack(fill='x', pady=5)

send_button_broadcast = tk.Button(broadcast_frame, text="Send",
                                  command=lambda: send_message(client_socket, None, text_input_broadcast,
                                                               text_area_broadcast))
send_button_broadcast.pack(pady=5)

frames["Broadcast"] = {"frame": broadcast_frame, "text_area": text_area_broadcast, "text_input": text_input_broadcast}

username = get_username()

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8080))
client_socket.send(username.encode())

Thread(target=receive_message, args=(client_socket, frames, notebook), daemon=True).start()

window.mainloop()
