# Dukaan — Django E-commerce Store

## Latest Update — Final Design Port

Poori site ka design ab pehle standalone HTML/CSS prototype mein finalize
kiya gaya version follow karti hai:
- Navbar: logo left, nav links center, **clean SVG line icons** (search,
  account, wishlist, cart) right side par — bilkul reference jaisa.
- Product detail page ab **image gallery + thumbnails + quantity stepper +
  Buy Now/Add to Cart side-by-side + delivery info** ke sath hai (Shopcart-
  style). Note: abhi thumbnails same photo repeat karte hain kyunki model
  mein sirf ek photo field hai — multiple photos ke liye model mein ek
  Gallery/Image model add karna hoga (bata dein agar chahiye).
- Product grid cards, buttons (Add to Cart / Buy Now) ab hamesha barabar
  size ke hain.
- Hero carousel real photos ke sath, smooth Ken Burns zoom animation.
- Gallery ("Most Recommended") section ka layout bug fix ho gaya hai
  (explicit grid placement use kiya gaya hai).

## Latest Update — Design Refresh

Site ab ek premium sneaker-store-style layout follow karti hai: photo hero
carousel, image promo cards, product grids with "Add to Cart" + "Buy Now",
an asymmetric photo gallery, a "Trending Now" banner, aur ek bara CTA banner
— sab **Luxury Dark (Black + Gold)** color scheme mein.

**Important — is baar naya migration chahiye hoga** kyunki `Product` model
mein ek naya field (`image_url`) add hua hai:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_products
```
`seed_products` dobara chalane se maujooda products ki photos (Picsum stock
photos) bhi update ho jayengi.

**Real product photos** lagane ke liye: Admin panel mein product open karein
aur "Image" field mein apni photo upload karein — wo hamesha `image_url`
(placeholder) se pehle dikhai degi.

Ek complete Django e-commerce project: rich homepage (hero, countdown sale,
new arrivals, blog, features, Instagram grid), product catalog (categories
with their own dedicated pages), site-wide search, session-based cart,
guest ya logged-in checkout, aur COD + Card + JazzCash payment options.

## Visual Upgrade (Latest)

- **Hero carousel** — 3 auto-rotating slides (5s interval) with dots and
  prev/next arrows, crossfade transition.
- **Refined color palette** — deep emerald teal, premium gold, ember-orange
  accent on a warm cream background.
- **Micro-animations** — product cards lift on hover, buttons have subtle
  press feedback, nav links get an underline sweep, countdown seconds pulse
  on each tick, New badges have a soft pulse glow.
- Respects `prefers-reduced-motion` for accessibility.

## What's New in This Version

- Poori site ka design "Dukaan" theme (teal/mustard/coral) mein hai — wahi
  look jo HTML demo mein tha, ab real backend ke sath.
- Har category (Shoes/Watches/Mobile Accessories) ka apna alag URL/page hai:
  `/category/shoes/`, `/category/watches/`, etc. — sirf ussi category ke
  products dikhte hain, kuch mix nahi hota.
- Top bar mein search (`/search/?q=...`), login/account icon, aur cart
  badge sab kaam karte hain.
- Checkout par teen payment options milte hain: Cash on Delivery, Card
  (Stripe), aur JazzCash.
- `Product.icon` field — jab tak real photo upload na ho, ek emoji
  placeholder dikhta hai (jaise ⌚ ya 👟).
- `Product.is_new` — checked karne par wo product "New Arrivals" section
  mein show hota hai.

## Setup (local machine par)

```bash
# 1. Virtual environment banayein
python -m venv venv
source venv/bin/activate        # Windows par: venv\Scripts\activate

# 2. Dependencies install karein
pip install -r requirements.txt

# 3. Database migrations banayein aur apply karein
python manage.py makemigrations
python manage.py migrate

# 4. Admin account banayein (products add karne ke liye)
python manage.py createsuperuser

# 5. (Optional) Sample products load karein
python manage.py seed_products

# 6. Server chalayein
python manage.py runserver
```

Browser mein `http://127.0.0.1:8000/` open karein. Admin panel:
`http://127.0.0.1:8000/admin/` — yahan se categories aur products add/edit karein
(images bhi upload kar sakte hain).

## Login / Guest Checkout

- `/accounts/login/` aur `/accounts/signup/` par login/signup available hai.
- Login zaroori nahi — koi bhi user bina account ke checkout kar sakta hai
  (guest order mein `user` field null rehta hai).

## Payment Methods

### Cash on Delivery
Kuch configure nahi karna — by default kaam karta hai.

### Stripe (card payment)
1. https://dashboard.stripe.com par free account banayein.
2. Test mode se apni **Secret key** lein.
3. Environment variable set karein, phir server chalayein:
   ```bash
   export STRIPE_SECRET_KEY="sk_test_..."
   export STRIPE_PUBLISHABLE_KEY="pk_test_..."
   python manage.py runserver
   ```
4. Checkout par "Card Payment (Stripe)" select karein — customer Stripe ke
   hosted payment page par redirect ho jayega.

### JazzCash
JazzCash ka koi official Python SDK nahi hai. Real integration is tarah hoti hai:

1. https://www.jazzcash.com.pk se merchant account lein — aapko `Merchant ID`,
   `Password`, aur `Integrity Salt` milega.
2. Environment variables set karein: `JAZZCASH_MERCHANT_ID`, `JAZZCASH_PASSWORD`,
   `JAZZCASH_INTEGRITY_SALT`.
3. `store/views.py` mein `jazzcash_checkout` view ke andar:
   - Order amount, merchant ID, txn ref number waghera se ek dictionary banayein
     (JazzCash docs mein exact field names diye hote hain — `pp_Amount`,
     `pp_MerchantID`, `pp_TxnRefNo`, etc.)
   - Un fields ko sorted order mein concatenate karke `Integrity Salt` ke sath
     HMAC-SHA256 se secure hash banayein (`pp_SecureHash` field).
   - Ek auto-submitting HTML form template banayein jo ye data JazzCash ke
     Payment URL (`https://sandbox.jazzcash.com.pk/...` for testing) par POST kare.
   - JazzCash customer ko payment ke baad aapke `pp_ReturnURL` par POST karke
     wapas bhejta hai — wahan payment verify karke order ko paid mark karein.
4. Filhaal `jazzcash_checkout` view sirf ek stub page dikhata hai jahan ye
   sab kuch add karna hai — poori field list aur hash formula JazzCash ke
   official integration guide (unke merchant portal) mein milta hai.

## Project Structure

```
ecommerce_project/
├── manage.py
├── requirements.txt
├── ecommerce_project/      # Django project settings
├── store/                  # Main e-commerce app
│   ├── models.py           # Category, Product, Order, OrderItem
│   ├── views.py            # All views: catalog, cart, checkout, payments
│   ├── cart.py             # Session-based cart (works for guests + users)
│   ├── forms.py            # Signup + checkout forms
│   ├── urls.py
│   ├── admin.py
│   ├── templates/
│   └── static/store/css/style.css
```

## Notes

- Database SQLite hai by default (`db.sqlite3`) — koi extra setup nahi chahiye.
- `DJANGO_DEBUG` aur `DJANGO_SECRET_KEY` production mein zaroor set karein
  (`settings.py` mein environment variables se read hote hain).
- Product images admin panel se upload karein — automatically `media/products/`
  mein save hongi.
