import os
from provdbconnector import ProvDb, Neo4jAdapter

NEO4J_USER = 'neo4j'
NEO4J_PASS = os.environ.get('NEO4J_PASSWORD', 'test')
NEO4J_HOST = os.environ.get('NEO4J_HOST', 'localhost')
NEO4J_BOLT_PORT = os.environ.get('NEO4J_BOLT_PORT', '7687')

# Auth info
auth_info = {"user_name": NEO4J_USER,
             "user_password": NEO4J_PASS,
             "host": NEO4J_HOST + ":" + NEO4J_BOLT_PORT
             }

# create the api
prov_api = ProvDb(adapter=Neo4jAdapter, auth_info=auth_info)


def save_document(document):
    print("Saving document")
    document_id = prov_api.save_document(document)
    print("Document Saved!")
    return document_id
