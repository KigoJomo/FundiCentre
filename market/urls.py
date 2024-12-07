from django.urls import path
from .views import home, register, CustomLoginView, shop, cart, profile, upload_product, product_detail, add_to_cart, remove_from_cart, update_cart_quantity, stk, token
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('shop/', shop, name='shop'),
    path('cart/', cart, name='cart'),
    path('profile/', profile, name='profile'),
    path('upload-product/', upload_product, name='upload_product'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart_quantity, name='update_cart_quantity'),
    
    # Mpesa API urls
    # path('pay/', pay, name='pay'),
    path('stk/', stk, name='stk'),
    path('token/', token, name='token'),
]