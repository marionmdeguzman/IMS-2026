/**
 * ims.js — IMS UI Enhancements
 * Loading spinners, sidebar toggle, flash messages, slot loading,
 * notification badge, confirmation modals, client-side member search.
 */
(function () {
  'use strict';

  /* ── Inject keyframes & global styles ─────────────────────────── */
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin    { to { transform: rotate(360deg); } }
    @keyframes ripple  { to { transform: scale(2.5); opacity: 0; } }
    @keyframes slideIn { from { transform: translateX(110%); opacity:0; } to { transform: translateX(0); opacity:1; } }
    @keyframes slideOut{ to   { transform: translateX(110%); opacity:0; } }
    @keyframes bodyFadeIn { from { opacity:0; } to { opacity:1; } }
    @keyframes fadeUp  { from { opacity:0; transform: translateY(12px); } to { opacity:1; transform: translateY(0); } }

    .modal-overlay {
      display: flex !important;
      visibility: hidden; opacity: 0; pointer-events: none;
      transition: opacity 0.22s ease, visibility 0.22s ease;
    }
    .modal-overlay.open { visibility: visible; opacity: 1; pointer-events: all; }
    .modal-overlay .modal {
      transform: translateY(14px) scale(0.97);
      transition: transform 0.28s cubic-bezier(0.34,1.56,0.64,1), opacity 0.22s ease;
      opacity: 0;
    }
    .modal-overlay.open .modal { transform: translateY(0) scale(1); opacity: 1; }

    #ims-progress {
      position: fixed; top: 0; left: 0; height: 3px; width: 0;
      background: linear-gradient(90deg, #6366F1, #8B5CF6);
      z-index: 99999; border-radius: 0 2px 2px 0;
      box-shadow: 0 0 10px rgba(99,102,241,0.55);
      transition: width 0.25s ease, opacity 0.3s ease;
      pointer-events: none;
    }
    #ims-toasts {
      position: fixed; top: 1.1rem; right: 1.1rem;
      z-index: 9999; display: flex; flex-direction: column; gap: 0.55rem;
      pointer-events: none;
    }
    .ims-toast {
      display: flex; align-items: center; gap: 0.6rem;
      padding: 0.75rem 1rem; border-radius: 10px;
      font-size: 0.875rem; font-weight: 500;
      box-shadow: 0 4px 20px rgba(0,0,0,0.12);
      pointer-events: all; min-width: 240px; max-width: 380px;
      animation: slideIn 0.35s cubic-bezier(0.34,1.56,0.64,1) both;
    }
    .ims-toast.hide { animation: slideOut 0.28s ease forwards; }
    .ims-toast-close {
      background: none; border: none; cursor: pointer;
      opacity: 0.45; font-size: 1.1rem; line-height: 1;
      color: inherit; padding: 0 0.1rem; flex-shrink: 0; transition: opacity 0.15s;
      margin-left: auto;
    }
    .ims-toast-close:hover { opacity: 0.9; }

    .alert-dismiss {
      margin-left: auto; background: none; border: none;
      font-size: 1.15rem; line-height: 1; cursor: pointer;
      opacity: 0.45; color: inherit; transition: opacity 0.15s;
    }
    .alert-dismiss:hover { opacity: 0.9; }

    .mk-row-hidden { opacity:0; transform: translateY(6px); }
    .mk-reveal { opacity:0; transform: translateY(16px); transition: opacity 0.38s ease, transform 0.38s ease; }
    .mk-reveal.mk-visible { opacity:1; transform: translateY(0); }
  `;
  document.head.appendChild(style);


  /* ── 1. Page progress bar ──────────────────────────────────────── */
  const bar = document.createElement('div');
  bar.id = 'ims-progress';
  document.body.prepend(bar);

  let growTimer = null, pct = 0;
  function startProgress() {
    pct = 5; bar.style.opacity = '1'; bar.style.width = pct + '%';
    clearInterval(growTimer);
    growTimer = setInterval(() => {
      pct = Math.min(pct + Math.random() * 10, 82);
      bar.style.width = pct + '%';
    }, 100);
  }
  function finishProgress() {
    clearInterval(growTimer);
    bar.style.width = '100%';
    setTimeout(() => { bar.style.opacity = '0'; }, 280);
    setTimeout(() => { bar.style.width = '0'; }, 600);
  }
  startProgress();
  if (document.readyState === 'complete') finishProgress();
  else window.addEventListener('load', finishProgress);
  window.addEventListener('pageshow', (e) => { if (e.persisted) finishProgress(); });
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (!link || link.dataset.noLoading !== undefined) return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript') || link.target === '_blank' || link.hasAttribute('download')) return;
    startProgress();
  });


  /* ── 2. Flash message auto-dismiss ────────────────────────────── */
  function dismissAlert(el) {
    if (!el || el._dismissing) return;
    el._dismissing = true;
    const h = el.offsetHeight;
    el.style.maxHeight = h + 'px';
    el.style.overflow = 'hidden';
    requestAnimationFrame(() => requestAnimationFrame(() => {
      el.style.transition = 'opacity 0.3s ease, max-height 0.38s ease, margin 0.38s ease, padding 0.38s ease';
      el.style.opacity = '0';
      el.style.maxHeight = '0';
      el.style.marginBottom = '0';
      el.style.paddingTop = '0';
      el.style.paddingBottom = '0';
      setTimeout(() => el.remove(), 420);
    }));
  }
  document.querySelectorAll('.alert').forEach((alert, i) => {
    const btn = document.createElement('button');
    btn.className = 'alert-dismiss';
    btn.innerHTML = '&times;';
    btn.addEventListener('click', () => dismissAlert(alert));
    alert.appendChild(btn);
    setTimeout(() => dismissAlert(alert), 4000 + i * 150);
  });


  /* ── 3. Toast system ───────────────────────────────────────────── */
  const toastContainer = document.createElement('div');
  toastContainer.id = 'ims-toasts';
  document.body.appendChild(toastContainer);

  const TOAST = {
    success: { bg: '#F0FDF4', border: '#BBF7D0', color: '#15803D' },
    error:   { bg: '#FFF5F5', border: '#FECACA', color: '#DC2626' },
    warning: { bg: '#FFFBEB', border: '#FDE68A', color: '#D97706' },
    info:    { bg: '#F5F3FF', border: '#DDD6FE', color: '#6D28D9' },
  };
  window.showToast = function (msg, type) {
    type = type || 'info';
    const s = TOAST[type] || TOAST.info;
    const t = document.createElement('div');
    t.className = 'ims-toast';
    t.style.cssText = `background:${s.bg};border:1px solid ${s.border};color:${s.color};`;
    t.innerHTML = `<span style="flex:1">${msg}</span><button class="ims-toast-close">&times;</button>`;
    toastContainer.appendChild(t);
    const remove = () => { t.classList.add('hide'); setTimeout(() => t.remove(), 300); };
    t.querySelector('.ims-toast-close').addEventListener('click', remove);
    setTimeout(remove, 4500);
  };


  /* ── 4. Form submit loading spinner ───────────────────────────── */
  document.addEventListener('submit', (e) => {
    const form = e.target;
    if (form.dataset.noLoading !== undefined) return;
    const btn = form.querySelector('[type="submit"]');
    if (!btn || btn.dataset.noLoading !== undefined) return;
    const label = btn.textContent.trim() || 'Processing…';
    btn.disabled = true;
    btn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
           style="animation:spin 0.7s linear infinite;flex-shrink:0">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
      </svg>
      ${label}
    `;
    setTimeout(() => { btn.disabled = false; btn.textContent = label; }, 10000);
  });


  /* ── 5. Button ripple ─────────────────────────────────────────── */
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 1.8;
    const r = document.createElement('span');
    r.style.cssText = `
      position:absolute;border-radius:50%;background:rgba(255,255,255,0.28);
      width:${size}px;height:${size}px;
      left:${e.clientX - rect.left - size / 2}px;top:${e.clientY - rect.top - size / 2}px;
      transform:scale(0);animation:ripple 0.55s ease-out forwards;pointer-events:none;
    `;
    if (getComputedStyle(btn).position === 'static') btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(r);
    setTimeout(() => r.remove(), 600);
  });


  /* ── 6. Mobile sidebar toggle ─────────────────────────────────── */
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  function openSidebar() {
    sidebar && sidebar.classList.add('open');
    overlay && overlay.classList.add('open');
  }
  function closeSidebar() {
    sidebar && sidebar.classList.remove('open');
    overlay && overlay.classList.remove('open');
  }
  mobileBtn && mobileBtn.addEventListener('click', openSidebar);
  overlay && overlay.addEventListener('click', closeSidebar);


  /* ── 7. Table row stagger animation ───────────────────────────── */
  document.querySelectorAll('.data-table tbody tr').forEach((row, i) => {
    row.classList.add('mk-row-hidden');
    row.style.transition = `opacity 0.28s ease ${i * 25}ms, transform 0.28s ease ${i * 25}ms`;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      row.style.opacity = '1';
      row.style.transform = 'translateY(0)';
      row.classList.remove('mk-row-hidden');
    }));
  });


  /* ── 8. Card scroll-reveal ────────────────────────────────────── */
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('mk-visible');
        revealObs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.06 });
  document.querySelectorAll('.card').forEach((card, i) => {
    card.classList.add('mk-reveal');
    card.style.transitionDelay = (i * 50) + 'ms';
    revealObs.observe(card);
  });


  /* ── 9. Animated stat counters ────────────────────────────────── */
  document.querySelectorAll('[data-count]').forEach((el) => {
    const target = parseInt(el.dataset.count, 10);
    if (isNaN(target)) return;
    let current = 0;
    const steps = 40;
    const delay = parseInt(el.dataset.countDelay || '0', 10);
    const increment = target / steps;
    setTimeout(() => {
      const timer = setInterval(() => {
        current = Math.min(current + increment, target);
        el.textContent = Math.round(current).toLocaleString();
        if (current >= target) clearInterval(timer);
      }, 900 / steps);
    }, delay);
  });


  /* ── 10. Input label highlight ────────────────────────────────── */
  document.querySelectorAll('.form-group').forEach((group) => {
    const field = group.querySelector('input, select, textarea');
    const label = group.querySelector('label');
    if (!field || !label) return;
    field.addEventListener('focus', () => { label.style.color = '#6366F1'; });
    field.addEventListener('blur', () => { label.style.color = ''; });
  });


  /* ── 11. Confirmation modal for dangerous actions ─────────────── */
  // Usage: add data-confirm="Are you sure?" data-confirm-title="Delete Member" to a form or button
  // The form will show a modal before submitting.
  const confirmModal = document.createElement('div');
  confirmModal.className = 'modal-overlay';
  confirmModal.id = 'ims-confirm-modal';
  confirmModal.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,0.5);z-index:400;backdrop-filter:blur(2px);align-items:center;justify-content:center;';
  confirmModal.innerHTML = `
    <div class="modal" style="background:white;border-radius:16px;max-width:440px;width:calc(100% - 2rem);padding:2rem;">
      <h3 id="ims-confirm-title" style="font-size:1.05rem;font-weight:700;margin-bottom:0.5rem;color:#111827;"></h3>
      <p id="ims-confirm-msg" style="font-size:0.875rem;color:#6B7280;margin-bottom:1.5rem;line-height:1.6;"></p>
      <div style="display:flex;gap:0.75rem;justify-content:flex-end;">
        <button id="ims-confirm-cancel" class="btn btn-ghost btn-sm">Cancel</button>
        <button id="ims-confirm-ok" class="btn btn-danger btn-sm">Confirm</button>
      </div>
    </div>
  `;
  document.body.appendChild(confirmModal);

  let pendingConfirmAction = null;
  document.getElementById('ims-confirm-cancel').addEventListener('click', () => {
    confirmModal.classList.remove('open');
    pendingConfirmAction = null;
  });
  document.getElementById('ims-confirm-ok').addEventListener('click', () => {
    confirmModal.classList.remove('open');
    if (pendingConfirmAction) pendingConfirmAction();
    pendingConfirmAction = null;
  });

  document.addEventListener('click', (e) => {
    const trigger = e.target.closest('[data-confirm]');
    if (!trigger) return;
    e.preventDefault();
    e.stopPropagation();
    const msg = trigger.dataset.confirm || 'Are you sure you want to proceed?';
    const title = trigger.dataset.confirmTitle || 'Confirm Action';
    document.getElementById('ims-confirm-title').textContent = title;
    document.getElementById('ims-confirm-msg').textContent = msg;
    confirmModal.classList.add('open');
    pendingConfirmAction = () => {
      const form = trigger.closest('form');
      if (form) {
        trigger.removeAttribute('data-confirm');
        form.submit();
      } else if (trigger.tagName === 'A') {
        window.location.href = trigger.href;
      }
    };
  });


  /* ── 12. Real-time member list search (debounced 300ms) ───────── */
  const memberSearch = document.getElementById('member-search-input');
  const memberRows = document.querySelectorAll('.member-row');
  if (memberSearch && memberRows.length) {
    let searchTimer = null;
    memberSearch.addEventListener('input', () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        const q = memberSearch.value.toLowerCase().trim();
        memberRows.forEach((row) => {
          const text = row.textContent.toLowerCase();
          row.style.display = !q || text.includes(q) ? '' : 'none';
        });
      }, 300);
    });
  }


  /* ── 13. AJAX slot loading for booking form ───────────────────── */
  const serviceSelect = document.getElementById('id_service');
  const dateInput = document.getElementById('id_date');
  const staffSelect = document.getElementById('id_staff');
  const slotContainer = document.getElementById('slot-container');
  const startTimeInput = document.getElementById('id_start_time');
  const endTimeInput = document.getElementById('id_end_time');
  const slotsUrl = document.body.dataset.slotsUrl;

  function loadSlots() {
    if (!slotContainer || !slotsUrl) return;
    const service = serviceSelect ? serviceSelect.value : '';
    const date = dateInput ? dateInput.value : '';
    const staff = staffSelect ? staffSelect.value : '';
    if (!service || !date) {
      slotContainer.innerHTML = '<p style="color:#9CA3AF;font-size:0.875rem;">Select a service and date to see available slots.</p>';
      return;
    }
    slotContainer.innerHTML = '<p style="color:#9CA3AF;font-size:0.875rem;">Loading slots…</p>';
    const url = `${slotsUrl}?service=${service}&date=${date}&staff=${staff}`;
    fetch(url)
      .then((r) => r.json())
      .then((data) => {
        if (!data.slots || data.slots.length === 0) {
          slotContainer.innerHTML = '<p style="color:#9CA3AF;font-size:0.875rem;">No available slots for this selection.</p>';
          return;
        }
        slotContainer.innerHTML = data.slots.map((s) => `
          <button type="button" class="slot-btn"
            data-start="${s.start}" data-end="${s.end}"
            style="padding:0.5rem 1rem;border:1.5px solid #E5E7EB;border-radius:8px;
                   background:white;cursor:pointer;font-size:0.875rem;font-weight:500;
                   color:#374151;transition:all 0.15s;">
            ${s.label}
          </button>
        `).join('');
        slotContainer.querySelectorAll('.slot-btn').forEach((btn) => {
          btn.addEventListener('click', () => {
            slotContainer.querySelectorAll('.slot-btn').forEach((b) => {
              b.style.background = 'white';
              b.style.borderColor = '#E5E7EB';
              b.style.color = '#374151';
            });
            btn.style.background = '#6366F1';
            btn.style.borderColor = '#6366F1';
            btn.style.color = 'white';
            if (startTimeInput) startTimeInput.value = btn.dataset.start;
            if (endTimeInput) endTimeInput.value = btn.dataset.end;
          });
        });
      })
      .catch(() => {
        slotContainer.innerHTML = '<p style="color:#DC2626;font-size:0.875rem;">Failed to load slots. Please try again.</p>';
      });
  }

  if (serviceSelect) serviceSelect.addEventListener('change', loadSlots);
  if (dateInput) dateInput.addEventListener('change', loadSlots);
  if (staffSelect) staffSelect.addEventListener('change', loadSlots);


  /* ── 14. Unread notification badge ───────────────────────────── */
  const notifBadge = document.querySelector('.notif-badge');
  if (notifBadge) {
    const count = parseInt(notifBadge.textContent, 10);
    notifBadge.style.display = count > 0 ? 'flex' : 'none';
  }


  /* ── 15. Sidebar active indicator glow ───────────────────────── */
  const activeNav = document.querySelector('.nav-item.active');
  if (activeNav) {
    activeNav.style.boxShadow = 'inset 3px 0 0 #818CF8';
  }


  /* ── 16. Auto-focus first form field ─────────────────────────── */
  const firstInput = document.querySelector(
    'main .card input:not([type="hidden"]):not([type="checkbox"]):not([readonly]):not([id="member-search-input"]), main .card select'
  );
  if (firstInput && !firstInput.closest('.modal-overlay')) {
    setTimeout(() => firstInput.focus({ preventScroll: true }), 350);
  }

})();
