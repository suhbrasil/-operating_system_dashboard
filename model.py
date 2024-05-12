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

    def get_all_process_memory(self):
        all_process_memory = {}
        try:
            # Iterate over all directories in /proc
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit():  # Check if it's a process ID (numeric directory)
                    pid = pid_dir
                    process_memory = self.get_process_memory_by_pid(pid)
                    if process_memory is not None:
                        all_process_memory[pid] = process_memory
        except FileNotFoundError:
            pass  # process has already terminated
        return all_process_memory

    def get_process_memory_by_pid(self, pid):
        process_memory = None  # Initialize to None
        try:
            with open(os.path.join('/proc', pid, 'status')) as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        memory = line.split()[1]  # memory in kB
                        process_memory = int(memory)
                        break
        except FileNotFoundError:
            pass  # process has already terminated
        return process_memory

    
    def get_all_page_usage(self):
        all_page_usage = {}
        try:
            # Iterate over all directories in /proc
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit():  # Check if it's a process ID (numeric directory)
                    pid = pid_dir
                    page_usage = self.get_page_usage_by_pid(pid)
                    if page_usage is not None:
                        all_page_usage[pid] = page_usage
        except FileNotFoundError:
            pass  # process has already terminated
        return all_page_usage

    def get_page_usage_by_pid(self, pid):
        page_usage = {'total': 0, 'code': 0, 'heap': 0, 'stack': 0}
        try:
            with open(f'/proc/{pid}/smaps', 'r') as f:
                for line in f:
                    if 'Size:' in line:
                        page_usage['total'] += int(line.split()[1])
                    elif '[heap]' in line:
                        page_usage['heap'] += int(next(f).split()[1])
                    elif '[stack]' in line:
                        page_usage['stack'] += int(next(f).split()[1])
                    elif '.text' in line:
                        page_usage['code'] += int(next(f).split()[1])
        except FileNotFoundError:
            pass  # process has already terminated
        except PermissionError:
            pass
        except Exception as e:
            print(f"Error occurred while retrieving page usage for PID {pid}: {e}")
        return page_usage

    def get_process_details(self, pid):
        process_details = {}
        try:
            # Read various files inside the /proc/{pid} directory to get process details
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as f:
                # Read the command line of the process
                cmdline = f.read().decode().replace('\x00', ' ').strip()
                process_details['Command Line'] = cmdline if cmdline else None
                
            with open(os.path.join('/proc', pid, 'status'), 'r') as f:
                # Read status information of the process
                for line in f:
                    key, value = line.split(':', 1)
                    process_details[key.strip()] = value.strip()
        except FileNotFoundError:
            pass  # Process might have terminated
        return process_details

    def get_all_process_details(self):
        all_process_details = {}
        try:
            # Iterate over all directories in /proc
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit():  # Check if it's a process ID (numeric directory)
                    pid = pid_dir
                    process_details = self.get_process_details(pid)
                    if process_details:
                        all_process_details[pid] = process_details
        except Exception as e:
            pass
        return all_process_details

