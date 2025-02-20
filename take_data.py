import path


class WordData:
    def __init__(self, index, _word, meaning):
        self.index = index
        self.word = _word
        self.meaning = meaning


class WordList:
    def __init__(self):
        self.index_list = []

        with open(path.word_txt, "r", encoding="utf-8") as f:
            word_list = f.readlines()

        index = 0
        for text_i in word_list:
            data = text_i.replace("\n", "").split("\t")
            self.index_list.append(WordData(index, data[0], data[1]))
            index += 1

    def get_data(self, index):
        return self.index_list[index]
