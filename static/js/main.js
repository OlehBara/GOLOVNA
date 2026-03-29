/**
 * FINSMART - Financial Literacy Platform
 * Main JavaScript File
 */

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initThemeToggle();
    initMobileMenu();
    initScrollToTop();
    initScrollAnimations();
    initNavigation();
    initContactForm();
    initCourseFilters();
});

// ============================================
// Theme Toggle
// ============================================
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    const htmlElement = document.documentElement;
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', function () {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        themeToggle.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            themeToggle.style.transform = 'rotate(0deg)';
        }, 300);
    });
}

// ============================================
// Mobile Menu Toggle
// ============================================
function initMobileMenu() {
    const burgerMenu = document.getElementById('burgerMenu');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileOverlay = document.getElementById('mobileOverlay');

    if (!burgerMenu || !mobileMenu) return;

    function toggleMobileMenu() {
        burgerMenu.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        mobileOverlay.classList.toggle('active');
        document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    }

    burgerMenu.addEventListener('click', toggleMobileMenu);
    mobileOverlay.addEventListener('click', toggleMobileMenu);

    // Close mobile menu when clicking on a link
    const mobileLinks = document.querySelectorAll('.mobile-nav .nav-link');
    mobileLinks.forEach(link => {
        link.addEventListener('click', toggleMobileMenu);
    });
}

// ============================================
// Scroll to Top Button
// ============================================
function initScrollToTop() {
    const scrollTopBtn = document.getElementById('scrollTop');
    if (!scrollTopBtn) return;

    window.addEventListener('scroll', function () {
        if (window.pageYOffset > 300) {
            scrollTopBtn.classList.add('visible');
        } else {
            scrollTopBtn.classList.remove('visible');
        }
    });

    scrollTopBtn.addEventListener('click', function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ============================================
// Scroll Animations
// ============================================
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function (entries) {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 100);
            }
        });
    }, observerOptions);

    // Observe all animated elements
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// ============================================
// Navigation Active State
// ============================================
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (!href) {
            return;
        }
        if (href === currentPath || (href === '/' && currentPath === '/')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ============================================
// Contact Form
// ============================================
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;

    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            message: document.getElementById('message').value
        };

        // Show success message
        const successMessage = document.getElementById('successMessage');
        if (successMessage) {
            successMessage.classList.add('show');

            // Reset form
            contactForm.reset();

            // Hide message after 5 seconds
            setTimeout(() => {
                successMessage.classList.remove('show');
            }, 5000);
        }
    });
}

// ============================================
// Course Filters
// ============================================
function initCourseFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('courseSearch');

    if (filterButtons.length === 0) return;

    // Filter by category
    filterButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            const category = this.dataset.category;
            filterCourses(category, searchInput ? searchInput.value : '');
        });
    });

    // Search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const activeFilter = document.querySelector('.filter-btn.active');
            const category = activeFilter ? activeFilter.dataset.category : 'all';
            filterCourses(category, this.value);
        });
    }
}

function filterCourses(category, searchTerm) {
    const courseCards = document.querySelectorAll('.course-card');

    courseCards.forEach(card => {
        const courseCategory = card.dataset.category || 'all';
        const courseTitle = card.querySelector('.course-title').textContent.toLowerCase();
        const courseDescription = card.querySelector('.course-description').textContent.toLowerCase();

        const matchesCategory = category === 'all' || courseCategory === category;
        const matchesSearch = searchTerm === '' ||
            courseTitle.includes(searchTerm.toLowerCase()) ||
            courseDescription.includes(searchTerm.toLowerCase());

        if (matchesCategory && matchesSearch) {
            card.style.display = 'block';
            setTimeout(() => {
                card.classList.add('visible');
            }, 100);
        } else {
            card.style.display = 'none';
            card.classList.remove('visible');
        }
    });
}

// ============================================
// Smooth Scroll for Anchor Links
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ============================================
// Helper Functions
// ============================================

// Get CSRF token for Django (use when implementing backend)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ============================================
// Console Welcome
// ============================================
console.log('%cFinSmart 💰', 'color: #1e5a8e; font-size: 24px; font-weight: bold;');
console.log('%cСистема рекомендацій з фінансової грамотності', 'color: #4A8FD5; font-size: 14px;');
console.log('%cСтворено для кращої фінансової освіти', 'color: #718096; font-size: 12px;');


// ============================================
// Shopping Cart Functionality
// ============================================
function addToCart(arg1, arg2) {
    let courseId = arg1;

    // Handle both addToCart(id) and addToCart(event, id)
    if (typeof arg1 === 'object' && arg2 !== undefined) {
        courseId = arg2;
    }

    // Find the button by ID
    const btn = document.getElementById(`btn-add-${courseId}`);
    if (!btn) {
        console.error('Button not found');
        return;
    }

    const originalText = btn.innerText;

    // Disable button and show loading state
    btn.disabled = true;
    btn.innerText = 'Додавання...';

    fetch(`/add-to-cart/${courseId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update cart badge
                const cartBtn = document.querySelector('.cart-btn');
                let badge = document.getElementById('cartBadge');

                if (badge) {
                    badge.innerText = data.cart_count;
                } else {
                    // Create badge if it doesn't exist
                    badge = document.createElement('span');
                    badge.id = 'cartBadge';
                    badge.className = 'cart-badge';
                    badge.innerText = data.cart_count;
                    if (cartBtn) {
                        cartBtn.appendChild(badge);
                    }
                }

                // Ensure badge is visible
                badge.classList.remove('d-none');

                // Show success animation on button
                btn.innerText = 'Додано!';
                btn.style.backgroundColor = '#10b981';
                btn.style.borderColor = '#10b981';
                btn.style.color = 'white';

                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerText = originalText;
                    btn.style.backgroundColor = '';
                    btn.style.borderColor = '';
                    btn.style.color = '';
                }, 2000);

            } else {
                showToast('Помилка: ' + data.message, 'error');

                btn.disabled = false;
                btn.innerText = originalText;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Сталася помилка при додаванні товару', 'error');

            btn.disabled = false;
            btn.innerText = originalText;
        });
}

function removeFromCart(itemId) {
    if (!confirm('Ви впевнені, що хочете видалити цей курс з кошика?')) {
        return;
    }

    fetch(`/cart/remove/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove item from DOM
                const itemRow = document.getElementById(`cart-item-${itemId}`);
                if (itemRow) {
                    itemRow.remove();
                }

                // Update total price
                const totalElement = document.getElementById('cart-total');
                if (totalElement) {
                    totalElement.innerText = `${data.total_price} грн`;
                }

                // Update cart badge
                const badge = document.getElementById('cartBadge');
                if (badge) {
                    badge.innerText = data.cart_count;
                    if (data.cart_count === 0) {
                        badge.classList.add('d-none');
                        // Optional: reload to show empty cart message if cart becomes empty
                        location.reload();
                    }
                }
            } else {
                showToast(data.message, 'error');

            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Сталася помилка при видаленні курсу', 'error');

        });
}

