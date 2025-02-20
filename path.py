import os
from pathlib import Path

main = Path(__file__).resolve().parent
record_json = os.path.join(main, 'records.json')
text_json = os.path.join(main, 'text.json')

word_txt = os.path.join(main, 'word.txt')
today_data = os.path.join(main, 'today_data')
today_mp3 = os.path.join(today_data, 'today_data_mp3')
yesterday_mp3 = os.path.join(today_data, 'yesterday_data_mp3')
last_run_date = os.path.join(today_data, 'last_run_date.txt')
Speech = os.path.join(main, 'Speech')
