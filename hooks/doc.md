# 按D:\50.code\35.git78py\trade78\hooks\model.md 考虑问题 
# 按D:\50.code\35.git78py\trade78\hooks\doc.md 处理问题

# pooloptimization
- 每分钟检查一次队列长度 如果低于多少了就添加

# __optimization_rowdo
- 六个参数 这里一般只3个 后三个直接可以写死一个值也可 调__optimization
- 获取日线或周线 先只日线

# 把原来的Stock_trade.py做规范化改版 现在如何写？先只考虑参数优化
- 原来是线程执行pooloptimization 死循环 
- 每分钟执行一次检测 如果队列完了就获取并添加到队列
- 现在有了循环了 应该直接检测就行了 optimization.py 加个获取任务是否完成
- 如果已完成 就获取 并添加到队列
- optimization原来的逻辑是每个策略三种参数值都执行一次，然后取最优值 
- 按日线级别执行全部历史记录回测 取最优值
- 现在修改为D:\50.code\35.git78py\trade78\src\center\strategy.py 为策略基类 每个策略都继承这个类 方便新增策略


# 不要修改 main.py task_thread_pool.py
- 现在应该修改optimization.py 实现队列线程池处理
- 


# 已经弄好了的逻辑参考
- main.py循环调用 center.py的run