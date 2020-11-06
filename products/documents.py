from elasticsearch     import Elasticsearch, helpers, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from .models           import Product
from .convert          import korean_to_englished_string, word_to_mapping
from kurly.settings    import ELASTICSEARCH

es_instance = None

def get_instance():
    global es_instance
    if es_instance:
        return es_instance
    auth = AWS4Auth(
        ELASTICSEARCH['AWS_ACCESS_KEY'],
        ELASTICSEARCH['AWS_SECRET_KEY'],
        ELASTICSEARCH['ES_REGION'],
        ELASTICSEARCH['SERVICE']
    )
    es_instance = Elasticsearch(
        hosts = [ELASTICSEARCH['ES_HOST']],
        http_auth = auth,
        user_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection,
        port = ELASTICSEARCH['ES_PORT']
    )
    return es_instance


def insertion():
    es = get_instance()
    index = 'products'
    body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "max_ngram_diff": 55
            },
            "analysis": {
                "analyzer": {
                    "name_analyzer": {
                        "type": "custom",
                        "tokenizer": "ngram_tokenizer"
                    }
                },
                "tokenizer": {
                    "ngram_tokenizer": {
                        "type": "ngram",
                        "min_gram": 1,
                        "max_gram": 50,
                        "token_chars": [
                            "letter"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "name": {
                    "type": "text",
                    "analyzer": "name_analyzer",
                    "search_analyzer": "name_analyzer"
                },
                "converted_name": {
                    "type": "text",
                    "analyzer": "name_analyzer",
                    "search_analyzer": "name_analyzer",
                }
            }
        }
    }
    es.indices.create(index = index, body = body)

    products = Product.objects.values('name')
    actions = [
        {
            "_index": index,
            "_id": idx + 1,
            "_source": {
                "name": product['name'],
                "converted_name": korean_to_englished_string(product['name'])
            }
        }
        for idx, product in enumerate(products)
    ]

    helpers.bulk(es, actions=actions, index=index)


def get_query(name):
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "name": name
                        }
                    },
                    {
                        "match": {
                            "converted_name": korean_to_englished_string(name)
                        }
                    },
                    {
                        "match": {
                            "converted_name": word_to_mapping(name)
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }
    return query