from carts.models import Cart

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            # User ka cart fetch karein
            cart = Cart.objects.get(user=request.user)
            # Cart me jitni bhi quantity hai, sabko jod lein (sum)
            count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            count = 0
            
    return {'cart_count': count} # Yeh variable ab har HTML file me available hoga