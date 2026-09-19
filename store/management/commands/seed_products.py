from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product

# NOTE: image_url values use Lorem Picsum (https://picsum.photos) — a free,
# no-attribution-required service that serves real stock photographs by a
# fixed "seed" (so the same seed always returns the same photo). They are
# generic placeholder photos, not literal product shots. Replace them with
# real product photography via the admin panel's "Image" upload field
# whenever you have actual photos — uploaded images always take priority.

SAMPLE_DATA = {
    'Shoes': [
        ('Classic Leather Sneaker', 4500, 'Premium leather sneaker, roz mareez wear ke liye perfect.', '👟', False),
        ('Running Sport Shoe', 3800, 'Lightweight running shoe, breathable mesh fabric ke sath.', '👟', False),
        ('Formal Loafer', 5200, 'Office aur formal events ke liye stylish loafer.', '👞', False),
        ('Suede Sneaker', 4700, 'Soft suede finish sneaker, casual outings ke liye ideal.', '👟', True),
    ],
    'Watches': [
        ('Minimalist Steel Watch', 6500, 'Simple aur elegant steel watch.', '⌚', False),
        ('Chronograph Leather Watch', 8900, 'Premium chronograph watch, genuine leather strap.', '⌚', False),
        ('Smart Fitness Watch', 7200, 'Heart rate, steps aur notifications track kare.', '⌚', False),
        ('Classic Analog Watch', 3900, 'Simple analog dial, daily wear ke liye perfect.', '⌚', True),
        ('Rose Gold Watch', 6200, 'Elegant rose gold finish watch, formal aur casual dono looks ke liye.', '⌚', True),
    ],
    'Mobile Accessories': [
        ('Fast Charger 20W', 1500, '20W fast charging adapter.', '🔌', False),
        ('Wireless Earbuds', 4200, 'Clear sound quality wireless earbuds.', '🎧', False),
        ('Power Bank 10000mAh', 3300, '10000mAh power bank, dual output ports.', '🔋', False),
        ('Bass Earbuds', 3500, 'Deep bass wireless earbuds, music aur calls dono ke liye behtareen.', '🎧', True),
    ],
}


def picsum(seed, w=600, h=600):
    return f'https://picsum.photos/seed/{seed}/{w}/{h}'


class Command(BaseCommand):
    help = 'Seeds sample categories and products so the store is not empty on first run.'

    def handle(self, *args, **options):
        for cat_name, products in SAMPLE_DATA.items():
            category, _ = Category.objects.get_or_create(
                name=cat_name, defaults={'slug': slugify(cat_name)}
            )
            for name, price, desc, icon, is_new in products:
                slug = slugify(name)
                Product.objects.update_or_create(
                    name=name,
                    defaults={
                        'slug': slug,
                        'category': category,
                        'price': price,
                        'description': desc,
                        'stock': 25,
                        'icon': icon,
                        'is_new': is_new,
                        'image_url': picsum(slug),
                    },
                )
        self.stdout.write(self.style.SUCCESS('Sample products seeded successfully.'))
