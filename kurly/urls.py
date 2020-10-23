from django.urls import include, path

urlpatterns = [
    path('user', include('user.urls')),
    path('products', include('products.urls')),
    path('review', include('review.urls'))
]
