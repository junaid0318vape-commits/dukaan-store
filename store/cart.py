"""
Simple session-based cart so it works for both guests and logged-in users
without needing a database Cart model.
"""
from decimal import Decimal
from .models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price),
            }
        self.save()

    def set_quantity(self, product, quantity):
        product_id = str(product.id)
        if quantity <= 0:
            self.remove(product)
            return
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total(self):
        return sum(
            Decimal(item['price']) * item['quantity'] for item in self.cart.values()
        )

    def get_items(self):
        """Returns a list of dicts with product objects attached, for template use."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_by_id = {str(p.id): p for p in products}

        items = []
        for product_id, item in self.cart.items():
            product = products_by_id.get(product_id)
            if not product:
                continue
            quantity = item['quantity']
            price = Decimal(item['price'])
            items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': price * quantity,
            })
        return items
