from django.urls import path
from .views import *

urlpatterns = [
    path("shop/", shop_view, name="shop_view"),
    path('buy/<int:product_id>/', buy_product, name='buy_product'),  
    path('confirm_purchase/<int:product_id>/', confirm_purchase, name='confirm_purchase'), 
    path('shop-swap/', shop_swap, name='shop_swap'), 
    path('buy-swap/<int:product_id>/', buy_product_swap, name='buy_product_swap'), 
    path('confirm_purchase_swap/<int:product_id>/', confirm_purchase_swap, name='confirm_purchase_swap')
]