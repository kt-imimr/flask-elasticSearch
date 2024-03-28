import json
from pprint import pprint
import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

from sentence_transformers import SentenceTransformer



class Search:
    def __init__(self):
        self.es = Elasticsearch('http://localhost:9200') # it export es when the class is called, because the constructor initiates the class
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)

    def search(self, **query_args):
        return self.es.search(index='demo_index', **query_args)
    
    def retrieve_document(self, id):
        return self.es.get(index='demo_index', id=id)
    
    def create_index(self):
        self.es.indices.delete(index='my_documents', ignore_unavailable=True)

        self.es.indices.create(
            index='my_documents',
            mappings={
                'properties': {
                    'embedding': {
                        'type': 'dense_vector',
                    },
                    'elser_embedding': {
                        'type': 'sparse_vector',
                    },
                }
            },
            settings={
                'index': {
                    'default_pipeline': 'elser-ingest-pipeline'
                }
            }
        )
    
    def delete_index(self):
        self.es.indices.delete(index='my_documents', ignore_unavailable=True)

    def get_embedding(self, text):
        return self.model.encode(text)

    def insert_document(self, document):
        return self.es.index(index='my_documents', document={
            **document,
            'embedding': self.get_embedding(document['summary'])
        })
    
    def insert_documents(self, documents):
        operations = []
        # self.process_pipeline('data_pipeline')
        for document in documents:
            operations.append({'index': {'_index': 'my_documents' }})
            # operations.append({'index': {'_index': 'my_documents', "pipeline": "data_pipeline" }})
            operations.append({
            **document,
            'embedding': self.get_embedding(document['summary'])
            })
        return self.es.bulk(operations=operations)

    def reindex(self):
        self.create_index()

        # open the file, and then ingest the documents
        # Use the ingest pipeline to transform and tokenize your data before indexing it into Elasticsearch. 
        # For example, if you have a list of documents, you can index them as follows:
        with open('data.json', 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents)
        # the documents here are basically going to be ingested without pipeline

    # not using pipeline
    def process_pipeline(self, pipeline_name):
        pipeline_settings = {
            "description": "Data transformation and tokenization pipeline",
            "processors": [
                {
                    "attachment": {
                        "field": "content",
                        "target_field": "text"
                    }
                },
                {
                    "lowercase": {
                        "field": "text"
                    }
                },
                {
                    # "tokenizer": {
                    #     "type": "standard",
                    #     "field": "text"
                    # }
                    "split": {
                        "field": "text",
                        "separator": " "
                    }
                }
            ]
        }

        self.es.ingest.put_pipeline(id=pipeline_name, body=pipeline_settings)
        return True

    def deploy_elser(self):
        # download ELSER v2
        self.es.ml.put_trained_model(model_id='.elser_model_2',
                                     input={'field_names': ['text_field']})
        
        # wait until ready
        while True:
            status = self.es.ml.get_trained_models(model_id='.elser_model_2',
                                                   include='definition_status')
            if status['trained_model_configs'][0]['fully_defined']:
                # model is ready
                break
            time.sleep(1)

        # deploy the model
        self.es.ml.start_trained_model_deployment(model_id='.elser_model_2')

        # define a pipeline
        self.es.ingest.put_pipeline(
            id='elser-ingest-pipeline',
            processors=[
                {
                    'inference': {
                        'model_id': '.elser_model_2',
                        'input_output': [
                            {
                                'input_field': 'summary',
                                'output_field': 'elser_embedding',
                            }
                        ]
                    }
                }
            ]
        )

