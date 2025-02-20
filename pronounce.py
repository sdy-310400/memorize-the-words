"""
程序思想：
有两个本地语音库，美音库Speech_US，英音库Speech_US
调用有道api，获取语音MP3，存入对应的语音库中
"""
import copy
import os
import threading
import urllib.request
from playsound import playsound, PlaysoundException
import path


class youdao:
    def __init__(self):
        """
        调用youdao API
        type = 0：美音
        type = 1：英音

        判断当前目录下是否存在两个语音库的目录
        如果不存在，创建
        """
        # 文件根目录
        self._filePath = None
        self._dirRoot = os.path.dirname(os.path.abspath(__file__))
        self._dirSpeech = os.path.join(self._dirRoot, 'Speech')  # 美音
        # 判断是否存在美音库
        if not os.path.exists('Speech'):
            # 不存在，就创建
            os.makedirs('Speech')

    def down(self, word: str, file_path: str = None):
        """
        下载单词的MP3
        判断语音库中是否有对应的MP3
        如果没有就下载
        """
        try:
            word = word.lower()  # 小写
        except AttributeError:
            raise EOFError("非英文", word)
        tmp = self._getWordMp3FilePath(word)
        temp_list = []
        for i in [0, 1]:
            if file_path is None:
                self._filePath = os.path.join(self._dirSpeech, word + str(i) + '.mp3')
            else:
                self._filePath = os.path.join(file_path, word + str(i) + '.mp3')
            if tmp is None:
                self._getURL(i)  # 组合URL
                # 调用下载程序，下载到目标文件夹
                # print('不存在 %s.mp3 文件\n将URL:\n' % word, self._url, '\n下载到:\n', self._filePath)
                # 下载到目标地址
                urllib.request.urlretrieve(self._url, filename=self._filePath)
                print(f'{self._filePath}.mp3 下载完成')
            else:
                print(f'已经存在{self._filePath}mp3, 不需要下载')
            temp_list.append(copy.copy(self._filePath))

        # 返回声音文件路径
        return temp_list

    def _getURL(self, _type: int = 0):
        """
        私有函数，生成发音的目标URL
        https://dict.youdao.com/dictvoice?type=0&audio=
        """
        # noinspection HttpUrlsUsage
        self._url = r'http://dict.youdao.com/dictvoice?type=' + str(
            _type) + r'&audio=' + self._word

    def _getWordMp3FilePath(self, word: str):
        """
        获取单词的MP3本地文件路径
        如果有MP3文件，返回路径(绝对路径)
        如果没有，返回None
        """
        word = word.lower()  # 小写
        self._word = word
        self._fileName = self._word + '0.mp3'
        self._filePath = os.path.join(self._dirSpeech, self._fileName)

        # 判断是否存在这个MP3文件
        if os.path.exists(self._filePath):
            # 存在这个mp3
            return self._filePath
        else:
            # 不存在这个MP3，返回none
            return None

    @staticmethod
    def clear_all_files(file_path: str):
        """
        清除所有下载好的MP3音频
        """
        # 遍历美音库和英音库

        # dir_path = os.path.join(self._dirRoot, "Speech")
        if os.path.exists(file_path):
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    if file.endswith('.mp3'):
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                        print(f"已删除文件: {file_path}")


class MemorizeWord:
    def __init__(self):
        self.sp = youdao()

    def download(self, words: list[str], file_path: str = None):
        for word in words:
            self.sp.down(word, file_path)
        print(f"位于{file_path}所有音频下载完成")

    def sing(self, word: str, file_path: str = None):
        def sing_func(_word: str, _file_path: os.path = None):
            for _file_path in self.sp.down(_word, _file_path):
                if os.path.exists(_file_path):
                    try:
                        playsound(_file_path)
                    except PlaysoundException:
                        print(f"{_file_path}未能正常打开")
                else:
                    print(f"文件 {_file_path} 不存在")

        try:
            thread = threading.Thread(target=sing_func, args=(word, file_path,))

        except UnicodeEncodeError:
            print(f"{word}未能朗读")
            return
        # 启动线程
        thread.start()

    def clear(self, file_path: str):
        self.sp.clear_all_files(file_path)


if __name__ == "__main__":
    mw = MemorizeWord()
    print(mw.sing("hello"))
    mw.clear(path.Speech)
