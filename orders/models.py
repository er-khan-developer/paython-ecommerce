from django.db import models
from django.contrib.auth.models import User 

# 2. Agar Product aur Address kisi dusre module (app) me hain, toh unhe import karein
from products.models import Product



class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    biller_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.biller_name} - {self.city} ({self.pincode})"  

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_session_id = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    # related_name='items' se hum order.items.all() karke fetch kar payenge
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Order karte waqt ki price store karna zaroori hai
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (Qty: {self.quantity})"

    def get_total_price(self):
        if self.price is None:
            return 0
        return self.price * self.quantity

    