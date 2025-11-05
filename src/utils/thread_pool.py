"""线程池管理模块"""
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any, Dict
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger


class ThreadPool:
    """线程池管理器"""

    def __init__(self, max_workers: int = 5):
        """
        初始化线程池

        Args:
            max_workers: 最大工作线程数
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logger

    def submit_task(self, func: Callable, *args, **kwargs):
        """
        提交单个任务

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            Future对象
        """
        return self.executor.submit(func, *args, **kwargs)

    def submit_tasks(self, func: Callable, tasks: List[Any]) -> List[Any]:
        """
        批量提交任务并等待所有任务完成

        Args:
            func: 要执行的函数
            tasks: 任务参数列表

        Returns:
            所有任务的结果列表
        """
        self.logger.info(f"提交 {len(tasks)} 个任务到线程池")

        futures = []
        for task in tasks:
            if isinstance(task, (list, tuple)):
                future = self.executor.submit(func, *task)
            elif isinstance(task, dict):
                future = self.executor.submit(func, **task)
            else:
                future = self.executor.submit(func, task)
            futures.append(future)

        # 等待所有任务完成并收集结果
        results = []
        completed = 0

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                completed += 1

                if completed % 10 == 0 or completed == len(futures):
                    self.logger.info(f"任务进度: {completed}/{len(futures)}")

            except Exception as e:
                self.logger.error(f"任务执行失败: {e}")
                results.append(None)

        self.logger.info(f"所有任务完成，成功: {len([r for r in results if r is not None])}/{len(tasks)}")
        return results

    def map(self, func: Callable, items: List[Any], timeout: int = None) -> List[Any]:
        """
        对列表中的每个元素执行函数（类似map）

        Args:
            func: 要执行的函数
            items: 元素列表
            timeout: 超时时间（秒）

        Returns:
            结果列表
        """
        return list(self.executor.map(func, items, timeout=timeout))

    def shutdown(self, wait: bool = True):
        """
        关闭线程池

        Args:
            wait: 是否等待所有任务完成
        """
        self.executor.shutdown(wait=wait)
        self.logger.info("线程池已关闭")


class TaskQueue:
    """任务队列管理器"""

    def __init__(self, max_size: int = 0):
        """
        初始化任务队列

        Args:
            max_size: 队列最大大小，0表示无限制
        """
        self.queue = queue.Queue(maxsize=max_size)
        self.logger = logger
        self.workers = []
        self.running = False

    def add_task(self, func: Callable, *args, **kwargs):
        """
        添加任务到队列

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        task = (func, args, kwargs)
        self.queue.put(task)

    def worker(self):
        """工作线程"""
        while self.running:
            try:
                task = self.queue.get(timeout=1)
                if task is None:
                    break

                func, args, kwargs = task
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"任务执行失败: {e}")
                finally:
                    self.queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"工作线程异常: {e}")

    def start(self, num_workers: int = 5):
        """
        启动工作线程

        Args:
            num_workers: 工作线程数量
        """
        self.running = True

        for i in range(num_workers):
            worker_thread = threading.Thread(target=self.worker, name=f"Worker-{i}")
            worker_thread.daemon = True
            worker_thread.start()
            self.workers.append(worker_thread)

        self.logger.info(f"启动了 {num_workers} 个工作线程")

    def wait_completion(self):
        """等待所有任务完成"""
        self.queue.join()
        self.logger.info("所有任务已完成")

    def stop(self):
        """停止所有工作线程"""
        self.running = False

        # 添加None作为停止信号
        for _ in self.workers:
            self.queue.put(None)

        # 等待所有线程结束
        for worker in self.workers:
            worker.join()

        self.workers.clear()
        self.logger.info("所有工作线程已停止")


class RateLimiter:
    """速率限制器（令牌桶算法）"""

    def __init__(self, rate: int, per: float = 1.0):
        """
        初始化速率限制器

        Args:
            rate: 速率（每per秒允许的请求数）
            per: 时间窗口（秒）
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = threading.current_thread().ident
        self.lock = threading.Lock()

    def acquire(self):
        """获取令牌（阻塞直到可以执行）"""
        import time

        with self.lock:
            current = time.time()
            time_passed = current - getattr(self, '_last_time', current)
            self._last_time = current

            self.allowance += time_passed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate

            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                time.sleep(sleep_time)
                self.allowance = 0.0
            else:
                self.allowance -= 1.0
