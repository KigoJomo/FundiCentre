# /market/views.py
import requests, json
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Product, ProductImage, Cart, CartItem, Order

from .credentials import MpesaAccessToken, LipanaMpesaPpassword

def register(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('home')
  else:
    form = CustomUserCreationForm()
  
  return render(request, 'auth/register.html', {'form': form})

class CustomLoginView(LoginView):
  authentication_form = CustomAuthenticationForm
  template_name = 'auth/login.html'


# Home page view
def home(request):
    return render(request, 'index.html')

# Shop page view
def shop(request):
    shop_items = Product.objects.all()
    
    context = {
       'shop_items': shop_items
    } 
    return render(request, 'shop.html', context)

# Cart page view
@login_required(login_url='login')
def cart(request):
  cart, created = Cart.objects.get_or_create(user=request.user)
  return render(request, 'cart.html', {'cart': cart})

# Profile page view
@login_required(login_url='login')
def profile(request):
  user_listings = Product.objects.filter(artisan=request.user)
  orders = Order.objects.filter(user=request.user).order_by('-created_at')
  context = {
    'user_listings': user_listings,
    'orders': orders
  }
  return render(request, 'profile.html', context)

@login_required(login_url='login')
def upload_product(request):
  if request.method == 'POST':
    name = request.POST.get('name')
    description = request.POST.get('description')
    price = request.POST.get('price')
    images = request.FILES.getlist('images')
    
    # print(f"Name: {name}")
    # print(f"Description: {description}")
    # print(f"Price: {price}")
    # print(f"Images: {images}")
    
    product = Product.objects.create(
      name=name,
      description=description,
      price=price,
      artisan=request.user
    )
    
    for image in images:
      ProductImage.objects.create(
        product=product,
        image=image
      )
      # print(f"Image: {image}")
    
    return redirect('/profile')
  
  return JsonResponse({'error': 'Invalid request method.'}, status=400)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'product_detail.html', {'product': product})

@login_required(login_url='login')
def add_to_cart(request, product_id):
  product = get_object_or_404(Product, id=product_id)
  cart, created = Cart.objects.get_or_create(user=request.user)
  
  cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
  if not created:
    cart_item.quantity += 1
    cart_item.save()
  
  messages.success(request, f"{product.name} was added to your cart.")
  return redirect('product_detail', slug=product.slug)

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')
  
def update_cart_quantity(request, item_id):
    """Update the quantity of a cart item (increase or decrease)."""
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        action = request.POST.get('action')  # "increase" or "decrease"
        
        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()  # Delete the item from the cart
                messages.info(request, f'{cart_item.product.name} was removed from your cart.')

        else:
            messages.error(request, 'Invalid action.')
        
        cart_item.save()
        return redirect('cart')  # Redirect back to the cart page
    
    return redirect('cart')

# Mpesa API views
def token(request):
    consumer_key = 'dNHxL2pRaRGEv7XmyQ3Usi19k2Kg9R8vzAnU5ejoDA6e5xdH'
    consumer_secret = 'ed4dtU0AY0gkCKkcOAuu5PagOT5gwvSnXfkGhtT06RVHTJ6fuMouBocGzh283TWD'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

# def pay(request):
#    return render(request, 'pay.html')



def stk(request):
    if request.method =="POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "FundiCentre",
            "TransactionDesc": "Purchase"
        }
        response = requests.post(api_url, json=request, headers=headers)
        return HttpResponse("Success")