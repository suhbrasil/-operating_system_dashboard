import threading
import time

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        meminfo = self.model.get_memory_info()
        processes, threads = self.model.get_processes_and_threads()

        self.view.set_click_callback(self.handle_click)
        self.view.memory_tab(meminfo)
        self.view.process_tab(processes, threads)
        self.view.global_data_tab()

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
    
    def handle_click(self, item_id):
        threads = self.model.get_threads(item_id)
        process_memory = self.model.get_process_memory(item_id)
        page_usage = self.model.get_page_usage(item_id)

        self.view.open_popup(item_id, threads, process_memory, page_usage)

    def start(self):
        # Inicia a thread para adquirir dados
        data_thread = threading.Thread(target=self.acquire_data)
        data_thread.daemon = True
        data_thread.start()

        self.view.mainloop()