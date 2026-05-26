from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-review/<int:id>/', views.add_review, name='add_review'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('new-password/', views.new_password, name='new_password'),
    path('checkout/', views.checkout, name='checkout'),
    path('increase-cart/<int:id>/', views.increase_cart, name='increase_cart'),
    path('decrease-cart/<int:id>/', views.decrease_cart, name='decrease_cart'),
]