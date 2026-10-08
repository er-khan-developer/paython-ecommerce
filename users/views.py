from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from products.models import Category, Product
from .forms import CustomSignupForm, LoginForm
import pyotp
from django.contrib.auth.models import User
from io import BytesIO
import base64
import qrcode
from .models import UserProfile
from carts.utils import merge_guest_cart



def home(request):
    categories = Category.objects.filter(parent__isnull=True).order_by('name')
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'categories': categories,
        'products': page_obj,
        'page_obj': page_obj,
    })


def product_filter(request):
    category_id = request.GET.get('category_id')
    subcategory_id = request.GET.get('subcategory_id')
    category = None
    selected_subcategory = None

    if category_id:
        category = Category.objects.filter(pk=category_id).first()

    if subcategory_id:
        selected_subcategory = Category.objects.filter(pk=subcategory_id).first()
        if selected_subcategory and selected_subcategory.parent:
            category = selected_subcategory.parent

    if subcategory_id and selected_subcategory:
        products = Product.objects.filter(
            category=selected_subcategory,
            is_available=True,
        ).order_by('-created_at')
    elif category:
        products = Product.objects.filter(
            Q(category=category) | Q(category__parent=category),
            is_available=True,
        ).order_by('-created_at')
    else:
        products = Product.objects.filter(is_available=True).order_by('-created_at')

    subcategories = []
    if category:
        subcategories = list(category.subcategories.values('id', 'name'))

    return JsonResponse({
        'category_label': category.name if category else 'All Categories',
        'subcategories': subcategories,
        'products_count': products.count(),
        'products_html': render_to_string(
            'products/_product_list.html',
            {'products': products},
        ),
    })


def signup(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            has_guest_cart = merge_guest_cart(request, user)
            return redirect('cart' if has_guest_cart else 'home')
    else:
        form = CustomSignupForm()

    return render(request, 'signup.html', {'form': form})


# 1. LOGIN VIEW (Email + Pass check karke 2FA par rokna)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)

            if user is not None:
                # User ki profile fetch ya create karein
                profile, created = UserProfile.objects.get_or_create(user=user)

                # Agar user ne 2FA enable kiya hua hai
                if profile.is_2fa_enabled:
                    request.session['pre_2fa_user_id'] = user.id
                    return redirect('verify_2fa')
                else:
                    user.backend = 'users.backends.EmailAuthBackend'
                    login(request, user)
                    has_guest_cart = merge_guest_cart(request, user)
                    return redirect('cart' if has_guest_cart else 'home')
            else:
                messages.error(request, 'Galat Email ya Password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def verify_2fa(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        otp = request.POST.get('otp')
        user = User.objects.get(id=user_id)
        totp = pyotp.TOTP(user.profile.totp_secret)

        if totp.verify(otp):
            # Apne custom backend ka sahi path yahan dein
            user.backend = 'users.login.EmailAuthenticate' # Agar aapka backend kisi aur naam se hai toh wo dein
            
            # User ko login karwayein
            login(request, user)
            has_guest_cart = merge_guest_cart(request, user)
            
            # Session se temporary ID hataeIN
            if 'pre_2fa_user_id' in request.session:
                del request.session['pre_2fa_user_id']
            
            # Session ko force save karein taaki logout/login ka confusion na ho
            request.session.modified = True
            
            return redirect('cart' if has_guest_cart else 'home')
        else:
            messages.error(request, 'Galat OTP! Kripya dubara try karein.')

    return render(request, 'verify_2fa.html')

# 3. SETUP 2FA & QR CODE VIEW
@login_required(login_url='login')
def setup_2fa(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        otp = request.POST.get('otp')
        totp = pyotp.TOTP(profile.totp_secret)

        if totp.verify(otp):
            profile.is_2fa_enabled = True
            profile.save()
            messages.success(request, '2FA successfully enable ho gaya hai!')
            return redirect('home')
        else:
            messages.error(request, 'Galat OTP! QR code scan karke sahi code daalein.')

    # QR Code Generate karne ka logic
    totp = pyotp.TOTP(profile.totp_secret)
    qr_uri = totp.provisioning_uri(name=request.user.email, issuer_name="Dada Pote Ki Kirana")

    img = qrcode.make(qr_uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return render(request, 'setup_2fa.html', {
        'qr_code': qr_base64,
        'secret_key': profile.totp_secret
    })