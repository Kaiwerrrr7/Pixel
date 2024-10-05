import asyncio
import threading
import queue
import time
import psutil
import logging
import os
from datetime import datetime

from core.errors import InvalidAccountExcept

class WorkerManager:
    def __init__(self, max_threads=5, max_memory_usage=None, max_cpu_usage=None, retry_limit=3):
        self.max_threads = max_threads
        self.max_memory_usage = max_memory_usage
        self.max_cpu_usage = max_cpu_usage
        self.retry_limit = retry_limit
        self.tasks = queue.Queue()
        self.threads = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.crashdump_folder = 'crashdumps'
        os.makedirs(self.crashdump_folder, exist_ok=True)

    async def worker(self):
        while not self.stop_event.is_set():
            try:
                item = self.tasks.get(timeout=1)
                if item is None:
                    break
                task, args, kwargs = item

                cancelled = False
                while not cancelled:
                    try:
                        while not self.check_resources() and not self.stop_event.is_set():
                            time.sleep(1)
                        if not self.stop_event.is_set():
                            await task(*args, **kwargs)
                        break
                    except Exception as e:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        log_filename = os.path.join(self.crashdump_folder, f'crashdump_{timestamp}.txt')
                        with open(log_filename, 'w') as log_file:
                            log_file.write(f"Error: {str(e)}\n")
                            log_file.write(f"Type: {type(e).__name__}\n")
                            import traceback
                            traceback.print_exc(file=log_file)
                        print(f"An error occurred. Details have been logged to {log_filename}")

                self.tasks.task_done()

            except queue.Empty:
                continue

    def add_task(self, task, *args, **kwargs):
        self.tasks.put((task, args, kwargs))


    def run_worker(self):
        asyncio.run(self.worker())

    def start_threads(self):
        for _ in range(self.max_threads):
            thread = threading.Thread(target=self.run_worker)
            thread.start()
            self.threads.append(thread)

    def stop_threads(self):
        self.stop_event.set()
        for _ in range(self.max_threads):
            self.tasks.put(None)
        for thread in self.threads:
            thread.join()

    def wait_for_completion(self):
        self.tasks.join()
        self.stop_threads()

    def check_resources(self):
        if self.max_memory_usage and psutil.virtual_memory().percent > self.max_memory_usage:
            return False
        if self.max_cpu_usage and psutil.cpu_percent() > self.max_cpu_usage:
            return False
        return True
