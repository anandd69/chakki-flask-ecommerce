from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, session)
from flask_login import login_user, logout_user, login_required, current_user
from models import (db, AdminUser, Product, ProductVariant, Category,
                    Setting, WhyCard, ProcessStep, Testimonial,
                    FooterLink, Order, OrderItem)
from datetime import datetime, timedelta
from sqlalchemy import func

admin = Blueprint('admin', __name__, url_prefix='/admin')

# ── LOGIN ─────────────────────────────────────────────────
@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = AdminUser.query.filter_by(username=username, is_active=True).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin.dashboard'))
        error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

# ── DASHBOARD ─────────────────────────────────────────────
@admin.route('/')
@admin.route('/dashboard')
@login_required
def dashboard():
    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)

    total_orders   = Order.query.count()
    today_orders   = Order.query.filter(func.date(Order.created_at) == today).count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_revenue  = db.session.query(func.sum(Order.total_amount)).filter(
                         Order.status != 'cancelled').scalar() or 0
    week_revenue   = db.session.query(func.sum(Order.total_amount)).filter(
                         Order.created_at >= week_ago,
                         Order.status != 'cancelled').scalar() or 0

    # Orders by status
    status_counts = dict(db.session.query(Order.status, func.count(Order.id))
                         .group_by(Order.status).all())

    # Last 5 orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # Revenue last 7 days chart data
    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        d = datetime.utcnow().date() - timedelta(days=i)
        rev = db.session.query(func.sum(Order.total_amount)).filter(
                  func.date(Order.created_at) == d,
                  Order.status != 'cancelled').scalar() or 0
        chart_labels.append(d.strftime('%d %b'))
        chart_data.append(float(rev))

    return render_template('admin/dashboard.html',
        total_orders=total_orders, today_orders=today_orders,
        pending_orders=pending_orders, total_revenue=total_revenue,
        week_revenue=week_revenue, status_counts=status_counts,
        recent_orders=recent_orders,
        chart_labels=chart_labels, chart_data=chart_data)

# ── PRODUCTS ──────────────────────────────────────────────
@admin.route('/products')
@login_required
def products():
    products = Product.query.order_by(Product.sort_order).all()
    return render_template('admin/products.html', products=products)

@admin.route('/products/new', methods=['GET', 'POST'])
@login_required
def product_new():
    categories = Category.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        p = Product(
            category_id = request.form.get('category_id') or None,
            name        = request.form['name'].strip(),
            slug        = request.form['slug'].strip(),
            short_desc  = request.form.get('short_desc', '').strip(),
            description = request.form.get('description', '').strip(),
            emoji       = request.form.get('emoji', '🌾').strip(),
            badge       = request.form.get('badge', '').strip() or None,
            badge_color = request.form.get('badge_color', '#4A7C59'),
            is_active   = 'is_active' in request.form,
            is_featured = 'is_featured' in request.form,
            sort_order  = int(request.form.get('sort_order', 0)),
        )
        db.session.add(p)
        db.session.flush()

        # Variants
        labels  = request.form.getlist('variant_label[]')
        prices  = request.form.getlist('variant_price[]')
        mrps    = request.form.getlist('variant_mrp[]')
        stocks  = request.form.getlist('variant_stock[]')
        weights = request.form.getlist('variant_weight[]')
        for i, lbl in enumerate(labels):
            if lbl.strip():
                v = ProductVariant(
                    product_id=p.id, size_label=lbl.strip(),
                    price=float(prices[i] or 0),
                    mrp=float(mrps[i]) if mrps[i] else None,
                    stock_qty=int(stocks[i] or 0),
                    weight_kg=float(weights[i]) if weights[i] else None,
                    is_default=(i == 0),
                )
                db.session.add(v)
        db.session.commit()
        flash('Product created successfully!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=None, categories=categories)

@admin.route('/products/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(pid):
    p = Product.query.get_or_404(pid)
    categories = Category.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        p.category_id = request.form.get('category_id') or None
        p.name        = request.form['name'].strip()
        p.slug        = request.form['slug'].strip()
        p.short_desc  = request.form.get('short_desc', '').strip()
        p.description = request.form.get('description', '').strip()
        p.emoji       = request.form.get('emoji', '🌾').strip()
        p.badge       = request.form.get('badge', '').strip() or None
        p.badge_color = request.form.get('badge_color', '#4A7C59')
        p.is_active   = 'is_active' in request.form
        p.is_featured = 'is_featured' in request.form
        p.sort_order  = int(request.form.get('sort_order', 0))

        # Update variants
        variant_ids = request.form.getlist('variant_id[]')
        labels  = request.form.getlist('variant_label[]')
        prices  = request.form.getlist('variant_price[]')
        mrps    = request.form.getlist('variant_mrp[]')
        stocks  = request.form.getlist('variant_stock[]')
        weights = request.form.getlist('variant_weight[]')

        existing = {str(v.id): v for v in p.variants}
        for i, lbl in enumerate(labels):
            if not lbl.strip():
                continue
            vid = variant_ids[i] if i < len(variant_ids) else ''
            if vid and vid in existing:
                v = existing[vid]
                v.size_label = lbl.strip()
                v.price      = float(prices[i] or 0)
                v.mrp        = float(mrps[i]) if mrps[i] else None
                v.stock_qty  = int(stocks[i] or 0)
                v.weight_kg  = float(weights[i]) if weights[i] else None
            else:
                v = ProductVariant(
                    product_id=p.id, size_label=lbl.strip(),
                    price=float(prices[i] or 0),
                    mrp=float(mrps[i]) if mrps[i] else None,
                    stock_qty=int(stocks[i] or 0),
                    weight_kg=float(weights[i]) if weights[i] else None,
                    is_default=(i == 0),
                )
                db.session.add(v)

        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=p, categories=categories)

@admin.route('/products/<int:pid>/delete', methods=['POST'])
@login_required
def product_delete(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True})

# ── ORDERS ────────────────────────────────────────────────
@admin.route('/orders')
@login_required
def orders():
    status_filter = request.args.get('status', '')
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@admin.route('/orders/<int:oid>')
@login_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template('admin/order_detail.html', order=order)

@admin.route('/orders/<int:oid>/status', methods=['POST'])
@login_required
def order_status(oid):
    order = Order.query.get_or_404(oid)
    new_status = request.form.get('status') or request.get_json().get('status')
    valid = ['pending','confirmed','processing','shipped','delivered','cancelled']
    if new_status in valid:
        order.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status, 'color': order.status_color})
    return jsonify({'success': False}), 400

# ── TESTIMONIALS ──────────────────────────────────────────
@admin.route('/testimonials')
@login_required
def testimonials():
    items = Testimonial.query.order_by(Testimonial.sort_order).all()
    return render_template('admin/testimonials.html', testimonials=items)

@admin.route('/testimonials/save', methods=['POST'])
@login_required
def testimonial_save():
    tid = request.form.get('id')
    t = Testimonial.query.get(tid) if tid else Testimonial()
    t.reviewer_name  = request.form['reviewer_name'].strip()
    t.reviewer_city  = request.form.get('reviewer_city', '').strip()
    t.avatar_initial = (t.reviewer_name[0].upper() if t.reviewer_name else 'A')
    t.rating         = int(request.form.get('rating', 5))
    t.review_text    = request.form['review_text'].strip()
    t.is_active      = 'is_active' in request.form
    t.sort_order     = int(request.form.get('sort_order', 0))
    if not tid:
        db.session.add(t)
    db.session.commit()
    flash('Testimonial saved!', 'success')
    return redirect(url_for('admin.testimonials'))

@admin.route('/testimonials/<int:tid>/delete', methods=['POST'])
@login_required
def testimonial_delete(tid):
    t = Testimonial.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    return jsonify({'success': True})

# ── HOMEPAGE CONTENT ──────────────────────────────────────
@admin.route('/content')
@login_required
def content():
    settings = Setting.all_dict()
    why_cards = WhyCard.query.order_by(WhyCard.sort_order).all()
    process_steps = ProcessStep.query.order_by(ProcessStep.step_number).all()
    footer_links = FooterLink.query.order_by(FooterLink.column_name, FooterLink.sort_order).all()
    return render_template('admin/content.html',
        settings=settings, why_cards=why_cards,
        process_steps=process_steps, footer_links=footer_links)

@admin.route('/content/settings', methods=['POST'])
@login_required
def save_settings():
    editable_keys = [
        'site_name','hero_badge','hero_headline','hero_headline_italic','hero_subtext',
        'hero_stat_1_num','hero_stat_1_label','hero_stat_2_num','hero_stat_2_label',
        'hero_stat_3_num','hero_stat_3_label','trust_badges','why_title','why_subtitle',
        'process_title','process_subtitle','sticky_bar_text','footer_tagline',
        'footer_copyright','contact_phone','contact_email','contact_address',
        'free_delivery_above','delivery_hours',
    ]
    for k in editable_keys:
        if k in request.form:
            Setting.set(k, request.form[k])
    flash('Settings saved!', 'success')
    return redirect(url_for('admin.content'))

@admin.route('/content/why-card/save', methods=['POST'])
@login_required
def why_card_save():
    cid = request.form.get('id')
    c = WhyCard.query.get(cid) if cid else WhyCard()
    c.icon        = request.form['icon'].strip()
    c.title       = request.form['title'].strip()
    c.description = request.form['description'].strip()
    c.sort_order  = int(request.form.get('sort_order', 0))
    c.is_active   = 'is_active' in request.form
    if not cid:
        db.session.add(c)
    db.session.commit()
    flash('Why card saved!', 'success')
    return redirect(url_for('admin.content') + '#why')

@admin.route('/content/why-card/<int:cid>/delete', methods=['POST'])
@login_required
def why_card_delete(cid):
    c = WhyCard.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/content/process-step/save', methods=['POST'])
@login_required
def process_step_save():
    sid = request.form.get('id')
    s = ProcessStep.query.get(sid) if sid else ProcessStep()
    s.step_number = int(request.form['step_number'])
    s.title       = request.form['title'].strip()
    s.description = request.form['description'].strip()
    s.is_active   = 'is_active' in request.form
    if not sid:
        db.session.add(s)
    db.session.commit()
    flash('Process step saved!', 'success')
    return redirect(url_for('admin.content') + '#process')

@admin.route('/content/process-step/<int:sid>/delete', methods=['POST'])
@login_required
def process_step_delete(sid):
    s = ProcessStep.query.get_or_404(sid)
    db.session.delete(s)
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/content/footer-link/save', methods=['POST'])
@login_required
def footer_link_save():
    lid = request.form.get('id')
    lnk = FooterLink.query.get(lid) if lid else FooterLink()
    lnk.column_name = request.form['column_name'].strip()
    lnk.label       = request.form['label'].strip()
    lnk.url         = request.form['url'].strip()
    lnk.sort_order  = int(request.form.get('sort_order', 0))
    lnk.is_active   = 'is_active' in request.form
    if not lid:
        db.session.add(lnk)
    db.session.commit()
    flash('Footer link saved!', 'success')
    return redirect(url_for('admin.content') + '#footer')

@admin.route('/content/footer-link/<int:lid>/delete', methods=['POST'])
@login_required
def footer_link_delete(lid):
    lnk = FooterLink.query.get_or_404(lid)
    db.session.delete(lnk)
    db.session.commit()
    return jsonify({'success': True})

# ── CATEGORIES ────────────────────────────────────────────
@admin.route('/categories')
@login_required
def categories():
    cats = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=cats)

@admin.route('/categories/save', methods=['POST'])
@login_required
def category_save():
    cid = request.form.get('id')
    c = Category.query.get(cid) if cid else Category()
    c.name        = request.form['name'].strip()
    c.slug        = request.form['slug'].strip()
    c.description = request.form.get('description', '').strip()
    c.sort_order  = int(request.form.get('sort_order', 0))
    c.is_active   = 'is_active' in request.form
    if not cid:
        db.session.add(c)
    db.session.commit()
    flash('Category saved!', 'success')
    return redirect(url_for('admin.categories'))

# ── ANALYTICS ─────────────────────────────────────────────
@admin.route('/analytics')
@login_required
def analytics():
    # Revenue by month (last 6 months)
    months_data = []
    for i in range(5, -1, -1):
        d = datetime.utcnow().replace(day=1) - timedelta(days=i*28)
        rev = db.session.query(func.sum(Order.total_amount)).filter(
            func.year(Order.created_at) == d.year,
            func.month(Order.created_at) == d.month,
            Order.status != 'cancelled'
        ).scalar() or 0
        cnt = Order.query.filter(
            func.year(Order.created_at) == d.year,
            func.month(Order.created_at) == d.month,
        ).count()
        months_data.append({'month': d.strftime('%b %Y'), 'revenue': float(rev), 'orders': cnt})

    # Top products
    top_products = db.session.query(
        OrderItem.product_name,
        func.sum(OrderItem.quantity).label('qty'),
        func.sum(OrderItem.subtotal).label('rev')
    ).group_by(OrderItem.product_name).order_by(func.sum(OrderItem.subtotal).desc()).limit(5).all()

    return render_template('admin/analytics.html',
        months_data=months_data, top_products=top_products)