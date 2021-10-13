import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import socket
import sys
import os
import hashlib
import time
from pathlib import Path
from PIL import ImageTk, Image
from tip import Tooltip

class Server(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        # self.root = root

        self.title("Server side")
        self.geometry('400x200+200+200')
        self.maxsize(width=400,height=200)

        self.show=ImageTk.PhotoImage(Image.open('icons\Custom-Icon-Design-Flatastic-6-Connect-point-tool.ico'))
        server_btn1=tk.Button(self, image=self.show, command=self.host, relief=tk.FLAT)
        server_btn1.grid(row=0, column=0)

        self.create=ImageTk.PhotoImage(Image.open('icons\connect ok.ico'))
        server_btn2=tk.Button(self, image=self.create, command=self.create_conn, relief=tk.FLAT)
        server_btn2.grid(row=0, column=1)

        self.sb2=tk.Scrollbar(self)
        self.sb2.grid(row=1, column=12, rowspan=5)

        self.list1=tk.Listbox(self,height=8,width=50)
        self.list1.grid(row=1,column=0,rowspan=5,columnspan=12)

        self.list1.configure(yscrollcommand=self.sb2.set)
        self.sb2.configure(command=self.list1.yview)

        self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length = 300)
        self.progress_bar.grid(column=0, row=7, rowspan=5, columnspan=12)
        
    class BufferedReceiver():
        def __init__(self, sock):
            self.sock = sock
            self.buffer = ""
            self.bufferPos = 0

        def _fetch(self):
            while self.bufferPos >= len(self.buffer):
                self.buffer = self.sock.recv(1024)
                # print(self.buffer)
                self.bufferPos = 0

        def take(self, amount):
            result = bytearray()
            while (len(result) < amount):
                # Fetch new data if necessary
                self._fetch()

                result.append(self.buffer[self.bufferPos])
                self.bufferPos += 1
            return bytes(result)

        def take_until(self, ch):
            result = bytearray()
            while True:
                # Fetch new data if necessary
                self._fetch()

                nextByte = self.buffer[self.bufferPos]
                self.bufferPos += 1

                result.append(nextByte)
                if bytes([nextByte]) == ch:
                    break

            return bytes(result)
    
    def create_conn(self):
        num = 5
        bufsize = 4096
        if num in range(10):
            while True:
                try:
                    self.conn, self.addr = self.s.accept()
                    self.list1.delete(0,tk.END)
                    self.list1.insert(tk.END,'Connected with ' + self.addr[0] + ':' + str(self.addr[1]))
                    self.reqCommand = self.conn.recv(1024).decode('utf-8', errors='ignore')
                    self.list1.insert(tk.END,'Client> %s' % self.reqCommand)
                    string = self.reqCommand.split(' ', 1)
                    if (self.reqCommand == 'quit'):
                        break
                    elif self.reqCommand == 'lls':
                        toSend = ""
                        path = os.getcwd()
                        dirs = os.listdir(path)
                        for f in dirs:
                            toSend = toSend + f + ' '
                        self.conn.send(toSend.encode('utf-8'))
                        # print path

                    elif self.reqCommand == 'Browse':
                        toSend = ""                    
                        file=filedialog.askdirectory(initialdir=os.getcwd(), title='Please select the folder of file')
                        try:
                            file = os.chdir(file)
                            dirs = os.listdir(file)
                            for f in dirs:
                                toSend = toSend + f + '<>'
                            self.conn.send(toSend.encode('utf-8'))
                        except OSError:
                            self.list1.insert(tk.END, 'No folder is selected')
                            tosend = 'No folder was selected by user'
                            self.conn.send(tosend.encode('utf-8'))
                    
                    elif string[0] == 'FileHash':
                        if string == 'verify':
                            BLOCKSIZE = 65536
                            hasher = hashlib.sha1()
                            with open(string[2], 'r') as afile:
                                buf = afile.read(BLOCKSIZE)
                                while len(buf) > 0:
                                    hasher.update(buf)
                                    buf = afile.read(BLOCKSIZE)
                            self.conn.send(hasher.hexdigest())
                            self.list1.insert(tk.END,'Hash Successful')

                        elif string == 'checkall':
                            BLOCKSIZE = 65536
                            hasher = hashlib.sha1()
                            path = os.getcwd()
                            dirs = os.listdir(path)
                            for f in dirs:
                                self.conn.send(f.encode('utf-8'))
                                with open(f, 'r') as afile:
                                    buf = afile.read(BLOCKSIZE)
                                    while len(buf) > 0:
                                        hasher.update(buf)
                                        buf = afile.read(BLOCKSIZE)
                                self.conn.send(hasher.hexdigest())
                                self.list1.insert(tk.END,'Hash Successful')

                    else:
                        string = self.reqCommand.split(' ', 1)  # in case of 'put' and 'get' method
                        if len(string) > 1:
                            reqFile = string[1]
                            # arrayDict = []

                            if string[0] == 'FileUpload':
                                receiver = self.BufferedReceiver(self.conn)
                                file_size = int(self.conn.recv(4096))
                                bufsize = 4096
                                # start writing at the beginning and use following variable to track
                                write_sectors = 0
                                path = os.getcwd()
                                if path[0] == 'C':
                                    split=path.split('\\')
                                    path2=Path(split[0]+'\\'+split[1]+'\\'+split[2]+'\\Downloads\\Lytenet')
                                else:
                                    split=path.split('/')
                                    path2=Path('/'+split[1]+'/'+split[2]+'/Downloads/Lytenet')
                                try:
                                    path2.mkdir()
                                except FileExistsError:
                                    pass
                                # this only opens the file, the while loop controls when to close
                                self.list1.insert(tk.END, 'Filesize: '+str(int(file_size/1024))+'KB')
                                with open(os.path.join(path2,reqFile), 'wb+') as file_to_write:
                                    # while written bytes to out is less than file_size
                                    
                                    c = 0
                                    self.progress_bar['maximum'] = file_size
                                    # while True:
                                    for i in range(0, file_size, bufsize):
                                        
                                        # Compute how much bytes we have left to receive
                                        bytes_left = file_size - bufsize * c

                                        # if we are almost done, do the final iteration
                                        if bytes_left <= bufsize:
                                            file_to_write.write(receiver.take(bytes_left))
                                            break

                                        # Otherwise, just continue receiving
                                        file_to_write.write(receiver.take(bufsize))
                                        c += 1
                                        self.progress_bar['value'] = i
                                        self.progress_bar.update()
                                file_to_write.close()
                                self.progress_bar['value']=0
                                self.list1.insert(tk.END,'Receive Successful')
                                
                            elif string[0] == 'FileDownload':
                                bufsize = 4096
                                with open(reqFile, 'rb') as file_to_send: #file_to_send:
                                    #get the entire filesize,which sets the read sector to EOF

                                    file_size = len(file_to_send.read())
                                    # reset the read file sector to the start of the file

                                    file_to_send.seek(0)
                                    #pass the file size over to client in a small info chunk

                                    self.list1.insert(tk.END, 'Filesize: '+str(int(file_size/1024))+'KB')
                                    self.conn.send((str(file_size) + '\n').encode())
                                    # send the total file size off the client
                                    c = 0
                                    self.progress_bar['maximum'] = file_size
                                    for i in range(0, file_size, bufsize): 
                                        if (c * bufsize) > file_size:
                                            break
                                        send_data = file_to_send.read(bufsize)
                                        self.conn.send(send_data)
                                        c += 1
                                        self.progress_bar['value'] = i
                                        self.progress_bar.update()
                                file_to_send.close()
                                self.progress_bar['value']=0
                                self.list1.insert(tk.END,'Send Successful')            
                    # self.conn.close()
                except:
                    self.list1.delete(0,tk.END)
                    self.list1.insert(tk.END, 'Attribute Error')
                
                
       
    def host(self):
        self.HOST = '0.0.0.0'
        self.PORT = 8000
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.list1.insert(tk.END,"Hostname :  "+self.host_name)
        self.list1.insert(tk.END,"Sender's ip address is : "+self.host_ip)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.list1.insert(tk.END,'Server Created')
        except OSError as msg:
            self.list1.insert(tk.END,'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        try:
            self.s.bind((self.HOST, self.PORT))
        except OSError as msg:
            self.list1.insert(tk.END,'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()
        self.list1.insert(tk.END,'Socket bind complete')
        self.s.listen(1)
        self.list1.insert(tk.END, 'Server now listening')


# root=Tk()
# Server(root)
# root.mainloop()
