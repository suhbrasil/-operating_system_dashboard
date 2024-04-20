import tkinter as tk
from tkinter import ttk
import pandas as pd
import os
import customtkinter

# Function to update the dataframe
def update_dataframe():
    for tree in tree_widgets.values():  # Iterate over all tree widgets
        # Your code to get/process data into a DataFrame
        processes = get_all_processes()
        df = pd.DataFrame.from_dict(processes)
        
        # Update the Treeview with the new data
        for i in tree.get_children():
            tree.delete(i)
        for index, row in df.iterrows():
            tree.insert("", "end", values=(row['ID'], row['Nome'], row['Status']))
    
    # Schedule the next update
    root.after(5000, update_dataframe)

# Function to get all processes
def get_all_processes():
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

# Main Tkinter application
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.title('Operating System Dashboard')
root.geometry('1200x800')  # Set window size

# Sidebar with buttons to add tabs
sidebar = customtkinter.CTkFrame(master=root, width=200)
sidebar.pack(side='left', fill='y')

# Notebook widget to create multiple tabs/pages
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Dictionary to store mapping between tabs and tree widgets
tree_widgets = {}

def get_cpu_usage():
    total_processes = 0
    total_threads = 0
    
    for entry in os.listdir('/proc'):
        if entry.isdigit():  
            pid = int(entry)
            try:
                with open(f'/proc/{pid}/status', 'r') as status_file:
                    for line in status_file:
                        total_processes += 1
            except FileNotFoundError:
                pass

    total_threads = sum(1 for entry in os.listdir('/proc') if entry.isdigit() and os.path.isdir(f'/proc/{entry}/task'))

    with open('/proc/stat', 'r') as stat_file:
        lines = stat_file.readlines()

    for line in lines:
        if line.startswith('cpu '):  # A linha 'cpu' contém as estatísticas globais de CPU
            cpu_stats = line.split()
            user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice = map(int, cpu_stats[1:])
            total_cpu_time = user + nice + system + idle + iowait + irq + softirq + steal + guest + guest_nice
            idle_time = idle + iowait
            cpu_usage = (total_cpu_time - idle_time) / total_cpu_time * 100.0
            idle_percentage = (idle_time / total_cpu_time) * 100.0
            return total_processes, total_threads, cpu_usage, idle_percentage

def add_tab(tab_name):
    # Remove the current tab
    for tab in notebook.tabs():
        notebook.forget(tab)
    tree_widgets.clear()
    
    # Add a new tab
    tab_frame = tk.Frame(root)
    tab_frame.pack(fill='both', expand=True)
    
    if tab_name == "Processes":
        # Add a Treeview to display process information
        tree = ttk.Treeview(tab_frame, columns=('ID', 'Nome', 'Status'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Nome', text='Nome')
        tree.heading('Status', text='Status')
        tree.pack(fill='both', expand=True)
        
        notebook.add(tab_frame)
        tree_widgets[0] = tree  # Add tree widget to dictionary
        
        # Update the Treeview with process data
        update_dataframe()
    elif tab_name == "CPU Usage":
        # Add a label to display CPU usage information
        cpu_label = tk.Label(tab_frame, text="CPU Usage: ")
        cpu_label.pack()
        
        # Add another label to display idle percentage
        idle_label = tk.Label(tab_frame, text="Idle Percentage: ")
        idle_label.pack()

        # Add a label to display CPU usage information
        total_process_label = tk.Label(tab_frame, text="Total process: ")
        total_process_label.pack()
        
        # Add another label to display idle percentage
        total_thread_label = tk.Label(tab_frame, text="Total threads: ")
        total_thread_label.pack()
        
        notebook.add(tab_frame)
        
        # Get CPU usage and idle percentage and display them
        total_processes, total_threads, cpu_usage, idle_percentage = get_cpu_usage()
        total_process_label.config(text=f"Total process: {total_processes:.2f}")
        total_thread_label.config(text=f"Total threads: {total_threads:.2f}")
        cpu_label.config(text=f"CPU Usage: {cpu_usage:.2f}%")
        idle_label.config(text=f"Idle Percentage: {idle_percentage:.2f}%")
        
    else:
        # Add a label to indicate an empty page
        empty_label = tk.Label(tab_frame, text="This page is empty.")
        empty_label.pack()
        
        notebook.add(tab_frame)

# Function to add a new tab button in the sidebar
def add_page(tab_name):
    add_tab(tab_name)

btn_page1 = customtkinter.CTkButton(sidebar, text="Processes", command=lambda: add_page("Processes"), width=50)
btn_page1.pack(padx=20, pady=10, anchor='center')  # Anchor to left side
btn_page2 = customtkinter.CTkButton(sidebar, text="CPU Usage", command=lambda: add_page("CPU Usage"), width=50)
btn_page2.pack(padx=20, pady=10, anchor='center')  # Anchor to left side
btn_page3 = customtkinter.CTkButton(sidebar, text="Empty Page 2", command=lambda: add_page("Empty Page 2"), width=50)
btn_page3.pack(padx=20, pady=10, anchor='center')  # Anchor to left side

# Add the table page as default
add_tab("Processes")

style = ttk.Style()
    
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

# Pack the notebook widget after the sidebar
notebook.pack(fill='both', expand=True)

# Run the Tkinter event loop
root.mainloop()
