import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import socket
import sys
import os
import hashlib
import time
from pathlib import Path
from tip import Tooltip

class Client(tk.Toplevel):

    def __init__(self, parent):
        
        '''
        It connects the PC to an inputted IP address
        
        '''
        
        super().__init__(parent)
        # self.root=root
        self.title('Client side')
        self.geometry('620x280+700+200')
        self.maxsize(width=620,height=280)

        server_btn1=tk.Button(self, text='Join server', width=15, command=self.start)
        server_btn1.grid(row=1, column=5)

        server_btn2=tk.Button(self, text='Browse Files', width=15, command=self.browse)
        server_btn2.grid(row=2, column=5)

        server_btn9=tk.Button(self, text='Browse Server', width=15, command=self.browse_server)
        server_btn9.grid(row=3, column=5)

        server_btn3=tk.Button(self, text='SEND COMMAND', width=15, command=self.send_command)
        server_btn3.grid(row=4, column=5)

        server_btn6=tk.Button(self, text='Upload File', width=15, command=self.upload)
        server_btn6.grid(row=5, column=5)

        server_btn7=tk.Button(self, text='Download file', width=15, command=self.download)
        server_btn7.grid(row=6, column=5)

        server_btn7=tk.Button(self, text='File Hash', width=15, command=self.hash)
        server_btn7.grid(row=7, column=5)

        server_btn8=tk.Button(self, text='Close', width=15, command=self.destroy)
        server_btn8.grid(row=8, column=5)

        l1=tk.Label(self, text='IP\'s address')
        l1.grid(row=0, column=0)

        self.word_text=tk.StringVar()
        self.e1=tk.Entry(self, textvariable=self.word_text)
        self.e1.grid(row=0,column=1)

        l2=tk.Label(self, text='Input Command')
        l2.grid(row=0, column=2)

        self.name_text=tk.StringVar()
        self.e2=tk.Entry(self, textvariable=self.name_text)
        self.e2.grid(row=0,column=3)

        self.sb1=tk.Scrollbar(self)
        self.sb1.grid(row=1,column=4, rowspan=8)

        self.list1=tk.Listbox(self,height=14,width=68)
        self.list1.grid(row=1,column=0,rowspan=8,columnspan=4)
        
        self.list1.configure(yscrollcommand=self.sb1.set)
        self.sb1.configure(command=self.list1.yview)

        self.list1.bind('<<ListboxSelect>>',self.get_selected_row)

        self.list1.insert(tk.END, 'Enter Sender IP address')
        
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length = 470)
        self.progress_bar.grid(column=1, row=9,columnspan=5,pady=3)


    def get_selected_row(self, event):
        global selected_tuple
        index=self.list1.curselection()[0]
        selected_tuple=self.list1.get(index)
        self.e2.delete(0,tk.END)
        self.e2.insert(tk.END,selected_tuple)

    def download(self):
        self.list1.delete(0, tk.END)
        try:
            file = 'FileDownload ' + self.name_text.get()
            #print(file)
            self.get(file)
        except OSError:
            self.list1.insert(tk.END, 'Connection not established')

    def upload(self):
        self.list1.delete(0, tk.END)
        try:
            file = 'FileUpload ' + self.name_text.get()
            #print(file)
            self.put(file)
        except OSError:
            self.list1.insert(tk.END, 'Connection not established')

    def hash(self):
        self.list1.delete(0, tk.END)
        try:
            file = 'FileHash ' + 'verify ' + self.name_text.get()
            #print(file)
            self.FileHash(file)
        except OSError:
            self.list1.insert(tk.END, 'Connection not established')


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


    def put(self, commandName):
        self.HOST = self.word_text.get()  # server name goes in here
        self.PORT = 8000
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket1.connect((self.HOST, self.PORT))
        string = commandName.split(' ', 1)
        inputFile = string[1]
        self.socket1.send(commandName.encode('utf-8'))  # has to be 4 bytes
        self.list1.delete(0, tk.END)
        bufsize = 4096
        c = 0
        with open(inputFile, "rb") as file_to_send1: #file_to_send:
            file_size = len(file_to_send1.read())
            # reset the read file sector to the start of the file
            file_to_send1.seek(0)
            #pass the file size over to client in a small info chunk

            self.list1.insert(tk.END, 'Filesize: '+str(int(file_size/1024))+'KB')
            self.socket1.send((str(file_size) + '\n').encode())
            # send the total file size off the client
            c = 0
            self.progress_bar['maximum'] = file_size
            for i in range(0, file_size, bufsize): 
                if (c * bufsize) > file_size:
                    break
                send_data = file_to_send1.read(bufsize)
                self.socket1.send(send_data)
                c += 1
                self.progress_bar['value'] = i
                self.progress_bar.update()
            file_to_send1.close()
            self.progress_bar['value']=0
            self.list1.insert(tk.END, 'Upload Successful')
        # self.socket1.close()
        return

    def get(self, commandName):
        self.HOST = self.word_text.get()  # server name goes in here
        self.PORT = 8000
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket1.connect((self.HOST, self.PORT))
        self.socket1.send(commandName.encode("utf-8"))

        receiver = self.BufferedReceiver(self.socket1)

        string = commandName.split(' ', 1)
        inputFile = string[1]
        self.list1.delete(0, tk.END)

        # before starting to write new file, get file size
        file_size = int(receiver.take_until(b'\n').decode().strip()) # from file_to_send3
        self.list1.insert(tk.END, 'Filesize: '+str(int(file_size/1024))+'KB')
        # set byte buffer size
        bufsize = 4096
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
        with open(os.path.join(path2, inputFile), 'wb+') as file_to_write:
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
            self.list1.insert(tk.END, 'Download Successful')
        # self.socket1.close()
        return


    def FileHash(self, commandName):
        string = commandName.split(' ')
        self.list1.delete(0, tk.END)
        if string == 'verify':
            self.verify(commandName)
        elif string == 'checkall':
            self.checkall(commandName)


    def verify(self, commandName):
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket1.connect((self.HOST, self.PORT))
        self.socket1.send(commandName.encode('utf-8'))
        hashValServer = self.socket1.recv(4096).decode('utf-8')
        string = commandName.split(' ')
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()
        self.list1.delete(0, tk.END)
        with open(string[2], 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        hashValClient = hasher.hexdigest()
        self.list1.insert(tk.END, 'hashValServer= %s' %hashValServer)
        self.list1.insert(tk.END, 'hashValClient= %s' %hashValClient)
        if hashValClient == hashValServer:
            self.list1.insert(tk.END, 'No updates')
        else:
            self.list1.insert(tk.END, 'Update Available')
        return


    def checkall(self, commandName):
        self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket1.connect((self.HOST, self.PORT))
        self.socket1.send(commandName.encode('utf-8'))
        string = commandName.split(' ')
        BLOCKSIZE = 65536
        hasher = hashlib.sha1()
        # f=self.socket1.recv(1024)
        self.list1.delete(0, tk.END)
        while True:
            f = self.socket1.recv(4096)
            with open(f, 'r') as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            hashValClient = hasher.hexdigest()
            hashValServer = self.socket1.recv(1024)

            self.list1.insert(tk.END, 'Filename =    %s' %f)
            self.list1.insert(tk.END, 'hashValServer= %s' %hashValServer)
            self.list1.insert(tk.END, 'hashValClient= %s' %hashValClient)
            if hashValClient == hashValServer:
                self.list1.insert(tk.END, 'No updates')
            else:
                self.list1.insert(tk.END, 'Update Available')
            if not f:
                break
        # self.socket1.close()
        return


    def quit(self, commandName):
        socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket1.connect((self.HOST, self.PORT))
        socket1.send(commandName.encode('utf-8'))
        # self.socket1.close()
        return


    def browse_server(self, commandName='Browse'):
        self.e2.delete(0, tk.END)
        self.e2.insert(tk.END, 'Browse')
        self.list1.delete(0, tk.END)  
        try:
            self.HOST = self.word_text.get()  # server name goes in here
            self.PORT = 8000
            self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket1.connect((self.HOST, self.PORT))
            self.socket1.send(commandName.encode('utf-8'))
            fileStr = self.socket1.recv(1024)
            try:
                fileList = fileStr.decode('utf-8').split('<>')
                for f in fileList:
                    self.list1.insert(tk.END, f)
                return
            except:
                self.list1.insert(tk.END, fileStr)
        except OSError:
            self.list1.insert(tk.END, 'Connection not established')
    

    def browse(self):
        file=filedialog.askdirectory(initialdir=os.getcwd(), title='Please select a Folder')
        self.list1.delete(0,tk.END)
        try:
            file = os.chdir(file)
            dirs = os.listdir(file)
            self.list1.delete(0, tk.END)
            for f in dirs:
                self.list1.insert(tk.END, f)
        except OSError:
            self.list1.insert(tk.END, 'No folder is selected')

    def send_command(self):
        self.list1.delete(0,tk.END)
        msg2 = self.name_text.get()
        inputCommand = msg2 #sys.stdin.readline().strip()
        while inputCommand == 'quit':
            quit('quit')
            break
        if inputCommand == 'ls':
            path = os.getcwd()
            dirs = os.listdir(path)
            self.list1.delete(0, tk.END)
            for f in dirs:
                self.list1.insert(tk.END, f)
        else:
            string = inputCommand.split(' ', 1)
            if string[0] == 'FileDownload':
                self.get(inputCommand)
            elif string[0] == 'FileUpload':
                self.put(inputCommand)
            elif string[0] == 'IndexGet':
                self.IndexGet(inputCommand)
            elif string[0] == 'FileHash':
                self.FileHash(inputCommand)
            elif string[0] == 'Browse':
                self.browse_server()

    def start(self):
        self.list1.delete(0,tk.END)
        try:
            self.HOST = self.word_text.get()  # server name goes in here
            self.PORT = 8000
            self.bufsize = 4096
            self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket1.connect((self.HOST, self.PORT))
            self.host_name = socket.gethostname()
            self.list1.insert(tk.END,"Hostname :  "+self.host_name)
            if 1:
                self.list1.delete(0,tk.END)
                self.list1.insert(tk.END, "****************")
                self.list1.insert(tk.END, 'Instruction')
                self.list1.insert(tk.END, '"FileUpload [filename]" to send the file the server ')
                self.list1.insert(tk.END, '"FileDownload [filename]" to download the file from the server ')
                self.list1.insert(tk.END, '"ls" to list all files in this directory')
                self.list1.insert(tk.END, '"lls" to list all files in the server')
                self.list1.insert(tk.END, '"FileHash verify <filename>" checksum of the modification of the mentioned file.')
                self.list1.insert(tk.END, '"quit" to exit')
                self.list1.insert(tk.END, '%s> ' % self.host_name)
        except OSError:
            self.list1.insert(tk.END, 'Connection not established')

