from django.urls import path
from schema_graph.views import Schema
from . import views
urlpatterns = [
     path('', views.home, name = "home-page"),
     path("schema/", Schema.as_view()),
]