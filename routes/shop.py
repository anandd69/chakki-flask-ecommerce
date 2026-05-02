from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from models import (db, Product, ProductVariant, Category, Setting, WhyCard,
                    ProcessStep, Testimonial, FooterLink, Order, OrderItem,
                    generate_order_number)
from config import Config
import re

shop = Blueprint('shop', __name__)

# ── HELPERS ───────────────────────────────────────────────
def get_cart():
    return session.get('cart', {})

def get_cart_count():
    return sum(item['qty'] for item in get_cart().values())

def get_cart_total():
    return sum(item['qty'] * item['price'] for item in get_cart().values())

def get_footer_links():
    links = FooterLink.query.filter_by(is_active=True).order_by(FooterLink.column_name, FooterLink.sort_order).all()
    grouped = {}
    for lnk in links:
        grouped.setdefault(lnk.column_name, []).append(lnk)
    return grouped

def base_context():
    s = Setting.all_dict()
    return {
        'settings': s,
        'cart_count': get_cart_count(),
        'footer_links': get_footer_links(),
    }

# ── HOME ──────────────────────────────────────────────────
@shop.route('/')
def home():
    ctx = base_context()
    ctx.update({
        'products': Product.query.filter_by(is_active=True, is_featured=True)
                        .order_by(Product.sort_order).all(),
        'why_cards': WhyCard.query.filter_by(is_active=True).order_by(WhyCard.sort_order).all(),
        'process_steps': ProcessStep.query.filter_by(is_active=True).order_by(ProcessStep.step_number).all(),
        'testimonials': Testimonial.query.filter_by(is_active=True).order_by(Testimonial.sort_order).all(),
    })
    return render_template('home.html', **ctx)

# ── PRODUCTS ──────────────────────────────────────────────
@shop.route('/products')
def products():
    ctx = base_context()
    cat_slug = request.args.get('category')
    query = Product.query.filter_by(is_active=True)
    active_cat = None
    if cat_slug:
        cat = Category.query.filter_by(slug=cat_slug, is_active=True).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
            active_cat = cat
    ctx.update({
        'products': query.order_by(Product.sort_order).all(),
        'categories': Category.query.filter_by(is_active=True).order_by(Category.sort_order).all(),
        'active_cat': active_cat,
    })
    return render_template('products.html', **ctx)

# ── PRODUCT DETAIL ────────────────────────────────────────
@shop.route('/products/<slug>')
def product_detail(slug):
    ctx = base_context()
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    ctx.update({
        'product': product,
        'variants': ProductVariant.query.filter_by(product_id=product.id).all(),
        'related': Product.query.filter_by(category_id=product.category_id, is_active=True)
                       .filter(Product.id != product.id).limit(3).all(),
    })
    return render_template('product_detail.html', **ctx)

# ── CART ──────────────────────────────────────────────────
@shop.route('/cart')
def cart():
    ctx = base_context()
    cart_items = []
    total = 0
    for key, item in get_cart().items():
        cart_items.append(item)
        total += item['qty'] * item['price']
    s = ctx['settings']
    free_del = float(s.get('free_delivery_above', 500))
    delivery_charge = 0 if total >= free_del else Config.DELIVERY_CHARGE
    ctx.update({
        'cart_items': cart_items,
        'subtotal': total,
        'delivery_charge': delivery_charge,
        'grand_total': total + delivery_charge,
        'free_delivery_above': free_del,
    })
    return render_template('cart.html', **ctx)

# ── ADD TO CART (JSON API) ────────────────────────────────
@shop.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    data = request.get_json() or request.form
    variant_id = int(data.get('variant_id', 0))
    qty = int(data.get('qty', 1))

    variant = ProductVariant.query.get(variant_id)
    if not variant:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    if variant.stock_qty < qty:
        return jsonify({'success': False, 'message': 'Insufficient stock'}), 400

    cart = get_cart()
    key = str(variant_id)
    if key in cart:
        cart[key]['qty'] += qty
    else:
        cart[key] = {
            'variant_id': variant_id,
            'product_id': variant.product_id,
            'name': variant.product.name,
            'size': variant.size_label,
            'price': float(variant.price),
            'emoji': variant.product.emoji,
            'qty': qty,
        }
    session['cart'] = cart
    session.modified = True

    return jsonify({
        'success': True,
        'message': f'{variant.product.name} added to cart!',
        'cart_count': get_cart_count(),
        'cart_total': get_cart_total(),
    })

# ── UPDATE CART ───────────────────────────────────────────
@shop.route('/update-cart', methods=['POST'])
def update_cart():
    data = request.get_json() or request.form
    variant_id = str(data.get('variant_id'))
    qty = int(data.get('qty', 0))
    cart = get_cart()
    if qty <= 0:
        cart.pop(variant_id, None)
    elif variant_id in cart:
        cart[variant_id]['qty'] = qty
    session['cart'] = cart
    session.modified = True

    total = get_cart_total()
    s = Setting.all_dict()
    free_del = float(s.get('free_delivery_above', 500))
    delivery_charge = 0 if total >= free_del else Config.DELIVERY_CHARGE

    return jsonify({
        'success': True,
        'cart_count': get_cart_count(),
        'subtotal': total,
        'delivery_charge': delivery_charge,
        'grand_total': total + delivery_charge,
    })

# ── CHECKOUT ──────────────────────────────────────────────
@shop.route('/checkout')
def checkout():
    if not get_cart():
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('shop.products'))
    ctx = base_context()
    cart_items = list(get_cart().values())
    total = get_cart_total()
    s = ctx['settings']
    free_del = float(s.get('free_delivery_above', 500))
    delivery_charge = 0 if total >= free_del else Config.DELIVERY_CHARGE
    ctx.update({
        'cart_items': cart_items,
        'subtotal': total,
        'delivery_charge': delivery_charge,
        'grand_total': total + delivery_charge,
    })
    return render_template('checkout.html', **ctx)

# ── PLACE ORDER ───────────────────────────────────────────
@shop.route('/place-order', methods=['POST'])
def place_order():
    cart = get_cart()
    if not cart:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    data = request.get_json() or request.form
    name    = data.get('name', '').strip()
    phone   = data.get('phone', '').strip()
    email   = data.get('email', '').strip()
    address = data.get('address', '').strip()
    city    = data.get('city', '').strip()
    pincode = data.get('pincode', '').strip()

    # Validation
    errors = {}
    if not name or len(name) < 2:
        errors['name'] = 'Please enter your full name.'
    if not re.match(r'^[6-9]\d{9}$', phone):
        errors['phone'] = 'Enter a valid 10-digit Indian mobile number.'
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        errors['email'] = 'Enter a valid email address.'
    if not address or len(address) < 10:
        errors['address'] = 'Please enter a complete delivery address.'
    if pincode and not re.match(r'^\d{6}$', pincode):
        errors['pincode'] = 'Enter a valid 6-digit PIN code.'

    if errors:
        return jsonify({'success': False, 'errors': errors}), 422

    subtotal = get_cart_total()
    s = Setting.all_dict()
    free_del = float(s.get('free_delivery_above', 500))
    delivery_charge = 0.0 if subtotal >= free_del else float(Config.DELIVERY_CHARGE)
    grand_total = subtotal + delivery_charge

    order = Order(
        order_number=generate_order_number(),
        customer_name=name, customer_phone=phone,
        customer_email=email or None,
        delivery_address=address, city=city, pincode=pincode,
        subtotal=subtotal, delivery_charge=delivery_charge,
        total_amount=grand_total, payment_method='COD',
    )
    db.session.add(order)
    db.session.flush()  # get order.id

    for key, item in cart.items():
        oi = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            variant_id=item['variant_id'],
            product_name=item['name'],
            variant_label=item['size'],
            quantity=item['qty'],
            unit_price=item['price'],
            subtotal=item['qty'] * item['price'],
        )
        db.session.add(oi)

    db.session.commit()
    session.pop('cart', None)
    session.modified = True

    return jsonify({
        'success': True,
        'order_number': order.order_number,
        'redirect': url_for('shop.order_success', order_number=order.order_number),
    })

# ── ORDER SUCCESS ─────────────────────────────────────────
@shop.route('/order-success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    ctx = base_context()
    ctx['order'] = order
    return render_template('order_success.html', **ctx)

# ── TRACK ORDER ───────────────────────────────────────────
@shop.route('/track-order', methods=['GET', 'POST'])
def track_order():
    ctx = base_context()
    order = None
    if request.method == 'POST':
        q = request.form.get('query', '').strip()
        if q:
            order = Order.query.filter(
                (Order.order_number == q.upper()) |
                (Order.customer_phone == q)
            ).order_by(Order.created_at.desc()).first()
            if not order:
                ctx['error'] = 'No order found. Check your order number or phone.'
    ctx['order'] = order
    return render_template('track_order.html', **ctx)

# ── VARIANT PRICE API ─────────────────────────────────────
@shop.route('/api/variant/<int:variant_id>')
def api_variant(variant_id):
    v = ProductVariant.query.get_or_404(variant_id)
    return jsonify({
        'id': v.id, 'price': float(v.price),
        'mrp': float(v.mrp) if v.mrp else None,
        'stock': v.stock_qty, 'discount': v.discount_pct,
    })