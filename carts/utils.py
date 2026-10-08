from .models import Cart, CartItem
from products.models import Product


GUEST_CART_SESSION_KEY = 'guest_cart'


def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return sum(item.quantity for item in cart.items.all()) if cart else 0

    guest_cart = request.session.get(GUEST_CART_SESSION_KEY, {})
    return sum(int(quantity) for quantity in guest_cart.values())


def merge_guest_cart(request, user):
    guest_cart = request.session.get(GUEST_CART_SESSION_KEY, {})
    if not guest_cart:
        return False

    cart, _ = Cart.objects.get_or_create(user=user)
    for product_id, quantity in guest_cart.items():
        try:
            product = Product.objects.get(pk=int(product_id))
            quantity = int(quantity)
        except (Product.DoesNotExist, TypeError, ValueError):
            continue

        if quantity < 1:
            continue

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
            item.save(update_fields=['quantity'])

    del request.session[GUEST_CART_SESSION_KEY]
    return True