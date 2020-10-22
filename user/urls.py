from django.urls import path

from .views import (
    SignUpView,
    SignInView,
    CartView,
    GoogleSignInView
)

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/cart', CartView.as_view()),
    path('/googlesignin', GoogleSignInView.as_view()),
]
