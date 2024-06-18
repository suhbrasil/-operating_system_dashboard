'''
Arquivo contendo o processo de aquisição dos dados para o dashboard
É o Model do padrão de projeto Model-View-Controller (MVC)
'''

import os
import os.path
import datetime

class Model:
    def __init__(self):
        # Inicializa as variáveis prev_idle, prev_total, total_processes e total_threads
        self.prev_idle, self.prev_total = self.get_idle_and_total_time()
        self.total_processes = 0
        self.total_threads = 0
        self.max_depth = 3

    # Função que pega as informções da memória no /proc/meminfo que serão utilizadas posteriormente na função de crição da tela de memória na View
    def get_memory_info(self):
        memory_info = {}
        with open('/proc/meminfo', 'r') as file:
            for line in file:
                key, value = line.split(':')
                key = key.strip()
                value = int(value.split()[0])
                memory_info[key] = value
        return memory_info
    
    # Função para calcular a porcentagem do uso de memória, utilizando informações obtidas na função get_memory_info
    def calculate_memory_usage(self, memory_info):
        total_memory = memory_info['MemTotal']
        free_memory = memory_info['MemFree']
        buffers_memory = memory_info['Buffers']
        cached_memory = memory_info['Cached']
        used_memory = total_memory - free_memory - buffers_memory - cached_memory
        memory_usage_percent = (used_memory / total_memory) * 100
        return memory_usage_percent
    
    # Pega as informações de cada processo e as informações de suas respectivas threads e armazena nos arrays processes e threads
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
    
    # Pega a porcentagem de uso da CPU
    def get_cpu_usage(self):
        # Pega o tempo de IDLE e tempo total anteriores para calcular o uso da CPU
        idle_time, total_time = self.get_idle_and_total_time()

        # Prevenir de dar erro caso haja uma divisão por zero
        if(total_time - self.prev_total) == 0:
            # armazena tempo de IDLE e tempo total para serem utilizados posteriormente
            self.prev_idle, self.prev_total = idle_time, total_time
            return 0.0
        
        # Cálculo da porcentagem de uso da CPU
        cpu_percentage = 100.0 - ((idle_time - self.prev_idle) / (total_time - self.prev_total) * 100.0)
        # armazena tempo de IDLE e tempo total para serem utilizados posteriormente
        self.prev_idle, self.prev_total = idle_time, total_time
        return cpu_percentage
    
    # Pega o tempo de IDLE e tempo total do ('/proc/stat')
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
    
    # Calcula o número total de processos e threads
    def get_total_processes_and_threads(self):
        total_processes = 0
        total_threads = 0
        # Itera sobre cada entrada no diretório /proc
        for entry in os.listdir('/proc'):
            # Checa se a entrada é um dígito
            if entry.isdigit():
                # Checa se é um processo
                if os.path.exists(f'/proc/{entry}/cmdline'):
                    total_processes += 1
                # Checa se é uma thread
                if os.path.isdir(f'/proc/{entry}/task'):
                    total_threads += len(os.listdir(f'/proc/{entry}/task'))
                    
        return total_processes, total_threads

    # Pega as informações da memória de cada processo
    def get_all_process_memory(self):
        all_process_memory = {}
        try:
            # Itera sobre todos os diretórios em /proc
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit():  
                    pid = pid_dir
                    process_memory = self.get_process_memory_by_pid(pid)
                    if process_memory is not None:
                        all_process_memory[pid] = process_memory
        except FileNotFoundError:
            pass  
        return all_process_memory

    # Pega as informações da memória de um processo específico a partir de seu PID
    def get_process_memory_by_pid(self, pid):
        process_memory = None 
        try:
            with open(os.path.join('/proc', pid, 'status')) as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        memory = line.split()[1] # Memória em kB
                        process_memory = int(memory)
                        break
        except FileNotFoundError:
            pass 
        return process_memory

    # Pega a quantidade de páginas de memória para todos os processos
    def get_all_page_usage(self):
        all_page_usage = {}
        try:
            # Itera sobre todos os diretórios em /proc
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit(): 
                    pid = pid_dir
                    page_usage = self.get_page_usage_by_pid(pid)
                    if page_usage is not None:
                        all_page_usage[pid] = page_usage
        except FileNotFoundError:
            pass 
        return all_page_usage

    # Pega a quantidade de páginas de memória (total, de código, heap e stack) para um processo específico a partir de seu PID
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
            pass  
        except PermissionError:
            pass
        except Exception as e:
            print(f"Erro com a quantidade de páginas para o processo {pid}: {e}")
        return page_usage

    # Pega as informações detalhas de um processo específico de acordo com seu PID
    def get_process_details(self, pid):
        process_details = {}
        try:
            # Lê vários arquivos dentro do diretório /proc/{pid} para obter os detalhes do processo
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as f:
                # Lê a linha de comando do processo
                cmdline = f.read().decode().replace('\x00', ' ').strip()
                process_details['Command Line'] = cmdline if cmdline else None
                
            with open(os.path.join('/proc', pid, 'status'), 'r') as f:
                # Lê a informação do status do processo
                for line in f:
                    key, value = line.split(':', 1)
                    process_details[key.strip()] = value.strip()
        except FileNotFoundError:
            pass  
        return process_details

    # Pega as informações detalhas de cada processo
    def get_all_process_details(self):
        all_process_details = {}
        try:
            # Itera sobre todos os diretórios em /proc
            for pid_dir in os.listdir('/proc'):
                if pid_dir.isdigit(): 
                    pid = pid_dir
                    process_details = self.get_process_details(pid)
                    if process_details:
                        all_process_details[pid] = process_details
        except Exception as e:
            pass
        return all_process_details

    # Converte bytes para gigabytes.
    def bytes_to_gb(self, bytes):
        return bytes / (1024 ** 3)

    # Pega as partições do disco
    def get_disk_partitions(self):
        partitions = []
        with open('/proc/partitions') as f:
            lines = f.readlines()[2:]  # Ignora as duas primeiras linhas
            for line in lines:
                words = line.split()
                if words:
                    partitions.append(words[3])
        return partitions

    # Pega o tamanho da memória de cada partição do disco
    def get_partition_usage(self, partition):
        partition_path = f"/sys/class/block/{partition}/size"
        with open(partition_path) as f:
            blocks = int(f.read().strip())
        total_size_bytes = blocks * 512  # Tamanho do bloco é 512 bytes
        
        mount_point = None
        with open('/proc/mounts') as f:
            for line in f:
                if line.startswith(f"/dev/{partition} "):
                    mount_point = line.split()[1]
                    break
        
        if mount_point:
            statvfs = os.statvfs(mount_point)
            free_size_bytes = statvfs.f_bfree * statvfs.f_frsize
            used_size_bytes = total_size_bytes - free_size_bytes
            percent_used = (used_size_bytes / total_size_bytes) * 100
            
            return {
                'partition': partition,
                'mount_point': mount_point,
                'total_size_gb': self.bytes_to_gb(total_size_bytes),
                'used_size_gb': self.bytes_to_gb(used_size_bytes),
                'free_size_gb': self.bytes_to_gb(free_size_bytes),
                'percent_used': percent_used,
            }
        else:
            return None

    # Retorna as informações de partição do disco
    def disk_partitions_info(self):
        partitions_info = []
        
        partitions = self.get_disk_partitions()
        for partition in partitions:
            usage_info = self.get_partition_usage(partition)
            if usage_info:
                partitions_info.append({
                    'Partições': usage_info['partition'], 
                    'Percentual usado': f"{usage_info['percent_used']:.2f}%",
                    'Total': f"{usage_info['total_size_gb']:.2f} GB",
                    'Usado': f"{usage_info['used_size_gb']:.2f} GB",
                    'Livre': f"{usage_info['free_size_gb']:.2f} GB", 
                })
                
        return partitions_info


    # Função que lê e percorre o diretório 
    def read_directory(self, path, depth):
        directory_tree = []
        if depth >= self.max_depth:
            return directory_tree
        
        try:
            entries = os.listdir(path)
            for entry in entries:
                full_path = os.path.join(path, entry)
                if self.is_directory(full_path):
                    directory_tree.append({
                        'name': entry,
                        'path': full_path,
                        'type': 'directory',
                        'children': self.read_directory(full_path, depth + 1) # Pega os "filhos" do diretório recursivamente
                    })
                else:
                    info = self.get_file_info(full_path)
                    directory_tree.append({
                        'name': entry,
                        'path': full_path,
                        'type': 'file',
                        'size': info['size'],
                        'permissions': info['permissions'],
                        'last_modified': info['last_modified']
                    })

        except PermissionError:
            pass
        except FileNotFoundError:
            pass
        return directory_tree

    def is_directory(self, path):
        try:
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            os.close(fd)
            return True
        except OSError:
            return False

    def get_file_info(self, path):
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0

        try:
            permissions = self.get_permissions(path)
        except OSError:
            permissions = "Unknown"

        try:
            last_modified = self.get_last_modified(path)
        except OSError:
            last_modified = "Unknown"

        return {
            'size': size,
            'permissions': permissions,
            'last_modified': last_modified
        }

    def get_permissions(self, path):
        mode = os.stat(path).st_mode
        perm_bits = {
            0o4000: 's',  # setuid
            0o2000: 's',  # setgid
            0o1000: 't',  # sticky
            0o0400: 'r',
            0o0200: 'w',
            0o0100: 'x',
        }
        perms = ''
        for p in [0o4000, 0o2000, 0o1000, 0o0400, 0o0200, 0o0100]:
            perms += perm_bits.get(mode & p, '-')
        return perms

    def get_last_modified(self, path):
        last_modified_timestamp = os.path.getmtime(path)
        last_modified_datetime = datetime.datetime.fromtimestamp(last_modified_timestamp)
        return last_modified_datetime.strftime('%Y-%m-%d %H:%M:%S')





