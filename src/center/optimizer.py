import queue
from concurrent.futures import ThreadPoolExecutor
from log78 import Logger78
from basic.task_thread_pool import TaskThreadPool

class Optimizer:
    def __init__(self, strategies, logger):
        self.strategies = strategies      
        self.logger = logger
        self.task_queue = queue.Queue()
        self.thread_pool = TaskThreadPool(self._run_task, self.task_queue, max_workers=10, logger=self.logger)

    def optimize(self, params):
        best_params = {}
        best_scores = {}

        for strategy_name, strategy in self.strategies.items():
            best_score = float('-inf')
            best_param_set = None

            for param_set in params[strategy_name]:
                score = self._evaluate_strategy(strategy, param_set)
                if score > best_score:
                    best_score = score
                    best_param_set = param_set

            best_params[strategy_name] = best_param_set
            best_scores[strategy_name] = best_score

        return best_params, best_scores

    def _evaluate_strategy(self, strategy, param_set):
        strategy_instance = strategy(self.api, self.logger, **param_set)
        signals = strategy_instance.execute()
        # 这里可以添加回测逻辑来计算策略的表现
        score = self._backtest(signals)
        return score

    def _backtest(self, signals):
        # 简单的回测逻辑示例
        return signals['positions'].sum()

    def add_tasks(self, tasks):
        """动态添加多个任务到队列中"""
        self.thread_pool.add_tasks(tasks)

    def is_task_done(self):
        """检查任务是否完成"""
        return self.thread_pool.get_queue_size() == 0

    def _run_task(self, task):
        try:
            self.optimize(task)
        except Exception as e:
            self.logger.ERROR(f"Error running task: {e}")

if __name__ == "__main__":
    # 示例用法
    strategies = {
        # 定义策略
    }
    api = None  # 定义API
    logger = Logger78.instance()

    optimizer = Optimizer(strategies, api, logger)

    # 动态添加多个任务
    new_tasks = [
        {"strategy_name": "strategy1", "param_set": {"param1": 1, "param2": 2}},
        {"strategy_name": "strategy2", "param_set": {"param1": 3, "param2": 4}},
    ]
    optimizer.add_tasks(new_tasks)

    # 检查任务是否完成
    print(f"任务是否完成: {optimizer.is_task_done()}")