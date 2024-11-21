from configobj import ConfigObj
from threading import Lock

class Config78:
    def __init__(self, filename):
        self.filename = filename
        self.lock = Lock()
        self.config = None
        self.reload()
         

    def get(self, section, key, default=None):        
        with self.lock:
            return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        with self.lock:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value
            self.config.write()
            self.config.reload()

    def delete(self, section, key):
        with self.lock:
            if section in self.config and key in self.config[section]:
                del self.config[section][key]
                self.config.write()
                self.config.reload()
    
    def reload(self):        
        self.config = ConfigObj(self.filename)

# 示例配置文件 config.ini
"""
[DEFAULT]
api_url = http://api.example.com
steam_user = default_user
"""

# # 示例用法
# config = ThreadSafeConfig('config.ini')

# # 读取配置
# api_url = config.get('DEFAULT', 'api_url')
# steam_user = config.get('DEFAULT', 'steam_user')



# # 写入配置
# config.set('DEFAULT', 'new_key', 'new_value')