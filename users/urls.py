from django.urls import path
from .views import serve_update_user_data


urlpatterns = [
    path('update/', serve_update_user_data),
]
