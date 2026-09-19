from .cart import Cart
from .models import Category


def cart_summary(request):
    cart = Cart(request)
    return {'cart_item_count': len(cart)}


def nav_categories(request):
    return {'nav_categories': Category.objects.all()}
