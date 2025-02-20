import json


class Settings:
    def __init__(self, file_path):
        """
        初始化设置类
        :param file_path: 存储设置的文件路径
        """
        self.file_path = file_path
        self.settings = {}
        self.load()
        self.pronounce = self.get('pronounce')

    def load(self):
        """
        从文件中加载设置
        """
        try:
            with open(self.file_path, 'r') as file:
                self.settings = json.load(file)
        except FileNotFoundError:
            self.settings = {}

    def save(self):
        """
        将设置保存到文件中
        """
        with open(self.file_path, 'w') as file:
            json.dump(self.settings, file, indent=4)

    def set(self, key, value):
        """
        设置一个新的设置项或更新现有设置项的值
        :param key: 设置项的键
        :param value: 设置项的值，可以是数值、布尔值、字符串等
        """
        self.settings[key] = value

    def get(self, key, default=None):
        """
        获取设置项的值
        :param key: 设置项的键
        :param default: 如果设置项不存在，返回的默认值
        :return: 设置项的值或默认值
        """
        return self.settings.get(key, default)

    def get_all_settings(self):
        """
        获取所有设置项
        :return: 包含所有设置项的字典
        """
        return self.settings

    def remove(self, key):
        """
        删除一个设置项
        :param key: 设置项的键
        """
        if key in self.settings:
            del self.settings[key]

    def has_key(self, key):
        """
        检查设置项是否存在
        :param key: 设置项的键
        :return: 如果设置项存在返回 True，否则返回 False
        """
        return key in self.settings

    def clear_non_matching_settings(self, required_keys):
        """
        清除不包含指定设置项的保存内容
        :param required_keys: 必须包含的设置项列表
        """
        keys_to_remove = [key for key in self.settings if key not in required_keys]
        for key in keys_to_remove:
            del self.settings[key]
        self.save()