-- ============================================================
-- CHAKKI PREMIUM — Full eCommerce Database Schema
-- MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS chakki_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE chakki_db;

-- ── SETTINGS ──────────────────────────────────────────────
CREATE TABLE settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    key_name VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO settings (key_name, value) VALUES
('site_name', 'Chakki Premium'),
('site_tagline', 'Pure. Fresh. Healthy. Direct from mill.'),
('site_logo', 'Chakki <span>Premium</span>'),
('contact_phone', '+91 98765 43210'),
('contact_email', 'hello@chakkipremium.com'),
('contact_address', 'Mill District, Jamnagar, Gujarat 361008'),
('free_delivery_above', '500'),
('delivery_hours', '24–48'),
('sticky_bar_text', '🌾 <strong>Fresh batch milled today!</strong> Order before 2pm for same-day dispatch.'),
('hero_badge', '🌾 Stone-Ground · Chemical-Free · Home Delivery'),
('hero_headline', 'Pure Chakki Atta'),
('hero_headline_italic', 'Straight from the Mill'),
('hero_subtext', 'Traditional stone-ground wheat flour, freshly milled with zero additives. Rich in fibre, full of flavour — delivered to your door across India.'),
('hero_stat_1_num', '50K+'),
('hero_stat_1_label', 'Happy Families'),
('hero_stat_2_num', '100%'),
('hero_stat_2_label', 'Chemical Free'),
('hero_stat_3_num', '24hr'),
('hero_stat_3_label', 'Fresh Delivery'),
('trust_badges', 'FSSAI Certified,ISO 22000,No Preservatives'),
('why_title', 'The Chakki Difference'),
('why_subtitle', 'We bring back the goodness of traditional stone-ground atta with modern hygiene standards.'),
('process_title', 'Farm to Your Kitchen in 4 Steps'),
('process_subtitle', 'We believe in full transparency. Here''s how your atta goes from golden wheat to your table.'),
('footer_tagline', 'Pure, freshly milled chakki atta delivered across India. No chemicals, no compromise.'),
('footer_copyright', '© 2026 Chakki Premium. All rights reserved.'),
('meta_description', 'Buy fresh stone-ground chakki atta online. Chemical-free, home delivery across India.'),
('analytics_ga_id', '');

-- ── ADMIN USERS ───────────────────────────────────────────
CREATE TABLE admin_users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(120),
    email VARCHAR(120),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin: admin / chakki@2026
INSERT INTO admin_users (username, password_hash, full_name, email) VALUES
('admin', 'pbkdf2:sha256:600000$placeholder', 'Admin User', 'admin@chakkipremium.com');

-- ── CATEGORIES ────────────────────────────────────────────
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO categories (name, slug, description, sort_order) VALUES
('Wheat Atta', 'wheat-atta', 'Traditional chakki-ground wheat flour', 1),
('Multigrain', 'multigrain', 'Blend of healthy grains', 2),
('Specialty', 'specialty', 'Ancient and specialty grains', 3),
('Organic', 'organic', 'Certified organic varieties', 4);

-- ── PRODUCTS ──────────────────────────────────────────────
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    short_desc VARCHAR(300),
    description TEXT,
    emoji VARCHAR(10) DEFAULT '🌾',
    badge VARCHAR(50),
    badge_color VARCHAR(20) DEFAULT '#4A7C59',
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- ── PRODUCT VARIANTS (size/price) ─────────────────────────
CREATE TABLE product_variants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    size_label VARCHAR(50) NOT NULL,
    weight_kg DECIMAL(5,2),
    price DECIMAL(10,2) NOT NULL,
    mrp DECIMAL(10,2),
    stock_qty INT DEFAULT 100,
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

INSERT INTO products (category_id, name, slug, short_desc, description, emoji, badge, is_featured, sort_order) VALUES
(1, 'Classic Sharbati Atta', 'classic-sharbati-atta', 'MP Sharbati wheat · Soft rotis · Daily use',
 'Our flagship atta made from premium MP Sharbati wheat. Cold-press stone grinding preserves all natural oils and nutrients. Makes incredibly soft rotis with a natural sweetness.',
 '🌾', 'Bestseller', TRUE, 1),
(1, 'Whole Wheat Atta', 'whole-wheat-atta', '100% whole grain · Nutritious · Extra bran',
 'Full whole grain atta with complete bran and germ intact. High in dietary fibre, iron and B-vitamins. Perfect for health-conscious families.',
 '🟫', 'High Fibre', TRUE, 2),
(2, 'Organic Multigrain Atta', 'organic-multigrain-atta', 'Wheat + Jowar + Bajra + Ragi blend',
 'A perfect blend of 5 grains — Wheat, Jowar, Bajra, Ragi and Oats — stone ground together. Rich in protein, fibre and micronutrients.',
 '🌿', 'Organic', TRUE, 3),
(3, 'Khapli (Emmer) Atta', 'khapli-emmer-atta', 'Ancient wheat variety · Low gluten · Diabetic friendly',
 'Khapli is an ancient emmer wheat variety with naturally lower gluten content and a lower glycemic index. Recommended by nutritionists for diabetic and health-conscious consumers.',
 '⭐', 'Premium', TRUE, 4);

INSERT INTO product_variants (product_id, size_label, weight_kg, price, mrp, stock_qty, is_default) VALUES
(1, '5 kg', 5.0, 320.00, 380.00, 200, TRUE),
(1, '10 kg', 10.0, 620.00, 740.00, 150, FALSE),
(1, '25 kg', 25.0, 1450.00, 1750.00, 80, FALSE),
(2, '5 kg', 5.0, 290.00, 340.00, 180, TRUE),
(2, '10 kg', 10.0, 560.00, 660.00, 120, FALSE),
(3, '5 kg', 5.0, 440.00, 520.00, 160, TRUE),
(3, '10 kg', 10.0, 860.00, 1000.00, 100, FALSE),
(4, '5 kg', 5.0, 580.00, 680.00, 90, TRUE),
(4, '10 kg', 10.0, 1100.00, 1300.00, 60, FALSE);

-- ── WHY SECTION CARDS ─────────────────────────────────────
CREATE TABLE why_cards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    icon VARCHAR(10) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO why_cards (icon, title, description, sort_order) VALUES
('🪨', 'Stone Ground', 'Traditional chakki grinding preserves natural nutrients, bran, and germ — unlike roller mills.', 1),
('🚫', 'Zero Chemicals', 'No bleaching agents, no preservatives, no artificial whitening. Just pure wheat, nothing else.', 2),
('🌾', 'Farm Sourced', 'Wheat sourced directly from trusted farmers in Punjab and Haryana. Traceable from farm to flour.', 3),
('🚚', 'Same-Day Mill', 'Milled fresh on the day of dispatch. No stale stock, no warehouse storage.', 4),
('💪', 'High Nutrition', 'Rich in dietary fibre, iron, and B-vitamins. Supports healthy digestion and energy levels.', 5),
('📦', 'Sealed Fresh', 'Nitrogen-flushed, food-grade packaging keeps atta fresh for up to 3 months from milling.', 6);

-- ── PROCESS STEPS ─────────────────────────────────────────
CREATE TABLE process_steps (
    id INT PRIMARY KEY AUTO_INCREMENT,
    step_number INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO process_steps (step_number, title, description) VALUES
(1, 'Source', 'Wheat handpicked from verified farms in Punjab & MP harvest season.'),
(2, 'Clean', '5-stage cleaning removes dust, stones, and impurities. No chemicals used.'),
(3, 'Grind', 'Cold-press stone chakki grinding retains all natural oils and nutrients.'),
(4, 'Pack & Deliver', 'Sealed same-day in food-grade packaging and dispatched to your door.');

-- ── TESTIMONIALS ──────────────────────────────────────────
CREATE TABLE testimonials (
    id INT PRIMARY KEY AUTO_INCREMENT,
    reviewer_name VARCHAR(100) NOT NULL,
    reviewer_city VARCHAR(100),
    avatar_initial CHAR(1),
    rating TINYINT DEFAULT 5 CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO testimonials (reviewer_name, reviewer_city, avatar_initial, rating, review_text, sort_order) VALUES
('Rahul Sharma', 'Delhi, NCR', 'R', 5, 'My rotis have never been softer. You can taste the freshness — it''s completely different from what we were buying at the store. Our whole family loves it.', 1),
('Priya Verma', 'Gurugram', 'P', 5, 'My husband is diabetic and the Khapli atta has been a lifesaver. Doctor-approved, tastes amazing, and the delivery is always on time. Highly recommend!', 2),
('Sunita Agarwal', 'Jaipur', 'S', 5, 'Switched from a leading brand to this and I''m not going back. Stone-ground makes such a difference. The multigrain atta is incredible for my kids'' lunchboxes.', 3);

-- ── FOOTER LINKS ──────────────────────────────────────────
CREATE TABLE footer_links (
    id INT PRIMARY KEY AUTO_INCREMENT,
    column_name VARCHAR(50) NOT NULL,
    label VARCHAR(100) NOT NULL,
    url VARCHAR(200) NOT NULL,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO footer_links (column_name, label, url, sort_order) VALUES
('Products', 'Sharbati Atta', '/products', 1),
('Products', 'Whole Wheat', '/products', 2),
('Products', 'Multigrain', '/products', 3),
('Products', 'Khapli Atta', '/products', 4),
('Company', 'About Us', '/about', 1),
('Company', 'Our Process', '/#process', 2),
('Company', 'Blog', '/blog', 3),
('Support', 'Contact Us', '/contact', 1),
('Support', 'Track Order', '/track-order', 2),
('Support', 'Return Policy', '/returns', 3),
('Support', 'FAQ', '/faq', 4);

-- ── ORDERS ────────────────────────────────────────────────
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(150) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_email VARCHAR(150),
    delivery_address TEXT NOT NULL,
    city VARCHAR(100),
    pincode VARCHAR(10),
    subtotal DECIMAL(10,2) NOT NULL,
    delivery_charge DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'COD',
    status ENUM('pending','confirmed','processing','shipped','delivered','cancelled') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ── ORDER ITEMS ───────────────────────────────────────────
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    variant_id INT NOT NULL,
    product_name VARCHAR(200),
    variant_label VARCHAR(50),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(id)
);

-- ── CONTENT SECTIONS (for misc editable content) ──────────
CREATE TABLE content_sections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    section_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200),
    content TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Useful indexes
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_products_active ON products(is_active, sort_order);
CREATE INDEX idx_variants_product ON product_variants(product_id);