import json
import redis
import time

from django.views      import View
from django.http       import JsonResponse
from django.core.cache import cache
from django.db.models  import Q, F, Value, Case, When, IntegerField, JSONField

from elasticsearch     import Elasticsearch, helpers

from .models           import Category, SubCategory, Product, ProductDeliveryType, ProductTag, ProductSeries
from .convert          import korean_to_englished_string


class CategoryView(View):
    def get(self, request):
        return JsonResponse(
            {'category': list(Category.objects.values())},
            status = 200
        )


class SubCategoryView(View):
    def get(self, request, id):
        return JsonResponse(
            {'sub_caegory': list(SubCategory.objects.filter(
                category__id = id).values())},
            status = 200
        )


class ProductsListView(View):
    def post(self, request):
        data = json.loads(request.body)
        sub_category_id = data.get('sub_category_id', None)
        sort_by_category = data.get('sort_by_category', '컬리추천')
        sort_by_delivery = data.get('sort_by_delivery', '샛별지역상품')
        sort_by_filter = data.get('sort_by_filter', '신상품순')

        # products = cache.get('products')

        products = Product.objects.prefetch_related('discout', 'tag', 'delivery_type').values(
            'id', 'name', 'image', 'discount__image', 'price', 'discount__percentage',
            'tag__name', 'delivery_type__name', 'is_recommended', 'is_new'
        ).annotate(
            tag_names = Value([], output_field = JSONField()),
            delivery_types = Value([], output_field = JSONField()),
            discount_price = Value(1, output_field = IntegerField())
        )
        for product in products:
            tag_names = [
                tags.tag.name for tags in ProductTag.objects.filter(product_id = product['id']) if tags
            ]
            delivery_types = [ 
                delivery_type.delivery_type.name for delivery_type in ProductDeliveryType.objects.filter(product_id = product['id'])
            ]
            if product['discount__percentage']:
                discount_percentage = 1 - (product['discount__percentage'] / 100)
            else:
                discount_percentage = 1
            product['tag_names'] = tag_names
            product['delivery_types'] = delivery_types
            product['discount_price'] = product['price'] * discount_percentage

        if sub_category_id:
            products = products.filter(sub_category__id = sub_category_id)

        # cache.set('products', products)

        # if sub_category_id

        if sort_by_category == '컬리추천':
            products = products.filter(is_recommended = True)
            
        if sort_by_category == '신상품':
            products = products.filter(is_new = True)
            
        
        # if sort_by_category == '베스트':


        # if sort_by_category == '알뜰쇼핑':
        #     sort_by_filter = '혜택순'
        
        # if sort_by_category == '추천':


        # if sort == '추천순' or sort == 'MD의 추천':

        # if sort == '신상품순' or sort == '신상품':
        
        # if sort == '인기상품순':

        # if sort == '낮은 가격순':

        # if sort == '높은 가격순':

        # if sort == '알뜰 상품' or '알뜰쇼핑'

        # if sort_by_delivery == '샛별지역상품':
        #     products = products.filter('devliery_types__contains' = sort_by_delivery)
        
        # if sort_by_delivery == '택배지역상품':

        return JsonResponse(
            {'products': list(products)},
            status = 200
        )


class ProductDetailView(View):
    def get(self, request, id):
        delivery_types = [ 
            delivery_type.delivery_type.name for delivery_type in ProductDeliveryType.objects.filter(product_id = id)
        ]
        product_series = [
            series for series in ProductSeries.objects.filter(product_id = id).values('name', 'price').annotate(
                product_series_id = F('id')
            )
        ]
        product = Product.objects.filter(id = id).prefetch_related('discount', 'delivery_type', 'productseries').values(
            'id', 'name', 'sub_title', 'price', 'image', 'discount__percentage', 'discount__image', 'unit',
            'weight', 'shipping_type', 'origin', 'allergen', 'expiration_date', 'information', 'description__title',
            'description__content', 'description__image', 'product_image', 'check_point'
        ).annotate(
            product_series = Value(product_series, output_field = JSONField()),
            delivery_types = Value(delivery_types, output_field = JSONField()),
            discount_price = Value(1, output_field = IntegerField())
        ).first()
        if product['discount__percentage']:
            discount_percentage = 1 - (product['discount__percentage'] / 100)
        else:
            discount_percentage = 1

        product['discount_price'] = product['price'] * discount_percentage
        
        for series_price in product['product_series']:
            series_price['price'] = series_price['price'] * discount_percentage

        return JsonResponse(
            {'product': product},
            status = 200
        )


class ProductSearchView(View):
    def get(self, request):
        es = Elasticsearch()
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
        es.indices.delete(index = index)
        print(es.indices.create(index = index, body = body))

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

        time.sleep(3)

        results = es.search(index=index, body={'query': {'match_all': {}}, 'size': 300})

        res = []
        for result in results['hits']['hits']:
            res.append(result['_source']['name'])

        return JsonResponse(
            {'products': res},
            status = 200
        )