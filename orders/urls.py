from django.urls import path
from . import views

urlpatterns = [
    # Checkout aur Payment se jude URLs
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    
    # User ke orders aur unki details se jude URLs
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),
]