from flask import Flask, render_template, request, jsonify, Blueprint
from werkzeug.utils import secure_filename

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/..")

# utils
from utils.check_file_type import Check_file_type
check_file_type = Check_file_type()


app = Flask(__name__)

upload_bp = Blueprint('upload', __name__)


# upload route
def allowed_file(file_stream):
    is_pdf = b'PDF' in file_stream
    return is_pdf

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    print("🐍 File: routes/upload.py | Line: 30 | upload_file ~ request.files",request.files)
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    print(f"🐍 file content_length: {file.content_length}\n, content_type: {file.content_type}\n, filename: {file.filename}\n, headers: {file.headers}\n, mimetype: {file.mimetype}\n, mimetype_params: {file.mimetype_params}\n, name: {file.name}\n, save: {file.save}\n, stream: {file.stream}" )
    print(f"🐍 file.stream: ", dir(file.stream))
    print(f"🐍 file: ", dir(file))

    file_stream = file.stream.read()
    
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file_stream):
        filename = secure_filename(file.filename)

        # get the extension, pdf in this case
        fileExt = filename.rsplit('.', 1)[1].lower()
        relative_file_path = os.path.join(f"./uploads/{fileExt}/", filename)
        file.stream.seek(0) # reset the pointer to 0
        file.save(relative_file_path) # save it

        

        


        return jsonify({"response": "File uploaded successfully and extracted info and indexed into elasticsearch."}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400
