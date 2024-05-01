#import tkinter as tk
#from tkinter import ttk
#import pandas as pd
#import os
#import customtkinter

import tkinter
import tkinter.messagebox
from tkinter import ttk
import customtkinter
import pandas as pd
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import os.path
import time

import numpy as np
import os

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()


        # Initialize previous idle and total times
        self.prev_idle, self.prev_total = self.get_idle_and_total_time()
        self.total_processes = 0
        self.total_threads = 0

        style = ttk.Style()

        style.theme_use("default")

        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading",
                background=[('active', '#3484F0')])
        
        style.configure("FigureCanvasTkAgg.Figure",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        style.map("FigureCanvasTkAgg.Figure",
                background=[('active', '#3484F0')])

        # configure window
        self.title("Dashboard")
        self.geometry(f"{1100}x{580}")

        self.tabview = customtkinter.CTkTabview(self, width=1100, height=580)
        self.tabview.add("Processos")
        self.tabview.add("Dados globais")
        self.tabview.add("Memória")
        self.tabview.pack()

        self.process_tab()
        self.global_data_tab()
        self.memory_tab()

    def update_memory_tab(self):
        meminfo = self.get_mem_info()
        df = pd.DataFrame.from_dict(meminfo, orient='index', columns=['Value'])
        self.mem_table.delete(*self.mem_table.get_children())  # Clear existing data
        for index, row in df.iterrows():
            self.mem_table.insert("", "end", values=(index, row['Value']))
        
        mem_percentage = self.get_memory_usage()
        self.memory.delete("1.0", tkinter.END)
        self.memory.insert("end", f"Uso da Memória:\n{mem_percentage:.2f}%\n", "center")
        
        self.after(1000, self.update_memory_tab)

    def get_memory_usage(self):
        mem_usage = self.get_mem_info()
        mem_total = mem_usage['MemTotal']
        mem_free = mem_usage['MemFree']
        mem_usage = 100 - (mem_free / mem_total) * 100
        return mem_usage

    def animate_memory(self):
        # append new data point to the x and y data
        self.x_data_mem.append(datetime.now())
        self.y_data_mem.append(self.get_memory_usage())
        # remove oldest data point
        self.x_data_mem = self.x_data_mem[1:]
        self.y_data_mem = self.y_data_mem[1:]
        #  update plot data
        self.plot_mem.set_xdata(self.x_data_mem)
        self.plot_mem.set_ydata(self.y_data_mem)
        self.ax_mem.set_xlim(self.x_data_mem[0], self.x_data_mem[-1])
        self.canvas_mem.draw_idle()  # redraw plot
        self.after(1000, self.animate_memory)  # repeat after 1s

    def memory_tab(self):  
        self.mem_table = ttk.Treeview(self.tabview.tab("Memória"), columns=("Memória", "Valor"), show="headings")     
        self.mem_table.grid(row=0, column=0, rowspan=2, padx=0, pady=0, sticky="nsew")
        self.mem_table.column("Memória", anchor="center", width=220)
        self.mem_table.column("Valor", anchor="center", width=220)
        self.mem_table.heading("Memória", text="Memória")
        self.mem_table.heading("Valor", text="Valor")

        meminfo = self.get_mem_info()
        for key, value in meminfo.items():
            self.mem_table.insert("", "end", values=(key, value))

        self.figure_mem = Figure(figsize=(7, 4), dpi=100)
        self.ax_mem = self.figure_mem.add_subplot(111)
        # format the x-axis to show the time
        self.myFmt = mdates.DateFormatter("%S")
        self.ax_mem.xaxis.set_major_formatter(self.myFmt)

        # initial x and y data
        dateTimeObj = datetime.now() + timedelta(seconds=-30)
        self.x_data_mem = [dateTimeObj + timedelta(seconds=i) for i in range(30)]
        self.y_data_mem = [0 for i in range(30)]
        # create the plot
        self.plot_mem = self.ax_mem.plot(self.x_data_mem, self.y_data_mem, label='Memória')[0]
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xlim(self.x_data_mem[0], self.x_data_mem[-1])

        self.canvas_mem = FigureCanvasTkAgg(self.figure_mem, self.tabview.tab("Memória"))
        self.canvas_mem.get_tk_widget().grid(row=0, column=1, columnspan=3, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.animate_memory()

        self.memory = customtkinter.CTkTextbox(self.tabview.tab("Memória"), font=("Monserrat", 18))
        self.memory.grid(row=1, column=1, columnspan=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.memory.tag_config("center", justify="center")

        self.after(1000, self.update_memory_tab)
    
    def process_tab(self):
        # create treeview table
        self.table = ttk.Treeview(self.tabview.tab("Processos"), columns=("ID", "Usuário", "Nome", "Status"), show="headings")
        self.table.column("ID", anchor="center", width=220)
        self.table.column("Usuário", anchor="center", width=220)
        self.table.column("Nome", anchor="center", width=440)
        self.table.column("Status", anchor="center", width=220)
        self.table.heading("ID", text="ID")
        self.table.heading("Usuário", text="Usuário")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Status", text="Status")

        processes = self.get_processes()
        df = pd.DataFrame.from_dict(processes)
        for index, row in df.iterrows():
            self.table.insert("", "end", values=(row['ID'], row['Usuário'], row['Nome'], row['Status']))
        
        self.table.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")  # Add sticky="nsew" to make it expand

        # Configure row and column weights to make the table expand to fill the available space
        self.tabview.tab("Processos").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Processos").grid_rowconfigure(0, weight=1)

        self.after(5000, self.update_page)

    def animate(self):
        # append new data point to the x and y data
        self.x_data.append(datetime.now())
        self.y_data.append(self.get_cpu_usage())
        # remove oldest data point
        self.x_data = self.x_data[1:]
        self.y_data = self.y_data[1:]
        #  update plot data
        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        self.canvas.draw_idle()  # redraw plot
        self.after(1000, self.animate)  # repeat after 1s

    def global_data_tab(self):

        self.tabview.tab("Dados globais").grid_columnconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Dados globais").grid_rowconfigure((0, 1, 2), weight=1)

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        # format the x-axis to show the time
        self.myFmt = mdates.DateFormatter("%S")
        self.ax.xaxis.set_major_formatter(self.myFmt)

        # initial x and y data
        dateTimeObj = datetime.now() + timedelta(seconds=-30)
        self.x_data = [dateTimeObj + timedelta(seconds=i) for i in range(30)]
        self.y_data = [0 for i in range(30)]
        # create the plot
        self.plot = self.ax.plot(self.x_data, self.y_data, label='CPU')[0]
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])

        self.canvas = FigureCanvasTkAgg(self.figure, self.tabview.tab("Dados globais"))
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.animate()

        self.cpu = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font=("Monserrat", 16))
        self.cpu.grid(row=1, column=0,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.cpu.tag_config("center", justify="center")
        self.idle = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font=("Montserrat", 16))
        self.idle.grid(row=1, column=1,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.idle.tag_config("center", justify="center")
        self.process = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font=("Montserrat", 16))
        self.process.grid(row=1, column=2,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.process.tag_config("center", justify="center")
        self.threads = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font=("Montserrat", 16))
        self.threads.grid(row=1, column=3,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.threads.tag_config("center", justify="center")

        self.update_cpu_percentage_text()  

    def update_cpu_percentage_text(self):
        # Update the CPU percentage text using the get_cpu_usage method
        cpu_percentage = self.get_cpu_usage()
        idle_percentage = 100.0 - cpu_percentage
        total_process, total_threads = self.get_total_processes_and_threads()
        self.cpu.delete("1.0", tkinter.END)
        self.cpu.insert("end", f"Uso da CPU:\n{cpu_percentage:.2f}%\n", "center")
        self.idle.delete("1.0", tkinter.END)
        self.idle.insert("end", f"Tempo ocioso:\n{idle_percentage:.2f}%\n", "center")
        self.process.delete("1.0", tkinter.END)
        self.process.insert("end", f"Quantidade de processos:\n{total_process: }\n", "center")
        self.threads.delete("1.0", tkinter.END)
        self.threads.insert("end", f"Quantidade de threads:\n{total_threads: }\n", "center")


        # Schedule the method to update the CPU percentage again after 1 second
        self.after(1000, self.update_cpu_percentage_text)

    def get_processes(self):
        processes = []

        # Mapear UIDs para nomes de usuário
        uid_to_username = {}
        with open('/etc/passwd', 'r') as passwd_file:
            for line in passwd_file:
                parts = line.strip().split(':')
                uid = parts[2]
                username = parts[0]
                uid_to_username[uid] = username

        # Iterar sobre os diretórios em /proc
        for entry in os.listdir('/proc'):
            # Verificar se a entrada é um diretório e representa um processo
            if entry.isdigit():
                pid = entry

                # Inicializar variáveis para armazenar informações do processo
                user = 'Unknown'
                name = 'Unknown'
                status = 'Unknown'

                # Tentar ler o arquivo status
                try:
                    with open(f'/proc/{pid}/status', 'r') as status_file:
                        # Ler as linhas do arquivo status
                        for line in status_file:
                            # Procurar por linhas contendo 'Uid:', 'Name:', e 'State:'
                            if line.startswith('Uid:'):
                                uid = line.split()[1]
                                user = uid_to_username.get(uid, 'Unknown')
                            elif line.startswith('Name:'):
                                name = line.split(':')[1].strip()
                            elif line.startswith('State:'):
                                status = line.split(':')[1].strip()
                except FileNotFoundError:
                    # Se o arquivo status não existe, pular este processo
                    continue

                # Adicionar as informações do processo à lista
                processes.append({'ID': pid, 'Usuário': user, 'Nome': name, 'Status': status})

        return reversed(processes)
    

    def get_cpu_usage(self):
        # Calculate CPU usage based on previous and current idle and total times
        idle_time, total_time = self.get_idle_and_total_time()
        cpu_percentage = 100.0 - ((idle_time - self.prev_idle) / (total_time - self.prev_total) * 100.0)
        self.prev_idle, self.prev_total = idle_time, total_time
        return cpu_percentage

    def get_idle_and_total_time(self):
        # Get initial idle and total times from /proc/stat
        with open('/proc/stat', 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('cpu'):
                cpu_info = line.split()
                idle_time = float(cpu_info[4])
                total_time = sum(float(x) for x in cpu_info[1:])
                return idle_time, total_time
            
    def get_total_processes_and_threads(self):
        total_processes = 0
        total_threads = 0
        # Iterate over entries in /proc directory
        for entry in os.listdir('/proc'):
            # Check if entry is a directory and represents a process or thread
            if entry.isdigit():
                # Check if it's a process
                if os.path.exists(f'/proc/{entry}/cmdline'):
                    total_processes += 1
                # Check if it's a thread
                if os.path.isdir(f'/proc/{entry}/task'):
                    total_threads += len(os.listdir(f'/proc/{entry}/task'))
                    
        return total_processes, total_threads

    def get_mem_info(self):
        meminfo = {}
        with open('/proc/meminfo') as f:
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].split()[0].strip()
                    meminfo[key] = int(value)
        return meminfo


    def update_page(self):
        # update the Treeview widget with new data
        processes = self.get_processes()
        df = pd.DataFrame.from_dict(processes)
        self.table.delete(*self.table.get_children())  # Clear existing data
        for index, row in df.iterrows():
            self.table.insert("", "end", values=(row['ID'], row['Usuário'], row['Nome'], row['Status']))

        # Schedule the method to update the page again after 5 seconds
        self.after(5000, self.update_page)
    
    
app = App()
app.mainloop()