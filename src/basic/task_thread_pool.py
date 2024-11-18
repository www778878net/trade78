# -*- coding:utf-8 -*- 
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from log78 import Logger78


class TaskThreadPool: 
    """线程池类 
    queue是外界传来的 外界通过自己保存然后queue.empty()判断线程是否执行完
    """  
    def __init__(self, dofun, task_queue, max_workers=10, logger=None):
        self.dofun = dofun
        self.task_queue = task_queue
        self.max_workers = max_workers
        self.isover = False
        self.isQuit = False
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()
        self.__t_now = 0
        self.logger: Logger78 = logger      

        threading.Thread(target=self.__init_thread_pool).start()

    def __init_thread_pool(self):
        while True:
            if self.isQuit:
                self.executor.shutdown(wait=True)
                return
            time.sleep(10)
            if self.task_queue.empty():
                for _ in range(6):
                    time.sleep(10)
                    if not self.task_queue.empty():
                        break
                if self.task_queue.empty():
                    self.isover = True
                    break

            with self.lock:
                if self.__t_now >= self.max_workers:
                    continue

            while not self.task_queue.empty():
                with self.lock:
                    if self.__t_now >= self.max_workers:
                        break
                    self.__t_now += 1

                self.executor.submit(self.__work)

    def __work(self):
        while not self.task_queue.empty():
            if self.isQuit:
                return
            try:
                args = self.task_queue.get(timeout=10)
                self.dofun(args)
                self.task_queue.task_done()
            except queue.Empty:
                break
            except Exception as err:
                self.logger.ERROR(err)
        with self.lock:
            self.__t_now -= 1

    def get_queue_size(self):
        """获取当前队列中的任务数量"""
        return self.task_queue.qsize()

    def add_tasks(self, tasks):
        """动态添加多个任务到队列中"""
        for task in tasks:
            self.task_queue.put(task)
        with self.lock:
            if self.isover:
                self.isover = False
                threading.Thread(target=self.__init_thread_pool).start()

if __name__ == "__main__":
    def __test(args):
        time.sleep(args[1])

    task_queue = queue.Queue()
    for i in range(20):
        task_queue.put((i, i + 1))

    p = TaskThreadPool(__test, task_queue)

    # 查询当前队列数量
    print(f"当前队列数量: {p.get_queue_size()}")

    # 动态添加多个任务
    new_tasks = [(20, 21), (21, 22), (22, 23)]
    p.add_tasks(new_tasks)
    print(f"添加任务后队列数量: {p.get_queue_size()}")