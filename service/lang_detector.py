# from polyglot.detect import Detector
# import nltk

# nltk.download('punkt')
# nltk.download('jieba')

# def set_language(detectors):
#     language1_and_bytes = [detectors[0].name, detectors[0].read_bytes]
#     print("🐍 File: info_analysis/app.py | Line: 62 | undefined ~ language1_and_bytes", language1_and_bytes)
#     language2_and_bytes = [detectors[1].name, detectors[1].read_bytes]
#     print("🐍 File: info_analysis/app.py | Line: 64 | undefined ~ language2_and_bytes", language2_and_bytes)
#     if(language1_and_bytes[1] > language2_and_bytes[1]):
#         if(language1_and_bytes[0] != "Chinese" and language1_and_bytes[0] != "English"):
#             language_setting = 'english'
#         else:
#             language_setting = language1_and_bytes[0].lower()
#     else:
#         if(language2_and_bytes[0] != 'Chinese' and language2_and_bytes[0] != 'English'):
#             language_setting = 'english'
#         else:
#             language_setting = language2_and_bytes[0].lower()
#     return language_setting


import re


def detect_lang(text):
    return 'chinese' if re.search(u'[\u4e00-\u9fff]', text) else 'english'

