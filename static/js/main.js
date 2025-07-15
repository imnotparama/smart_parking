document.addEventListener('DOMContentLoaded', () => {
  // === THEME TOGGLE ===
  const themeBtn = document.getElementById('themeToggle');
  const html = document.documentElement;

  function applyTheme(theme) {
    html.dataset.theme = theme;
    localStorage.setItem('theme', theme);
    if (themeBtn) {
      themeBtn.innerHTML = theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    }
  }

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const newTheme = html.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    });
  }
  applyTheme(localStorage.getItem('theme') || 'dark');

  // === SIDEBAR TOGGLE ===
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const body = document.body;

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
  }
  if (window.innerWidth > 900) {
      applySidebarState(localStorage.getItem('sidebarState') || 'expanded');
  } else {
      applySidebarState('collapsed');
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
        if (slot.classList.contains('occupied') || slot.classList.contains('yours')) {
            return; // Prevent selecting occupied or own slot
        }
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

  // ✅ NEW: Real-time slot status updater
  const floorSelector = document.querySelector('select[name="floor"]');
  async function updateSlotStatuses() {
      if (!floorSelector) return;
      const selectedFloor = floorSelector.value;
      
      try {
          const response = await fetch(`/api/slots/?floor=${selectedFloor}`);
          if (!response.ok) throw new Error('Network response was not ok.');
          const data = await response.json();

          const allSlots = document.querySelectorAll('.parking-slot');
          // Reset 'yours' class from all slots first
          allSlots.forEach(s => s.classList.remove('yours'));

          data.slots.forEach(apiSlot => {
              const slotElement = document.querySelector(`.parking-slot[data-slot-id="${apiSlot.id}"]`);
              if (slotElement) {
                  const isUserBooking = apiSlot.id === data.user_booking_slot_id;
                  
                  // Update availability
                  if (apiSlot.is_available && !isUserBooking) {
                      slotElement.classList.remove('occupied');
                      slotElement.tabIndex = 0;
                  } else {
                      slotElement.classList.add('occupied');
                      slotElement.tabIndex = -1;
                  }

                  // Mark user's own booking
                  if (isUserBooking) {
                      slotElement.classList.add('yours');
                      slotElement.classList.remove('occupied'); // 'yours' takes precedence
                  }
              }
          });

      } catch (error) {
          console.error("Failed to fetch slot statuses:", error);
      }
  }

  // ✅ NEW: Poll for updates only on the home page
  if (bookingPage) {
      // Update immediately on floor change
      floorSelector.addEventListener('change', function() {
          this.form.submit(); // Submit to reload page for the new floor
      });
      // Poll every 15 seconds for real-time updates
      setInterval(updateSlotStatuses, 15000);
      // Run once on page load as well
      updateSlotStatuses();
  }
});