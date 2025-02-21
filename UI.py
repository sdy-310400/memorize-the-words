import csv
import datetime
import logging
import os
import subprocess
import sys
import functools
import threading
import time

import keyboard
import take_data
import path
import main
import record
import settings

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QLabel, QLineEdit, QWidgetAction, \
    QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QMessageBox, QDialog, QTextEdit, QDialogButtonBox
from PyQt5.QtCore import Qt

from pronounce import MemorizeWord

# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(pastime)s - %(levelness)s - %(message)s',
                    filename='add_word.log',  # 日志文件名为 app.log
                    filemode='a')  # 追加模式写入日志


# noinspection PyUnresolvedReferences
class UI:
    def __init__(self):
        """
        UI 类的构造函数，用于初始化整个界面。

        创建 QApplication 实例，主窗口，显示标签等，并调用初始化主窗口、菜单和布局的函数，最后显示窗口。
        """
        self.recorder = record.Record()
        self._settings = settings.Settings("settings.json")
        self.memorize_word = MemorizeWord()

        self.action_pronunciation = None
        self.top_right_button = None
        self.word_index = None
        self.running = None
        self.input_edit = None
        self.now_word = None
        self.using_word_length = None
        self.daily_tasks = None
        self.daily_tasks_length = None

        self.app = QApplication(sys.argv)
        self.win = QMainWindow(None)
        self.label_1 = QLabel(self.win)
        self.label_2 = QLabel(self.win)
        self.display_label = QLabel(self.win)

        self.selected_1_study_mode = main.StudyMode.New_Learning
        self.selected_2_data_sources_type = main.DataSourcesType.Today
        self.selected_3_word_mode = main.WordMode.C_to_E
        self.temp_file_path = os.path.join(path.main, "temp_file.csv")  # 用于保存临时文件路径

        self.init_main_window()
        self.init_menu()
        self.init_layout()

        self.win.show()
        self.win.closeEvent = self.close_event_handler
        self.word_manager = take_data.WordListManager()
        self.init_today_data()
        sys.exit(self.app.exec_())

    def down_load_mp3(self, data, file_path=None):
        def down_loading(_data, _file_path=None):
            word_list = []
            for data_i in _data:
                word_list.append(self.word_manager.get_data_by_index(data_i).word)
            self.memorize_word.download(word_list, file_path=_file_path)

        down_thread = threading.Thread(target=down_loading, args=(data, file_path,))
        down_thread.start()
        time.sleep(1.5)

    def init_today_data(self):
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
        self.memorize_word.clear(path.today_mp3)
        self.memorize_word.clear(path.today_mp3)

        today_data = main.Main(main.StudyMode.New_Learning, 15, main.DataSourcesType.NotLearnedYet,
                               study_mode=record.RecordType.TodayData).data
        yesterday_data = self.recorder.get(record.RecordType.LearnedAlready, today - datetime.timedelta(days=1))
        down_load_thread_1_today = threading.Thread(target=self.down_load_mp3, args=(today_data, path.today_mp3,))
        down_load_thread_1_today.start()
        down_load_thread_2_yesterday = threading.Thread(target=self.down_load_mp3,
                                                        args=(yesterday_data, path.yesterday_mp3,))
        down_load_thread_2_yesterday.start()
        self.recorder.write(record.RecordType.TodayData, datetime.date.today(), today_data)

        # 更新记录文件中的日期
        with open(path.last_run_date, 'w') as f:
            f.write(str(today))

    def init_main_window(self):
        """
        初始化主窗口的位置、大小等属性。

        设置主窗口的几何形状、固定大小，并将其移动到屏幕中心位置。
        """
        self.win.setGeometry(0, 0, 1000, 600)
        self.win.setFixedSize(1000, 600)
        x = (2560 - self.win.width()) // 2
        y = (1440 - self.win.height()) // 2
        self.win.move(x, y)

    def init_menu(self):
        """
        初始化菜单栏及相关菜单。

        包含模式菜单、设置菜单和记录菜单的创建及相关操作。
        """
        menubar = QMenuBar(self.win)

        def init_mode_menu():
            """
            初始化模式菜单。

            包含模式菜单的各种选项设置、操作和事件处理。
            """

            def set_selected_mode_text(index, text):
                """
                根据类别索引和文本更新选中的模式。

                参数:
                index (int): 类别索引
                text (str): 要设置的模式文本
                """
                match index:
                    case 1:
                        self.selected_1_study_mode = text
                        print(text)
                    case 2:
                        self.selected_2_data_sources_type = text
                        print(text)
                    case 3:
                        self.selected_3_word_mode = text
                        print(text)


            def handle_mode_selection(category, _action):
                """
                处理模式选择操作。

                当选择一个模式时，更新其他动作的选中状态，更新显示文本等。

                参数:
                category (int): 类别索引
                action (QAction): 被选中的动作
                """

                def close_other_action(index):
                    """
                    关闭同一类别中除当前动作外的其他动作的选中状态。

                    参数:
                    index (int): 类别索引
                    """
                    for other_action in self.get_actions_by_category(index):
                        if other_action.text() != _action.text():
                            other_action.setChecked(False)
                    set_selected_mode_text(index, _action.text())

                if category == 1:
                    if _action.text() == main.StudyMode.New_Learning:
                        self.turn_action(False)
                    else:
                        self.turn_action(True)

                if _action.text() in [self.selected_1_study_mode, self.selected_2_data_sources_type,
                                      self.selected_3_word_mode]:
                    _action.setChecked(True)
                else:
                    close_other_action(category)

                self.display_text = (f"0/0 {self.selected_1_study_mode} "
                                     f"数据：{self.selected_2_data_sources_type} 模式：{self.selected_3_word_mode}")
                self.display_label.setText(self.display_text)

            def handle_input_change():
                """
                处理输入框文本变化事件。

                检查输入是否为有效数字，并输出相应信息。
                """
                text = self.input_edit.text()
                try:
                    num = float(text)
                    if num > 0:
                        print(f"输入的有效数字为: {num}")
                    else:
                        print("输入的数字应大于0，请重新输入")
                except ValueError:
                    print("请输入有效的数字")

            def init_mode_action(mode_options, index):
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
                    _action = QAction(option, self.win)
                    _action.setCheckable(True)
                    if i == 0:  # 新增：将第一个选项默认勾选
                        _action.setChecked(True)
                    # noinspection PyUnresolvedReferences
                    _action.triggered.connect(functools.partial(handle_mode_selection, index, _action))
                    mode_menu.addAction(_action)
                    actions.append(_action)
                return actions

            mode_menu = QMenu("模式", menubar)
            mode_options_1 = main.study_mode_list
            init_mode_action(mode_options_1, 1)

            mode_menu.addSeparator()
            mode_options_2 = main.data_sources_type_list
            actions_2 = init_mode_action(mode_options_2, 2)
            # 将第 2 类选项初始设为不可用
            for action in actions_2:
                action.setEnabled(False)

            mode_menu.addSeparator()
            mode_options_3 = main.word_mode_list
            actions_3 = init_mode_action(mode_options_3, 3)
            for action in actions_3:
                action.setEnabled(False)

            self.input_edit = QLineEdit()
            self.input_edit.setText("15")
            self.input_edit.setPlaceholderText("")
            self.input_edit.textChanged.connect(handle_input_change)

            widget = QWidget(None)
            layout = QHBoxLayout(widget)

            label = QLabel("数量:")
            layout.addWidget(label)
            layout.addWidget(self.input_edit)
            self.input_edit.setFixedWidth(65)

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
            self.action_pronunciation = QAction("发音", self.win)
            self.action_pronunciation.setCheckable(True)
            self.action_pronunciation.setChecked(self._settings.pronounce)
            settings_menu.addAction(self.action_pronunciation)
            menubar.addMenu(settings_menu)

        # noinspection PyUnresolvedReferences
        def init_record_menu():
            """
            初始化记录菜单。

            创建记录相关的动作，并添加到记录菜单中。
            """
            record_menu = QMenu("记录", menubar)
            action_record_1 = QAction("已学单词", self.win)
            action_record_1.triggered.connect(lambda: self.handle_menu_action_click(record.RecordType.LearnedAlready))
            action_record_2 = QAction("掌握单词", self.win)
            action_record_2.triggered.connect(lambda: self.handle_menu_action_click(record.RecordType.FullyMastered))
            action_record_3 = QAction("记录本", self.win)
            action_record_3.triggered.connect(lambda: self.handle_menu_action_click(record.RecordType.Logbook))
            action_record_4 = QAction("添加今日单词", self.win)
            action_record_4.triggered.connect(lambda: self.handle_daily_task_menu_click(action_record_4.text()))
            record_menu.addAction(action_record_1)
            record_menu.addAction(action_record_2)
            record_menu.addAction(action_record_3)
            record_menu.addAction(action_record_4)
            menubar.addMenu(record_menu)

        def init_daily_tasks_menu():
            daily_tasks_menu = QMenu("任务", menubar)
            tasks_1 = QAction("每日任务", self.win)
            tasks_1.triggered.connect(lambda: self.handle_daily_task_menu_click(tasks_1.text()))
            tasks_2 = QAction("加练5个", self.win)
            tasks_2.triggered.connect(lambda: self.handle_daily_task_menu_click(tasks_2.text()))
            daily_tasks_menu.addAction(tasks_1)
            daily_tasks_menu.addAction(tasks_2)

            menubar.addMenu(daily_tasks_menu)

        init_mode_menu()
        init_settings_menu()
        init_record_menu()
        init_daily_tasks_menu()

        self.win.setMenuBar(menubar)

    def turn_action(self, ac=False, _all=False, reset=False):
        """
        启用或禁用第 2 类和第 3 类的动作。

        参数:
        ac (bool): 是否启用动作
        """
        if reset:
            for other_action in self.get_actions_by_category(1):
                other_action.setEnabled(True)
            self.input_edit.setText("15")
            self.input_edit.setEnabled(True)
        elif _all:
            for other_action in self.get_actions_by_category(1):
                other_action.setEnabled(ac)
            self.input_edit.setEnabled(ac)

        for other_action in self.get_actions_by_category(2):
            other_action.setEnabled(ac)
        for other_action in self.get_actions_by_category(3):
            other_action.setEnabled(ac)

    def get_actions_by_category(self, category):
        """
        根据类别获取相应的动作列表。

        参数:
        category (int): 类别索引

        返回:
        list[QAction]: 属于该类别的动作列表
        """
        _mode_menu = None
        _menubar = self.win.menuBar()
        for action in _menubar.actions():
            if action.text() == "模式":
                _mode_menu = action.menu()
        if _mode_menu is not None:
            actions = _mode_menu.actions()
            if category == 1:
                return [act for act in actions if
                        act.text().startswith('第一类') or act.text() in main.study_mode_list]
            elif category == 2:
                return [act for act in actions if
                        act.text().startswith('第二类') or act.text() in main.data_sources_type_list]
            elif category == 3:
                return [act for act in actions if
                        act.text().startswith('第三类') or act.text() in main.word_mode_list]
        return []

    def init_layout(self):
        """
        初始化界面布局。

        包含顶部、中间和底部布局的创建和设置。
        """
        main_layout = QVBoxLayout()

        def init_top_layout():
            """
            初始化顶部布局。

            创建并添加顶部的显示标签和按钮。
            """
            top_layout = QHBoxLayout()
            self.display_label.setText("0/0 %s 数据：%s 模式：%s" % (
                self.selected_1_study_mode, self.selected_2_data_sources_type, self.selected_3_word_mode))
            top_layout.addWidget(self.display_label, 0, Qt.AlignTop | Qt.AlignLeft)

            self.top_right_button = QPushButton("开始", self.win)
            self.top_right_button.setFixedWidth(60)
            self.top_right_button.clicked.connect(lambda: self.run())
            top_layout.addWidget(self.top_right_button, 1, Qt.AlignTop | Qt.AlignRight)
            top_right_button1 = QPushButton("提示", self.win)
            top_right_button1.setFixedWidth(60)
            top_right_button1.clicked.connect(lambda: self.handle_button_click(top_right_button1.text()))
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

            self.label_1 = QLabel("----------", central_widget)
            font_1 = QFont()
            font_1.setPointSize(33)
            self.label_1.setFont(font_1)
            self.label_1.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.label_1.setWordWrap(True)
            central_layout.addWidget(self.label_1)

            self.label_2 = QLabel("----------", central_widget)
            font_2 = QFont()
            font_2.setPointSize(33)
            self.label_2.setFont(font_2)
            self.label_2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.label_2.setWordWrap(True)
            central_layout.addWidget(self.label_2)
            central_layout.setSpacing(70)

            main_layout.addWidget(central_widget)

        def init_bottom_layout():
            """
            初始化底部布局。

            创建并添加底部的保存和斩杀按钮。
            """
            bottom_layout = QHBoxLayout()

            bottom_left_button = QPushButton("保存", self.win)
            bottom_left_button.setFixedWidth(60)
            bottom_left_button.clicked.connect(lambda: self.handle_button_click(bottom_left_button.text()))
            bottom_layout.addWidget(bottom_left_button, 0, Qt.AlignBottom | Qt.AlignLeft)

            bottom_right_button = QPushButton("斩杀", self.win)
            bottom_right_button.setFixedWidth(60)
            bottom_right_button.clicked.connect(lambda: self.handle_button_click(bottom_right_button.text()))
            bottom_layout.addWidget(bottom_right_button, 0, Qt.AlignBottom | Qt.AlignRight)

            main_layout.addLayout(bottom_layout)

        init_top_layout()
        init_controls_layout()
        init_bottom_layout()

        main_widget = QWidget(None)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)
        self.win.setCentralWidget(main_widget)

    def handle_menu_action_click(self, record_type):
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

    def handle_daily_task_menu_click(self, text):
        print(self.input_edit)
        print("点击了菜单: %s" % text)
        match text:
            case "每日任务":
                self.daily_tasks = main.DailyTasks.study
                self.daily_tasks_length = 15
                self.using_word_length = 15
                self.run()
                print("任务一结束")
            case "加练5个":
                self.daily_tasks = main.DailyTasks.study
                self.using_word_length = 5
                self.daily_tasks_length = 5
                self.run()
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

    def close_event_handler(self, event):
        """
        处理窗口关闭事件，在关闭窗口时删除临时文件
        """
        print(event)
        self._settings.set("pronounce", self.action_pronunciation.isChecked())
        self.memorize_word.clear(path.Speech)
        self._settings.save()

    def change_index(self, boolean_value):
        if boolean_value:
            if self.running.index < self.using_word_length * 2 - 1:
                self.running.index += 1
            else:
                print(f"当前值已经是 {self.using_word_length * 2 - 1}，不能再增加了。")
                self.top_right_button.setText("结束")
        else:
            if self.running.index > 0:
                self.running.index -= 1
            else:
                print("当前值已经是0，不能再减少了。")
        self.print_text()

    def print_text(self):
        def get_text_based_on_mode(index, label):
            """
            根据选择的单词模式和索引获取要显示的文本
            :param index: 数据索引
            :param label: 要设置文本的标签
            :return: 要显示的文本
            """
            data = self.word_manager.get_data_by_index(self.running.data[index])
            self.now_word = data.word
            # 先根据混合模式确定基础的文本选择
            if self.selected_3_word_mode == main.WordMode.Mixed_Mode:
                primary_text = data.word if self.running.random_table_01[index] == 0 else data.meaning
            elif self.selected_3_word_mode == main.WordMode.C_to_E:
                primary_text = data.meaning
            else:  # main.Word_Mode.E_to_C
                primary_text = data.word

            # 根据标签确定最终要返回的文本
            if label == self.label_1:
                return primary_text
            else:
                # 若不是 label_1，则返回另一个值
                return data.word if primary_text == data.meaning else data.meaning

        def update_labels():
            self.word_index = self.running.index // 2
            print(self.running.index)
            text_1 = get_text_based_on_mode(self.word_index, self.label_1)
            text_2 = get_text_based_on_mode(self.word_index, self.label_2)
            if self.running.index % 2 == 0:
                # 根据模式设置 label_1 的文本
                self.label_1.setText(text_1)
                self.label_2.setText("")
            else:
                # 根据模式设置 label_1 的文本
                self.label_1.setText(text_1)
                self.label_2.setText(text_2)

            if self.action_pronunciation.isChecked():
                if self.daily_tasks != main.DailyTasks.study:
                    self.memorize_word.sing(self.now_word, file_path=path.today_mp3)
                elif self.daily_tasks != main.DailyTasks.review:
                    self.memorize_word.sing(self.now_word, file_path=path.yesterday_mp3)
                else:
                    self.memorize_word.sing(self.now_word)

        update_labels()

        self.display_label.setText("%d/%d %s 数据:%s 模式:%s"
                                   % (self.word_index + 1, self.using_word_length, self.selected_1_study_mode,
                                      self.selected_2_data_sources_type,
                                      self.selected_3_word_mode))

    def reset_data(self):
        self.label_1.setText("--------")
        self.label_2.setText("--------")
        self.display_label.setText("0/0 %s 数据：%s 模式：%s"
                                   % (self.selected_1_study_mode, self.selected_2_data_sources_type,
                                      self.selected_3_word_mode))
        self.running = None
        self.word_index = 0
        keyboard.remove_all_hotkeys()
        self.top_right_button.setText("开始")
        if self.selected_1_study_mode == main.StudyMode.New_Learning:
            self.turn_action(reset=True)
        else:
            self.turn_action(True, True)

    def init_run(self, goon=None):
        if self.daily_tasks is None:
            self.using_word_length = int(self.input_edit.text())
        if self.top_right_button.text() == "重置":
            self.reset_data()
            return False
        elif self.top_right_button.text() == "结束" and goon is None:
            if self.handle_button_click("结束"):
                self.reset_data()
            return False
        self.top_right_button.setText("重置")
        self.turn_action(False, True)
        if self.running is None:
            keyboard.add_hotkey('down', self.change_index, args=(True,))
            keyboard.add_hotkey('up', self.change_index, args=(False,))
        return True

    def init_run_data(self, selected_1_study_mode, selected_2_data_sources_type, selected_3_word_mode, length, sp=None):
        self.selected_1_study_mode = selected_1_study_mode
        self.selected_2_data_sources_type = selected_2_data_sources_type
        self.selected_3_word_mode = selected_3_word_mode
        print(self.selected_1_study_mode, self.selected_2_data_sources_type, selected_3_word_mode)
        self.running = main.Main(self.selected_3_word_mode, length, self.selected_2_data_sources_type,
                                 self.selected_1_study_mode, sp)
        self.using_word_length = len(self.running.data)
        if self.daily_tasks != main.DailyTasks.study:
            if self.daily_tasks != main.DailyTasks.review:
                self.down_load_mp3(self.running.data)
        self.print_text()

    def run(self, goon=None):
        if not self.init_run(goon=goon):
            return

        if self.daily_tasks == main.DailyTasks.study:
            self.init_run_data(main.StudyMode.New_Learning, main.DataSourcesType.NotLearnedYet, main.WordMode.E_to_C,
                               self.daily_tasks_length, sp=main.DailyTasks.study)
        elif self.daily_tasks == main.DailyTasks.review:
            self.init_run_data(main.StudyMode.New_Learning, main.DataSourcesType.Yesterday, main.WordMode.Mixed_Mode,
                               self.daily_tasks_length, sp=main.DailyTasks.review)
        elif self.selected_1_study_mode == main.StudyMode.New_Learning:
            self.init_run_data(main.StudyMode.New_Learning, main.DataSourcesType.NotLearnedYet, main.WordMode.E_to_C,
                               int(self.input_edit.text()))
        else:
            try:
                self.init_run_data(self.selected_1_study_mode, self.selected_2_data_sources_type,
                                   self.selected_3_word_mode, int(self.input_edit.text()))
            except EOFError:
                self.running = None
                self.label_1.setText(
                    f"该数据源没有数据（{self.selected_1_study_mode}/{self.selected_2_data_sources_type}）")
                self.label_2.setText("")
                keyboard.remove_all_hotkeys()

    def handle_button_click(self, text):
        print(f"点击了按钮: {text}")
        match text:
            case "提示":
                if self.running is not None:
                    print("执行")
                    self.memorize_word.sing(self.now_word)
            case "保存":
                if self.running is not None:
                    self.recorder.add(record.RecordType.Logbook, datetime.date.today(),
                                      self.running.word_manager[self.word_index])
            case "斩杀":
                if self.running is not None:
                    self.recorder.add(record.RecordType.FullyMastered, datetime.date.today(),
                                      self.running.word_manager[self.word_index])
                    self.running.word_manager.pop(self.word_index)
                    self.running.random_table_01.pop(self.word_index)
                    if self.word_index == int(self.input_edit.text()) - 1:
                        self.word_index -= 1
                    self.using_word_length -= 1
                    self.running.index -= 2
                    self.print_text()

            case "结束":
                reply = QMessageBox.question(self.win, '确认退出', '你确定要退出吗？',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    print("确认")
                    if self.daily_tasks == main.DailyTasks.study:
                        self.reset_data()
                        self.daily_tasks = main.DailyTasks.review
                        try:
                            self.run(True)
                        except EOFError:
                            self.label_1.setText("昨日没有数据")
                            self.label_2.setText("")
                        return False
                    return True
                else:
                    print("取消")
                    return False


if __name__ == '__main__':
    ui = UI()
