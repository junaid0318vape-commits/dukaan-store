from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import SignUpForm, CheckoutForm
from .models import Category, Product, Order, OrderItem


def home(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    new_arrivals = Product.objects.filter(is_active=True, is_new=True)[:4]
    spotlight = Product.objects.filter(is_active=True).order_by('?').first()

    return render(request, 'store/home.html', {
        'categories': categories,
        'products': products,
        'active_category': active_category,
        'new_arrivals': new_arrivals,
        'spotlight': spotlight,
    })


def category_page(request, slug):
    """A dedicated single-category page (its own URL) — shows ONLY this
    category's products, nothing else mixed in."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    return render(request, 'store/category_page.html', {
        'category': category,
        'products': products,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'store/search_results.html', {
        'query': query,
        'products': products,
    })


def blog_detail(request):
    return render(request, 'store/blog_detail.html')


@require_POST
def newsletter_subscribe(request):
    email = request.POST.get('email', '').strip()
    if email:
        messages.success(request, 'Shukriya! Aap subscribe ho gaye.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.add(product, quantity)
    messages.success(request, f'{product.name} cart mein add ho gaya.')
    next_url = request.POST.get('next') or reverse('cart')
    return redirect(next_url)


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.set_quantity(product, quantity)
    return redirect('cart')


@require_POST
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart')


def cart_view(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {
        'cart_items': cart.get_items(),
        'cart_total': cart.get_total(),
    })


def checkout(request):
    cart = Cart(request)
    cart_items = cart.get_items()
    if not cart_items:
        messages.info(request, 'Aapka cart khali hai.')
        return redirect('home')

    initial = {}
    if request.user.is_authenticated:
        initial = {'full_name': request.user.get_full_name() or request.user.username,
                   'email': request.user.email}

    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    price=item['price'],
                    quantity=item['quantity'],
                )
            order.recalculate_total()

            payment_method = form.cleaned_data['payment_method']

            if payment_method == 'cod':
                cart.clear()
                messages.success(request, 'Order place ho gaya! Cash on delivery par payment karein.')
                return redirect('order_success', order_id=order.id)

            elif payment_method == 'stripe':
                return redirect('stripe_checkout', order_id=order.id)

            elif payment_method == 'jazzcash':
                return redirect('jazzcash_checkout', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart.get_total(),
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, 'Account ban gaya! Khush aamdeed.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# ---------------------------------------------------------------------------
# Stripe (card payment)
# ---------------------------------------------------------------------------

def stripe_checkout(request, order_id):
    """
    Creates a Stripe Checkout Session and redirects the customer to Stripe's
    hosted payment page. Requires STRIPE_SECRET_KEY to be set (see README).
    """
    order = get_object_or_404(Order, id=order_id)

    if not settings.STRIPE_SECRET_KEY:
        messages.error(request, 'Stripe abhi configure nahi hai. STRIPE_SECRET_KEY set karein (README dekhein).')
        return redirect('checkout')

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    line_items = [{
        'price_data': {
            'currency': 'pkr',
            'product_data': {'name': item.product_name},
            # Stripe expects the smallest currency unit
            'unit_amount': int(item.price * 100),
        },
        'quantity': item.quantity,
    } for item in order.items.all()]

    success_url = request.build_absolute_uri(
        reverse('stripe_payment_success', args=[order.id])
    ) + '?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = request.build_absolute_uri(reverse('checkout'))

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )

    order.stripe_checkout_session_id = session.id
    order.save(update_fields=['stripe_checkout_session_id'])

    return redirect(session.url, permanent=False)


def stripe_payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True
    order.status = 'paid'
    order.save(update_fields=['is_paid', 'status'])

    cart = Cart(request)
    cart.clear()

    messages.success(request, 'Payment successful!')
    return redirect('order_success', order_id=order.id)


# ---------------------------------------------------------------------------
# JazzCash (Pakistan mobile wallet)
# ---------------------------------------------------------------------------

def jazzcash_checkout(request, order_id):
    """
    JazzCash has no official Python SDK — integration is a direct POST to
    their Merchant API with a secure hash. This view is a stub that shows
    where to plug in real credentials; see README.md for the full flow.
    """
    order = get_object_or_404(Order, id=order_id)

    if not settings.JAZZCASH_MERCHANT_ID:
        messages.error(
            request,
            'JazzCash abhi configure nahi hai. JAZZCASH_MERCHANT_ID, '
            'JAZZCASH_PASSWORD, JAZZCASH_INTEGRITY_SALT set karein (README dekhein).'
        )
        return redirect('checkout')

    # Real implementation: build the JazzCash request dict, compute the
    # HMAC-SHA256 secure hash with JAZZCASH_INTEGRITY_SALT, then render
    # an auto-submitting form that POSTs to JazzCash's payment URL.
    # Left as a clearly marked extension point — see README.md.
    return render(request, 'store/jazzcash_stub.html', {'order': order})
