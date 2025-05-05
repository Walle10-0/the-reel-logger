'''
This file contains all the urls for the account pages
It maps the URL to a function (or class) in views.py.
Each page is given a name for dynamic references (so I can change the link here without issue).
'''
from django.urls import path

from .views import SignUpView


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
]