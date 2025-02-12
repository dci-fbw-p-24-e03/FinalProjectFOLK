from django.shortcuts import render, redirect
from .models import Product, Order
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.

def shop_view(request):
    products = Product.objects.all()  
    return render(request, 'shop.html', {'products': products})

#shows confirmation
@login_required
def buy_product(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'buy_confirmation.html', {'product': product})

#confirms purchase and creates order
@login_required
def confirm_purchase(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user

    total_price = product.price

    if user.coins >= total_price:
        # Create order
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=1,
            total=total_price
        )

        # Deduct coins from user
        user.coins -= total_price
        user.save()

        return HttpResponse(f"Order successfully placed for {product.name}! Total: ${total_price}")
    else:
        return HttpResponse("Not enough coins to complete the purchase.", status=400)

