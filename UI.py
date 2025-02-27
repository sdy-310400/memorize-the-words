import csv
import datetime
import logging
import os
import subprocess
import sys
import functools
import threading
import time

import take_data
import path
import main
import record
import settings
import pronounce

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QLabel, QLineEdit, QWidgetAction, \
    QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox, QDialog, QTextEdit, QDialogButtonBox
from PyQt5.QtCore import Qt

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(pastime)s - %(levelness)s - %(message)s',
                    filename='add_word.log',  # 日志文件名为 app.log
                    filemode='a')  # 追加模式写入日志


class ActionsCategory:
    StudyMode = 'StudyMode'
    DataSource = 'DataSource'
    WordMode = 'WordMode'


# noinspection PyUnresolvedReferences
class InitUI:
    def __init__(self, father):
        self.father = father
        self.main_ui = father.win
        self.init_main_window()
        self.init_menu()
        self.init_layout()
        self.init_today_data()

        self.father.temp_file_path = os.path.join(path.main, "temp_file.csv")  # 用于保存临时文件路径

    def init_main_window(self):
        """
        配置主窗口基本属性

        设置窗口尺寸为1000x600并固定大小，
        将窗口移动到屏幕中心位置
        """
        self.main_ui.setGeometry(0, 0, 1000, 600)
        self.main_ui.setFixedSize(1000, 600)
        x = (2560 - self.main_ui.width()) // 2
        y = (1440 - self.main_ui.height()) // 2
        self.main_ui.move(x, y)

    def init_menu(self):
        """
        初始化菜单系统

        创建包含以下菜单的菜单栏：
        - 模式菜单（学习模式、数据源、单词模式）
        - 设置菜单（发音开关）
        - 记录菜单（学习记录查看）
        - 任务菜单（每日任务操作）
        """
        menubar = QMenuBar(self.main_ui)

        def init_mode_menu():
            """
            初始化模式菜单。

            包含模式菜单的各种选项设置、操作和事件处理。
            """

            def set_selected_mode_text(actions_category, text):
                """
                根据类别索引和文本更新选中的模式。

                参数:
                index (int): 类别索引
                text (str): 要设置的模式文本
                """
                match actions_category:
                    case ActionsCategory.StudyMode:
                        self.father.selected_1_study_mode = text
                        print(text)
                    case ActionsCategory.DataSource:
                        self.father.selected_2_data_sources_type = text
                        print(text)
                    case ActionsCategory.WordMode:
                        self.father.selected_3_word_mode = text
                        print(text)

            def handle_mode_selection(category, _action):
                """
                处理模式选择操作。

                当选择一个模式时，更新其他动作的选中状态，更新显示文本等。

                参数:
                category (int): 类别索引
                action (QAction): 被选中的动作
                """

                def close_other_action(actions_category):
                    """
                    关闭同一类别中除当前动作外的其他动作的选中状态。

                    参数:
                    index (int): 类别索引
                    """
                    for other_action in self.father.get_actions_by_category(actions_category):
                        if other_action.text() != _action.text():
                            other_action.setChecked(False)
                    set_selected_mode_text(actions_category, _action.text())

                if category == ActionsCategory.StudyMode:
                    if _action.text() == main.StudyMode.New_Learning:
                        self.father.turn_action(False)
                    else:
                        self.father.turn_action(True)

                if _action.text() in [self.father.selected_1_study_mode, self.father.selected_2_data_sources_type,
                                      self.father.selected_3_word_mode]:
                    _action.setChecked(True)
                else:
                    close_other_action(category)

                self.father.display_text = (f"0/0 {self.father.selected_1_study_mode} "
                                            f"数据：{self.father.selected_2_data_sources_type} "
                                            f"模式：{self.father.selected_3_word_mode}")
                self.father.display_label.setText(self.father.display_text)

            def handle_input_change():
                """
                处理输入框文本变化事件。

                检查输入是否为有效数字，并输出相应信息。
                """
                text = self.father.input_edit.text()
                try:
                    num = float(text)
                    if num > 0:
                        print(f"输入的有效数字为: {num}")
                    else:
                        print("输入的数字应大于0，请重新输入")
                except ValueError:
                    print("请输入有效的数字")

            def init_mode_action(mode_options, actions_category):
                """
                初始化模式动作。

                为每个模式选项创建可勾选的动作，并添加到菜单中，将第一个选项默认勾选，连接触发事件。

                参数:
                mode_options (list[str]): 模式选项列表
                index (int): 类别索引

                返回:
                list[QAction]: 创建的动作列表
                """
                actions = []
                for i, option in enumerate(mode_options):
                    _action = QAction(option, self.father.win)
                    _action.setCheckable(True)
                    if i == 0:  # 新增：将第一个选项默认勾选
                        _action.setChecked(True)
                    # noinspection PyUnresolvedReferences
                    _action.triggered.connect(functools.partial(handle_mode_selection, actions_category, _action))
                    mode_menu.addAction(_action)
                    actions.append(_action)
                return actions

            mode_menu = QMenu("模式", menubar)
            mode_options_1 = main.study_mode_list
            init_mode_action(mode_options_1, ActionsCategory.StudyMode)

            mode_menu.addSeparator()
            mode_options_2 = main.data_sources_type_list
            actions_2 = init_mode_action(mode_options_2, ActionsCategory.DataSource)
            # 将第 2 类选项初始设为不可用
            for action in actions_2:
                action.setEnabled(False)

            mode_menu.addSeparator()
            mode_options_3 = main.word_mode_list
            actions_3 = init_mode_action(mode_options_3, ActionsCategory.WordMode)
            for action in actions_3:
                action.setEnabled(False)

            self.father.input_edit = QLineEdit()
            self.father.input_edit.setText("15")
            self.father.input_edit.setPlaceholderText("")
            self.father.input_edit.textChanged.connect(handle_input_change)

            widget = QWidget(None)
            layout = QHBoxLayout(widget)

            label = QLabel("数量:")
            layout.addWidget(label)
            layout.addWidget(self.father.input_edit)
            self.father.input_edit.setFixedWidth(65)

            widget_action = QWidgetAction(mode_menu)
            widget_action.setDefaultWidget(widget)
            mode_menu.addAction(widget_action)

            menubar.addMenu(mode_menu)

        def init_settings_menu():
            """
            初始化设置菜单。

            创建发音设置动作，并将其添加到设置菜单中，连接触发事件。
            """
            settings_menu = QMenu("设置", menubar)
            # 创建一个可勾选的 QAction 实例
            self.father.action_pronunciation = QAction("发音", self.father.win)
            self.father.action_pronunciation.setCheckable(True)
            self.father.action_pronunciation.setChecked(self.father.settings.pronounce)

            clear_cache = QAction("清除缓存", self.father.win)
            clear_cache.action_record_1 = QAction("已学单词", self.father.win)
            clear_cache.triggered.connect(
                lambda: self.father.handle_menu_click(clear_cache.text()))
            settings_menu.addAction(self.father.action_pronunciation)
            settings_menu.addAction(clear_cache)
            menubar.addMenu(settings_menu)

        # noinspection PyUnresolvedReferences
        def init_record_menu():
            """
            初始化记录菜单。

            创建记录相关的动作，并添加到记录菜单中。
            """
            record_menu = QMenu("记录", menubar)
            action_record_1 = QAction("已学单词", self.father.win)
            action_record_1.triggered.connect(
                lambda: self.father.handle_record_menu_action_click(record.RecordType.LearnedAlready))
            action_record_2 = QAction("掌握单词", self.father.win)
            action_record_2.triggered.connect(
                lambda: self.father.handle_record_menu_action_click(record.RecordType.FullyMastered))
            action_record_3 = QAction("记录本", self.father.win)
            action_record_3.triggered.connect(
                lambda: self.father.handle_record_menu_action_click(record.RecordType.Logbook))
            action_record_4 = QAction("添加今日单词", self.father.win)
            action_record_4.triggered.connect(lambda: self.father.handle_menu_click(action_record_4.text()))
            record_menu.addAction(action_record_1)
            record_menu.addAction(action_record_2)
            record_menu.addAction(action_record_3)
            record_menu.addAction(action_record_4)
            menubar.addMenu(record_menu)

        def init_daily_tasks_menu():
            daily_tasks_menu = QMenu("任务", menubar)
            tasks_1 = QAction("每日任务", self.father.win)
            tasks_1.triggered.connect(lambda: self.father.handle_menu_click(tasks_1.text()))
            tasks_2 = QAction("加练5个", self.father.win)
            tasks_2.triggered.connect(lambda: self.father.handle_menu_click(tasks_2.text()))
            daily_tasks_menu.addAction(tasks_1)
            daily_tasks_menu.addAction(tasks_2)

            menubar.addMenu(daily_tasks_menu)

        init_mode_menu()
        init_settings_menu()
        init_record_menu()
        init_daily_tasks_menu()

        self.father.win.setMenuBar(menubar)

    def init_layout(self):
        """
        构建主界面布局

        创建包含以下部分的布局：
        - 顶部布局（状态显示和控制按钮）
        - 中央布局（单词显示区域）
        - 底部布局（功能操作按钮）
        """
        main_layout = QVBoxLayout()

        def init_top_layout():
            """
            初始化顶部布局。

            创建并添加顶部的显示标签和按钮。
            """
            top_layout = QHBoxLayout()
            self.father.display_label.setText("0/0 %s 数据：%s 模式：%s" % (
                self.father.selected_1_study_mode, self.father.selected_2_data_sources_type,
                self.father.selected_3_word_mode))
            top_layout.addWidget(self.father.display_label, 0, Qt.AlignTop | Qt.AlignLeft)

            self.father.top_right_button = QPushButton("开始", self.father.win)
            self.father.top_right_button.setFixedWidth(60)
            self.father.top_right_button.clicked.connect(lambda: self.father.run())
            top_layout.addWidget(self.father.top_right_button, 1, Qt.AlignTop | Qt.AlignRight)
            top_right_button1 = QPushButton("提示", self.father.win)
            top_right_button1.setFixedWidth(60)
            top_right_button1.clicked.connect(lambda: self.father.handle_button_click(top_right_button1.text()))
            top_layout.addWidget(top_right_button1, 0, Qt.AlignTop | Qt.AlignRight)
            main_layout.addLayout(top_layout)

        # noinspection DuplicatedCode
        def init_controls_layout():
            """
            初始化中间布局。

            创建并添加中间的文本标签，设置字体和对齐方式。
            """
            central_widget = QWidget(None)
            central_layout = QVBoxLayout(central_widget)
            central_layout.setContentsMargins(0, 0, 0, 0)
            central_layout.setSpacing(0)
            central_layout.setStretchFactor(central_widget, 9)

            self.father.label_1 = QLabel("----------", central_widget)
            font_1 = QFont()
            font_1.setPointSize(33)
            self.father.label_1.setFont(font_1)
            self.father.label_1.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.father.label_1.setWordWrap(True)
            central_layout.addWidget(self.father.label_1)

            self.father.label_2 = QLabel("----------", central_widget)
            font_2 = QFont()
            font_2.setPointSize(33)
            self.father.label_2.setFont(font_2)
            self.father.label_2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.father.label_2.setWordWrap(True)
            central_layout.addWidget(self.father.label_2)
            central_layout.setSpacing(70)

            main_layout.addWidget(central_widget)

        def init_bottom_layout():
            """
            初始化底部布局。

            创建并添加底部的保存和斩杀按钮。
            """
            bottom_layout = QHBoxLayout()

            bottom_left_button = QPushButton("保存", self.father.win)
            bottom_left_button.setFixedWidth(60)
            bottom_left_button.clicked.connect(lambda: self.father.handle_button_click(bottom_left_button.text()))
            bottom_layout.addWidget(bottom_left_button, 0, Qt.AlignBottom | Qt.AlignLeft)

            bottom_right_button = QPushButton("斩杀", self.father.win)
            bottom_right_button.setFixedWidth(60)
            bottom_right_button.clicked.connect(lambda: self.father.handle_button_click(bottom_right_button.text()))
            bottom_layout.addWidget(bottom_right_button, 0, Qt.AlignBottom | Qt.AlignRight)

            main_layout.addLayout(bottom_layout)

        init_top_layout()
        init_controls_layout()
        init_bottom_layout()

        main_widget = QWidget(None)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.father.win.setCentralWidget(main_widget)

    def init_today_data(self):
        """
        初始化今日学习数据

        检查上次运行日期，若为首次今日运行则：
        1. 清理临时文件
        2. 获取今日新词和昨日复习词
        3. 启动MP3下载线程
        4. 更新最后运行日期记录
        """
        # 获取当前日期
        today = datetime.date.today()

        # 检查记录文件是否存在
        if os.path.exists(path.last_run_date):
            # 读取文件中的日期
            with open(path.last_run_date, 'r') as f:
                last_run_date_str = f.read().strip()
                try:
                    # 将字符串转换为日期对象
                    last_run_date = datetime.datetime.strptime(last_run_date_str, '%Y-%m-%d').date()
                    # 如果上次运行日期是今天，不执行主要逻辑
                    if last_run_date == today:
                        print("今天已经运行过，不再执行。")
                        return
                except ValueError:
                    # 处理日期格式错误的情况
                    pass
        else:
            with open(path.last_run_date, 'r'):
                pass

        # 执行主要逻辑
        print("正在执行主要逻辑...")
        # 这里可以放你需要每天只运行一次的代码
        self.father.memorize_word.clear(path.today_mp3)

        today_data = main.Main(main.StudyMode.New_Learning, 15, main.DataSourcesType.NotLearnedYet,
                               study_mode=record.RecordType.TodayData).data
        yesterday_data = self.father.recorder.get(record.RecordType.LearnedAlready, today - datetime.timedelta(days=1))
        down_load_thread_1_today = threading.Thread(target=self.father.down_load_mp3,
                                                    args=(today_data, path.today_mp3,))
        down_load_thread_1_today.start()
        down_load_thread_2_yesterday = threading.Thread(target=self.father.down_load_mp3,
                                                        args=(yesterday_data, path.yesterday_mp3,))
        down_load_thread_2_yesterday.start()
        self.father.recorder.write(record.RecordType.TodayData, datetime.date.today(), today_data)

        # 更新记录文件中的日期
        with open(path.last_run_date, 'w') as f:
            f.write(str(today))


# noinspection PyUnresolvedReferences
class StudyRun:
    def __init__(self, father, study_mode, data_source_type, word_mode,
                 sp: main.DailyTasks.DailyTasksData = main.DailyTasks.DailyTasksData(None, None)):
        self.father = father

        self.study_mode = study_mode
        self.word_mode = word_mode
        self.data_source_type = data_source_type
        self.daily_tasks = sp

        self.now_using_word_length = None
        self.word_index = None
        self.running = None
        self.run()

    def change_index(self, boolean_value):
        """
        控制单词索引变化

        :param boolean_value: True增加索引，False减少索引
        功能：更新显示内容并检查边界条件
        """
        if boolean_value:
            if self.running.index < self.now_using_word_length * 2 - 1:
                self.running.index += 1
            else:
                print(f"当前值已经是 {self.now_using_word_length * 2 - 1}，不能再增加了。")
                self.father.top_right_button.setText("结束")
        else:
            if self.running.index > 0:
                self.running.index -= 1
            else:
                print("当前值已经是0，不能再减少了。")
        self.print_text()

    def print_text(self):
        """
        更新单词显示内容

        根据当前学习模式和索引：
        1. 设置中英对照显示
        2. 更新状态栏进度
        3. 根据设置自动发音
        """

        def get_text_based_on_mode(index, label):
            """
            根据选择的单词模式和索引获取要显示的文本
            :param index: 数据索引
            :param label: 要设置文本的标签
            :return: 要显示的文本
            """
            data = self.father.word_manager.get_data_by_index(self.running.data[index])
            self.now_word = data.word
            # 先根据混合模式确定基础的文本选择
            if self.word_mode == main.WordMode.Mixed_Mode:
                primary_text = data.word if self.running.random_table_0_and_1[index] == 0 else data.meaning
            elif self.word_mode == main.WordMode.C_to_E:
                primary_text = data.meaning
            else:  # main.Word_Mode.E_to_C
                primary_text = data.word

            # 根据标签确定最终要返回的文本
            if label == self.father.label_1:
                return primary_text
            else:
                # 若不是 label_1，则返回另一个值
                return data.word if primary_text == data.meaning else data.meaning

        def update_labels():
            self.word_index = self.running.index // 2
            print(self.running.index)
            text_1 = get_text_based_on_mode(self.word_index, self.father.label_1)
            text_2 = get_text_based_on_mode(self.word_index, self.father.label_2)
            if self.running.index % 2 == 0:
                # 根据模式设置 label_1 的文本
                self.father.label_1.setText(text_1)
                self.father.label_2.setText("")
            else:
                # 根据模式设置 label_1 的文本
                self.father.label_1.setText(text_1)
                self.father.label_2.setText(text_2)

            if self.father.action_pronunciation.isChecked():
                if self.daily_tasks.daily_name is not None:
                    if self.daily_tasks.daily_name == main.DailyTasks.study:
                        self.father.memorize_word.sing(self.now_word, file_path=path.today_mp3)
                    elif self.daily_tasks.daily_name == main.DailyTasks.review:
                        self.father.memorize_word.sing(self.now_word, file_path=path.yesterday_mp3)
                else:
                    self.father.memorize_word.sing(self.now_word)

        self.now_using_word_length = len(self.running.data)
        update_labels()

        self.father.display_label.setText("%d/%d %s 数据:%s 模式:%s"
                                          % (self.word_index + 1, self.now_using_word_length,
                                             self.study_mode,
                                             self.data_source_type,
                                             self.word_mode))

    def reset_data(self):
        """
        重置学习状态

        功能：
        1. 清空显示内容
        2. 移除键盘热键
        3. 恢复菜单初始状态
        """
        self.father.label_1.setText("--------")
        self.father.label_2.setText("--------")
        self.father.display_label.setText("0/0 %s 数据：%s 模式：%s"
                                          % (self.study_mode,
                                             self.data_source_type,
                                             self.word_mode))
        self.running = None
        self.word_index = 0
        # keyboard.remove_all_hotkeys()

        for shortcut in self.father.shortcuts:
            shortcut.deleteLater()
        self.father.shortcuts = []

        self.father.top_right_button.setText("开始")
        if self.study_mode == main.StudyMode.New_Learning:
            self.father.turn_action(reset=True)
        else:
            self.father.turn_action(True, True)

    def bind_shortcuts(self):
        """
        绑定快捷键
        """
        # 示例：绑定 Ctrl+N 快捷键到 self.handle_new_action 方法
        new_action = QAction(self.father.win)
        new_action.setShortcut("down")
        new_action.triggered.connect(lambda: self.change_index(True))
        self.father.win.addAction(new_action)
        self.father.shortcuts.append(new_action)

        # 示例：绑定 Ctrl+S 快捷键到 self.handle_save_action 方法
        save_action = QAction(self.father.win)
        save_action.setShortcut("up")
        save_action.triggered.connect(lambda: self.change_index(False))
        self.father.win.addAction(save_action)
        self.father.shortcuts.append(save_action)

    def init_run(self, goon=None):
        """
        初始化学习流程

        :param goon: 是否继续之前的任务
        :return: 是否成功初始化
        功能：
        1. 设置界面按钮状态
        2. 绑定键盘热键
        """
        if self.daily_tasks.daily_name is None:
            self.now_using_word_length = int(self.father.input_edit.text())
        else:
            self.now_using_word_length = self.daily_tasks.length

        if self.father.top_right_button.text() == "重置":
            self.reset_data()
            return False
        elif self.father.top_right_button.text() == "结束" and goon is None:
            if self.father.handle_button_click("结束"):
                self.reset_data()
            return False
        self.father.top_right_button.setText("重置")
        self.father.turn_action(False, True)
        if self.running is None:
            self.bind_shortcuts()
        return True

    def init_run_data(self, sp: main.DailyTasks.DailyTasksData = main.DailyTasks.DailyTasksData(None, None)):
        """
        初始化学习数据
        :param sp: 特殊任务标识
        功能：加载对应数据并初始化显示
        """
        print(self.study_mode, self.data_source_type, self.word_mode)

        self.running = main.Main(self.word_mode, self.now_using_word_length, self.data_source_type, self.study_mode, sp)

        self.now_using_word_length = len(self.running.data)
        if self.daily_tasks != main.DailyTasks.study:
            if self.daily_tasks != main.DailyTasks.review:
                self.father.down_load_mp3(self.running.data)
        self.print_text()

    def run(self, goon=None):
        """
        启动学习流程

        :param goon: 是否继续之前的任务
        功能：根据当前配置启动学习或复习流程
        """

        if not self.init_run(goon=goon):
            return

        if type(self.daily_tasks) == main.DailyTasks.DailyTasksData:
            self.init_run_data(sp=self.daily_tasks)
        else:
            try:
                self.init_run_data()
            except EOFError:
                self.father.running = None
                self.father.label_1.setText(
                    f"该数据源没有数据（{self.study_mode}/{self.data_source_type}）")
                self.father.label_2.setText("")
                # keyboard.remove_all_hotkeys()"""


# noinspection PyUnresolvedReferences
class UI:
    def __init__(self):
        """
        初始化应用程序的主界面和核心组件

        创建 QApplication 实例、主窗口、菜单栏、布局等核心元素，
        并初始化今日数据加载和日志记录功能。
        """

        self.shortcuts = []
        self.recorder = record.Record()
        self.settings = settings.Settings("settings.json")
        self.memorize_word = pronounce.MemorizeWord()
        self.word_manager = take_data.WordListManager()
        self.running_manage = None

        self.action_pronunciation = None
        self.top_right_button = None
        self.input_edit = None
        self.daily_tasks_length = None
        self.label_1 = None
        self.label_2 = None

        self.selected_1_study_mode = main.StudyMode.New_Learning
        self.selected_2_data_sources_type = main.DataSourcesType.NotLearnedYet
        self.selected_3_word_mode = main.WordMode.E_to_C

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MemorizeWords")
        self.app.setWindowIcon(QIcon("icon.jpg"))

        self.win = QMainWindow(None)
        self.win.show()
        self.win.closeEvent = self.close_event_handler

        self.display_label = QLabel(self.win)
        self.init_ui = InitUI(self)

        sys.exit(self.app.exec_())

    def down_load_mp3(self, data, file_path=None):
        """
        异步下载单词发音MP3文件

        :param data: 需要下载的单词数据列表
        :param file_path: 文件保存路径，默认为None使用默认路径
        """

        def down_loading(_data, _file_path=None):
            word_list = []
            for data_i in _data:
                word_list.append(self.word_manager.get_data_by_index(data_i).word)
            self.memorize_word.download(word_list, file_path=_file_path)

        down_thread = threading.Thread(target=down_loading, args=(data, file_path,))
        down_thread.start()
        time.sleep(1.5)

    def turn_action(self, ac=False, _all=False, reset=False):
        """
        控制菜单项的可用状态

        :param ac: 是否启用二级菜单项
        :param _all: 是否同时控制一级菜单项
        :param reset: 是否重置为初始状态
        """
        if reset:
            for other_action in self.get_actions_by_category(ActionsCategory.StudyMode):
                other_action.setEnabled(True)
            self.input_edit.setText("15")
            self.input_edit.setEnabled(True)
        elif _all:
            for other_action in self.get_actions_by_category(ActionsCategory.StudyMode):
                other_action.setEnabled(ac)
            self.input_edit.setEnabled(ac)

        for other_action in self.get_actions_by_category(ActionsCategory.DataSource):
            other_action.setEnabled(ac)
        for other_action in self.get_actions_by_category(ActionsCategory.WordMode):
            other_action.setEnabled(ac)

    def get_actions_by_category(self, category):
        """
        按分类获取菜单动作

        :param category: Ac（1-学习模式，2-数据源，3-单词模式）
        :return: 对应分类的菜单动作列表
        """
        _mode_menu = None
        _menubar = self.win.menuBar()
        for action in _menubar.actions():
            if action.text() == "模式":
                _mode_menu = action.menu()
        if _mode_menu is not None:
            actions = _mode_menu.actions()
            if category == ActionsCategory.StudyMode:
                return [act for act in actions if
                        act.text().startswith('第一类') or act.text() in main.study_mode_list]
            elif category == ActionsCategory.DataSource:
                return [act for act in actions if
                        act.text().startswith('第二类') or act.text() in main.data_sources_type_list]
            elif category == ActionsCategory.WordMode:
                return [act for act in actions if
                        act.text().startswith('第三类') or act.text() in main.word_mode_list]
        return []

    def handle_record_menu_action_click(self, record_type):
        """
        处理记录菜单点击事件

        :param record_type: 记录类型（LearnedAlready/FullyMastered等）
        功能：将对应记录数据导出为CSV并用Excel打开
        """
        print(f"点击了菜单选项: {record_type}")

        data = self.recorder.get(record_type, dic=True)

        def dict_to_csv(data_dict, header=('日期', '单词')):
            """
            将键值对写入 CSV 文件，其中值为列表时，列表元素各占一格，列表元素通过 get_data 获取具体内容。

            :param data_dict: 包含键值对的字典，值可以是列表
            :param header: 可选参数，CSV 文件的表头，默认为 ('键', '值')
            :return: 生成的临时 CSV 文件的路径
            """
            # 找出值列表中的最大长度
            max_value_length = max(len(value) if isinstance(value, list) else 1 for value in data_dict.values())
            # 生成表头，如果值是列表，会根据最大长度扩展表头
            extended_header = [header[0]] + [f"{header[1]}_{i + 1}" for i in range(max_value_length)]

            with open(self.temp_file_path, "w", newline="") as temp_file:
                writer = csv.writer(temp_file)
                # 写入表头
                writer.writerow(extended_header)
                for key, value in data_dict.items():
                    # 如果值不是列表，将其转换为包含一个元素的列表
                    if not isinstance(value, list):
                        value = [value]
                    # 使用 get_data 函数获取列表元素的具体内容
                    content_list = []
                    for num in value:
                        result = self.word_manager.get_data_by_index(num)
                        content_list.append(f"{result.word}-{result.meaning}")
                    # 补齐值列表的长度，使其达到最大长度
                    row = [key] + content_list + ['' for _ in range(max_value_length - len(content_list))]
                    writer.writerow(row)
                temp_file.close()

        def open_and_delete_temp_csv(data_dict):
            """
            生成临时 CSV 文件，用 Excel 打开，关闭后删除文件。

            :param data_dict: 包含键值对的字典，值可以是列表
            """
            dict_to_csv(data_dict)
            # 调用 Excel 打开临时文件
            subprocess.run(['start', 'excel', self.temp_file_path], shell=True)

        open_and_delete_temp_csv(data)
        print(data)

    def handle_menu_click(self, text):
        """
                处理每日任务菜单点击事件

                :param text: 菜单项文本
                功能：
                - "每日任务"：启动15个单词学习
                - "加练5个"：启动5个补充学习
                - "添加今日单词"：弹出对话框输入单词并验证
                """"""
        处理每日任务菜单点击事件
        
        :param text: 菜单项文本
        功能：
        - "每日任务"：启动15个单词学习
        - "加练5个"：启动5个补充学习
        - "添加今日单词"：弹出对话框输入单词并验证
        """
        print(self.input_edit)
        print("点击了菜单: %s" % text)
        match text:
            case "每日任务":
                daily_tasks = main.DailyTasks.DailyTasksData(main.DailyTasks.study, 15)
                self.run(daily_tasks)
                """daily_tasks = main.DailyTasks.DailyTasksData(main.DailyTasks.review, 15)
                self.run(daily_tasks)"""
                print("任务一结束")
            case "加练5个":
                daily_tasks = main.DailyTasks.DailyTasksData(main.DailyTasks.review, 5)
                self.run(daily_tasks)
            case "添加今日单词":
                # 创建一个对话框
                dialog = QDialog(self.win)
                dialog.setWindowTitle("添加今日单词")
                dialog.resize(500, 500)

                # 创建一个多行文本输入框，至少15行
                text_edit = QTextEdit(dialog)

                # 创建按钮盒，包含确认和取消按钮
                button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)

                # 布局
                layout = QVBoxLayout()
                layout.addWidget(text_edit)
                layout.addWidget(button_box, alignment=Qt.AlignCenter)
                dialog.setLayout(layout)

                # 禁用回车键触发按钮点击
                text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
                text_edit.installEventFilter(self.win)

                # 显示对话框并获取结果
                if dialog.exec_() == QDialog.Accepted:
                    words = text_edit.toPlainText()
                    # 这里可以添加处理输入的单词的代码，例如保存到文件等
                    print("输入的单词：", words)
                    temp_word_list = words.split("\n")
                    for word in temp_word_list:
                        index = self.word_manager.get_data_by_word(word)
                        if index is not None:
                            self.recorder.add(record.RecordType.LearnedAlready, datetime.date.today(), index)
                        else:
                            logging.info("单词%s不在单词表" % word)  # 记录开始初始化今日数据的日志
                            print("单词%s不在单词表" % word)
            case "清除缓存":
                print("清除缓存")
                self.recorder.clear_cache()

    def close_event_handler(self, event):
        """
        处理窗口关闭事件

        功能：
        1. 保存发音设置
        2. 清理临时语音文件
        3. 持久化配置
        """
        print(event)
        self.settings.set("pronounce", self.action_pronunciation.isChecked())
        self.memorize_word.clear(path.Speech)
        self.settings.save()

    def handle_button_click(self, text):
        """
        处理功能按钮点击事件

        :param text: 按钮文本
        功能：
        - "提示"：朗读当前单词
        - "保存"：记录到生词本
        - "斩杀"：标记为已掌握
        - "结束"：确认退出流程
        """

        print(f"点击了按钮: {text}")
        match text:
            case "提示":
                if self.running_manage is not None:
                    print("执行")
                    self.memorize_word.sing(self.running_manage.now_word)
            case "保存":
                if self.running_manage is not None:
                    self.recorder.add(record.RecordType.Logbook, datetime.date.today(),
                                      self.running_manage.running.data[self.running_manage.word_index])
            case "斩杀":
                # 获取当前单词在数据列表中的实际索引
                word_index = self.running_manage.running.index // 2
                # 记录到已掌握
                self.recorder.add(record.RecordType.FullyMastered, datetime.date.today(),
                                  self.running_manage.running.data[word_index])
                # 移除对应的单词数据和随机表条目
                self.running_manage.running.data.pop(word_index)
                self.running_manage.running.random_table_0_and_1.pop(word_index)
                # 调整当前索引，防止越界
                max_index = len(self.running_manage.running.data) * 2 - 1
                self.running_manage.running.index = min(self.running_manage.running.index, max_index)

                # 刷新显示
                self.running_manage.print_text()

            case "结束":
                reply = QMessageBox.question(self.win, '确认退出', '你确定要退出吗？',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    print("确认")
                    return True
                else:
                    print("取消")
                    return False

    def run(self, sp=main.DailyTasks.DailyTasksData(None, None)):
        """
        启动学习流程

        :param sp:
        功能：根据当前配置启动学习或复习流程
        """
        self.running_manage = StudyRun(self, self.selected_1_study_mode,
                                       self.selected_2_data_sources_type, self.selected_3_word_mode, sp=sp)


if __name__ == '__main__':
    ui = UI()
