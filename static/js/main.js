document.addEventListener('DOMContentLoaded', () => {
  // === THEME TOGGLE ===
  const themeBtn = document.getElementById('themeToggle');
  const html = document.documentElement;
  const body = document.body;

  function applyTheme(theme) {
    html.dataset.theme = theme;
    body.dataset.theme = theme;
    localStorage.setItem('theme', theme);
    if (themeBtn) {
      themeBtn.innerHTML = theme === 'dark' 
        ? '<i class="fa-solid fa-sun"></i>' 
        : '<i class="fa-solid fa-moon"></i>';
      themeBtn.setAttribute('aria-label', theme === 'dark' 
        ? 'Switch to light mode' 
        : 'Switch to dark mode');
    }
    if (window.updateChartsForTheme) {
      window.updateChartsForTheme(theme);
    }
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      applyTheme(html.dataset.theme === 'dark' ? 'light' : 'dark');
    });
    themeBtn.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') themeBtn.click();
    });
  }

  applyTheme(localStorage.getItem('theme') || 'dark');

  // === SIDEBAR TOGGLE ===
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');

  function applySidebarState(state) {
    if (state === 'collapsed') {
      sidebar.classList.add('collapsed');
      body.classList.add('sidebar-collapsed');
    } else {
      sidebar.classList.remove('collapsed');
      body.classList.remove('sidebar-collapsed');
    }
    localStorage.setItem('sidebarState', state);
  }

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      const newState = sidebar.classList.contains('collapsed') ? 'expanded' : 'collapsed';
      applySidebarState(newState);
    });
    sidebarToggle.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') sidebarToggle.click();
    });
    applySidebarState(localStorage.getItem('sidebarState') || 'expanded');
  }

  // === INTERACTIVE BOOKING FORM ===
  const bookingPage = document.querySelector('.booking-page-layout');
  if (bookingPage) {
    const allSlots = document.querySelectorAll('.parking-slot');
    const summarySlot = document.getElementById('summary-slot');
    const summaryAmount = document.getElementById('summary-amount');
    const bookNowBtn = document.getElementById('book-now-btn');
    const slotIdInput = document.querySelector('input[name="slot_id"]');
    const durationSelect = document.querySelector('select[name="duration"]');
    let selectedPrice = 0;

    allSlots.forEach(slot => {
      slot.addEventListener('click', () => {
        if (slot.classList.contains('occupied')) return;
        allSlots.forEach(s => s.classList.remove('selected'));
        slot.classList.add('selected');

        selectedPrice = parseFloat(slot.dataset.price);
        summarySlot.textContent = slot.dataset.slotName;
        slotIdInput.value = slot.dataset.slotId;
        bookNowBtn.disabled = false;
        updateTotal();
      });
    });

    if (durationSelect) {
      durationSelect.addEventListener('change', updateTotal);
    }

    function updateTotal() {
      if (selectedPrice > 0) {
        const duration = parseInt(durationSelect.value, 10);
        const total = selectedPrice * duration;
        summaryAmount.textContent = `₹${total.toFixed(2)}`;
        bookNowBtn.textContent = `Book Now - ₹${total.toFixed(2)}`;
      }
    }
  }

  // === RIPPLE EFFECT ===
  document.querySelectorAll('.touch-ripple').forEach(btn => {
    btn.addEventListener('click', e => {
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      const rect = btn.getBoundingClientRect();
      ripple.style.left = `${e.clientX - rect.left}px`;
      ripple.style.top = `${e.clientY - rect.top}px`;
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // === MAIN CONTENT FOCUS (Accessibility) ===
  const mainContent = document.getElementById('mainContent');
  if (mainContent) mainContent.focus();

  // === TOAST NOTIFICATIONS ===
  window.showToast = function(msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 3000);
  };

  // === COPY SLOT NUMBER TO CLIPBOARD ===
  document.querySelectorAll('.slot-label').forEach(label => {
    label.addEventListener('dblclick', () => {
      navigator.clipboard.writeText(label.textContent.trim());
      window.showToast('Slot copied!', 'success');
    });
  });

  // === SMOOTH SCROLL ON NAVIGATION ===
  document.querySelectorAll('a, button[type="submit"]').forEach(el => {
    el.addEventListener('click', () => {
      setTimeout(() => window.scrollTo({ top: 0, behavior: 'smooth' }), 100);
    });
  });

  // === CHART.JS THEME SYNC ===
  window.updateChartsForTheme = function(theme) {
    if (window.Chart && Chart.instances) {
      Object.values(Chart.instances).forEach(chart => {
        chart.options.plugins.legend.labels.color = theme === 'dark' ? '#fff' : '#2c3e50';
        chart.options.scales.x.ticks.color = theme === 'dark' ? '#fff' : '#2c3e50';
        chart.options.scales.y.ticks.color = theme === 'dark' ? '#fff' : '#2c3e50';
        chart.update();
      });
    }
  };

  if (window.updateChartsForTheme) {
    window.updateChartsForTheme(body.dataset.theme);
  }

  // === ENTER KEY SUBMIT ===
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('keydown', e => {
      if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) submitBtn.click();
        e.preventDefault();
      }
    });
  });
});
