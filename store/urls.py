from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_page, name='category_page'),
    path('search/', views.search, name='search'),
    path('blog/watch-buying-guide/', views.blog_detail, name='blog_detail'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),

    path('checkout/stripe/<int:order_id>/', views.stripe_checkout, name='stripe_checkout'),
    path('checkout/stripe/<int:order_id>/success/', views.stripe_payment_success, name='stripe_payment_success'),
    path('checkout/jazzcash/<int:order_id>/', views.jazzcash_checkout, name='jazzcash_checkout'),
]
