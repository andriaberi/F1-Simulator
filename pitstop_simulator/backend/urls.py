from django.urls import path
from .views import *

urlpatterns = [
    path("message", hello, name="message")
]