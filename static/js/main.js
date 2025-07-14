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
});