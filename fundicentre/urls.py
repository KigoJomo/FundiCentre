from django.urls import path
from .views import home, register, CustomLoginView, shop, cart, profile
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('shop/', shop, name='shop'),
    path('cart/', cart, name='cart'),
    path('profile/', profile, name='profile'),
]
