import socket
from app import db, Todo

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 55000  # Port to listen on (non-privileged ports are > 1023)




with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(data)
            new_tab = Todo(content = data)
            try:
                db.session.add(new_tab)
                db.session.commit()
            except:
                print("cant do that")
            conn.sendall(data)
