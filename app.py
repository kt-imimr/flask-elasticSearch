import re
from flask import Flask, render_template, request, jsonify
from search import Search


import datetime


# api routes
from routes.upload import upload_bp

app = Flask(__name__)
app.register_blueprint(upload_bp, url_prefix='/api')



es = Search()


@app.get('/')
def index():
    return render_template('index.html')

@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    filters, parsed_query = extract_filters(query)
    print("🐍 File: search-tutorial/app.py | Line: 28 | handle_search ~ parsed_query",parsed_query)
    print("🐍 File: search-tutorial/app.py | Line: 28 | handle_search ~ filters",filters)
    from_ = request.form.get('from_', type=int, default=0)

    if parsed_query:
        search_query = {
            # 'must': {
            #     'multi_match': {
            #         'query': parsed_query,
            #         'fields': ['filename', 'summary', 'content'],
            #         # can configure search analyzer here, e.g. 'analyzer': 'stop'
            #     }
            # }
            'should': [
                {
                    'match': {
                        'content':{
                            'query': parsed_query
                        }
                    }
                },
                {
                    'match': {
                        'content':{
                            'query': parsed_query,
                            'operator': 'and'
                        }
                    }
                },
                {
                    'match_phrase': {
                        'content':{
                            'query': parsed_query,
                            'boost': 2
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
        # query={
        #     'bool': {
        #         **search_query,
        #         **filters
        #     }
        # },
        query={
            'bool': {
                **search_query,
            }
        },
        size=10,
        from_=from_
    )

    results_vector_search = es.search(
        knn={
            'field': 'embedding',
            'query_vector': es.get_embedding(parsed_query),
            'k': 10,
            'num_candidates': 10,
            **filters,
        },
    )


    return render_template('index.html', 
                           results_text_search=results_text_search['hits']['hits'],  # text-search
                           results_vector_search=results_vector_search['hits']['hits'], # vector-search
                           query=query, from_=from_,
                           total=results_text_search['hits']['total']['value']) # total_page

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


