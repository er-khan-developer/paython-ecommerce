from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem


@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # Check karein ki request AJAX (JS) se aayi hai ya nahi
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        cart_count = sum(item.quantity for item in cart.items.all())
        return JsonResponse({'success': True, 'cart_count': cart_count})

    return redirect('cart')

# Naya Buy Now Function (Item add karega aur direct Checkout par bhej dega)
@login_required(login_url='login')
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    # Cart me dalne ke baad direct Checkout page par redirect
    return redirect('checkout')

@login_required(login_url='login')
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    # Cart me mojood sabhi items ka total amount calculate karna
    total_amount = sum(item.get_total_price() for item in cart.items.all())
    return render(request, 'cart.html', {'cart': cart, 'total_amount': total_amount})


@login_required(login_url='login')
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity += 1
    item.save()
    
    # Naya total calculate karein
    cart = item.cart
    total_amount = sum(i.get_total_price() for i in cart.items.all())
    
    return JsonResponse({
        'success': True,
        'quantity': item.quantity,
        'item_total': item.get_total_price(),
        'cart_total': total_amount,
        'cart_count': sum(i.quantity for i in cart.items.all())
    })

@login_required(login_url='login')
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
        return JsonResponse({
            'success': True,
            'quantity': item.quantity,
            'item_total': item.get_total_price(),
            'cart_total': sum(i.get_total_price() for i in cart.items.all()),
            'cart_count': sum(i.quantity for i in cart.items.all()),
            'is_deleted': False
        })
    else:
        item.delete()
        return JsonResponse({
            'success': True,
            'cart_total': sum(i.get_total_price() for i in cart.items.all()),
            'cart_count': sum(i.quantity for i in cart.items.all()),
            'is_deleted': True
        })

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    item.delete()
    
    return JsonResponse({
        'success': True,
        'cart_total': sum(i.get_total_price() for i in cart.items.all()),
           'cart_count': sum(i.quantity for i in cart.items.all())
    })
