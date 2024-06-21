'''
Arquivo contendo o processamento dos dados para o dashboard
É a View do padrão de projeto Model-View-Controller (MVC)
'''

import tkinter
from tkinter import *
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
import matplotlib.ticker as mticker
import os
import os.path



class View(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("Dark")  # Setado mode escuro para a tela
        customtkinter.set_default_color_theme("dark-blue")  # Setado tema escuro-azul
        
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

        # Configuração da janela
        self.title("Dashboard")
        self.geometry(f"{1100}x{580}")

        # Criação das tabs
        self.tabview = customtkinter.CTkTabview(self, width=1100, height=580)
        self.tabview.add("Processos")
        self.tabview.add("Dados globais")
        self.tabview.add("Memória")
        self.tabview.add("Sistema de arquivos")
        self.tabview.add("Diretórios")
        self.tabview.pack()

    # Função que irá gerenciar a abertura do pop up com as informações detalhadas e do uso de memória de cada processo 
    # Ele será exibido ao clicar no ID do processo listado na aba "Processos"
    def open_popup(self, event, process_memory, page_usage, process_details, process_resources):
        # Identifica a coluna que o clique foi acionado
        col = self.table.identify_column(event.x)

        # Checa se o clique foi na coluna 1 (seta para exibir as threads)
        if col == "#1": 
            item_id = self.table.identify_row(event.y)
            current_value = self.table.set(item_id, "Num")
            new_value = "▼" if current_value == "▶" else "▶"
            self.table.set(item_id, "Num", value=new_value)
            self.table.item(item_id, open=not self.table.item(item_id, "open"))

        # Checa se o clique foi na coluna 2 (ID do processo)
        # Se o clique for na coluna 2, irá criar os elementos do pop up 
        if col == "#2":  
            item_id = self.table.identify_row(event.y)
            top = Toplevel()
            top.geometry("1000x600")
            top.title(item_id)
            
            # Cria a tabela com as informações detalhadas do processo
            top.table_details = ttk.Treeview(top, columns=("Command Line", "State", "UID", "GID", "PPID"), show="headings")
            top.table_details.column("Command Line", anchor="center", width=90)
            top.table_details.column("State", anchor="center", width=90)
            top.table_details.column("UID", anchor="center", width=90)
            top.table_details.column("GID", anchor="center", width=90)
            top.table_details.column("PPID", anchor="center", width=90)
            
            top.table_details.heading("Command Line", text="Command Line")
            top.table_details.heading("State", text="State")
            top.table_details.heading("UID", text="UID")
            top.table_details.heading("GID", text="GID")
            top.table_details.heading("PPID", text="PPID")
            top.table_details.grid(row=0, column=0, columnspan=1, padx=0, pady=0, sticky="nsew")  # ADicionar sticky="nsew" para fazer a tabela expandir
            top.grid_rowconfigure((0, 1), weight=1)
            top.grid_columnconfigure((0, 1, 2), weight=1)
            
            for pid, details in process_details.items():
                if pid == item_id:
                    top.table_details.insert("", "end", values=(
                        details.get('Command Line'),
                        details.get('State'),
                        details.get('Uid'),
                        details.get('Gid'),
                        details.get('PPid')
                    ))

            # Cria uma caixa de texto com o uso de memória do processo
            top.memory_usage = customtkinter.CTkTextbox(top, font=("Monserrat", 15))
            top.memory_usage.grid(row=0, column=1, columnspan=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
            top.memory_usage.tag_config("center", justify="center")
            if item_id in process_memory:
                if process_memory[item_id]:
                    top.memory_usage.insert("end", f"Uso da Memória:\n{process_memory[item_id]} kB\n", "center")
                else:
                    top.memory_usage.insert("end", "Uso da Memória:\n0 kB\n", "center")
            else:
                top.memory_usage.insert("end", "Uso da Memória:\n0 kB\n", "center")
                
            top.page_usage = customtkinter.CTkTextbox(top, font=("Monserrat", 15))
            top.page_usage.grid(row=0, column=2, columnspan=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
            top.page_usage.tag_config("center", justify="center")
            if item_id in page_usage:
                top.page_usage.insert("end", f"Uso de páginas:\nTotal: {page_usage[item_id]['total']} kB\nCódigo: {page_usage[item_id]['code']} kB\nHeap: {page_usage[item_id]['heap']} kB\nStack: {page_usage[item_id]['stack']} kB\n", "center")

            #  Cria a tabela com as informações atuais dos recursos abertos/alocados pelo processo
            top.table_resources = ttk.Treeview(top, columns=("Arquivos Abertos", "Semáforos/Mutexes", "Sockets"), show="headings")
            top.table_resources.column("Arquivos Abertos", anchor="center", width=300)
            top.table_resources.column("Semáforos/Mutexes", anchor="center", width=300)
            top.table_resources.column("Sockets", anchor="center", width=300)
            
            top.table_resources.heading("Arquivos Abertos", text="Arquivos Abertos")
            top.table_resources.heading("Semáforos/Mutexes", text="Semáforos/Mutexes")
            top.table_resources.heading("Sockets", text="Sockets")
            top.table_resources.grid(row=2, column=0, columnspan=3, padx=0, pady=0, sticky="nsew")  # Adicionar sticky="nsew" para fazer a tabela expandir
            
            if item_id in process_resources:
                resources = process_resources[item_id]
                max_len = max(len(resources.get('open_files', [])), len(resources.get('sockets', [])), len(resources.get('semaphores_mutexes', [])))

                for i in range(max_len):
                    open_file = resources.get('open_files', [])[i] if i < len(resources.get('open_files', [])) else ""
                    socket = resources.get('sockets', [])[i] if i < len(resources.get('sockets', [])) else ""
                    semaphore_mutex = resources.get('semaphores_mutexes', [])[i] if i < len(resources.get('semaphores_mutexes', [])) else ""

                    formatted_open_file = f"Arquivo: {open_file['file_descriptor']}, Caminho: {open_file['file_path']}" if open_file else ""
                    formatted_socket = f"Tipo: {socket['type']}, Local: {socket['local_address']}, Remoto: {socket['remote_address']}" if socket else ""
                    formatted_semaphore_mutex = f"Semáforo/Mutex: {semaphore_mutex}" if semaphore_mutex else ""

                    top.table_resources.insert("", "end", values=(formatted_open_file, formatted_semaphore_mutex, formatted_socket))
            
            self.update_popup(top, item_id, process_memory, page_usage, process_details)
          
    # Atualização dos dados do pop-up  
    def update_popup(self, top, item_id, process_memory, page_usage, process_details):
        top.geometry("1000x600")
        top.title(item_id)
        
        top.table_details.delete(*top.table_details.get_children())
        for pid, details in process_details.items():
            if pid == item_id:
                top.table_details.insert("", "end", values=(
                    details.get('Command Line'),
                    details.get('State'),
                    details.get('Uid'),
                    details.get('Gid'),
                    details.get('PPid')
                ))
        
        top.memory_usage.delete("1.0", tkinter.END)
        if item_id in process_memory:
            if process_memory[item_id]:
                top.memory_usage.insert("end", f"Uso da Memória:\n{process_memory[item_id]} kB\n", "center")
            else:
                top.memory_usage.insert("end", "Uso da Memória:\n0 kB\n", "center")
        else:
            top.memory_usage.insert("end", "Uso da Memória:\n0 kB\n", "center")
        
        top.page_usage.delete("1.0", tkinter.END)
        if item_id in page_usage:
            top.page_usage.insert("end", f"Uso de páginas:\nTotal: {page_usage[item_id]['total']} kB\nCódigo: {page_usage[item_id]['code']} kB\nHeap: {page_usage[item_id]['heap']} kB\nStack: {page_usage[item_id]['stack']} kB\n", "center")

        top.after(1000, lambda: self.update_popup(top, item_id, process_memory, page_usage, process_details))
    
    # Cria os elementos da aba Processos
    def process_tab(self, processes, threads, process_memory, page_usage, process_details, process_resources):
        # Cria a tabela dos processos, exibindo o ID, usuário, Nome e Status de cada um
        self.table = ttk.Treeview(self.tabview.tab("Processos"), columns=("Num", "ID", "Usuário", "Nome", "Status"), show="headings")
        self.table.column("ID", anchor="center", width=216)
        self.table.column("Usuário", anchor="center", width=216)
        self.table.column("Nome", anchor="center", width=432)
        self.table.column("Status", anchor="center", width=216)
        self.table.heading("ID", text="ID")
        self.table.heading("Usuário", text="Usuário")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Status", text="Status")

        self.table.heading("Num", text="")
        self.table.column("Num", width=40, anchor="w")
        threads_info = []

        df = pd.DataFrame.from_dict(processes)
        for index, row in df.iterrows():
            process_id = row['ID']
            self.table.insert("", "end", process_id, values=("▶", row['ID'], row['Usuário'], row['Nome'], row['Status']))

            for thread in threads:
                if(thread['PID'] == process_id):
                    threads_info.append({'ID': thread['ID'], 'Usuário': thread['Usuário'], 'Nome': thread['Nome'], 'Status': thread['Status']})
                    
            for thread in threads_info:
                self.table.insert(process_id, "end", values=("", thread['ID'], thread['Usuário'], thread['Nome'], thread['Status']))
            self.table.item(process_id, open=False) 

        self.table.bind("<Button-1>", lambda event, p_mem=process_memory, pag_us=page_usage, p_details=process_details, p_resources=process_resources: self.open_popup(event, p_mem, pag_us, p_details, p_resources))
        
        self.table.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.tabview.tab("Processos").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Processos").grid_rowconfigure(0, weight=1)
        
    # Atualiza os dados da aba Processos
    def update_process(self, processes, threads):
        df = pd.DataFrame.from_dict(processes)
        self.table.delete(*self.table.get_children())  
        threads_info = []
        

        for index, row in df.iterrows():
            process_id = row['ID']
            self.table.insert("", "end", process_id, values=("▶", row['ID'], row['Usuário'], row['Nome'], row['Status']))

            for thread in threads:
                if(thread['PID'] == process_id):
                    threads_info.append({'ID': thread['ID'], 'Usuário': thread['Usuário'], 'Nome': thread['Nome'], 'Status': thread['Status']})
                    
            for thread in threads_info:
                self.table.insert(process_id, "end", values=("", thread['ID'], thread['Usuário'], thread['Nome'], thread['Status']))
            self.table.item(process_id, open=False) 

    # Cria os elementos da aba Dados globais
    def global_data_tab(self):
        self.tabview.tab("Dados globais").grid_columnconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Dados globais").grid_rowconfigure((0, 1, 2), weight=1)

        # Cria o gráfico com a porcentagem de uso da CPU pelo tempo
        self.figure = Figure(figsize=(10, 2), dpi=100, facecolor="k")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('k')
        self.myFmt = mdates.DateFormatter("%S")
        self.ax.xaxis.set_major_formatter(self.myFmt)
    
        for label in self.ax.xaxis.get_ticklabels():
            label.set_color('w')
        for label in self.ax.yaxis.get_ticklabels():
            label.set_color('w')
        for line in self.ax.yaxis.get_ticklines():
            line.set_color('w')
        for line in self.ax.xaxis.get_ticklines():
            line.set_color('w')
        for line in self.ax.xaxis.get_gridlines():
            line.set_color('w')

        for line in self.ax.yaxis.get_gridlines():
            line.set_color('w')
            line.set_markeredgewidth(8)

        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        
        dateTimeObj = datetime.now() + timedelta(seconds=-30)
        self.x_data = [dateTimeObj + timedelta(seconds=i) for i in range(30)]
        self.y_data = [0 for i in range(30)]
        self.plot = self.ax.plot(self.x_data, self.y_data, label='CPU')[0]
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])

        self.canvas = FigureCanvasTkAgg(self.figure, self.tabview.tab("Dados globais"))
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, padx=(20, 0), pady=(20, 0), sticky="nsew")
        
        # Cria caixas de texto com a parcentagem de uso da CPU, tempo ocioso, quantidade de processo e de threads
        self.cpu = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font = ("Monserrat", 15))
        self.cpu.grid(row=1, column=0,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.cpu.tag_config("center", justify="center")
        self.idle = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font = ("Monserrat", 15))
        self.idle.grid(row=1, column=1,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.idle.tag_config("center", justify="center")
        self.process = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font = ("Monserrat", 15))
        self.process.grid(row=1, column=2,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.process.tag_config("center", justify="center")
        self.threads = customtkinter.CTkTextbox(self.tabview.tab("Dados globais"), font = ("Monserrat", 15))
        self.threads.grid(row=1, column=3,padx=(10, 0), pady=(10, 0), sticky="nsew")
        self.threads.tag_config("center", justify="center")

    # Atualiza os elementos da aba Dados Globais
    def update_global_data(self, cpu_percentage, idle_percentage, total_process, total_threads):
        current_time = datetime.now()
        self.x_data.append(current_time)
        self.y_data.append(cpu_percentage)

        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)

        one_minute_ago = current_time - timedelta(minutes=1)
        self.ax.set_xlim(one_minute_ago, current_time)

        self.ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.ax.yaxis.set_major_formatter(mticker.PercentFormatter())

        self.canvas.draw_idle()
        
        self.cpu.delete("1.0", tkinter.END)
        self.cpu.insert("0.0", f"Uso da CPU: {cpu_percentage:.2f}%\n", "center")
        self.idle.delete("1.0", tkinter.END)
        self.idle.insert("0.0", f"Tempo ocioso: {idle_percentage:.2f}%\n", "center")
        self.process.delete("1.0", tkinter.END)
        self.process.insert("0.0", f"Quantidade de processos: {total_process: }\n", "center")
        self.threads.delete("1.0", tkinter.END)
        self.threads.insert("0.0", f"Quantidade de threads: {total_threads: }\n", "center")

    # Cria os elementos da aba Memória
    def memory_tab(self, meminfo):  
        #Cria a tabela os as informações da memória
        self.mem_table = ttk.Treeview(self.tabview.tab("Memória"), columns=("Memória", "Valor"), show="headings")     
        self.mem_table.grid(row=0, column=0, rowspan=3, padx=0, pady=0, sticky="nsew")
        self.mem_table.column("Memória", anchor="center", width=120)
        self.mem_table.column("Valor", anchor="center", width=120)
        self.mem_table.heading("Memória", text="Memória")
        self.mem_table.heading("Valor", text="Valor")

        for key, value in meminfo.items():
            self.mem_table.insert("", "end", values=(key, value))

        # Cria o gráfico da porcentagem de memória pelo tempo
        self.figure_mem = Figure(figsize=(10, 2.5), dpi=100, facecolor="k")
        self.ax_mem = self.figure_mem.add_subplot(111)
        self.ax_mem.set_facecolor('k')
        self.myFmt = mdates.DateFormatter("%S")
        self.ax_mem.xaxis.set_major_formatter(self.myFmt)

        for label in self.ax_mem.xaxis.get_ticklabels():
            label.set_color('w')
        for label in self.ax_mem.yaxis.get_ticklabels():
            label.set_color('w')
        for line in self.ax_mem.yaxis.get_ticklines():
            line.set_color('w')
        for line in self.ax_mem.xaxis.get_ticklines():
            line.set_color('w')
        for line in self.ax_mem.xaxis.get_gridlines():
            line.set_color('w')

        for line in self.ax_mem.yaxis.get_gridlines():
            line.set_color('w')
            line.set_markeredgewidth(8)

        self.ax_mem.spines['bottom'].set_color('white')
        self.ax_mem.spines['left'].set_color('white')

        dateTimeObj = datetime.now() + timedelta(seconds=-30)
        self.x_data_mem = [dateTimeObj + timedelta(seconds=i) for i in range(30)]
        self.y_data_mem = [0 for i in range(30)]
        self.plot_mem = self.ax_mem.plot(self.x_data_mem, self.y_data_mem, label='Memória')[0]
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xlim(self.x_data_mem[0], self.x_data_mem[-1])

        self.canvas_mem = FigureCanvasTkAgg(self.figure_mem, self.tabview.tab("Memória"))
        self.canvas_mem.get_tk_widget().grid(row=0, column=1, columnspan=3, rowspan=1, padx=(5, 0), pady=(5, 0), sticky="nsew")

        # Cria caixas de texto com a porcentagem de uso da memória, a quantidade de memória livre, virtual e física
        self.memory_usage = customtkinter.CTkTextbox(self.tabview.tab("Memória"), font=("Monserrat", 15))
        self.memory_usage.grid(row=1, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.memory_usage.tag_config("center", justify="center")

        self.free_memory = customtkinter.CTkTextbox(self.tabview.tab("Memória"), font=("Monserrat", 15))
        self.free_memory.grid(row=1, column=2, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.free_memory.tag_config("center", justify="center")

        self.RAM_memory = customtkinter.CTkTextbox(self.tabview.tab("Memória"), font=("Monserrat", 15))
        self.RAM_memory.grid(row=2, column=1, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.RAM_memory.tag_config("center", justify="center")

        self.virtual_memory = customtkinter.CTkTextbox(self.tabview.tab("Memória"), font=("Monserrat", 15))
        self.virtual_memory.grid(row=2, column=2, padx=(5, 0), pady=(5, 0), sticky="nsew")
        self.virtual_memory.tag_config("center", justify="center")

    # Atualiza os elementos da aba Memória
    def update_memory_tab(self, meminfo, memory_usage_percent):
        current_time = datetime.now()
        
        self.x_data_mem.append(current_time)
        self.y_data_mem.append(memory_usage_percent)
        self.x_data_mem = self.x_data_mem[1:]
        self.y_data_mem = self.y_data_mem[1:]
        self.plot_mem.set_xdata(self.x_data_mem)
        self.plot_mem.set_ydata(self.y_data_mem)

        one_minute_ago = current_time - timedelta(minutes=1)
        self.ax_mem.set_xlim(one_minute_ago, current_time)

        self.ax_mem.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.ax_mem.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.ax_mem.yaxis.set_major_formatter(mticker.PercentFormatter())
        self.canvas_mem.draw_idle()

        df = pd.DataFrame.from_dict(meminfo, orient='index', columns=['Value'])
        self.mem_table.delete(*self.mem_table.get_children())  
        for index, row in df.iterrows():
            self.mem_table.insert("", "end", values=(index, row['Value']))

        self.memory_usage.delete("1.0", tkinter.END)
        self.memory_usage.insert("end", f"Uso da Memória:\n{memory_usage_percent:.2f}%\n", "center")

        self.free_memory.delete("1.0", tkinter.END)
        self.free_memory.insert("end", f"Memória livre:\n{meminfo['MemFree']/1000000:.2f}GB\n", "center")

        self.RAM_memory.delete("1.0", tkinter.END)
        self.RAM_memory.insert("end", f"Memória física:\n{meminfo['MemTotal']/1000000:.2f}GB\n", "center")

        self.virtual_memory.delete("1.0", tkinter.END)
        self.virtual_memory.insert("end", f"Memória virtual:\n{meminfo['SwapTotal']/1000000:.2f}GB\n", "center")

    # Cria os elementos da aba Arquivos
    def files_tab(self, partitions):
        # Cria a tabela dos processos, exibindo o ID, usuário, Nome e Status de cada um
        self.files_table = ttk.Treeview(self.tabview.tab("Sistema de arquivos"), columns=("Partições", "Percentual usado", "Total", "Usado", "Livre", ), show="headings")
        self.files_table.column("Partições", anchor="center", width=200)
        self.files_table.column("Percentual usado", anchor="center", width=200)
        self.files_table.column("Total", anchor="center", width=200)
        self.files_table.column("Usado", anchor="center", width=200)
        self.files_table.column("Livre", anchor="center", width=200)
        
        self.files_table.heading("Partições", text="Partições")
        self.files_table.heading("Percentual usado", text="Percentual usado")
        self.files_table.heading("Total", text="Total")
        self.files_table.heading("Usado", text="Usado")
        self.files_table.heading("Livre", text="Livre")
        
        for index, row in enumerate(partitions):
            self.files_table.insert("", "end", index, values=(row['Partições'], row['Percentual usado'], row['Total'], row['Usado'], row['Livre']))

        self.files_table.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.tabview.tab("Sistema de arquivos").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Sistema de arquivos").grid_rowconfigure(0, weight=1)
        
    # Atualiza os dados da aba Arquivos
    def update_files_tab(self, partitions):
        self.files_table.delete(*self.files_table.get_children())  

        for index, row in enumerate(partitions):
            self.files_table.insert("", "end", index, values=(row['Partições'], row['Percentual usado'], row['Total'], row['Usado'], row['Livre']))
            
    def directory_tab(self, directory_tree):
        self.directory_tree = ttk.Treeview(self.tabview.tab("Diretórios"))
        self.directory_tree.pack(expand=True, fill='both')
        
        # Configurar colunas e cabeçalhos
        self.directory_tree["columns"] = ("Tamanho", "Permissões", "Última modificação")
        self.directory_tree.column("#0", width=300, minwidth=150)
        self.directory_tree.column("Tamanho", width=100, anchor="center")
        self.directory_tree.column("Permissões", width=150, anchor="center")
        self.directory_tree.column("Última modificação", width=200, anchor="w")

        self.directory_tree.heading("#0", text="Nome", anchor='w')
        self.directory_tree.heading("Tamanho", text="Tamanho")
        self.directory_tree.heading("Permissões", text="Permissões")
        self.directory_tree.heading("Última modificação", text="Última modificação")
        

        for item in directory_tree:
            self.insert_item_directory_tab('', item)
            

    def insert_item_directory_tab(self, parent, item):
        if item['type'] == 'directory':
            node = self.directory_tree.insert(parent, 'end', text=item['name'], open=False)
            for child in item.get('children', []):
                self.insert_item_directory_tab(node, child)
        else:
            self.directory_tree.insert(parent, 'end', values=(f"{item['size']} bytes", item['permissions'], item['last_modified']), text=item['name'])
       