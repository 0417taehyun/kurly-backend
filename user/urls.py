from django.urls import path

from .views import (
    SignUpView,
    SignInView,
    GoogleSignInView
)

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/googlesignin', GoogleSignInView.as_view()),
]
