# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

import sys
import os
from client import Client
from server import Server
from PIL import ImageTk, Image
from tip import Tooltip

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('LyteNet File Transfer')
        self.geometry('400x200+500+200')

        self.icon=ImageTk.PhotoImage(Image.open('icons\jaayee.png'))
        self.wm_iconphoto(self, self.icon)

        self.label1=tk.Label(self, text='Create Server')
        self.label1.grid(row=2, column=1, ipadx=160)

        self.label2=tk.Label(self, text='Join Server')
        self.label2.grid(row=4, column=1, ipadx=160)

        self.join=ImageTk.PhotoImage(Image.open('icons\connect circle.ico'))
        self.client1_btn=tk.Button(self, image=self.join, command=self.open_client, relief=tk.FLAT)
        self.client1_btn.grid(row=3, column=1, ipady=10)

        self.create=ImageTk.PhotoImage(Image.open('icons\connect2.ico'))
        self.client2_btn=tk.Button(self, image=self.create, command=self.open_server, relief=tk.FLAT)
        self.client2_btn.grid(row=1, column=1, ipady=10)

        Tooltip(widget=self.client1_btn,text='Join Server', bg='black', fg='white')
        Tooltip(widget=self.client2_btn,text='Create Server')
        
        
        
    def open_client(self):
        client_window= Client(self)
        client_window.grab_set()

    def open_server(self):
        server_window= Server(self)
        server_window.grab_set()


if __name__=='__main__':
    app=App()
    app.maxsize(400,200)
    app.mainloop()
