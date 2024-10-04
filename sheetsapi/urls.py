from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path("event1/", views.Event1.as_view(), name="event1"),
    path("event2/", views.Event2.as_view(), name="event2"),
    path("event3/", views.Event3.as_view(), name="event3"),
]