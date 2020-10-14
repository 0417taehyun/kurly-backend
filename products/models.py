from django.db import models

class Category(models.Model): 
    name = models.CharField(max_length = 64)

    class Meta: 
        db_table = 'categories'

class SubCategory(models.Model): 
    category = models.ForeignKey('Category', on_delete = models.CASCADE)
    name     = models.CharField(max_length = 64)

    class Meta: 
        db_table = 'sub_categories'

class Product(models.Model): 
    sub_category    = models.ForeignKey('SubCategory', on_delete = models.CASCADE)
    name            = models.CharField(max_length = 64)
    sub_title       = models.CharField(max_length = 128, null = True)
    price           = models.PositiveIntegerField()
    image           = models.CharField(max_length =  512)
    unit            = models.CharField(max_length = 64)
    weight          = models.CharField(max_length = 64)
    shipping_type   = models.CharField(max_length = 128)
    delivery_type   = models.ManyToManyField('DeliveryType', through = 'ProductDeliveryType', related_name = 'product_with_delivery_type')
    origin          = models.CharField(max_length = 128, null = True)
    allergen        = models.CharField(max_length = 512, null = True)
    expiration_date = models.CharField(max_length = 128, null = True)
    information     = models.CharField(max_length = 512, null = True)
    description     = models.ForeignKey('Description', on_delete = models.CASCADE)
    product_image   = models.CharField(max_length = 512)
    discount        = models.ForeignKey('Discount', on_delete = models.CASCADE, null = True)
    is_recommended  = models.BooleanField(default = False)
    is_new          = models.BooleanField(default = False)
    check_point     = models.CharField(max_length = 512)
    tag             = models.ManyToManyField('Tag', through = 'ProductTag', related_name = 'product_with_tag')

    class Meta: 
        db_table = 'products'

class Description(models.Model): 
    image   = models.CharField(max_length = 512)
    title   = models.CharField(max_length = 256)
    content = models.CharField(max_length = 1024)

    class Meta: 
        db_table = 'descriptions'

class Discount(models.Model): 
    percentage = models.PositiveIntegerField()
    image      = models.CharField(max_length = 512)

    class Meta: 
        db_table = 'discounts'

class ProductDeliveryType(models.Model): 
    product        = models.ForeignKey('Product', on_delete = models.CASCADE)
    delivery_type  = models.ForeignKey('DeliveryType', on_delete = models.CASCADE)

    class Meta: 
        db_table = 'product_delivery_types'

class DeliveryType(models.Model): 
    name = models.CharField(max_length = 64)

    class Meta: 
        db_table = 'delivery_types'

class ProductSeries(models.Model): 
    name    = models.CharField(max_length = 64)
    price   = models.PositiveIntegerField()
    product = models.ForeignKey('Product', on_delete = models.CASCADE)

    class Meta: 
        db_table = 'product_series'

class ProductTag(models.Model): 
    product = models.ForeignKey('Product', on_delete = models.CASCADE)
    tag     = models.ForeignKey('Tag', on_delete = models.CASCADE)

class Tag(models.Model): 
    name = models.CharField(max_length = 64)