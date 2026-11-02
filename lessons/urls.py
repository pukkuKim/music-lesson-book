from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "api/assignments/<int:pk>/check/",
        views.check_assignment,
        name="check_assignment",
    ),
]
