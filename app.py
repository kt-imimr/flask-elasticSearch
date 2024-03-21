import re
from flask import Flask, render_template, request, jsonify
from search import Search

from werkzeug.utils import secure_filename
import os

import datetime

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

es = Search()

@app.get('/')
def index():
    return render_template('index.html')

@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)

    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['name', 'summary', 'content'],
                }
            }
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }

    results = es.search(
        query={
            'bool': {
                **search_query,
                **filters
            }
        },
        aggs={
            'category-agg': {
                'terms': {
                    'field': 'category.keyword',
                }
            },
            'year-agg': {
                'date_histogram': {
                    'field': 'updated_at',
                    'calendar_interval': 'year',
                    'format': 'yyyy',
                },
            },
        },
        size=5,
        from_=from_
    )
    aggs = {
        'Category': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['category-agg']['buckets']
        },
        'Year': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['year-agg']['buckets']
            if bucket['doc_count'] > 0
        },
    }

    keys_aggs_year = list(aggs["Year"].keys())
    len_aggs_year = len(keys_aggs_year)
    if len_aggs_year > 0:
        for key in keys_aggs_year:
            my_datetime = datetime.datetime.fromtimestamp(key / 1000)
            my_year = my_datetime.strftime("%Y")
            aggs["Year"][my_year] = aggs["Year"].pop(key)

    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'], aggs=aggs)

def extract_filters(query):
    filters = []

    filter_regex = r'category:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'term': {
                'category.keyword': {
                    'value': m.group(1)
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    filter_regex = r'year:([^\s]+)\s*'
    m = re.search(filter_regex, query)
    if m:
        filters.append({
            'range': {
                'updated_at': {
                    'gte': f'{m.group(1)}||/y',
                    'lte': f'{m.group(1)}||/y',
                }
            },
        })
        query = re.sub(filter_regex, '', query).strip()

    return {'filter': filters}, query


@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['name']
    paragraphs = document['_source']['content'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)



@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')


# upload route
def allowed_file(filename):
    # print("🐍 File: search-tutorial/app.py | Line: 95 | allowed_file ~ filename.rsplit('.', 1)[[1]].lower()",filename.rsplit('.', 1)[1])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
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
        file.save(file_path)

        # 2nd Once saved, extract info and analyze it
            # 2.1 infoExtract(file_path)
            # 2.2 analyze
        

        # 3rd es pipeline and ingest (vector)

        # 4nd es index



        return jsonify({"response": "File uploaded successfully and extracting info and analyzing it."})
    else:
        return jsonify({"error": "Invalid file type"})


if __name__ == '__main__':
    app.run(debug=True)