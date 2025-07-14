<<<<<<< HEAD
document.addEventListener('DOMContentLoaded', () => {
    // === THEME TOGGLE ===
    const themeBtn = document.getElementById('themeToggle');
    const html = document.documentElement;
    const applyTheme = (theme) => {
        html.dataset.theme = theme;
        if (themeBtn) themeBtn.innerHTML = theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        localStorage.setItem('theme', theme);
    };
    if (themeBtn) themeBtn.addEventListener('click', () => applyTheme(html.dataset.theme === 'dark' ? 'light' : 'dark'));
    applyTheme(localStorage.getItem('theme') || 'dark');

    // === SIDEBAR TOGGLE ===
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const body = document.body;
    const applySidebarState = (state) => {
        if (state === 'collapsed') {
            sidebar.classList.add('collapsed');
            body.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('collapsed');
            body.classList.remove('sidebar-collapsed');
        }
        localStorage.setItem('sidebarState', state);
    };
    if (sidebarToggle && sidebar && body) {
        sidebarToggle.addEventListener('click', () => {
            const newState = sidebar.classList.contains('collapsed') ? 'expanded' : 'collapsed';
            applySidebarState(newState);
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

        if(durationSelect) {
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
=======
// Smart Parking Analysis - main.js
document.addEventListener('DOMContentLoaded', () => {
  // === THEME TOGGLE ===
  const body = document.body;
  const themeBtn = document.getElementById('themeToggle');
  const storedTheme = localStorage.getItem('theme');
  if (storedTheme) body.dataset.theme = storedTheme;

  function swapThemeIcon() {
    themeBtn.firstElementChild.className =
      body.dataset.theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    themeBtn.setAttribute('aria-label', body.dataset.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
  swapThemeIcon();

  themeBtn.addEventListener('click', () => {
    body.dataset.theme = body.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', body.dataset.theme);
    swapThemeIcon();
    // Update Chart.js colors if present
    if (window.updateChartsForTheme) window.updateChartsForTheme(body.dataset.theme);
  });
  themeBtn.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') themeBtn.click(); });

  // === SIDEBAR TOGGLE ===
  const sidebarBtn = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (localStorage.getItem('sidebar') === 'collapsed') sidebar.classList.add('collapsed');
  sidebarBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebar', sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded');
  });
  sidebarBtn.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') sidebarBtn.click(); });

  // === RIPPLE EFFECT ===
  document.querySelectorAll('.touch-ripple').forEach(btn => {
    btn.addEventListener('click', e => {
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      const rect = btn.getBoundingClientRect();
      ripple.style.left = `${e.clientX - rect.left}px`;
      ripple.style.top  = `${e.clientY - rect.top}px`;
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // === FOCUS MAIN CONTENT ON LOAD (for accessibility) ===
  const mainContent = document.getElementById('mainContent');
  if (mainContent) mainContent.focus();

  // === TOAST NOTIFICATIONS (for future use) ===
  window.showToast = function(msg, type='info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 400); }, 3000);
  };

  // === COPY SLOT NUMBER TO CLIPBOARD (for future use) ===
  document.querySelectorAll('.slot-label').forEach(label => {
    label.addEventListener('dblclick', () => {
      navigator.clipboard.writeText(label.textContent.trim());
      window.showToast('Slot copied!', 'success');
    });
  });

  // === SMOOTH SCROLL TO TOP ON NAVIGATION ===
  document.querySelectorAll('a, button[type="submit"]').forEach(el => {
    el.addEventListener('click', () => {
      setTimeout(() => window.scrollTo({top:0,behavior:'smooth'}), 100);
    });
  });

  // === CHART.JS THEME SYNC (if using analytics) ===
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
  // Initial chart theme sync
  if (window.updateChartsForTheme) window.updateChartsForTheme(body.dataset.theme);

  // === ENTER KEY SUBMIT FOR FORMS ===
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('keydown', e => {
      if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        form.querySelector('button[type="submit"],input[type="submit"]')?.click();
        e.preventDefault();
      }
    });
  });
>>>>>>> 18187760977c2cd45c2e06343dbdba7c88205fea
});