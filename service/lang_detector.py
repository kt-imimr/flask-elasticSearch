import re

def detect_lang(text):
    return 'chinese' if re.search(u'[\u4e00-\u9fff]', text) else 'english'

