import datetime
import random
import record

"""
这个程序主要实现了根据不同模式和数据来源进行单词学习的功能。
在 Main 类的构造函数中，根据传入的参数确定学习模式、数据数量和数据来源类型，
然后获取相应的数据并运行学习模式。在学习模式中，根据不同的模式显示单词或释义，
并通过键盘事件来控制学习进度和执行其他操作。
其中，take_data_sources 方法负责根据数据来源类型获取数据，
random_select_and_permute 方法用于对数据进行随机选择和排列，
mode_run 方法则是整个学习过程的核心逻辑，包括数据展示和键盘事件处理。
"""


class DailyTasks:
    study = "study"
    review = "review"

    class DailyTasksData:
        def __init__(self, daily_name, length):
            self.daily_name = daily_name
            self.length = length


class StudyMode:
    New_Learning = "新学习"
    Review = "复习"
    Review_Fully_Grasp = "回顾完全掌握"


study_mode_list = [StudyMode.New_Learning, StudyMode.Review, StudyMode.Review_Fully_Grasp]


# 定义了三种模式，分别是中文到英文（C_to_E）、英文到中文（E_to_C）和混合模式（Mixed_Mode）
class WordMode:
    C_to_E = "c_to_e"
    E_to_C = "e_to_c"
    Mixed_Mode = "混合"


word_mode_list = [WordMode.C_to_E, WordMode.E_to_C, WordMode.Mixed_Mode]


# 定义了多种数据来源类型，包括昨天（Yesterday）、前天（TheDayBeforeYesterday）等不同时间范围，以及已学习（Learned）、
# 未学习（NotLearnedYet）、完全掌握（FullyMastered）等状态
class DataSourcesType:
    Today = "今天"
    Yesterday = "昨天"
    TheDayBeforeYesterday = "前天"
    ThirdDays = "三天前"
    SevenDays = "7天"
    Learned = "已学习"
    NotLearnedYet = "未学习"
    FullyMastered = "完全掌握"


data_sources_type_list = [DataSourcesType.Today, DataSourcesType.Yesterday, DataSourcesType.TheDayBeforeYesterday,
                          DataSourcesType.ThirdDays, DataSourcesType.SevenDays, DataSourcesType.Learned]


class Main:
    def __init__(self, word_mode: WordMode, number: int, data_sources_type: DataSourcesType, study_mode: StudyMode,
                 special_mode = DailyTasks.DailyTasksData(None, None)):
        """
        初始化函数，用于设置学习的模式、要获取的数据数量和数据来源类型，
        同时初始化数据来源列表、记录类实例、获取当前日期和单词数据类实例，
        最后调用获取数据来源和运行学习模式的方法。

        :param word_mode: 学习模式，取值为 Mode 类中定义的三种模式之一
        :param number: 要获取的数据数量
        :param data_sources_type: 数据来源类型，取值为 DataSourcesType 类中定义的类型之一
        """
        # 初始化模式、要获取的数据数量和数据来源类型
        self.special_mode = special_mode
        self.study_mode = study_mode
        self.index = 0
        self.word_mode = word_mode
        self.number = number
        self.data_sources_type = data_sources_type
        self.data_sources = []
        # 初始化 Record 类的实例，用于数据记录操作（可能是读取或写入学习进度等相关数据）
        self.record = record.Record()

        # 获取当前日期
        self.today = datetime.date.today()

        """if self.special_mode is not None and self.number == 5:
            self.data_sources_type = DataSourcesType.NotLearnedYet"""

        # 调用方法获取数据来源
        self.take_data_sources()

        if self.special_mode.daily_name is None:
            self.data = self.random_select_and_permute(self.data_sources, num_to_select=self.number)
        else:
            self.data = self.data_sources
            self.number = self.special_mode.length

        match word_mode:
            case WordMode.C_to_E:
                self.random_table_0_and_1 = [1] * self.number
            case WordMode.E_to_C:
                self.random_table_0_and_1 = [0] * self.number
            case WordMode.Mixed_Mode:
                self.random_table_0_and_1 = [random.randint(0, 1) for _ in range(self.number)]
        if len(self.data) == 0:
            print(word_mode, number, data_sources_type, study_mode)
            raise EOFError("没有数据！")

    def take_data_sources(self):
        """
        根据不同的数据来源类型，从记录或其他数据源中获取相应的数据，
        存储在 data_sources 列表中。对于未学习的数据来源类型，会避免选取重复的数字。

        :return: 无返回值，数据存储在 self.data_sources 中
        """
        # 根据数据来源类型进行不同的操作

        if self.special_mode.daily_name == DailyTasks.study:
            if self.special_mode.length == 15:
                self.data_sources = self.record.get(record.RecordType.TodayData, self.today)
                return
            else:
                self.data_sources_type = DataSourcesType.NotLearnedYet
        elif self.special_mode.daily_name == StudyMode.Review:
            temp_list = []
            day_number = 1
            while len(temp_list) < self.number:
                temp_list.extend(self.record.get(record.RecordType.LearnedAlready,
                                                 self.today - datetime.timedelta(days=day_number)))
                day_number += 1
            self.data_sources = temp_list[:self.number]
            return

        """ if self.number != 5 and self.special_mode is not None:
            if self.special_mode == DailyTasks.study:
                self.data_sources = self.record.get(record.RecordType.TodayData, self.today)
                return
            elif self.special_mode == DailyTasks.review:
                temp_list = []
                day_number = 1
                while len(temp_list) < self.number:
                    temp_list.extend(self.record.get(record.RecordType.LearnedAlready,
                                                     self.today - datetime.timedelta(days=day_number)))
                    day_number += 1
                self.data_sources = temp_list[:self.number]
                return
        """

        match self.data_sources_type:
            case DataSourcesType.Today:
                self.data_sources = self.reduce_days(0)
            # 如果是昨天的数据来源类型，调用 reduce_days 方法获取昨天的数据
            case DataSourcesType.Yesterday:
                self.data_sources = self.reduce_days(1)
            # 如果是前天的数据来源类型，调用 reduce_days 方法获取前天的数据
            case DataSourcesType.TheDayBeforeYesterday:
                self.data_sources = self.reduce_days(2)
            # 如果是前三天的数据来源类型，调用 reduce_days 方法获取前三天的数据
            case DataSourcesType.ThirdDays:
                self.data_sources = self.reduce_days(3)
            # 如果是七天的数据来源类型，调用 reduce_days 方法获取七天的数据
            case DataSourcesType.SevenDays:
                self.data_sources = self.reduce_days(7)
            # 如果是已学习的数据来源类型，从记录中获取已学习的数据
            case DataSourcesType.Learned:
                self.data_sources = self.record.get(record.RecordType.LearnedAlready)
            # 如果是未学习的数据来源类型
            case DataSourcesType.NotLearnedYet:
                all_existing_numbers = set()
                # 合并 fully_mastered 和 learned_already 字典中的所有数字到一个集合，用于避免选取重复的数字
                for d in [self.record.fully_mastered, self.record.learned_already]:
                    for value_list in d.values():
                        all_existing_numbers.update(value_list)
                # 循环选取指定数量的未学习数据
                while len(self.data_sources) < self.number:
                    random_number = random.randint(0, 7508)
                    if random_number not in all_existing_numbers:
                        self.data_sources.append(random_number)
                        all_existing_numbers.add(random_number)  # 将已选数字添加到集合中，避免重复选择
            # 如果是完全掌握的数据来源类型，将 fully_mastered 中的所有数据添加到数据来源列表
            case DataSourcesType.FullyMastered:
                for item_list in self.record.fully_mastered.values():
                    self.data_sources.extend(item_list)

    def reduce_days(self, days: int):
        """
        根据指定的天数范围，从记录中获取相应天数内的已学习数据。

        :param days: 要获取数据的天数范围
        :return: 返回获取到的已学习数据列表
        """
        _return = []

        if self.study_mode == StudyMode.Review:
            record_type = record.RecordType.LearnedAlready
        elif self.study_mode == StudyMode.Review_Fully_Grasp:
            record_type = record.RecordType.FullyMastered
        else:
            record_type = None

        if days != 0:
            # 循环获取指定天数范围内的已学习数据
            for day in range(1, days + 1):
                _return.extend(self.record.get(record_type,
                                               self.today - datetime.timedelta(days=day)))
        else:
            _return.extend(self.record.get(record_type, self.today))
        return _return

    @staticmethod
    def random_select_and_permute(input_list: list[int], num_to_select: int = None):
        """
        从给定的数字列表中选择任意个数（可指定数量，默认全选）的元素，随机排列后组成新列表。

        :param input_list: 输入的数字列表
        :param num_to_select: 要选择的元素个数，默认为 None，表示选择全部元素
        :return: 随机排列后的新列表
        """
        # 如果未指定要选择的数量或指定数量大于输入列表长度，则选择全部元素
        if num_to_select is None or num_to_select > len(input_list):
            num_to_select = len(input_list)

        # 从输入列表中随机选取指定数量的元素
        selected_list = random.sample(input_list, num_to_select)
        # 对选取的元素进行随机排列
        random.shuffle(selected_list)
        return selected_list


if __name__ == '__main__':
    pass
