from flask import Flask, render_template, request, jsonify, Blueprint
from werkzeug.utils import secure_filename

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")

# utils
from utils.upload import Check_file_type
check_file_type = Check_file_type()


app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# upload route
def allowed_file(filename):
    # print("🐍 File: search-tutorial/app.py | Line: 95 | allowed_file ~ filename.rsplit('.', 1)[[1]].lower()",filename.rsplit('.', 1)[1])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # 1st determine whether its file extension
        fileExt = filename.rsplit('.', 1)[1].lower()
        print("🐍 File: search-tutorial/app.py | Line: 109 | upload_file ~ fileExt",fileExt)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'] + f"/{fileExt}/", filename)
        print("🐍 File: search-tutorial/app.py | Line: 163 | upload_file ~ file_path",file_path)
        file.save(file_path)

        
        is_pdf = check_file_type.is_pdf(file_path)
        if(is_pdf):
            with pdfplumber.open(SAMPLE_DATA_PATH) as pdf:
                text_content = ""
                for page in pdf.pages:
                    text_content += page.extract_text()

            words = text_content.split()  # Split text into individual words
            word_frequency = Counter(words)

            # import en_core_web_sm
            nlp = spacy.load('en_core_web_sm')

            # nlp = en_core_web_sm.load()
            max_similarity = 0
            for word in words:
                doc = nlp(word)
                searchWord = nlp("sed")
                similarity = searchWord.similarity(doc)
                if similarity > max_similarity:
                    max_similarity = similarity
                    print("🐍 File: python/app.py | Line: 31 | undefined ~ similarity",similarity, word)


        # 2nd Once saved, extract info and analyze it
            # 2.1 infoExtract(file_path)
            # 2.2 analyze
        
        ## pipeline, ingest,





# transform the string before indexing,

# or tokenize things before indexing.



# embedding



# hard to understand.



        # 3rd es pipeline and ingest (vector)

        # 4nd es index

        return jsonify({"response": "File uploaded successfully and extracting info and analyzing it."})
    else:
        return jsonify({"error": "Invalid file type"})
