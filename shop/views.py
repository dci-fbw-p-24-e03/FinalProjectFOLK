from django.shortcuts import render, redirect
from .models import Product, Order
from django.contrib.auth.decorators import login_required

# from django.http import HttpResponse
# Create your views here.


def shop_view(request):
    products = Product.objects.all()
    return render(request, "shop.html", {"products": products})


# shows confirmation
@login_required
def buy_product(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, "buy_confirmation.html", {"product": product})


# confirms purchase and creates order
@login_required
def confirm_purchase(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    total_price = product.price

    if user.coins >= total_price:
        # Create order
        order = Order.objects.create(
            user=user, product=product, quantity=1, total=total_price
        )
        
        #save item in 'show_products_users' table
        product.users.add(user)
        product.save()
        
        user.coins -= total_price
        user.save()

        return render(
            request,
            "purchase_success.html",
            {"product": product, "total_price": total_price},
        )
    else:
        return render(
            request,
            "purchase_success.html",
            {"error_message": "Not enough coins to complete the purchase."},
        )


# Views for partials (fetched and swapped into <main> in basic.html
# to not reload the entire page)


def shop_swap(request):
    products = Product.objects.all()
    return render(
        request,
        template_name="shop_swap.html",
        context={"products": products},
    )

@login_required
def buy_product_swap(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, "buy_confirmation_swap.html", {"product": product})


@login_required
def confirm_purchase_swap(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    total_price = product.price

    if user.coins >= total_price:
        # Create order
        order = Order.objects.create(
            user=user, product=product, quantity=1, total=total_price
        )

        user.coins -= total_price
        user.save()

        return render(
            request,
            "purchase_success_swap.html",
            {"product": product, "total_price": total_price},
        )
    else:
        return render(
            request,
            "purchase_success_swap.html",
            {"error_message": "Not enough coins to complete the purchase."},
        )
