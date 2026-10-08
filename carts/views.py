from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem
from .utils import GUEST_CART_SESSION_KEY, get_cart_count


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
    else:
        guest_cart = request.session.get(GUEST_CART_SESSION_KEY, {})
        product_id = str(product.id)
        guest_cart[product_id] = guest_cart.get(product_id, 0) + 1
        request.session[GUEST_CART_SESSION_KEY] = guest_cart

    # Check karein ki request AJAX (JS) se aayi hai ya nahi
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse({'success': True, 'cart_count': get_cart_count(request)})

    return redirect('cart')

# Naya Buy Now Function (Item add karega aur direct Checkout par bhej dega)

def buy_now(request, product_id):
    add_to_cart(request, product_id)

    # Cart me dalne ke baad direct Checkout page par redirect
    return redirect('checkout')


def cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = list(cart.items.select_related('product').all()) if cart else []
        items = [
            {'id': item.id, 'product': item.product, 'quantity': item.quantity,
             'total_price': item.get_total_price()}
            for item in cart_items
        ]
    else:
        cart = None
        guest_cart = request.session.get(GUEST_CART_SESSION_KEY, {})
        products = Product.objects.filter(id__in=guest_cart.keys())
        items = [
            {'id': product.id, 'product': product,
             'quantity': int(guest_cart[str(product.id)]),
             'total_price': product.price * int(guest_cart[str(product.id)])}
            for product in products
        ]

    total_amount = sum(item['total_price'] for item in items)
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total_amount': total_amount})


def increase_quantity(request, item_id):
    if not request.user.is_authenticated:
        return update_guest_cart(request, item_id, 'increase')

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


def decrease_quantity(request, item_id):
    if not request.user.is_authenticated:
        return update_guest_cart(request, item_id, 'decrease')

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

def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return update_guest_cart(request, item_id, 'remove')

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = item.cart
    item.delete()
    
    return JsonResponse({
        'success': True,
        'cart_total': sum(i.get_total_price() for i in cart.items.all()),
           'cart_count': sum(i.quantity for i in cart.items.all())
    })


def update_guest_cart(request, product_id, action):
    product = get_object_or_404(Product, id=product_id)
    guest_cart = request.session.get(GUEST_CART_SESSION_KEY, {})
    key = str(product.id)
    quantity = int(guest_cart.get(key, 0))

    if action == 'increase':
        quantity += 1
        guest_cart[key] = quantity
    elif action == 'decrease' and quantity > 1:
        quantity -= 1
        guest_cart[key] = quantity
    else:
        guest_cart.pop(key, None)

    request.session[GUEST_CART_SESSION_KEY] = guest_cart
    total = sum(
        Product.objects.get(pk=int(product_id)).price * int(item_quantity)
        for product_id, item_quantity in guest_cart.items()
    )
    return JsonResponse({
        'success': True,
        'quantity': quantity if key in guest_cart else 0,
        'item_total': product.price * quantity,
        'cart_total': total,
        'cart_count': get_cart_count(request),
        'is_deleted': key not in guest_cart,
    })
