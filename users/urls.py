from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    # Django ke in-built login/logout views use kar rahe hain
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
]