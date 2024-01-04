from re import S
import threading
import socket
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import time

TEXT_BOX_WIDTH = 405
TEXT_BOX_HEIGHT = 420
# Server address and port
HOST = '127.0.0.1'
PORT = 59000
global if100_subscription
if100_subscription = False
global sps101_subscription
sps101_subscription = False

sps_or_if100 = None
global justunsubsIF100
justunsubsIF100 = False
global justsubsIF100
justsubsIF100 = False
global justunsubssps101
justunsubssps101 = False
global justsubssps101
justsubssps101 = False


# Initialize the main window
window = tk.Tk()
window.title("CLIENT")
window.configure(bg="black")
window.geometry("900x700")
# Styling the label
button_style = {
    "font": ("Helvetica", 10, "bold"),  
    "fg": "#76EE00",                      
    "bg": "black",                 
    "padx": 10,                         
    "pady": 5,                          
    "borderwidth": 2,                   
    "relief": "raised"                  
}

greeting = tk.Label(text="Enter the IP address:",bg="black",fg="yellow")
greeting.pack()
ip_entry = tk.Entry(fg="yellow", bg="#303030", width=50)
ip_entry.pack()

greeting2 = tk.Label(text="Enter the port number:",bg="black",fg="yellow")
greeting2.pack()
port_entry = tk.Entry(fg="yellow", bg="#303030", width=50)
port_entry.pack()

greeting3 = tk.Label(text="Enter your alias:",bg="black",fg="yellow")
greeting3.pack()
username_entry = tk.Entry(fg="yellow", bg="#303030", width=50)
username_entry.pack()


client = None


subscribed_channels = set()
registered_aliases = []

def start_client(sps_or_if100):
    global client
    disconnect_button.config(state=tk.NORMAL)
    if100_subscribe_button.config(state= tk.ACTIVE)
    sps101_subscribe_button.config(state= tk.ACTIVE)
    if100_unsubscribe_button.config(state= tk.DISABLED)
    sps101_unsubscribe_button.config(state= tk.DISABLED)
    if100_send_button.config(state= tk.DISABLED)
    sps101_send_button.config(state= tk.DISABLED)
 
    host = ip_entry.get()
    port = int(port_entry.get())
    alias = username_entry.get()
    """
    if alias not in registered_aliases:
        registered_aliases.append(alias)
    else:
        registered_aliases.remove(alias)
        exit()
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        connect_button.config(state=tk.DISABLED)
        receive_thread = threading.Thread(target=client_receive, args=(client, alias, sps_or_if100))
        receive_thread.start()
    except Exception as e:
        update_message_box(f'Connection Error: {e}', sps_or_if100)


def client_receive(client, alias, sps_or_if100):
   
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            length = len(message)
            last_fifteen = message[length - 15:]
            if message == 'alias?':
                client.send(alias.encode('utf-8'))
            elif last_fifteen == "###specialif100":
                message = message.replace("###specialif100", "")
                message = message.replace(f"{alias}:", "")
                sps_or_if100 = "IF100"
                update_message_box(message, sps_or_if100)
            elif last_fifteen == "###specialsp101":
                message = message.replace("###specialsp101", "")
                message = message.replace(f"{alias}:", "")
                sps_or_if100 = "SPS101"
                update_message_box(message, sps_or_if100)
            elif message == "This alias is already in use.":
                client.close()
                
                window.destroy()
                
                warning_window = tk.Tk()
                warning_window.title("Warning!")
                warning_window.configure(bg="white")
                warning_window.geometry("100x100")
                Warning_sign = tk.Label(warning_window, text="There already exists a user with same alias!")
                Warning_sign.place()
                warning_window.mainloop()
                time.sleep(3)
                warning_window.destroy()
                exit()
            else:
                
                message = message.replace(f"{alias}:", "")
                update_message_box(message, sps_or_if100)
        except Exception as e:
            update_message_box(f'Error: {e}', sps_or_if100)
            client.close()
            break

def update_message_box(message, sps_or_if100):
   
    
    
    # Define the task to be run in the Tkinter main thread
    def task(message, sps_or_if100):
       
        
        
        if sps_or_if100 == "IF100":
          
            if100_message_box.insert(tk.END, f"{message}\n")
            if100_message_box.see(tk.END)
        elif sps_or_if100 == "SPS101":
           
            sps101_message_box.insert(tk.END, f"{message}\n")
            sps101_message_box.see(tk.END)
        
    # Schedule the task to be run in the Tkinter main thread
    window.after(0, task(message, sps_or_if100))

def channel_namer(sps_or_if100):
    if sps_or_if100 == "IF100":
        channel = "IF100"
    elif sps_or_if100 == "SPS101":
        channel = "SPS101"
    else:
        channel = "None"
    return channel

def send_message(sps_or_if100):
    channel = channel_namer(sps_or_if100)
    if channel == "None":
        update_message_box("Please subscribe to a channel.")
        return;
    elif channel == "IF100":
        if client:
            if channel in subscribed_channels:
                message_content = if100_send_message_entry.get()
                message = f'message:{channel}:{username_entry.get()}: {message_content}###specialif100'
                client.send(message.encode('utf-8'))
                if100_send_message_entry.delete(0, tk.END)
                # Update the chat box immediately for user feedback
                sps_or_if100 = "IF100"
                update_message_box(f"You: {message_content}", sps_or_if100)
                
            else:
                update_message_box("Not subscribed to the selected channel.",sps_or_if100)
        else:
            update_message_box("Not connected to server.", sps_or_if100)
    elif channel == "SPS101":
        if client:
            if channel in subscribed_channels:
                message_content = sps101_send_message_entry.get()
                message = f'message:{channel}:{username_entry.get()}: {message_content}###specialsp101'
                client.send(message.encode('utf-8'))
                sps101_send_message_entry.delete(0, tk.END)
                # Update the chat box immediately for user feedback
                sps_or_if100 = "SPS101"
                update_message_box(f"You: {message_content}",sps_or_if100)
                
            else:
                update_message_box("Not subscribed to the selected channel.",sps_or_if100)
        else:
            update_message_box("Not connected to server.",sps_or_if100)
            

def subscribe_to_channel(channel):
    
    client.send(f'subscribe:{channel}'.encode('utf-8'))
    subscribed_channels.add(channel)
    
        #update_message_box("Client not connected or already subscribed to channel.")
    
        
def unsubscribe_to_channel(channel, sps_or_if100):
    global if100_subscription, sps101_subscription
    if client and channel in subscribed_channels:
        client.send(f'unsubscribe:{channel}'.encode('utf-8'))
        update_message_box(f"Unsubscribed from {channel}.", sps_or_if100)
        subscribed_channels.remove(channel)
        if channel == "IF100":
            if100_subscription = False
        elif channel == "SPS101":
            sps101_subscription = False
    else:
        update_message_box("Client not connected or not subscribed to channel.", sps_or_if100)
        
def disconnect(sps_or_if100):
    global client
    if client:
        client.send('disconnect123'.encode('utf-8'))
        client.close()
        connect_button.config(state=tk.NORMAL)
        disconnect_button.config(state=tk.DISABLED)
        if100_send_button.config(state= tk.DISABLED)
        sps101_send_button.config(state= tk.DISABLED)
        if100_subscribe_button.config(state= tk.DISABLED)
        sps101_subscribe_button.config(state= tk.DISABLED)
        if100_unsubscribe_button.config(state= tk.DISABLED)
        sps101_unsubscribe_button.config(state= tk.DISABLED)
        update_message_box('Disconnected from server.', sps_or_if100)
        client = None

connect_button = tk.Button(window, text="Connect", command=lambda:start_client(sps_or_if100))
connect_button.pack()

disconnect_button = tk.Button(window, text="Disconnect", command=lambda:disconnect(sps_or_if100))
disconnect_button.pack()

def subscribe_to_if100(sps_or_if100):
    global if100_subscription
    if100_subscription = True
    subscribe_to_channel("IF100")
    
    if100_send_button.invoke()
    if100_unsubscribe_button.config(state = tk.ACTIVE)
    if100_subscribe_button.config(state = tk.DISABLED)
    if100_send_button.config(state= tk.NORMAL)

def unsubscribe_to_if100(sps_or_if100):
    global if100_subscription
    if100_subscription = False
    unsubscribe_to_channel("IF100", sps_or_if100)
    if100_subscribe_button.config(state= tk.ACTIVE)
    if100_unsubscribe_button.config(state = tk.DISABLED)
    if100_send_button.config(state= tk.DISABLED)
    
def subscribe_to_sps101(sps_or_if100):
    global sps101_subscription
    sps101_subscription = True
    subscribe_to_channel("SPS101")
    sps101_send_button.invoke()
    sps101_unsubscribe_button.config(state = tk.ACTIVE)
    sps101_subscribe_button.config(state = tk.DISABLED)
    sps101_send_button.config(state= tk.NORMAL)
    
def unsubscribe_to_sps101(sps_or_if100):
    global sps101_subscription
    sps101_subscription = False
    unsubscribe_to_channel("SPS101",sps_or_if100)
    sps101_subscribe_button.config(state= tk.ACTIVE)
    sps101_unsubscribe_button.config(state = tk.DISABLED)
    sps101_send_button.config(state= tk.DISABLED)
    
    
if100_subscribe_button = tk.Button(window, text="Subscribe to IF100", command=lambda:subscribe_to_if100(sps_or_if100),**button_style)
if100_subscribe_button.place(x=15,y=125)
if100_subscribe_button.config(state = tk.DISABLED)

if100_unsubscribe_button = tk.Button(window, text="Unsubscribe to IF100", command=lambda:unsubscribe_to_if100(sps_or_if100),**button_style)
if100_unsubscribe_button.place(x=15, y= 173)
if100_unsubscribe_button.config(state = tk.DISABLED)

sps101_subscribe_button = tk.Button(window, text="Subscribe to SPS101", command=lambda:subscribe_to_sps101(sps_or_if100),**button_style)
sps101_subscribe_button.place(x=725, y=125)
sps101_subscribe_button.config(state = tk.DISABLED)

sps101_unsubscribe_button = tk.Button(window, text="Unsubscribe to SPS101", command=lambda:unsubscribe_to_sps101(sps_or_if100),**button_style)
sps101_unsubscribe_button.place(x=725, y=173)
sps101_unsubscribe_button.config(state = tk.DISABLED)



if100_send_message_entry = tk.Entry(window, fg="yellow", bg="#1A1A1A", width=40)
if100_send_message_entry.place(x=80, y = 215)

def if100_activated():
    global sps_or_if100
    sps_or_if100 = "IF100"
    send_message(sps_or_if100)

if100_send_button = tk.Button(window, text="Send", command=if100_activated, **button_style)
if100_send_button.place(relx=0.07, rely=0.3, anchor='ne')
if100_send_button.config(state= tk.DISABLED)

sps101_send_message_entry = tk.Entry(window, fg="yellow", bg="#1A1A1A", width=40)
sps101_send_message_entry.place(x=475, y = 220)

def sps101_activated():
    global sps_or_if100
    sps_or_if100 = "SPS101"
    send_message(sps_or_if100)    


    
sps101_send_button = tk.Button(window, text="Send", command=sps101_activated,**button_style)
sps101_send_button.place(x=825, y=215)
sps101_send_button.config(state= tk.DISABLED)

# Styling the label
IF100_label_style = {
    "font": ("Helvetica", 16, "bold"),  # Modern font with bold style and size 16
    "fg": "#EE2C2C",                      # White text color
    "bg": "black",                   # Dark blue background
    "padx": 10,                         # Horizontal padding
    "pady": 5,                          # Vertical padding
    "borderwidth": 2,                   # Border width
    "relief": "raised"                  # 3D raised effect
}

text_box_width = 405  
text_box_height = 420  
# Text box for displaying messages
IF100_label_box = tk.Label(window, text="IF100", **IF100_label_style)
IF100_label_box.place(relx=0.2, rely=0.26, anchor='w')
if100_message_box = tk.Text(window, height=10, width=50, **button_style)
if100_message_box.place(relx=0.025, rely=0.66, anchor='w', width=text_box_width, height=text_box_height)

# Text box for displaying messages
SPS101_label_box = tk.Label(text="SPS101", **IF100_label_style)
SPS101_label_box.place(relx=0.75, rely=0.25, anchor='e')
sps101_message_box = tk.Text(window, height=10, width=50, **button_style)
sps101_message_box.place(relx=.975, rely=0.66, anchor='e', width=text_box_width, height=text_box_height)

frame = Frame(window, width=25, height=20)
frame.pack()
frame.place(x=25, y = 15)

frame2 = Frame(window, width=25, height=20)
frame2.pack()
frame2.place(x=775, y = 15)
# Create an object of tkinter ImageTk
orgImage = Image.open("CIA.jpeg")
# Resize the image using resize() method
resized_img = orgImage.resize((100, 100))
img = ImageTk.PhotoImage(resized_img)

# Create a Label Widget to display the text or Image
label = Label(frame, image = img)
label.pack()

label2 = Label(frame2, image = img)
label2.pack()

window.mainloop()
