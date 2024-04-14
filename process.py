import ctypes
import os
import time
import csv

# Define a estrutura para armazenar as informações do uso do processador
class CPUUsage(ctypes.Structure):
    _fields_ = [("user", ctypes.c_ulong),
                ("nice", ctypes.c_ulong),
                ("system", ctypes.c_ulong),
                ("idle", ctypes.c_ulong),
                ("iowait", ctypes.c_ulong),
                ("irq", ctypes.c_ulong),
                ("softirq", ctypes.c_ulong),
                ("steal", ctypes.c_ulong),
                ("guest", ctypes.c_ulong),
                ("guest_nice", ctypes.c_ulong)]

# Carrega a biblioteca do sistema
libc = ctypes.CDLL(None)
libc.get_cpu_usage = ctypes.CDLL(None).getloadavg
libc.get_cpu_usage.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
libc.get_cpu_usage.restype = ctypes.c_int

# Define o tipo de retorno e os argumentos da função opendir
libc.opendir.restype = ctypes.c_void_p
libc.opendir.argtypes = [ctypes.c_char_p]

# Define o tipo de retorno e os argumentos da função readdir
libc.readdir.restype = ctypes.POINTER(ctypes.c_void_p)
libc.readdir.argtypes = [ctypes.c_void_p]

# Define o tipo de retorno e os argumentos da função closedir
libc.closedir.restype = ctypes.c_int
libc.closedir.argtypes = [ctypes.c_void_p]

# Obtém todos os processos do diretório /proc com suas informações
def get_all_processes():
    processes = []
    
    for entry in os.listdir('/proc'):
        if entry.isdigit():  # Verifica se o diretório é um processo (PID é um número)
            pid = int(entry)
            try:
                 # Abre o arquivo 'status' do processo para obter informações
                with open(f'/proc/{pid}/status', 'r') as status_file:
                    process_info = {}
                    # Lê o conteúdo do arquivo de status
                    for line in status_file:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            process_info[key] = value
                    processes.append(process_info)
            except (ValueError, FileNotFoundError):
                pass

    return processes

# Obtém as informações de uso do processador
def get_cpu_usage():
    load_avg = (ctypes.c_double * 3)()
    if libc.get_cpu_usage(load_avg, 3) == -1:
        return None
    return load_avg

# Obtém as threads de um processo
def get_threads_info(pid):
    threads = []
    for thread_id in os.listdir(f"/proc/{pid}/task"):
        threads.append(int(thread_id))
    return threads

# Obtém informações detalhadas de um processo
def get_process_details(pid):
    details = {}
    status_path = f"/proc/{pid}/status"
    try:
        with open(status_path, 'r') as status_file:
            for line in status_file:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    details[key] = value
    except FileNotFoundError:
        pass
    return details

# Monitora os processos
def monitor_processes():
    sidebar = {}
    
    # Exibe a lista de processos com seus respectivos usuários
    processes = get_all_processes()
    for process_info in processes:
        pid = process_info.get('Pid')
        if pid:
            pid = int(pid)
            sidebar['Nome'] = process_info.get('Name', 'N/A')
            sidebar['Threads'] = process_info.get('State', 'N/A')
            sidebar['Usuário'] = process_info.get('Uid', 'N/A')
            sidebar['Estado'] = process_info.get('State', 'N/A')
            sidebar['PID'] = pid
            
            #for key, value in details.items():
             #   print(f"{key}: {value}")
            #print("-" * 20)
    return sidebar


