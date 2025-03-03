import pickle
import path


class WordDictionary:
    def __init__(self, index_file):
        with open(index_file, 'rb') as f:
            data = pickle.load(f)
            self._word_dict = data["dict_data"]  # 原始字典
            self._index_list = data["index_list"]  # 排序索引列表

    def get_data_by_index(self, index):
        """
        通过数字索引获取数据
        :param index: 数字位置 (0-based)
        :return: (单词, 数据) 或 None
        """
        if 0 <= index < len(self._index_list):
            word = self._index_list[index]
            return word, self._word_dict.get(word)
        return None

    def get_data_by_word(self, word):
        """
        通过单词获取数据 (兼容大小写)
        :return: 数据字典 或 None
        """
        return self._word_dict.get(word.lower())

    def get_index_by_word(self, word):
        """
        获取单词在索引列表中的位置
        :return: (索引位置, 总词数) 或 (-1, 总词数)
        """
        target = word.lower()
        try:
            return self._index_list.index(target), len(self._index_list)
        except ValueError:
            return -1, len(self._index_list)


class WordData:
    def __init__(self, index, _word, meaning):
        self.index = index
        self.word = _word
        self.meaning = meaning
        # 更多词条待使用{"topic_id": "30", "word_level_id": "575", "tag_id": "0", "word": "accidental", "word_audio":
        # "us_accidental_20231102133228215_e8a4997dde5ee8b7310f.mp3", "image_file":
        # "21962eeb926cfb6b231b80b1f44ddb08_141440_1575258179.jpeg", "accent": "/ˌæksɪˈdentl/", "mean_cn":
        # "adj.偶然的，意外的", "mean_en": "happening by chance; not planned", "sentence_phrase": "", "deformation_img":
        # "d_107_30_0_2_20150809000156.png", "sentence": "He suffered an accidental fall because of the banana
        # peel.", "sentence_trans": "他因为踩到香蕉皮而意外摔倒了。", "sentence_audio":
        # "a0afa74d097e27a177587f6e2ef19d1c_42142_1575258177.mp3", "cloze_data": "{\"syllable\":\"ac-ci-den-tal\"",
        # "cloze": "acci-den-t[al]", "options": "[\"el|le|nl|ol\"]", "tips": "[[\"t[al]\"", "word_etyma": ""}


class WordListManager:
    def __init__(self):
        self.pickle = WordDictionary(path.word_index)
        """
        self.index_list = []
        with open(path.word_txt, "r", encoding="utf-8") as f:
            word_list = f.readiness()

        index = 0
        for text_i in word_list:
            data = text_i.replace("\n", "").split("\t")
            self.index_list.append(WordData(index, data[0], data[1]))
            index += 1"""

    def get_data_by_index(self, index: int):
        word, data = self.pickle.get_data_by_index(index)
        return WordData(self.pickle.get_index_by_word(data["word"])[0], word, data["mean_cn"])

    def get_index_by_word(self, word: str):
        """try:
                    temp_index = 0
                    for data in self.index_list:
                        if data.word == word:
                            return temp_index
                        temp_index += 1
                except ValueError:
                    print("word not found：", word)
                    return None"""
        return self.pickle.get_index_by_word(word)[0]


if __name__ == "__main__":
    data_test = WordListManager()
    a = data_test.get_data_by_index(1)
    print(data_test.get_data_by_index(1).word)
    print(data_test.get_index_by_word("man"))
