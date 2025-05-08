import threading
import queue
import time

class RequestHandler:
    def __init__(self, worker_id):
        self.worker_id = worker_id

    def handle_request(self, request):
        print(f"Worker {self.worker_id} processing request: {request}")
        time.sleep(1)  # Simulate processing time

class LoadBalancer:
    def __init__(self, num_workers=4):
        self.request_queue = queue.Queue()
        self.workers = [RequestHandler(i) for i in range(num_workers)]
        self.worker_threads = []
        self.running = False

    def start(self):
        self.running = True
        for worker in self.workers:
            t = threading.Thread(target=self.worker_loop, args=(worker,))
            t.start()
            self.worker_threads.append(t)

    def stop(self):
        self.running = False
        for t in self.worker_threads:
            t.join()

    def worker_loop(self, worker):
        while self.running:
            try:
                request = self.request_queue.get(timeout=1)
                worker.handle_request(request)
                self.request_queue.task_done()
            except queue.Empty:
                continue

    def distribute_request(self, request):
        self.request_queue.put(request)

# Example usage:
# lb = LoadBalancer(num_workers=4)
# lb.start()
# for i in range(10):
#     lb.distribute_request(f"Request-{i}")
# lb.stop()
