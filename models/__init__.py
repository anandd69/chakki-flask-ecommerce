from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random, string

db = SQLAlchemy()

# ── ADMIN USER ────────────────────────────────────────────
class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)
    full_name    = db.Column(db.String(120))
    email        = db.Column(db.String(120))
    is_active    = db.Column(db.Boolean, default=True)
    last_login   = db.Column(db.DateTime)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

# ── SETTINGS ──────────────────────────────────────────────
class Setting(db.Model):
    __tablename__ = 'settings'
    id         = db.Column(db.Integer, primary_key=True)
    key_name   = db.Column(db.String(100), unique=True, nullable=False)
    value      = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=''):
        row = cls.query.filter_by(key_name=key).first()
        return row.value if row else default

    @classmethod
    def set(cls, key, value):
        row = cls.query.filter_by(key_name=key).first()
        if row:
            row.value = value
        else:
            row = cls(key_name=key, value=value)
            db.session.add(row)
        db.session.commit()

    @classmethod
    def all_dict(cls):
        return {r.key_name: r.value for r in cls.query.all()}

# ── CATEGORIES ────────────────────────────────────────────
class Category(db.Model):
    __tablename__ = 'categories'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    slug        = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    sort_order  = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)
    products    = db.relationship('Product', backref='category', lazy=True)

# ── PRODUCTS ──────────────────────────────────────────────
class Product(db.Model):
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name        = db.Column(db.String(200), nullable=False)
    slug        = db.Column(db.String(200), unique=True, nullable=False)
    short_desc  = db.Column(db.String(300))
    description = db.Column(db.Text)
    emoji       = db.Column(db.String(10), default='🌾')
    badge       = db.Column(db.String(50))
    badge_color = db.Column(db.String(20), default='#4A7C59')
    is_active   = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    sort_order  = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    variants    = db.relationship('ProductVariant', backref='product',
                                  lazy=True, cascade='all, delete-orphan')

    @property
    def default_variant(self):
        v = ProductVariant.query.filter_by(product_id=self.id, is_default=True).first()
        return v or (self.variants[0] if self.variants else None)

# ── PRODUCT VARIANTS ──────────────────────────────────────
class ProductVariant(db.Model):
    __tablename__ = 'product_variants'
    id          = db.Column(db.Integer, primary_key=True)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size_label  = db.Column(db.String(50), nullable=False)
    weight_kg   = db.Column(db.Numeric(5, 2))
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    mrp         = db.Column(db.Numeric(10, 2))
    stock_qty   = db.Column(db.Integer, default=100)
    is_default  = db.Column(db.Boolean, default=False)

    @property
    def discount_pct(self):
        if self.mrp and float(self.mrp) > float(self.price):
            return int((1 - float(self.price)/float(self.mrp)) * 100)
        return 0

# ── WHY CARDS ─────────────────────────────────────────────
class WhyCard(db.Model):
    __tablename__ = 'why_cards'
    id          = db.Column(db.Integer, primary_key=True)
    icon        = db.Column(db.String(10), nullable=False)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sort_order  = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)

# ── PROCESS STEPS ─────────────────────────────────────────
class ProcessStep(db.Model):
    __tablename__ = 'process_steps'
    id          = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, nullable=False)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active   = db.Column(db.Boolean, default=True)

# ── TESTIMONIALS ──────────────────────────────────────────
class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    id             = db.Column(db.Integer, primary_key=True)
    reviewer_name  = db.Column(db.String(100), nullable=False)
    reviewer_city  = db.Column(db.String(100))
    avatar_initial = db.Column(db.String(1))
    rating         = db.Column(db.Integer, default=5)
    review_text    = db.Column(db.Text, nullable=False)
    is_active      = db.Column(db.Boolean, default=True)
    sort_order     = db.Column(db.Integer, default=0)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

# ── FOOTER LINKS ──────────────────────────────────────────
class FooterLink(db.Model):
    __tablename__ = 'footer_links'
    id          = db.Column(db.Integer, primary_key=True)
    column_name = db.Column(db.String(50), nullable=False)
    label       = db.Column(db.String(100), nullable=False)
    url         = db.Column(db.String(200), nullable=False)
    sort_order  = db.Column(db.Integer, default=0)
    is_active   = db.Column(db.Boolean, default=True)

# ── ORDERS ────────────────────────────────────────────────
class Order(db.Model):
    __tablename__ = 'orders'
    id               = db.Column(db.Integer, primary_key=True)
    order_number     = db.Column(db.String(20), unique=True, nullable=False)
    customer_name    = db.Column(db.String(150), nullable=False)
    customer_phone   = db.Column(db.String(20), nullable=False)
    customer_email   = db.Column(db.String(150))
    delivery_address = db.Column(db.Text, nullable=False)
    city             = db.Column(db.String(100))
    pincode          = db.Column(db.String(10))
    subtotal         = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_charge  = db.Column(db.Numeric(10, 2), default=0)
    total_amount     = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method   = db.Column(db.String(50), default='COD')
    status           = db.Column(db.String(20), default='pending')
    notes            = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items            = db.relationship('OrderItem', backref='order',
                                       lazy=True, cascade='all, delete-orphan')

    STATUS_COLORS = {
        'pending':    '#C8922A',
        'confirmed':  '#3B82F6',
        'processing': '#8B5CF6',
        'shipped':    '#F59E0B',
        'delivered':  '#4A7C59',
        'cancelled':  '#EF4444',
    }

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, '#888')

def generate_order_number():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"CP{datetime.utcnow().strftime('%y%m%d')}{suffix}"

# ── ORDER ITEMS ───────────────────────────────────────────
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id            = db.Column(db.Integer, primary_key=True)
    order_id      = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id    = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_id    = db.Column(db.Integer, db.ForeignKey('product_variants.id'), nullable=False)
    product_name  = db.Column(db.String(200))
    variant_label = db.Column(db.String(50))
    quantity      = db.Column(db.Integer, nullable=False)
    unit_price    = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal      = db.Column(db.Numeric(10, 2), nullable=False)