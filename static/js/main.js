/**
 * =================================================================================
 * |   Smart Parking Analysis - Main JavaScript File v12.0 (Interactive)         |
 * |-------------------------------------------------------------------------------|
 * |   This file handles all frontend interactivity, including:                    |
 * |   - Theme and sidebar state management.                                     |
 * |   - Live-updating charts for the admin dashboard.                           |
 * |   - Interactive, sortable tables.                                           |
 * |   - Real-time search and filtering for parking slots.                       |
 * |   - Dynamic tooltips and a reusable modal system.                           |
 * |   - Countdown timers for active bookings.                                   |
 * =================================================================================
 */

document.addEventListener('DOMContentLoaded', () => {

    /**
     * =============================================================
     * Utility Functions
     * =============================================================
     */

    /**
     * Delays the execution of a function until after a certain time has passed
     * since the last time it was invoked. Useful for search inputs.
     * @param {Function} func The function to debounce.
     * @param {number} delay The delay in milliseconds.
     * @returns {Function} The debounced function.
     */
    function debounce(func, delay = 250) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
            }, delay);
        };
    }


    /**
     * =============================================================
     * Core UI Initialization
     * =============================================================
     */

    /**
     * Handles theme switching (dark/light) and persists the choice in localStorage.
     * Also checks for the user's OS preference as a default.
     */
    function initializeThemeToggle() {
        const themeBtn = document.getElementById('themeToggle');
        if (!themeBtn) return;

        const html = document.documentElement;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const applyTheme = (theme) => {
            html.dataset.theme = theme;
            localStorage.setItem('theme', theme);
            themeBtn.innerHTML = theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
        };

        themeBtn.addEventListener('click', () => {
            const newTheme = html.dataset.theme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });

        // Apply theme on load: 1. localStorage, 2. OS preference, 3. Default to dark
        const savedTheme = localStorage.getItem('theme');
        applyTheme(savedTheme ? savedTheme : (prefersDark ? 'dark' : 'light'));
    }

    /**
     * Handles collapsing and expanding the sidebar, persisting state.
     * It now also re-evaluates the state on window resize.
     */
    function initializeSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        const body = document.body;
        if (!sidebarToggle || !sidebar || !body) return;

        const applySidebarState = (state) => {
            const isCollapsed = state === 'collapsed';
            sidebar.classList.toggle('collapsed', isCollapsed);
            body.classList.toggle('sidebar-collapsed', isCollapsed);
            localStorage.setItem('sidebarState', state);
        };

        sidebarToggle.addEventListener('click', () => {
            const newState = sidebar.classList.contains('collapsed') ? 'expanded' : 'collapsed';
            applySidebarState(newState);
        });

        const handleResize = () => {
            if (window.innerWidth <= 768) {
                applySidebarState('collapsed');
            } else {
                const savedState = localStorage.getItem('sidebarState') || 'expanded';
                applySidebarState(savedState);
            }
        };

        // Initial setup
        handleResize();

        // Adjust on window resize
        window.addEventListener('resize', handleResize);
    }

    /**
     * Hides Django notification messages after a few seconds.
     */
    function initializeMessageObserver() {
        const messageContainer = document.querySelector('.django-messages');
        if (!messageContainer) return;

        const messages = messageContainer.querySelectorAll('.message');
        messages.forEach((message, index) => {
            setTimeout(() => {
                message.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => message.remove(), 500);
            }, 5000 + index * 500);
        });
    }


    /**
     * =============================================================
     * Admin Dashboard Interactivity
     * =============================================================
     */

    /**
     * Initializes all interactive elements on the admin dashboard.
     */
    function initializeAdminDashboard() {
        const dashboard = document.getElementById('adminDashboard');
        if (!dashboard) return;

        console.log("Admin Dashboard JS Initialized.");
        initializeCharts();
        initializeSortableTables();
    }

    /**
     * Creates and configures charts using Chart.js.
     */
    function initializeCharts() {
        const revenueChartCtx = document.getElementById('revenueChart');
        const bookingsChartCtx = document.getElementById('bookingsChart');
        if (!revenueChartCtx || !bookingsChartCtx) return;

        // Common Chart.js options for our theme
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: 'var(--text-light)',
                        font: {
                            family: "'Poppins', sans-serif",
                            weight: '500',
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: 'var(--text-light)' },
                    grid: { color: 'var(--border)' }
                },
                y: {
                    ticks: { color: 'var(--text-light)' },
                    grid: { color: 'var(--border)' }
                }
            }
        };

        // --- Revenue Line Chart ---
        // In a real app, this data would come from an API endpoint.
        const revenueData = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            datasets: [{
                label: 'Revenue (₹)',
                data: [12000, 19000, 15000, 25000, 22000, 30000, 28000],
                borderColor: 'var(--primary)',
                backgroundColor: 'var(--primary-light)',
                fill: true,
                tension: 0.4,
            }]
        };

        new Chart(revenueChartCtx, {
            type: 'line',
            data: revenueData,
            options: commonOptions
        });


        // --- Booking Status Doughnut Chart ---
        const bookingStatusData = {
            labels: ['Completed', 'Active', 'Cancelled'],
            datasets: [{
                label: 'Booking Status',
                data: [350, 45, 15],
                backgroundColor: ['var(--info)', 'var(--primary)', 'var(--danger)'],
                borderColor: 'var(--card-bg-solid)',
                borderWidth: 4,
                hoverOffset: 10
            }]
        };

        new Chart(bookingsChartCtx, {
            type: 'doughnut',
            data: bookingStatusData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom', // Better for doughnuts
                        labels: {
                            color: 'var(--text-light)',
                            font: { family: "'Poppins', sans-serif", weight: '500' }
                        }
                    }
                }
            }
        });
    }

    /**
     * Adds click-to-sort functionality to all tables with the 'sortable' class.
     */
    function initializeSortableTables() {
        document.querySelectorAll('th.sortable').forEach(headerCell => {
            headerCell.addEventListener('click', () => {
                const tableElement = headerCell.closest('table');
                const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
                const currentIsAsc = headerCell.classList.contains('sorted-asc');

                // Reset other headers
                tableElement.querySelectorAll('th').forEach(th => th.classList.remove('sorted-asc', 'sorted-desc'));

                // Set new sort order
                const direction = currentIsAsc ? 'desc' : 'asc';
                headerCell.classList.toggle('sorted-asc', direction === 'asc');
                headerCell.classList.toggle('sorted-desc', direction === 'desc');

                sortTableByColumn(tableElement, headerIndex, direction === 'asc');
            });
        });
    }

    /**
     * Sorts an HTML table.
     * @param {HTMLTableElement} table The table to sort.
     * @param {number} columnIndex The index of the column to sort by.
     * @param {boolean} asc Determines if the sort is ascending.
     */
    function sortTableByColumn(table, columnIndex, asc = true) {
        const dirModifier = asc ? 1 : -1;
        const tBody = table.tBodies[0];
        const rows = Array.from(tBody.querySelectorAll('tr'));

        const sortedRows = rows.sort((a, b) => {
            let aColText = a.querySelector(`td:nth-child(${columnIndex + 1})`).textContent.trim();
            let bColText = b.querySelector(`td:nth-child(${columnIndex + 1})`).textContent.trim();
            
            // Handle numeric sorting for columns with numbers (e.g., ID, Price)
            const aIsNumeric = !isNaN(parseFloat(aColText)) && isFinite(aColText);
            const bIsNumeric = !isNaN(parseFloat(bColText)) && isFinite(bColText);

            if (aIsNumeric && bIsNumeric) {
                return (parseFloat(aColText) - parseFloat(bColText)) * dirModifier;
            }

            return aColText.localeCompare(bColText, undefined, { sensitivity: 'base' }) * dirModifier;
        });

        // Remove all existing rows
        while (tBody.firstChild) {
            tBody.removeChild(tBody.firstChild);
        }

        // Re-add sorted rows
        tBody.append(...sortedRows);
    }


    /**
     * =============================================================
     * Booking Page Interactivity
     * =============================================================
     */

    /**
     * Manages all interactivity on the main booking page.
     */
    function initializeBookingPage() {
        const bookingPage = document.querySelector('.booking-page-layout');
        if (!bookingPage) return;

        const allSlots = bookingPage.querySelectorAll('.parking-slot');
        const summarySlot = document.getElementById('summary-slot');
        const summaryAmount = document.getElementById('summary-amount');
        const bookNowBtn = document.getElementById('book-now-btn');
        const slotIdInput = bookingPage.querySelector('input[name="slot_id"]');
        const durationSelect = bookingPage.querySelector('select[name="duration"]');
        let selectedPrice = 0;

        // Slot selection logic
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

        // Staggered animation for slots
        allSlots.forEach((slot, index) => {
            slot.style.setProperty('--animation-delay', `${index * 0.02}s`);
        });

        // Initialize advanced filtering and tooltips for this page
        initializeSlotFilters(allSlots);
        initializeTooltips(allSlots);
    }

    /**
     * Sets up real-time search and checkbox filtering for parking slots.
     * @param {NodeListOf<Element>} slots - A NodeList of all parking slot elements.
     */
    function initializeSlotFilters(slots) {
        const searchInput = document.getElementById('slotSearchInput');
        const availableOnlyCheckbox = document.getElementById('filterAvailable');
        if (!searchInput && !availableOnlyCheckbox) return;

        const filterSlots = () => {
            const searchTerm = searchInput.value.toLowerCase();
            const showOnlyAvailable = availableOnlyCheckbox.checked;
            let visibleCount = 0;

            slots.forEach(slot => {
                const slotName = slot.dataset.slotName.toLowerCase();
                const isAvailable = slot.classList.contains('available');
                
                const matchesSearch = slotName.includes(searchTerm);
                const matchesAvailability = !showOnlyAvailable || isAvailable;

                if (matchesSearch && matchesAvailability) {
                    slot.classList.remove('filtered-out');
                    visibleCount++;
                } else {
                    slot.classList.add('filtered-out');
                }
            });
            // You could add a "no results" message here if visibleCount is 0
        };
        
        searchInput.addEventListener('input', debounce(filterSlots, 300));
        availableOnlyCheckbox.addEventListener('change', filterSlots);
    }

    /**
     * Initializes tooltips for elements that have a `data-tooltip` attribute.
     * @param {NodeListOf<Element>} elements - Elements to attach tooltips to.
     */
    function initializeTooltips(elements) {
        let tooltip = document.querySelector('.tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            document.body.appendChild(tooltip);
        }

        elements.forEach(el => {
            // Only add tooltips to non-available slots for this use case
            if (el.classList.contains('occupied') || el.classList.contains('yours')) {
                const tooltipText = el.classList.contains('occupied') ? 'This slot is currently occupied.' : 'This is your currently booked slot.';
                
                el.addEventListener('mouseenter', (e) => {
                    tooltip.textContent = tooltipText;
                    tooltip.classList.add('visible');
                    const rect = el.getBoundingClientRect();
                    tooltip.style.left = `${rect.left + rect.width / 2}px`;
                    tooltip.style.top = `${rect.top}px`;
                });

                el.addEventListener('mouseleave', () => {
                    tooltip.classList.remove('visible');
                });
            }
        });
    }


    /**
     * =============================================================
     * Timers and Modals
     * =============================================================
     */

    /**
     * Creates a live countdown timer on the "My Bookings" page that
     * auto-refreshes the page when the timer expires.
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
                countdownElement.textContent = "COMPLETED";
                setTimeout(() => window.location.reload(), 2000); // Reload to update UI
                return;
            }

            const hours = String(Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
            const minutes = String(Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
            const seconds = String(Math.floor((distance % (1000 * 60)) / 1000)).padStart(2, '0');
            countdownElement.textContent = `${hours}:${minutes}:${seconds}`;
        }, 1000);
    }
    
    /**
     * Initializes a reusable modal system.
     * Looks for triggers with `data-modal-target` and opens the corresponding modal.
     */
    function initializeModals() {
        const openModalTriggers = document.querySelectorAll('[data-modal-target]');
        const closeModalTriggers = document.querySelectorAll('[data-modal-close]');
        const overlay = document.querySelector('.modal-overlay');

        openModalTriggers.forEach(trigger => {
            trigger.addEventListener('click', () => {
                const modal = document.querySelector(trigger.dataset.modalTarget);
                openModal(modal);
            });
        });

        if (overlay) {
            overlay.addEventListener('click', () => {
                const modals = document.querySelectorAll('.modal-overlay.visible');
                modals.forEach(modal => closeModal(modal));
            });
        }
        
        closeModalTriggers.forEach(trigger => {
            trigger.addEventListener('click', () => {
                const modal = trigger.closest('.modal-overlay');
                closeModal(modal);
            });
        });
        
        function openModal(modal) {
            if (modal == null) return;
            modal.classList.add('visible');
        }

        function closeModal(modal) {
            if (modal == null) return;
            modal.classList.remove('visible');
        }
    }


    /**
     * =============================================================
     * Run All Initializers on Page Load
     * =============================================================
     */
    initializeThemeToggle();
    initializeSidebar();
    initializeMessageObserver();
    initializeBookingPage();
    initializeCountdownTimer();
    initializeAdminDashboard();
    initializeModals();

});