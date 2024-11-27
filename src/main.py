import os
import sys
import asyncio
import argparse
from upinfopy import UpInfo, Api78
from log78 import ConsoleLog78, FileLog78, Logger78, KafkaServerLog78
from basic.center import Center
from basic.config78 import Config78

# 添加项目根目录到 PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 解析命令行参数
parser = argparse.ArgumentParser(description='Run the trading bot.')
parser.add_argument('--config', type=str, default='development.ini', help='Path to the configuration file')
args = parser.parse_args()

# 自动加上 config 目录
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
config_file = os.path.join(config_path, args.config)

# 检查配置文件是否存在，如果不存在则使用 config.ini
if not os.path.exists(config_file):
    config_file = os.path.join(config_path, 'config.ini')

# 读取配置文件
config = Config78(config_file)

# 从配置文件、环境变量和命令行参数读取配置
use_kafka_log = (os.getenv('USE_KAFKA_LOG') or config.get('DEFAULT', 'use_kafka_log', 'false')).lower() == 'true'
env = os.getenv('APP_ENV', config.get('DEFAULT', 'app_env', 'production')).lower()
bootstrap_servers = os.getenv('BOOTSTRAP_SERVERS', config.get('DEFAULT', 'bootstrap_servers', '192.168.31.181:30008')).lower()
topic = os.getenv('TOPIC', config.get('DEFAULT', 'topic', 'log-topic')).lower()

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
    center = Center(logger,config)
    #while True:
    await center.run()        
        # with open('/tmp/healthy', 'w') as f:
        #     f.write('healthy')
   
        # await asyncio.sleep(10)  # 等待一秒钟

def init():  
    up = UpInfo()
    up.sid = os.getenv('sid', config.get('DEFAULT', 'sid', '')).lower()
    up.uname =  os.getenv('uname', config.get('DEFAULT', 'uname', 'guest')).lower() 
    up.api =  os.getenv('api', config.get('DEFAULT', 'api', '')).lower()     
    UpInfo.setMaster(up)
    return 

if __name__ == "__main__":
    asyncio.run(main())