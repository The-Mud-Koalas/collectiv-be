from django.urls import path
from .views import serve_get_user_data, serve_update_user_data


urlpatterns = [
    path('data/', serve_get_user_data),
    path('update/', serve_update_user_data),
]
