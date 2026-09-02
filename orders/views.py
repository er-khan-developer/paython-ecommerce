from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from django.urls import reverse
import stripe
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.

# Top par Address model bhi import kar lein
from .models import Order, OrderItem, Address 

@login_required(login_url='login')
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    total_amount = sum(item.get_total_price() for item in cart.items.all())

    if total_amount == 0:
        return redirect('cart')

    # User ke pehle se save kiye hue addresses nikal lein
    saved_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        # Check karein user ne konsa radio button select kiya hai
        selected_address_id = request.POST.get('selected_address')

        if selected_address_id == 'new' or not selected_address_id:
            # Naya address database me save karein
            address = Address.objects.create(
                user=request.user,
                biller_name=request.POST.get('biller_name'),
                mobile_number=request.POST.get('mobile_number'),
                address_line=request.POST.get('address_line'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                pincode=request.POST.get('pincode')
            )
        else:
            # Purana save kiya hua address use karein
            address = Address.objects.get(id=selected_address_id, user=request.user)

        # Order me billing_address pass karein
        order = Order.objects.create(
            user=request.user, 
            total_amount=total_amount,
            billing_address=address
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order, product=item.product, 
                price=item.product.price, quantity=item.quantity
            )

        # Stripe Checkout Session (Purana code)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': f'Order #{order.id}'},
                    'unit_amount': int(total_amount * 100), 
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
            client_reference_id=order.id,
        )
        order.stripe_session_id = checkout_session.id
        order.save()
        return redirect(checkout_session.url, code=303)

    # HTML page par saved_addresses bhejein
    return render(request, 'checkout.html', {'cart': cart, 'total_amount': total_amount, 'addresses': saved_addresses})

@login_required(login_url='login')
def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        # Order dhundh kar usko Paid mark karein
        order = Order.objects.get(stripe_session_id=session_id)
        order.is_paid = True
        order.save()
        
        # Payment ho gayi, ab Cart khali kar dein
        Cart.objects.filter(user=request.user).delete()
        
    return render(request, 'success.html')

@login_required(login_url='login')
def payment_cancel(request):
    return render(request, 'cancel.html')


@login_required(login_url='login')
def my_orders(request):
    # 1. Saare orders nikalein
    order_list = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # 2. Paginator setup karein (Ek page par 5 orders dikhane hain)
    paginator = Paginator(order_list, 2) 
    
    # 3. URL se page number nikalein (jaise: ?page=2)
    page_number = request.GET.get('page')
    
    # 4. Us page ke orders fetch karein
    orders = paginator.get_page(page_number)
    
    return render(request, 'my_orders.html', {'orders': orders})

@login_required(login_url='login')
def order_detail(request, order_id):
    # request.user lagana zaroori hai taaki koi dusre ka order na dekh sake
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


@login_required(login_url='login')
def invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'invoice.html', {'order': order})