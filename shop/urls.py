from django.urls import path
from .views import *

urlpatterns = [
    path("shop/", shop_view, name="shop_view"),
    path('buy/<int:product_id>/', buy_product, name='buy_product'),  
    path('confirm_purchase/<int:product_id>/', confirm_purchase, name='confirm_purchase'), 
    path('shop-partial/', shop_partial, name='shop_partial'), 
]