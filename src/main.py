# main.py 启动和初始化环境
import os
import asyncio
import argparse
from upinfopy import Api78
from log78 import ConsoleLog78, FileLog78, Logger78, KafkaServerLog78
from basic.center import Center

# 解析命令行参数
parser = argparse.ArgumentParser(description='Run the trading bot.')
parser.add_argument('--use_kafka_log', type=str, default='false', help='Use Kafka for logging')
args = parser.parse_args()

# 设置环境变量
use_kafka_log = args.use_kafka_log.lower() == 'true'
env = os.getenv('APP_ENV', 'development').lower()
bootstrap_servers = os.getenv('bootstrap_servers', '192.168.31.181:30008').lower()
topic = os.getenv('topic', 'log-topic').lower()

# 打印环境变量以进行调试
print(f"USE_KAFKA_LOG: {use_kafka_log}")
print(f"APP_ENV: {env}")
print(f"bootstrap_servers: {bootstrap_servers}")
print(f"topic: {topic}")

logger = Logger78.instance()
if use_kafka_log:
    logger.setup(
        KafkaServerLog78(bootstrap_servers, topic),
        FileLog78(),
        ConsoleLog78()
    )
else:
    logger.setup(
        None,
        FileLog78(),
        ConsoleLog78()
    )




async def main():
    init()
   
    with open('/tmp/healthy', 'w') as f:
        f.write('healthy')    
    center = Center(logger)
    while True:
        await center.run()        
        with open('/tmp/healthy', 'w') as f:
            f.write('healthy')
   
        await asyncio.sleep(1)  # 等待一秒钟

def init():  
    
    return 

if __name__ == "__main__":
    asyncio.run(main())