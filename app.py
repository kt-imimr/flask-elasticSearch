import re
from flask import Flask, render_template, request, jsonify
from search import Search

from flask_cors import CORS



# api routes
from routes.upload import upload_bp
from service.lang_detector import detect_lang

app = Flask(__name__)
app.register_blueprint(upload_bp, url_prefix='/api')
CORS(app)




es = Search()


@app.get('/')
def index():
    return render_template('index.html')

@app.post('/')
def handle_search():
    query = request.get_json().get('query')
    print("🐍 File: search-tutorial/app.py | Line: 27 | handle_search ~ query",query)
    lang = detect_lang(query)
    print("🐍 File: search-tutorial/app.py | Line: 29 | handle_search ~ lang",lang)

    filters, parsed_query = extract_filters(query)
    from_ = request.form.get('from_', type=int, default=0)

    if parsed_query:
        search_query = {
            'should': [
                {
                    'match': {
                        'transformed_content':{
                            'query': parsed_query,
                            'analyzer': "smartcn_with_stop" # using different analyzer at the search api for the respective content results in different scoring result. 
                        }
                    }
                },
                {
                    'match': {
                        'transformed_content':{
                            'query': parsed_query,
                            'operator': 'and',
                            'analyzer': "my_analyzer"
                        }
                    }
                },
                {
                    'match_phrase': {
                        'transformed_content':{
                            'query': parsed_query,
                            'boost': 2,
                            'analyzer': "smartcn_with_stop"
                        }
                    }
                }
            ]
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }

    results_text_search = es.search(
        query={
            'bool': {
                **search_query,
            }
        },
        size=10,
        from_=from_
    )

    # results_vector_search = es.search(
    #     knn={
    #         'field': 'embedding',
    #         'query_vector': es.get_embedding(parsed_query),
    #         'k': 10,
    #         'num_candidates': 10,
    #         **filters,
    #     },
    # )

    # return render_template('index.html', 
    #                        results_text_search=results_text_search['hits']['hits'],  # text-search
    #                     #    results_vector_search=results_vector_search['hits']['hits'], # vector-search
    #                        query=query, from_=from_,
    #                        total=results_text_search['hits']['total']['value']) # total_page

    # for react,
    return {
        'results_text_search': results_text_search['hits']['hits'],
        'query': query,
        'from_': from_,
        'total': results_text_search['hits']['total']['value']
    }

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
    title = document['_source']['filename']
    paragraphs = document['_source']['content'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)

@app.post("/crawl")
def handle_web_crawling():
    domain = request.form.get("domain")
    subpath = request.form.get("subpath")
    if 'https://' not in domain or 'http://' not in domain:
        domain = f"https://{domain}"
    return render_template('crawl.html', domain=domain, subpath=subpath)

# ===== API ends here =======================================================================================

@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')

@app.cli.command("deploy_elser")
def deploy_elser():
    """Deploy the ELSER v2 model to Elasticsearch."""
    try:
        es.deploy_elser()
    except Exception as exc:
        print(f'Error: {exc}')
    else:
        print(f'ELSER model deployed.')


