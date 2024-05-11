import os
import os.path

class Model:
    def __init__(self):
        # Initialize previous idle and total times
        self.prev_idle, self.prev_total = self.get_idle_and_total_time()
        self.total_processes = 0
        self.total_threads = 0

    def get_memory_info(self):
        memory_info = {}
        with open('/proc/meminfo', 'r') as file:
            for line in file:
                key, value = line.split(':')
                key = key.strip()
                value = int(value.split()[0])
                memory_info[key] = value
        return memory_info
    
    def calculate_memory_usage(self, memory_info):
        total_memory = memory_info['MemTotal']
        free_memory = memory_info['MemFree']
        buffers_memory = memory_info['Buffers']
        cached_memory = memory_info['Cached']
        used_memory = total_memory - free_memory - buffers_memory - cached_memory
        memory_usage_percent = (used_memory / total_memory) * 100
        return memory_usage_percent
    
    
    
    def get_processes_and_threads(self):
        processes = []
        threads = []

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

                # Iterar sobre os diretórios em /proc
                for entry in os.listdir(f'/proc/{pid}/task'):
                    # Verificar se a entrada é um diretório e representa um processo
                    if entry.isdigit():
                        tid = entry

                        # Inicializar variáveis para armazenar informações do thread
                        user = 'Unknown'
                        name = 'Unknown'
                        status = 'Unknown'

                        # Tentar ler o arquivo status
                        try:
                            with open(f'/proc/{pid}/task/{tid}/status', 'r') as status_file:
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
                            # Se o arquivo status não existe, pular este thread
                            continue

                        # Adicionar as informações do thread à lista
                        threads.append({'ID': tid, 'Usuário': user, 'Nome': name, 'Status': status, 'PID': pid})
                        
        return reversed(processes), threads
    
    def get_cpu_usage(self):
        # Calculate CPU usage based on previous and current idle and total times
        idle_time, total_time = self.get_idle_and_total_time()

        if(total_time - self.prev_total) == 0:
            self.prev_idle, self.prev_total = idle_time, total_time
            return 0.0
        
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