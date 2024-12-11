# /market/views.py
import requests, json
from requests.auth import HTTPBasicAuth
from django.db import transaction
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Product, ProductImage, Cart, CartItem, Order, OrderItem

from .credentials import MpesaAccessToken, LipanaMpesaPpassword


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "auth/register.html", {"form": form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = "auth/login.html"


# Home page view
def home(request):
    featured = Product.objects.order_by('?')[:3]
    latest = Product.objects.order_by('-id')[:6]
    
    context = {
        'featured': featured,
        'latest': latest
    }
    
    return render(request, "index.html", context)


# Shop page view
def shop(request):
    shop_items = Product.objects.all()

    context = {"shop_items": shop_items}
    return render(request, "shop.html", context)


# Cart page view
@login_required(login_url="login")
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart.html", {"cart": cart})


# Profile page view
@login_required(login_url="login")
def profile(request):
    user_listings = Product.objects.filter(artisan=request.user)
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    context = {"user_listings": user_listings, "orders": orders}
    return render(request, "profile.html", context)


@login_required(login_url="login")
def upload_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        images = request.FILES.getlist("images")

        product = Product.objects.create(
            name=name, description=description, price=price, artisan=request.user
        )

        for image in images:
            ProductImage.objects.create(product=product, image=image)
        
        messages.success(request, "Product added succesfully!")

        return redirect("/profile")

    return JsonResponse({"error": "Invalid request method."}, status=400)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "product_detail.html", {"product": product})


def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.artisan != request.user:
        return HttpResponseForbidden("You are not authorized to update this product.")
    
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")

        # Add new images if uploaded
        images = request.FILES.getlist("images")
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("product_detail", slug=product.slug)

    return redirect("product_detail", slug=product.slug)


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if product.artisan != request.user:
        return HttpResponseForbidden("You are not authorized to delete this product.")
    
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('profile')
    
    return HttpResponseForbidden("Invalid request method.")


@login_required(login_url="login")
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} was added to your cart.")
    return redirect('cart')


@login_required(login_url="login")
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


def update_cart_quantity(request, item_id):
    """Update the quantity of a cart item (increase or decrease)."""
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id)

        action = request.POST.get("action")  # "increase" or "decrease"

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()  # Delete the item from the cart
                messages.info(
                    request, f"{cart_item.product.name} was removed from your cart."
                )

        else:
            messages.error(request, "Invalid action.")

        cart_item.save()
        return redirect("cart")  # Redirect back to the cart page

    return redirect("cart")


@login_required(login_url="login")
@transaction.atomic
def create_order(request):
    try:
        cart = Cart.objects.get(user=request.user)
        
        if not cart.cartitem_set.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('cart')
        
        total_amount = cart.get_total()
        
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status='PENDING'
        )
        
        for cart_item in cart.cartitem_set.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        cart.cartitem_set.all().delete()
        
        messages.success(request, f"Order #{order.id} created successfully!")
        
        return redirect('profile')
    
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found!")
        return redirect('cart')
    except Exception as e:
        messages.error(request, f"Error creating order: {str(e)}")
        return redirect('cart')

@login_required(login_url="login")
@transaction.atomic
def buy_now(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        
        order = Order.objects.create(
            user=request.user,
            total_amount=product.price,
            status='PENDING'
        )
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=product.price
        )
        
        messages.success(request, f"Order #{order.id} created!")
        return redirect('profile')
    
    except Exception as e:
        messages.error(request, f"Error creating order: {str(e)}")
        return redirect('product_detail', slug=product.slug)



# Mpesa API views
def token(request):
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, "token.html", {"token": validated_mpesa_access_token})


def stk(request, product_id=None):
    if request.method == "POST":
        phone = request.POST["phone"]
        amount = request.POST["amount"]
        
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        
        request_data = {
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
            "TransactionDesc": "Purchase",
        }
        response = requests.post(api_url, json=request_data, headers=headers)
        
        # if response.status_code == 200:
        #     if product_id:
        #         return buy_now(request, product_id)
        #     else:
        #         return create_order(request)
        # else:
        #     messages.error(request, "Payment Failed!")
        #     return redirect('cart')
    
    if product_id:
        return buy_now(request, product_id)
    else:
        return create_order(request)
    
    # return redirect('cart')
