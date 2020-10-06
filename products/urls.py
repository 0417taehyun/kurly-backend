from django.urls    import path

from products.views import CategoryView, SubCategoryView, ProductsListView, ProductDetailView ,ProductSearchView

urlpatterns = [
    path('/category', CategoryView.as_view()),
    path('/category/<int:id>', SubCategoryView.as_view()),
    path('/', ProductsListView.as_view()),
    path('/<int:id>', ProductDetailView.as_view()),
    path('/search', ProductSearchView.as_view()),
]