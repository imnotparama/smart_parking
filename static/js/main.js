/**
 * Smart Parking Analysis - Main JavaScript File v9.0 (Modal Removed)
 *
 * This file handles all frontend interactivity, including:
 * - Theme and sidebar state management.
 * - Interactive booking form with real-time updates.
 * - Live search and filtering for parking slots.
 * - A countdown timer for active bookings.
 */
document.addEventListener('DOMContentLoaded', () => {

    /**
     * Handles theme switching (dark/light) and persists the choice.
     */
    function initializeThemeToggle() {
        const themeBtn = document.getElementById('themeToggle');
        if (!themeBtn) return;
        const html = document.documentElement;
        const applyTheme = (theme) => {
            html.dataset.theme = theme;
            localStorage.setItem('theme', theme);
            themeBtn.innerHTML = theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        };
        themeBtn.addEventListener('click', () => applyTheme(html.dataset.theme === 'dark' ? 'light' : 'dark'));
        applyTheme(localStorage.getItem('theme') || 'dark');
    }

    /**
     * Handles collapsing and expanding the sidebar.
     */
    function initializeSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        const body = document.body;
        if (!sidebarToggle || !sidebar || !body) return;
        const applySidebarState = (state) => {
            sidebar.classList.toggle('collapsed', state === 'collapsed');
            body.classList.toggle('sidebar-collapsed', state === 'collapsed');
            localStorage.setItem('sidebarState', state);
        };
        sidebarToggle.addEventListener('click', () => applySidebarState(sidebar.classList.contains('collapsed') ? 'expanded' : 'collapsed'));
        const initialState = window.innerWidth > 768 ? (localStorage.getItem('sidebarState') || 'expanded') : 'collapsed';
        applySidebarState(initialState);
    }

    /**
     * Manages all interactivity on the main booking page.
     */
    function initializeBookingPage() {
        const bookingPage = document.querySelector('.booking-page-layout');
        if (!bookingPage) return;

        const allSlots = document.querySelectorAll('.parking-slot');
        const summarySlot = document.getElementById('summary-slot');
        const summaryAmount = document.getElementById('summary-amount');
        const bookNowBtn = document.getElementById('book-now-btn');
        const slotIdInput = document.querySelector('input[name="slot_id"]');
        const durationSelect = document.querySelector('select[name="duration"]');
        let selectedPrice = 0;

        allSlots.forEach(slot => {
            slot.addEventListener('click', () => {
                if (!slot.classList.contains('available')) return;
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
                const duration = parseFloat(durationSelect.value);
                const total = selectedPrice * duration;
                summaryAmount.textContent = `₹${total.toFixed(2)}`;
                bookNowBtn.textContent = `Book Now - ₹${total.toFixed(2)}`;
            }
        }

        allSlots.forEach((slot, index) => {
            slot.style.setProperty('--animation-delay', `${index * 0.02}s`);
        });
    }

    /**
     * Creates a live countdown timer on the "My Bookings" page.
     */
    function initializeCountdownTimer() {
        const activeBookingCard = document.getElementById('activeBookingCard');
        if (!activeBookingCard) return;

        const countdownElement = document.getElementById('countdownTimer');
        const endTime = new Date(activeBookingCard.dataset.endTime).getTime();

        const timerInterval = setInterval(() => {
            const now = new Date().getTime();
            const distance = endTime - now;
            if (distance < 0) {
                clearInterval(timerInterval);
                countdownElement.textContent = "EXPIRED";
                return;
            }
            const hours = String(Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
            const minutes = String(Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
            const seconds = String(Math.floor((distance % (1000 * 60)) / 1000)).padStart(2, '0');
            countdownElement.textContent = `${hours}:${minutes}:${seconds}`;
        }, 1000);
    }

    // Run all initialization functions on page load
    initializeThemeToggle();
    initializeSidebar();
    initializeBookingPage();
    initializeCountdownTimer();
    // The initializeConfirmationModal() function has been completely removed.
});