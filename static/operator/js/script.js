// ============================================
// Travel Agency Admin Dashboard JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // Sidebar Toggle (Mobile)
    // ============================================
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mainContent = document.getElementById('mainContent');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 992) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // ============================================
    // Navigation System
    // ============================================
    const navLinks = document.querySelectorAll('.nav-link[data-section]');
    const contentSections = document.querySelectorAll('.content-section');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetSection = this.getAttribute('data-section');
            
            // Remove active class from all nav items
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to clicked nav item
            this.closest('.nav-item').classList.add('active');
            
            // Hide all content sections
            contentSections.forEach(section => {
                section.classList.remove('active');
            });
            
            // Show target section
            const target = document.getElementById(targetSection);
            if (target) {
                target.classList.add('active');
                
                // Close sidebar on mobile after navigation
                if (window.innerWidth <= 992) {
                    sidebar.classList.remove('show');
                }
            }
        });
    });

    // ============================================
    // Tour Form Handling
    // ============================================
    const tourForm = document.getElementById('tourForm');
    const tourPreview = document.getElementById('tourPreview');

    if (tourForm) {
        // Real-time preview update
        const previewFields = ['tourTitle', 'tourDescription', 'tourDuration', 'tourMaxGuests', 'tourPrice', 'tourImage'];
        
        previewFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', updateTourPreview);
            }
        });

        // Form submission
        tourForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('tourTitle').value,
                description: document.getElementById('tourDescription').value,
                duration: document.getElementById('tourDuration').value,
                maxGuests: document.getElementById('tourMaxGuests').value,
                price: document.getElementById('tourPrice').value,
                category: document.getElementById('tourCategory').value,
                destination: document.getElementById('tourDestination').value,
                image: document.getElementById('tourImage').value,
                accessibility: {
                    wheelchair: document.getElementById('wheelchairAccess').checked,
                    audioGuide: document.getElementById('audioGuideAccess').checked,
                    signLanguage: document.getElementById('signLanguageAccess').checked
                },
                status: document.getElementById('tourStatus').value
            };

            // Here you would send data to your backend API
            console.log('Tour Data:', formData);
            
            // Show success message
            alert('Tour saved successfully!');
            
            // Optionally redirect to tours list
            // Switch to tours section
            document.querySelector('.nav-link[data-section="tours"]').click();
            
            // Reset form
            resetTourForm();
        });
    }

    // Update tour preview
    function updateTourPreview() {
        const title = document.getElementById('tourTitle').value || 'Tour Title';
        const description = document.getElementById('tourDescription').value || 'Tour description will appear here...';
        const duration = document.getElementById('tourDuration').value || '0';
        const maxGuests = document.getElementById('tourMaxGuests').value || '0';
        const price = document.getElementById('tourPrice').value || '0';
        const image = document.getElementById('tourImage').value || 'https://via.placeholder.com/400x200?text=Tour+Image';

        tourPreview.innerHTML = `
            <div class="tour-preview-card">
                <div class="tour-preview-image" style="background-image: url('${image}')"></div>
                <div class="tour-preview-body">
                    <div class="tour-preview-title">${title}</div>
                    <p class="small text-muted mb-2">${description.substring(0, 100)}${description.length > 100 ? '...' : ''}</p>
                    <div class="tour-preview-meta">
                        <span><i class="bi bi-clock"></i> ${duration} Days</span>
                        <span><i class="bi bi-people"></i> Max ${maxGuests}</span>
                    </div>
                    <div class="tour-preview-price">$${parseFloat(price).toLocaleString()}</div>
                </div>
            </div>
        `;
    }

    // Reset tour form
    window.resetTourForm = function() {
        if (tourForm) {
            tourForm.reset();
            tourPreview.innerHTML = '<p class="text-muted text-center">Fill in the form to see preview</p>';
        }
    };

    // ============================================
    // Tour Management Functions
    // ============================================
    window.editTour = function(tourId) {
        alert(`Edit tour #${tourId} - This would open an edit form`);
        // In a real application, you would:
        // 1. Fetch tour data from API
        // 2. Populate the form
        // 3. Switch to add-tour section
        // 4. Change form to edit mode
    };

    window.viewTour = function(tourId) {
        alert(`View tour #${tourId} - This would show tour details`);
        // In a real application, you would show a modal or navigate to a detail page
    };

    window.deleteTour = function(tourId) {
        if (confirm(`Are you sure you want to delete tour #${tourId}?`)) {
            alert(`Tour #${tourId} deleted successfully`);
            // In a real application, you would:
            // 1. Send DELETE request to API
            // 2. Remove the tour card from DOM
            // 3. Show success notification
        }
    };

    // Filter tours
    window.filterTours = function() {
        const searchTerm = document.getElementById('tourSearch').value.toLowerCase();
        const statusFilter = document.getElementById('tourStatusFilter').value;
        const categoryFilter = document.getElementById('tourCategoryFilter').value;

        const tourCards = document.querySelectorAll('.tour-management-card');
        
        tourCards.forEach(card => {
            const title = card.querySelector('h5').textContent.toLowerCase();
            const statusBadge = card.querySelector('.tour-status-badge');
            const status = statusBadge ? statusBadge.textContent.toLowerCase() : '';

            const matchesSearch = title.includes(searchTerm);
            const matchesStatus = !statusFilter || status.includes(statusFilter);
            // Note: Category filtering would require adding category data to cards

            if (matchesSearch && matchesStatus) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    };

    // ============================================
    // Booking Management Functions
    // ============================================
    window.viewBooking = function(bookingId) {
        alert(`View booking ${bookingId} - This would show booking details`);
        // In a real application, show booking details modal
    };

    window.confirmBooking = function(bookingId) {
        if (confirm(`Confirm booking ${bookingId}?`)) {
            alert(`Booking ${bookingId} confirmed successfully`);
            // In a real application, update booking status via API
        }
    };

    window.editBooking = function(bookingId) {
        alert(`Edit booking ${bookingId} - This would open edit form`);
        // In a real application, open booking edit form
    };

    // ============================================
    // Responsive Handling
    // ============================================
    window.addEventListener('resize', function() {
        if (window.innerWidth > 992) {
            sidebar.classList.remove('show');
        }
    });

    // ============================================
    // Initialize
    // ============================================
    
    // Set default active section
    const defaultSection = document.querySelector('.content-section.active') || document.getElementById('dashboard');
    if (defaultSection) {
        defaultSection.classList.add('active');
    }

    // Initialize tour preview if form exists
    if (tourPreview) {
        updateTourPreview();
    }

    console.log('Travel Agency Admin Dashboard initialized successfully!');
});

// ============================================
// Utility Functions
// ============================================

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show notification (you can integrate with a notification library)
function showNotification(message, type = 'info') {
    // Simple alert for now - replace with a proper notification system
    alert(message);
}

// ============================================
// Chart Initialization (if using Chart.js)
// ============================================

// Uncomment and configure if you want to add charts
/*
function initCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#1e3a5f',
                    backgroundColor: 'rgba(30, 58, 95, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Popularity Chart
    const popularityCtx = document.getElementById('popularityChart');
    if (popularityCtx) {
        new Chart(popularityCtx, {
            type: 'bar',
            data: {
                labels: ['Tour 1', 'Tour 2', 'Tour 3', 'Tour 4'],
                datasets: [{
                    label: 'Bookings',
                    data: [45, 32, 28, 20],
                    backgroundColor: '#4a90e2'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Initialize charts when reports section is viewed
document.addEventListener('DOMContentLoaded', function() {
    const reportsLink = document.querySelector('.nav-link[data-section="reports"]');
    if (reportsLink) {
        reportsLink.addEventListener('click', function() {
            setTimeout(initCharts, 300);
        });
    }
});
*/
