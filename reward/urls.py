from .views import serve_redeem_reward
from django.urls import path


urlpatterns = [
    path('redeem/', serve_redeem_reward),
]

