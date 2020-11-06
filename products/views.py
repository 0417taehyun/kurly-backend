import json
import redis
import random, time

from django.views      import View
from django.http       import JsonResponse
from django.core.cache import cache
from django.db.models  import F, Count, Value, IntegerField, JSONField

from elasticsearch     import Elasticsearch, helpers

from .models           import Category, SubCategory, Product, ProductDeliveryType, ProductTag, ProductSeries
from .documents        import get_instance, get_query, insertion
from review.models     import Review


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
        category_id = data.get('category_id', None)
        sub_category_id = data.get('sub_category_id', None)
        sort_by_category = data.get('sort_by_category', '컬리추천')
        sort_by_sub_category = data.get('sort_by_sub_category', None)
        sort_by_delivery = data.get('sort_by_delivery', '샛별지역상품')
        sort_by_filter = data.get('sort_by_filter', None)
        products = cache.get('products')

        if not products:
            products = Product.objects.prefetch_related('discount', 'tag', 'delivery_type', 'review_set').values(
                'id', 'name', 'image', 'discount__image', 'price', 'discount__percentage', 'is_recommended', 'is_new'
            ).annotate(
                tag_names = Value([], output_field = JSONField()),
                delivery_types = Value([], output_field = JSONField()),
                discount_price = Value(1, output_field = IntegerField())
            )
    
        cache.set('products', products)

        if sub_category_id:
            sub_category_name = SubCategory.objects.get(id = sub_category_id)
            if sub_category_name == '전체보기':
                category_id = Category.objects.get(subcategory__id = sub_category_id).id
                products = products.filter(sub_category_category__id = category_id)
            else:    
                products = products.filter(sub_category__id = sub_category_id)

        if sort_by_sub_category == 'MD의 추천':
            products = products.filter(is_recommended = True, sub_category__category_id = category_id)

        if sort_by_sub_category == "알뜰 상품":
            products = products.exclude(discount__percentage = None)

        if sort_by_sub_category == 'MD의 추천':
            products = products.filter(is_recommended = True)

        if sort_by_sub_category == "오늘의 신상품":
            products = products.filter(is_new = True)

        if sort_by_sub_category == "지금 가장 핫한 상품":
            products = products.exclude(review__id = None)

        if sort_by_category == '신상품':
            sort_by_filter == "신상품순"

        if sort_by_category == "알뜰쇼핑":
            products = products.exclude(discount__percentage = None)

        if sort_by_category == "베스트":
            products = products.exclude(review__id = None)

        if sort_by_category != "컬리추천":
            if sort_by_filter == "혜택순":
                products = products.all().order_by('-discount__percentage')

            if sort_by_filter == "신상품순":
                products = products.filter(is_new = True)

            if sort_by_filter == "인기상품순":
                products = products.all().annotate(count = Count('review__product_id')).order_by('-count')

            if sort_by_filter == "낮은 가격순":
                products = products.all().order_by('price')

            if sort_by_filter == "높은 가격순":
                products = products.all().order_by('-price')

            if sort_by_filter == "추천순":
                products = products.order_by('-is_recommended')
        
            products = products.filter(delivery_type__name__contains = sort_by_delivery[:2])
            
        tags = ProductTag.objects.values('product_id', 'tag__name')
        delivery_types = ProductDeliveryType.objects.values('product_id', 'delivery_type__name')
        for product in products:
            tag_names = []
            for tag in tags:
                if tag['product_id'] == product['id']:
                    tag_names.append(tag['tag__name'])
            product['tag_names'] = tag_names

            delivery_type_names = []
            for delivery_type in delivery_types:
                if delivery_type['product_id'] == product['id']:
                    delivery_type_names.append(delivery_type['delivery_type__name'])
            product['delivery_types'] = delivery_type_names

            if product['discount__percentage']:
                discount_percentage = 1 - (product['discount__percentage'] / 100)
            else:
                discount_percentage = 1
            product['discount_price'] = int(product['price'] * discount_percentage)

        if sort_by_sub_category == "이 상품 어때요?":
            products = random.choices(products, k=8)

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

        product['discount_price'] = int(product['price'] * discount_percentage)
        
        for series_price in product['product_series']:
            series_price['price'] = int(series_price['price'] * discount_percentage)

        return JsonResponse(
            {'product': product},
            status = 200
        )


class ProductSearchView(View):
    def post(self, request):
        insertion()
        time.sleep(3)
        data = json.loads(request.body)
        keyword = data['keyword']

        es = get_instance()
        results = es.search(index='products', body=get_query(keyword))

        products = []
        for result in results['hits']['hits']:
            product = {
                'id': result['_id'],
                'name': result['_source']['name']
            }
            products.append(product)
        return JsonResponse(
            {'products': products},
            status = 200
        )