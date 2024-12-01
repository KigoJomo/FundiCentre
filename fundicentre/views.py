# /fundicentre/views.py
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required

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
    shop_items = [
        {
            "id": 1,
            "name": "Mahogany Coffee Table",
            "description": "A sturdy and stylish coffee table made from mahogany, perfect for Kenyan living rooms.",
            "price": 7500.00,
            "image_url": "https://via.placeholder.com/150"
        },
        {
            "id": 2,
            "name": "Kikuyu Woven Chair",
            "description": "A comfortable and durable chair handwoven by artisans, ideal for any space.",
            "price": 3500.00,
            "image_url": "https://via.placeholder.com/150"
        },
        {
            "id": 3,
            "name": "Swahili-Style Sofa Set",
            "description": "A beautifully crafted sofa set with intricate Swahili designs, offering both comfort and elegance.",
            "price": 25000.00,
            "image_url": "https://via.placeholder.com/150"
        },
        {
            "id": 4,
            "name": "4-Drawer Wardrobe",
            "description": "A spacious wardrobe with 4 drawers, made from durable hardwood to keep your clothes organized.",
            "price": 18000.00,
            "image_url": "https://via.placeholder.com/150"
        },
        {
            "id": 5,
            "name": "Dining Table with 6 Chairs",
            "description": "A modern dining table set with six chairs, perfect for family meals and gatherings.",
            "price": 32000.00,
            "image_url": "https://via.placeholder.com/150"
        },
    ]

    context = {
       'shop_items': shop_items
    } 
    return render(request, 'shop.html', context)

# Cart page view
@login_required(login_url='login')
def cart(request):
    return render(request, 'cart.html')

# Profile page view
@login_required(login_url='login')
def profile(request):
    return render(request, 'profile.html')