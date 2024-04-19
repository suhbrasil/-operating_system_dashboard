import ctypes
import os
import time
import pandas as pd
import numpy as np
import panel as pn
import array as arr
from process import *
import tkinter as tk
from pandastable import Table, TableModel
pn.extension('tabulator')

import hvplot.pandas

# Definindo a estrutura para armazenar informações de cada processo
class ProcessInfo(ctypes.Structure):
    _fields_ = [("pid", ctypes.c_int),
                ("name", ctypes.c_char * 256),
                ("status", ctypes.c_char * 16)]

libc = ctypes.CDLL(None)
pd.set_option('future.no_silent_downcasting', True)

def get_all_processes():
    processes = []
    for entry in os.listdir('/proc'):
        if entry.isdigit():  # Verifica se o diretório é um processo (PID é um número)
            pid = int(entry)
            try:
                # Abre o arquivo 'status' do processo para obter informações
                with open(f'/proc/{pid}/status', 'r') as status_file:
                    for line in status_file:
                        if line.startswith('Name:'):
                            name = line.split(':', 1)[1].strip()
                        elif line.startswith('State:'):
                            status = line.split(':', 1)[1].strip()
                processes.append({'PID': pid, 'Nome': name, 'Status': status})
            except FileNotFoundError:
                pass
    return reversed(processes)



processes = get_all_processes()
# Processamento e apresentação dos dados
df = pd.DataFrame.from_dict(processes)
df_pane = pn.widgets.DataFrame(df, autosize_mode='fit_columns', width=400)
df_pane

janela = tk.Tk()
janela.title("Dashboard")

frame = tk.Frame(janela)
frame.pack()

pt = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
pt.show()

janela.mainloop()
