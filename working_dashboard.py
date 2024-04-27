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

import numpy as np
import os

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

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
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{1100}x{580}")

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.add("Processos")
        self.tabview.add("Dados globais")
        self.tabview.add("Memória")

    def process_tab(self):
        

        # configure grid layout (4x4)
        # o weight = 1 significa que a coluna vai redimencionar quando a tela mudar de tamanho e weight = 0 não redimenciona a coluna
        # 0: primeira coluna, 1: segunda coluna, ...
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="CustomTkinter", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_process_table, text="Processos")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_cpu, text="CPU")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        #self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        #self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Aparência:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Claro", "Escuro"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="Tamanho:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.current_widgets = []


    def clear_widgets(self):
        # Clear existing widgets
        for widget in self.current_widgets:
            widget.destroy()
        self.current_widgets = []


    def sidebar_process_table(self):
        self.clear_widgets()

        # create treeview table
        self.table = ttk.Treeview(self, columns=("ID", "Nome", "Status"), show="headings")
        self.table.column("ID", anchor="center", stretch="no", width=180)
        self.table.column("Nome", anchor="center", width=310)
        self.table.column("Status", anchor="center", width=180)
        self.table.heading("ID", text="ID")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Status", text="Status")

        processes = self.get_all_processes()
        df = pd.DataFrame.from_dict(processes)
        for index, row in df.iterrows():
            self.table.insert("", "end", values=(row['ID'], row['Nome'], row['Status']))
        
        self.table.grid(row=0, column=1, rowspan=4,columnspan=4,padx=0, pady=0, sticky="nsew")  # Add sticky="nsew" to make it expand
        self.current_widgets.append(self.table)
        self.after(5000, self.update_page)

    def sidebar_cpu(self):
        self.clear_widgets()
        self.cpu()

    @staticmethod
    def get_cpu_usage():
        # Read the first line of /proc/stat
        with open('/proc/stat', 'r') as stat_file:
            stat_line = stat_file.readline()

        # Discard the first word of the first line (it's always "cpu")
        stat_values = stat_line.split()[1:]

        # Sum all of the times found on that first line to get the total time
        total_time = sum(map(int, stat_values))

        # Divide the fourth column ("idle") by the total time
        idle_time = int(stat_values[3])
        idle_fraction = idle_time / total_time

        # Subtract the idle fraction from 1.0 to get the time spent being not idle
        not_idle_fraction = 1.0 - idle_fraction

        # Multiply by 100 to get a percentage
        cpu_usage = not_idle_fraction * 100

        return cpu_usage


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

    def cpu(self):
        self.figure = Figure(figsize=(5, 5), dpi=100)
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

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.animate()
        

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("CTkTabview")
        self.tabview.add("Tab 2")
        self.tabview.add("Tab 3")
        self.tabview.tab("CTkTabview").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)

        
        self.table = ttk.Treeview(self.tabview.tab("CTkTabview"), columns=("ID", "Nome", "Status"), show="headings")
        self.table.column("ID", anchor="center", stretch="no", width=80)
        self.table.column("Nome", anchor="center", width=210)
        self.table.column("Status", anchor="center", width=80)
        self.table.heading("ID", text="ID")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Status", text="Status")

        processes = self.get_all_processes()
        df = pd.DataFrame.from_dict(processes)
        for index, row in df.iterrows():
            self.table.insert("", "end", values=(row['ID'], row['Nome'], row['Status']))
        
        self.table.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")  # Add sticky="nsew" to make it expand


        self.combobox_1 = customtkinter.CTkComboBox(self.tabview.tab("CTkTabview"),
                                                    values=["Value 1", "Value 2", "Value Long....."])
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("CTkTabview"), text="Open CTkInputDialog",
                                                        command=self.open_input_dialog_event)
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Tab 2"), text="CTkLabel on Tab 2")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        # create radiobutton frame
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="CTkRadioButton Group:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # create slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        self.seg_button_1 = customtkinter.CTkSegmentedButton(self.slider_progressbar_frame)
        self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="CTkScrollableFrame")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []
        for i in range(100):
            switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"CTkSwitch {i}")
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches.append(switch)

        # create checkbox and switch frame
        self.checkbox_slider_frame = customtkinter.CTkFrame(self)
        self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.checkbox_1 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_2 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_3 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")

        # set default values
        #self.sidebar_button_3.configure(state="disabled", text="Disabled CTkButton")
        self.checkbox_3.configure(state="disabled")
        self.checkbox_1.select()
        self.scrollable_frame_switches[0].select()
        self.scrollable_frame_switches[4].select()
        self.radio_button_3.configure(state="disabled")
        self.appearance_mode_optionemenu.set("Escuro")
        self.scaling_optionemenu.set("100%")
        self.combobox_1.set("CTkComboBox")
        self.slider_1.configure(command=self.progressbar_2.set)
        self.slider_2.configure(command=self.progressbar_3.set)
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()
        #self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        self.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        self.seg_button_1.set("Value 2")

        # Add created widgets to the current_widgets list
        #self.current_widgets.append(self.textbox)
        self.current_widgets.append(self.canvas.get_tk_widget())
        self.current_widgets.append(self.tabview)
        self.current_widgets.append(self.table)
        self.current_widgets.append(self.combobox_1)
        self.current_widgets.append(self.string_input_button)
        self.current_widgets.append(self.label_tab_2)

        self.after(1000, self.animate)

    def update_page(self):
        # update the Treeview widget with new data
        processes = self.get_all_processes()
        df = pd.DataFrame.from_dict(processes)
        self.table.delete(*self.table.get_children())  # Clear existing data
        for index, row in df.iterrows():
            self.table.insert("", "end", values=(row['ID'], row['Nome'], row['Status']))

        # Schedule the method to update the page again after 5 seconds
        self.after(5000, self.update_page)

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        if(new_appearance_mode == "Claro"):
            customtkinter.set_appearance_mode("Light")
        else:
            customtkinter.set_appearance_mode("Dark")

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def get_all_processes(self):
        processes = []
        
        for entry in os.listdir('/proc'):
            if entry.isdigit():  
                pid = int(entry)
                try:
                    with open(f'/proc/{pid}/status', 'r') as status_file:
                        for line in status_file:
                            if line.startswith('Name:'):
                                name = line.split(':', 1)[1].strip()
                            elif line.startswith('State:'):
                                status = line.split(':', 1)[1].split('(', 1)[-1].split(')', 1)[0].strip()
                    processes.append({'ID': pid, 'Nome': name, 'Status': status})
                except FileNotFoundError:
                    pass
        
        return reversed(processes)
    
    
app = App()
app.mainloop()