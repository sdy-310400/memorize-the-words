import datetime

import path
import json


# RecordType类定义了一些数据类型的常量，方便在代码中统一使用
class RecordType:
    Logbook = "Logbook"
    LearnedAlready = "LearnedAlready"
    FullyMastered = "FullyMastered"
    TodayData = "TodayData"


# RecordJson类用于处理与JSON文件的读写操作
class RecordJson:
    def __init__(self):
        """
        初始化方法，指定要操作的JSON文件路径，默认为record.json
        这里通过导入的path模块中的text_json来确定文件路径
        """
        self.file_path = path.record_json

    def _read_file_data(self):
        """
        内部私有方法，从JSON文件中读取数据
        :return: 返回读取到的整个文件数据（外层是字典形式），如果文件不存在或者解析出错返回None
        首先尝试打开文件并使用json.load进行数据加载，如果文件不存在会抛出FileNotFoundError异常，
        如果数据格式有误会抛出json.JSONDecodeError异常，在这些异常情况下都会返回None
        """
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            raise EOFError(f"文件 {self.file_path} 不存在")
        except json.JSONDecodeError:
            raise EOFError(f"文件 {self.file_path} 中数据格式有误，无法正确解析")

    def read_data_by_type(self, data_type):
        """
        根据指定类型读取对应的数据（字典形式）
        :param data_type: 要读取数据的类型标识字符串，合法取值为 "Logbook", "LearnedAlready", "FullyMastered", "TodayData"
        先调用_read_file_data读取整个文件数据，如果文件数据存在，则从其中获取指定类型的数据并返回，
        如果不存在该类型数据则返回None
        :return: 返回指定类型对应的字典数据，如果不存在该类型数据则返回None
        """
        file_data = self._read_file_data()
        if file_data:
            return file_data.get(data_type)
        return None

    def write_data(self, data_type, data_dict: dict):
        """
        将指定类型的数据（字典形式）写入到JSON文件中
        :param data_type: 要写入数据的类型标识字符串，如 "type1"
        :param data_dict: 要写入的对应类型的数据，为字典形式
        首先读取文件现有数据，如果文件数据不存在则初始化为空字典。然后将指定类型的数据更新到文件数据中，
        最后尝试将更新后的文件数据写入文件，如果文件不存在会抛出FileNotFoundError异常，
        如果数据无法进行JSON序列化会抛出TypeError异常
        """
        file_data = self._read_file_data()
        if file_data is None:
            file_data = {}
        file_data[data_type] = data_dict
        try:
            with open(self.file_path, 'w') as file:
                json.dump(file_data, file, indent=4)
        except FileNotFoundError:
            raise EOFError(f"文件 {self.file_path} 不存在，无法写入数据")
        except TypeError:
            raise EOFError(f"传入的数据 {data_dict} 无法进行JSON序列化，不能写入文件")


# Record类作为主要的记录类，封装了对RecordJson类的操作
class Record:
    def __init__(self):
        # 初始化时创建RecordJson类的实例，用于后续的读写操作
        self.record_manager = RecordJson()
        self.logbook = self.record_manager.read_data_by_type(RecordType.Logbook)
        self.learned_already = self.record_manager.read_data_by_type(RecordType.LearnedAlready)
        self.fully_mastered = self.record_manager.read_data_by_type(RecordType.FullyMastered)
        self.today_data = self.record_manager.read_data_by_type(RecordType.TodayData)

    def get(self, _type: RecordType, _date: datetime.date = None, dic: bool = None):
        if _date is None:
            _return = []
            # 读取指定类型的所有数据
            data_dic = self.record_manager.read_data_by_type(_type)
            # 遍历数据字典中的每个键值对，将值扩展到返回列表中
            if dic is not None:
                return data_dic

            for i in data_dic.values():
                _return.extend(i)
            return _return
        try:
            # 尝试读取指定类型和日期的数据，如果不存在则返回空列表
            return self.record_manager.read_data_by_type(_type)[str(_date)]
        except KeyError:
            return []

    def write(self, _type, _date: datetime.date, data_list: [int]):
        # 读取指定类型的现有数据
        wired = self.record_manager.read_data_by_type(_type)
        # 创建包含指定日期和数据列表的字典项
        item = {str(_date): data_list}
        # 将新的字典项更新到现有数据中
        wired.update(item)
        # 将更新后的数据写入文件
        self.record_manager.write_data(_type, wired)

    def add(self, _type: RecordType, _date: datetime.date, word_index: int):
        assert isinstance(word_index, int)
        wired = self.record_manager.read_data_by_type(_type)
        _date_str = str(_date)
        if _date_str in wired.keys():
            wired[_date_str].append(word_index)
        else:
            wired.update({_date_str: [word_index]})
        self.record_manager.write_data(_type, wired)

    def clear_cache(self):
        """清除TodayData类型中非今日的数据"""
        today = datetime.date.today()
        today_str = str(today)
        # 读取TodayData数据，若不存在则初始化为空字典
        today_data = self.record_manager.read_data_by_type(RecordType.TodayData) or {}
        # 仅保留今日的数据
        filtered_data = {k: v for k, v in today_data.items() if k == today_str}
        # 将过滤后的数据写回文件
        self.record_manager.write_data(RecordType.TodayData, filtered_data)



if __name__ == '__main__':
    test = Record()
    test.clear_cache()

