import os
import time
import ctypes

# Constantes e estruturas necessárias para acessar informações de processo
SYS_sysinfo = 116 # Número da chamada de sistema para sysinfo()

class sysinfo_struct(ctypes.Structure):
    _fields_ = [
        ('uptime', ctypes.c_long),
        ('loads', ctypes.c_ulong * 3),
        ('totalram', ctypes.c_ulong),
        ('freeram', ctypes.c_ulong),
        ('sharedram', ctypes.c_ulong),
        ('bufferram', ctypes.c_ulong),
        ('totalswap', ctypes.c_ulong),
        ('freeswap', ctypes.c_ulong),
        ('procs', ctypes.c_ushort),
        ('totalhigh', ctypes.c_ulong),
        ('freehigh', ctypes.c_ulong),
        ('mem_unit', ctypes.c_uint),
        ('_f', ctypes.c_char * 20)  # Ignorado; reservado para uso futuro
    ]

# Carregando a biblioteca C padrão do sistema operacional
libc = ctypes.CDLL(None)

# Protótipos das chamadas de sistema
libc.sysinfo.argtypes = [ctypes.POINTER(sysinfo_struct)]
libc.sysinfo.restype = ctypes.c_int

# Função para obter informações do sistema
def get_sysinfo():
    info = sysinfo_struct()
    libc.sysinfo(ctypes.byref(info))
    return info

# Função para listar informações de todos os processos em execução
def list_processes():
    processes = []
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                pid_int = int(pid)
                process_info = {}
                with open(f'/proc/{pid}/status') as f:
                    for line in f:
                        key, value = line.split(':', 1)
                        process_info[key.strip()] = value.strip()
                processes.append(process_info)
            except Exception as e:
                print(f"Erro ao processar o processo {pid}: {e}")
    return processes

# Função para exibir informações do sistema e dos processos
def display_info(interval=5):
    while True:
        # Obtendo informações do sistema
        sys_info = get_sysinfo()
        print("Informações do sistema:")
        print("Total de RAM:", sys_info.totalram, "bytes")
        print("RAM livre:", sys_info.freeram, "bytes")

        # Obtendo informações de todos os processos
        all_processes = list_processes()
        print("\nInformações de todos os processos:")
        for process in all_processes:
            print(f"PID: {process.get('Pid', 'N/A')}, Nome: {process.get('Name', 'N/A')}, Uso de Memória: {process.get('VmRSS', 'N/A')} kB")

        # Aguardar intervalo de tempo antes de atualizar as informações
        time.sleep(interval)

if __name__ == "__main__":
    display_info()