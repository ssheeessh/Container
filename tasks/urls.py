from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.index, name="index"),
    path("check/", views.check_access, name="check_access"),
    path("logs/", views.logs_view, name="logs"),
]