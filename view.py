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
import matplotlib.ticker as mticker
import os
import os.path



class View(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
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


    def process_tab(self, processes, threads):
        # create treeview table
        self.table = ttk.Treeview(self.tabview.tab("Processos"), columns=("Num", "ID", "Usuário", "Nome", "Status"), show="headings")
        self.table.column("ID", anchor="center", width=216)
        self.table.column("Usuário", anchor="center", width=216)
        self.table.column("Nome", anchor="center", width=432)
        self.table.column("Status", anchor="center", width=216)
        self.table.heading("ID", text="ID")
        self.table.heading("Usuário", text="Usuário")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Status", text="Status")

        # Add a column to display the expand/collapse button/icon
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
            self.table.item(process_id, open=False)  # Start with threads collapsed

        # Bind the click event to toggle the node (process) expansion
        self.table.bind("<Button-1>", self.toggle_process)

        
        self.table.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")  # Add sticky="nsew" to make it expand

        # Configure row and column weights to make the table expand to fill the available space
        self.tabview.tab("Processos").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Processos").grid_rowconfigure(0, weight=1)


    def toggle_process(self, event):
        item_id = self.table.identify_row(event.y)
        current_value = self.table.set(item_id, "Num")
        new_value = "▼" if current_value == "▶" else "▶"
        self.table.set(item_id, "Num", value=new_value)
        self.table.item(item_id, open=not self.table.item(item_id, "open"))


    def update_process(self, processes, threads):
        # update the Treeview widget with new data
        df = pd.DataFrame.from_dict(processes)
        self.table.delete(*self.table.get_children())  # Clear existing data
        threads_info = []
        

        for index, row in df.iterrows():
            process_id = row['ID']
            self.table.insert("", "end", process_id, values=("▶", row['ID'], row['Usuário'], row['Nome'], row['Status']))

            for thread in threads:
                if(thread['PID'] == process_id):
                    threads_info.append({'ID': thread['ID'], 'Usuário': thread['Usuário'], 'Nome': thread['Nome'], 'Status': thread['Status']})
                    
            for thread in threads_info:
                self.table.insert(process_id, "end", values=("", thread['ID'], thread['Usuário'], thread['Nome'], thread['Status']))
            self.table.item(process_id, open=False)  # Start with threads collapsed



    def global_data_tab(self):
        self.tabview.tab("Dados globais").grid_columnconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Dados globais").grid_rowconfigure((0, 1, 2), weight=1)

        self.figure = Figure(figsize=(10, 2), dpi=100, facecolor="k")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('k')
        # format the x-axis to show the time
        self.myFmt = mdates.DateFormatter("%S")
        self.ax.xaxis.set_major_formatter(self.myFmt)
    
        for label in self.ax.xaxis.get_ticklabels():
            # label is a Text instance
            label.set_color('w')
        for label in self.ax.yaxis.get_ticklabels():
            # label is a Text instance
            label.set_color('w')
            # label.set_rotation(45)
            # label.set_fontsize(1)
        for line in self.ax.yaxis.get_ticklines():
            # line is a Line2D instance
            line.set_color('w')
        for line in self.ax.xaxis.get_ticklines():
            # line is a Line2D instance
            line.set_color('w')
            # line.set_markersize(25)
            # line.set_markeredgewidth(3)
        for line in self.ax.xaxis.get_gridlines():
            line.set_color('w')

        for line in self.ax.yaxis.get_gridlines():
            line.set_color('w')
            line.set_markeredgewidth(8)

        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        

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



    def update_global_data(self, cpu_percentage, idle_percentage, total_process, total_threads):
        # Append new data point to the x and y data
        current_time = datetime.now()
        self.x_data.append(current_time)
        self.y_data.append(cpu_percentage)

        # Update plot data
        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)

        # Update x-axis range to show the last 1 minute
        one_minute_ago = current_time - timedelta(minutes=1)
        self.ax.set_xlim(one_minute_ago, current_time)

        # Update x-axis ticks to show seconds from 0 to 60
        self.ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.ax.yaxis.set_major_formatter(mticker.PercentFormatter())

        # Redraw plot
        self.canvas.draw_idle()

        # Update the CPU percentage text using the get_cpu_usage method   
        
        self.cpu.delete("1.0", tkinter.END)
        self.cpu.insert("0.0", f"Uso da CPU: {cpu_percentage:.2f}%\n", "center")
        self.idle.delete("1.0", tkinter.END)
        self.idle.insert("0.0", f"Tempo ocioso: {idle_percentage:.2f}%\n", "center")
        self.process.delete("1.0", tkinter.END)
        self.process.insert("0.0", f"Quantidade de processos: {total_process: }\n", "center")
        self.threads.delete("1.0", tkinter.END)
        self.threads.insert("0.0", f"Quantidade de threads: {total_threads: }\n", "center")


    def memory_tab(self, meminfo):  
        self.mem_table = ttk.Treeview(self.tabview.tab("Memória"), columns=("Memória", "Valor"), show="headings")     
        self.mem_table.grid(row=0, column=0, rowspan=3, padx=0, pady=0, sticky="nsew")
        self.mem_table.column("Memória", anchor="center", width=120)
        self.mem_table.column("Valor", anchor="center", width=120)
        self.mem_table.heading("Memória", text="Memória")
        self.mem_table.heading("Valor", text="Valor")

        for key, value in meminfo.items():
            self.mem_table.insert("", "end", values=(key, value))

        self.figure_mem = Figure(figsize=(10, 2.5), dpi=100, facecolor="k")
        self.ax_mem = self.figure_mem.add_subplot(111)
        self.ax_mem.set_facecolor('k')
        # format the x-axis to show the time
        self.myFmt = mdates.DateFormatter("%S")
        self.ax_mem.xaxis.set_major_formatter(self.myFmt)

        for label in self.ax_mem.xaxis.get_ticklabels():
            # label is a Text instance
            label.set_color('w')
        for label in self.ax_mem.yaxis.get_ticklabels():
            # label is a Text instance
            label.set_color('w')
            # label.set_rotation(45)
            # label.set_fontsize(1)
        for line in self.ax_mem.yaxis.get_ticklines():
            # line is a Line2D instance
            line.set_color('w')
        for line in self.ax_mem.xaxis.get_ticklines():
            # line is a Line2D instance
            line.set_color('w')
            # line.set_markersize(25)
            # line.set_markeredgewidth(3)
        for line in self.ax_mem.xaxis.get_gridlines():
            line.set_color('w')

        for line in self.ax_mem.yaxis.get_gridlines():
            line.set_color('w')
            line.set_markeredgewidth(8)

        self.ax_mem.spines['bottom'].set_color('white')
        self.ax_mem.spines['left'].set_color('white')

        # initial x and y data
        dateTimeObj = datetime.now() + timedelta(seconds=-30)
        self.x_data_mem = [dateTimeObj + timedelta(seconds=i) for i in range(30)]
        self.y_data_mem = [0 for i in range(30)]
        # create the plot
        self.plot_mem = self.ax_mem.plot(self.x_data_mem, self.y_data_mem, label='Memória')[0]
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.set_xlim(self.x_data_mem[0], self.x_data_mem[-1])

        self.canvas_mem = FigureCanvasTkAgg(self.figure_mem, self.tabview.tab("Memória"))
        self.canvas_mem.get_tk_widget().grid(row=0, column=1, columnspan=3, rowspan=1, padx=(5, 0), pady=(5, 0), sticky="nsew")

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
        



    def update_memory_tab(self, meminfo, memory_usage_percent):
        current_time = datetime.now()
        
        # append new data point to the x and y data
        self.x_data_mem.append(current_time)
        self.y_data_mem.append(memory_usage_percent)
        # remove oldest data point
        self.x_data_mem = self.x_data_mem[1:]
        self.y_data_mem = self.y_data_mem[1:]
        #  update plot data
        self.plot_mem.set_xdata(self.x_data_mem)
        self.plot_mem.set_ydata(self.y_data_mem)

        # Update x-axis range to show the last 1 minute
        one_minute_ago = current_time - timedelta(minutes=1)
        self.ax_mem.set_xlim(one_minute_ago, current_time)

        # Update x-axis ticks to show seconds from 0 to 60
        self.ax_mem.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
        self.ax_mem.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.ax_mem.yaxis.set_major_formatter(mticker.PercentFormatter())
        self.canvas_mem.draw_idle()  # redraw plot

        # update memory table
        df = pd.DataFrame.from_dict(meminfo, orient='index', columns=['Value'])
        self.mem_table.delete(*self.mem_table.get_children())  # Clear existing data
        for index, row in df.iterrows():
            self.mem_table.insert("", "end", values=(index, row['Value']))

        # update memory text
        self.memory_usage.delete("1.0", tkinter.END)
        self.memory_usage.insert("end", f"Uso da Memória:\n{memory_usage_percent:.2f}%\n", "center")

        self.free_memory.delete("1.0", tkinter.END)
        self.free_memory.insert("end", f"Memória livre:\n{meminfo['MemFree']/1000000:.2f}GB\n", "center")

        self.RAM_memory.delete("1.0", tkinter.END)
        self.RAM_memory.insert("end", f"Memória física:\n{meminfo['MemTotal']/1000000:.2f}GB\n", "center")

        self.virtual_memory.delete("1.0", tkinter.END)
        self.virtual_memory.insert("end", f"Memória virtual:\n{meminfo['SwapTotal']/1000000:.2f}GB\n", "center")

