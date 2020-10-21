from django.db import models
from products.models import Product, ProductSeries

class User(models.Model):
    account       = models.CharField(max_length = 32)
    password      = models.CharField(max_length = 64, null = True)
    name          = models.CharField(max_length = 32, null = True)
    email         = models.EmailField(max_length = 64)
    phone_number  = models.CharField(max_length = 32, null = True)
    address       = models.CharField(max_length = 128, null = True)
    gender        = models.CharField(max_length = 32, null = True)
    birth         = models.CharField(max_length = 32, null = True)
    google_id     = models.CharField(max_length = 32, null = True)
    cart_list     = models.ManyToManyField('products.Product', through = 'CartList')
    
    class Meta:
        db_table = 'users'

class CartList(models.Model):
    product        = models.ForeignKey('products.Product', on_delete = models.CASCADE)
    user           = models.ForeignKey('User', on_delete = models.CASCADE)
    series         = models.ForeignKey('products.ProductSeries', on_delete = models.CASCADE)
    count          = models.IntegerField()

    class Meta:
        db_table = 'carts'