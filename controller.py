'''
Arquivo contendo a apresentação dos resultados para o dashboard
É a Controller do padrão de projeto Model-View-Controller (MVC)
'''

import threading
import time

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Traz os dados informações da memória, processos e threads, quantidade de páginas e detalhes do processo de suas respectivas funções definidas no Model
        meminfo = self.model.get_memory_info()
        processes, threads = self.model.get_processes_and_threads()
        process_memory = self.model.get_all_process_memory()
        page_usage = self.model.get_all_page_usage()
        process_details = self.model.get_all_process_details()

        # Cria as abas Memória, Dados globais e Processos, definidas na view, passando os dados trazidos do model
        self.view.memory_tab(meminfo)
        self.view.process_tab(processes, threads, process_memory, page_usage, process_details)
        self.view.global_data_tab()

    # Apuração dos dados
    # Irá pegar os dados passados pelo model e exibi-los nas views e irá atualizar esses dados a cada 1 segundo para reexibi-los
    def acquire_data(self):
        while True:
            cpu_percentage = self.model.get_cpu_usage()
            idle_percentage = 100.0 - cpu_percentage
            total_process, total_threads = self.model.get_total_processes_and_threads()
            meminfo = self.model.get_memory_info()
            memory_usage_percent = self.model.calculate_memory_usage(meminfo)
            processes, threads = self.model.get_processes_and_threads()

            self.view.update_global_data(cpu_percentage, idle_percentage, total_process, total_threads)
            self.view.update_memory_tab(meminfo, memory_usage_percent)
            self.view.update_process(processes, threads)

            time.sleep(1)  # Atualiza os dados a cada segundo
        
    # Inicia a thread para adquirir dados
    def start(self):
        data_thread = threading.Thread(target=self.acquire_data)
        data_thread.daemon = True
        data_thread.start()

        self.view.mainloop()