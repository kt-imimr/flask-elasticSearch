from flask import Flask, render_template, request, jsonify, Blueprint
from werkzeug.utils import secure_filename

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")

# utils
from utils.check_file_type import Check_file_type
check_file_type = Check_file_type()


app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

# upload route
def allowed_file(filename):
    print("🐍 File: search-tutorial/app.py | Line: 95 | allowed_file ~ filename.rsplit('.', 1)[[1]].lower()",filename.rsplit('.', 1)[1])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    print("🐍 File: routes/upload.py | Line: 30 | upload_file ~ request.files",request.files)
    if 'file' not in request.files:
        return jsonify({"error": "No file"})
    file = request.files['file']
    print(f"🐍 file content_length: {file.content_length}\n, content_type: {file.content_type}\n, filename: {file.filename}\n, headers: {file.headers}\n, mimetype: {file.mimetype}\n, mimetype_params: {file.mimetype_params}\n, name: {file.name}\n, save: {file.save}\n, stream: {file.stream}" )
    print(f"🐍 file.stream: ", dir(file.stream))
    print(f"🐍 file.stream: ", type(file.stream.readlines()))
    head_bytes = file.stream.readlines()[1]
    is_pdf = 'PDF' in head_bytes
    
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
        # is_pdf = check_file_type.is_pdf(file_path)

        


        return jsonify({"response": "File uploaded successfully and extracted info and indexed into elasticsearch."})
    else:
        return jsonify({"error": "Invalid file type"})
