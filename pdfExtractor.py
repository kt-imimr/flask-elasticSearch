import pdfplumber
from collections import Counter
import spacy
from sklearn.metrics.pairwise import cosine_similarity

with pdfplumber.open('test.pdf') as pdf:
    text_content = ""
    for page in pdf.pages:
        text_content += page.extract_text()
    
words = text_content.split()  # Split text into individual words
word_frequency = Counter(words)

nlp = spacy.load('en_core_web_md')

word1 = nlp('word1')
word2 = nlp('word2')
similarity = word1.similarity(word2)
