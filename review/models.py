from django.db import models

class Review(models.Model):
    product         = models.ForeignKey('products.Product', on_delete = models.CASCADE)
    user            = models.ForeignKey('user.User', on_delete = models.CASCADE)
    product_name    = models.CharField(max_length = 32)
    title           = models.CharField(max_length = 32)
    comment         = models.TextField()
    review_image    = models.URLField(max_length = 1024, null = True)
    created_at      = models.DateTimeField(auto_now_add = True)
    updated_at      = models.DateTimeField(auto_now = True)
    
    class Meta:
        db_table    = 'reviews'
