from django.urls import path
from .views import home

app_name = "dashboards"

urlpatterns = [
path('', home, name='home'),
]