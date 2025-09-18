from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from .models import User,UserAddress
from django.contrib.auth.decorators import login_required


def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name','')
        phone = request.POST.get('phone','')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect('signup')
        else:
            User.objects.create_user(email=email, password=password, name=name, phone=phone)
            messages.success(request, "Account created. Please log in.")
            return redirect('/profile/login/')
    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('/')
        messages.error(request, "Invalid credentials")
        return redirect('/accounts/login/')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

class ResetPasswordView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.txt'
    success_url = reverse_lazy('password_reset_done')

class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('login')

@login_required
def add_address(request):
    if request.method == "POST":
        address_line = request.POST.get("address_line")
        city = request.POST.get("city","")
        state = request.POST.get("state","")
        postal_code = request.POST.get("postal_code","")
        country = request.POST.get("country", "India")

        if address_line:
            UserAddress.objects.create(
                user=request.user,
                address_line=address_line,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
            )
            messages.success(request, f"Address added successfully!")

            
        else:
            messages.error(request, "Please add address")

    return render(request, "accounts/add_address.html") 

@login_required
def profile(request):
    return render(request, "accounts/profile.html")

@login_required
def address_list(request):
    addresses = UserAddress.objects.filter(user=request.user)
    return render(request, "accounts/address_list.html", {"addresses": addresses})
@login_required
def edit_address(request, id):
    address = get_object_or_404(UserAddress, id=id, user=request.user)
    
    if request.method == "POST":
        address.address_line = request.POST.get("address_line")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.postal_code = request.POST.get("postal_code")
        address.country = request.POST.get("country")
        address.save()
        return redirect("address_list")  # go back to address list page
    
    return render(request, "accounts/add_address.html", {"address": address})

