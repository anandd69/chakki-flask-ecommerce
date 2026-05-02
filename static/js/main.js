/* ============================================================
   CHAKKI PREMIUM — Main JavaScript
   ============================================================ */

// ── CSRF TOKEN ────────────────────────────────────────────
function getCsrfToken() {
  const meta = document.querySelector('meta[name=csrf-token]');
  if (meta) return meta.content;
  const input = document.querySelector('input[name=csrf_token]');
  return input ? input.value : '';
}

// ── TOAST NOTIFICATIONS ───────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.4s ease forwards';
    setTimeout(() => toast.remove(), 400);
  }, duration);
}

// ── CART BADGE UPDATE ─────────────────────────────────────
function updateCartBadge(count) {
  const badge = document.getElementById('cartBadge');
  if (!badge) return;
  badge.textContent = count;
  badge.style.display = count > 0 ? 'flex' : 'none';
}

// ── ADD TO CART ───────────────────────────────────────────
async function addToCart(variantId, qty = 1) {
  try {
    const resp = await fetch('/add-to-cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify({ variant_id: variantId, qty: qty }),
    });
    const data = await resp.json();
    if (data.success) {
      showToast(data.message || 'Added to cart!', 'success');
      updateCartBadge(data.cart_count);
      // Pulse animation on cart btn
      const cartBtn = document.getElementById('cartBtn');
      if (cartBtn) {
        cartBtn.style.transform = 'scale(1.3)';
        setTimeout(() => cartBtn.style.transform = '', 300);
      }
    } else {
      showToast(data.message || 'Could not add to cart.', 'error');
    }
    return data;
  } catch (err) {
    showToast('Network error. Please try again.', 'error');
    return { success: false };
  }
}

// Sync version that returns the response for checkout flow
async function addToCartSync(variantId, qty = 1) {
  return addToCart(variantId, qty);
}

// ── STICKY BAR ────────────────────────────────────────────
(function initStickyBar() {
  const bar = document.getElementById('stickyBar');
  if (!bar) return;
  let shown = false;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 500 && !shown) { bar.classList.add('show'); shown = true; }
    else if (window.scrollY <= 500 && shown) { bar.classList.remove('show'); shown = false; }
  }, { passive: true });
})();

// ── HAMBURGER MENU ────────────────────────────────────────
(function initHamburger() {
  const btn = document.getElementById('hamburger');
  const links = document.getElementById('navLinks');
  if (!btn || !links) return;
  btn.addEventListener('click', () => links.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (!btn.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
    }
  });
})();

// ── SCROLL REVEAL ─────────────────────────────────────────
(function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));
})();

// ── SMOOTH SCROLL for hash links ──────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── PHONE NUMBER INPUT: digits only ───────────────────────
document.querySelectorAll('input[type=tel]').forEach(input => {
  input.addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').slice(0, 10);
  });
});

// ── PINCODE INPUT: digits only ────────────────────────────
document.querySelectorAll('input[name=pincode]').forEach(input => {
  input.addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').slice(0, 6);
  });
});

// ── ACTIVE NAV LINK ───────────────────────────────────────
(function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (path.startsWith('/products') && href.includes('/products'))) {
      a.classList.add('active');
    }
  });
})();