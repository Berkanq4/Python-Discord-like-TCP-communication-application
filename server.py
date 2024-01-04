from math import log
import tkinter as tk
import threading
import socket
from threading import Lock
broadcast_lock = Lock()

def clear_text_box(text_widget):
    text_widget.delete('1.0', tk.END)

def start_server():
    host = str(entry2.get())  # Get IP address from entry widget
    port = int(entry.get())  # Get port number from entry widget
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    clients = []
    aliases = []
    client_channels = {}
    channels = {
        'IF100': [],
        'SPS101': []
    }
 
    while True:
        
        def broadcast_message(message, channel, sender):
            with broadcast_lock:
                for client in channels[channel]:
                
                    if client == sender:
                        continue
                    else:
                        try:
                            client.send(f"{message}".encode('utf-8'))
                        except Exception as e:
                            print(f"Could not send message to {client}, error: {e}")
                            channels[channel].remove(client)
                            if client in clients:
                                clients.remove(client)
        def handle_client(client, alias):
            while True:
                try:
                    message = client.recv(1024).decode('utf-8')
                    if message == "disconnect123":
                        print(f"{alias} has disconnected.")
                        log_box.insert(tk.END, f"{alias} has disconnected.\n")
                        if alias in aliases:
                            aliases.remove(alias)
                        if client in clients:
                            clients.remove(client)
                        if alias in channels['IF100']:
                            channels['IF100'].remove(alias)
                        if alias in channels['SPS101']:
                            channels['SPS101'].remove(alias)
                        if alias in all_box.get("1.0", tk.END):
                            all_box.delete(f"{alias}\n")
                        client.close()
                        aliases.remove(alias)
                        break
                    if message.startswith('subscribe:'):
                        _, channel = message.split(':')
                        if client not in channels[channel]:
                            channels[channel].append(client)
                            client_channels.update({client:channel})
                            broadcast_message(f"{alias} has joined {channel}", channel, client)
                
                    elif message.startswith('unsubscribe:'):
                        _, channel = message.split(':')
                        if channel in channels and client in channels[channel]:
                            channels[channel].remove(client)
                        
                            broadcast_message(f"{alias} has left {channel}", channel, client)
                        
                    elif message.startswith('message:'):
                        _, channel, content = message.split(':', 2)
                        if client in channels[channel]:
                            broadcast_message(f"{content}", channel, client)
                        else:
                            client.send("You are not subscribed to this channel.".encode('utf-8'))
                    else:
                        client.send("Invalid message format.".encode('utf-8'))
                    
                except Exception as e:
                    print(f"{alias}: {str(e)}")
                    for ch in channels.values():
                        if client in ch:
                            ch.remove(client)
                    client.close()
                    break



        def receive():
            while True:
                print('Server is running and listening ...')
                log_box.insert(tk.END, "Server is running and listening ...\n")
                client, address = server.accept()
                print(f'connection is established with {str(address)}')
                log_box.insert(tk.END, f"connection is established with {str(address)}\n")
            
                # Receive the initial message from the client
                client.send('alias?'.encode('utf-8'))
                alias = client.recv(1024).decode('utf-8')
                if alias in aliases:
                    client.send("This alias is already in use.".encode('utf-8'))
                          
                else:
                    client.send('Welcome to the server!'.encode('utf-8'))
                    aliases.append(alias)
                    clients.append(client)
                    clear_text_box(all_box)
                    clear_text_box(if100_box)
                    clear_text_box(sps101_box)
                    for i in aliases:
                        all_box.insert(tk.END, f"{i}\n")
                    for i in channels['IF100']:
                        if100_box.insert(tk.END, f"{i}\n")
                    for i in channels['SPS101']:
                        sps101_box.insert(tk.END, f"{i}\n")
                    print(f'The alias of this client is {alias}'.encode('utf-8'))
                    log_box.insert(tk.END, f'The alias of this client is {alias}'.encode('utf-8'))
                    thread = threading.Thread(target=handle_client, args=(client, alias))
                    thread.start()
                        


        receive()

window = tk.Tk()
window.title("Tkinter Server")
window.geometry("900x700")

greeting = tk.Label(text="Enter the port number:")
greeting.pack()

entry = tk.Entry(fg="yellow", bg="red", width=50)
entry.pack()

greeting2 = tk.Label(text="Enter the IP number:")
greeting2.pack()

entry2 = tk.Entry(fg="yellow", bg="red", width=50)
entry2.pack()

button = tk.Button(
    text="Start Server",
    width=10,
    height=3,
    bg="black",
    fg="#BDB76B",
    command=lambda: threading.Thread(target=start_server).start()
)
button.pack()

label_y_coordinate = 195
text_box_y_coordinate = 225

greeting3 = tk.Label(window, text="Server Logs:")
greeting3.place(x=10, y=label_y_coordinate)

log_box = tk.Text(window, height=20, width=30)
log_box.place(x=10, y=text_box_y_coordinate)

greeting4 = tk.Label(window, text="IF100 users:")
greeting4.place(x=300, y=label_y_coordinate)

if100_box = tk.Text(window, height=20, width=30)
if100_box.place(x=300, y=text_box_y_coordinate)

greeting5 = tk.Label(window, text="SPS101 users:")
greeting5.place(x=590, y=label_y_coordinate)

sps101_box = tk.Text(window, height=20, width=30)
sps101_box.place(x=590, y=text_box_y_coordinate)

greeting6 = tk.Label(window, text="All users:")
greeting6.place(x=880, y=label_y_coordinate)

all_box = tk.Text(window, height=20, width=30)
all_box.place(x=880, y=text_box_y_coordinate)

# Ensure that the window is wide enough to accommodate all elements
window.geometry("1200x700")

window.mainloop()
