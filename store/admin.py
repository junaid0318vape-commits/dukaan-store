from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_new', 'is_active']
    list_filter = ['category', 'is_active', 'is_new']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'price', 'quantity', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'items_summary', 'payment_method', 'is_paid', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_method', 'is_paid']
    search_fields = ['full_name', 'phone', 'email']
    inlines = [OrderItemInline]

    def items_summary(self, obj):
        return ", ".join(f"{item.product_name} x{item.quantity}" for item in obj.items.all())
    items_summary.short_description = "Products"