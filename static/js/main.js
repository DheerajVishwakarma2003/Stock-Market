// Main JavaScript file for Stock Market Prediction System

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Form validation for stock symbol
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        const stockInput = document.getElementById('stock_symbol');
        const predictBtn = document.getElementById('predictBtn');

        predictionForm.addEventListener('submit', function(e) {
            const stockSymbol = stockInput.value.trim().toUpperCase();
            
            if (stockSymbol.length < 1) {
                e.preventDefault();
                alert('Please enter a valid stock symbol');
                return;
            }

            // Show loading state
            predictBtn.disabled = true;
            predictBtn.innerHTML = '🔄 Predicting... Please wait';
            
            // Update input value to uppercase
            stockInput.value = stockSymbol;
        });

        // Convert to uppercase as user types
        stockInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Password strength indicator (for register page)
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput && window.location.pathname.includes('register')) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = getPasswordStrength(password);
            
            // You can add a strength indicator UI here if needed
            console.log('Password strength:', strength);
        });
    }

    // Confirm before logout
    const logoutLink = document.querySelector('a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }
});

// Helper function to check password strength
function getPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]+/)) strength++;
    if (password.match(/[A-Z]+/)) strength++;
    if (password.match(/[0-9]+/)) strength++;
    if (password.match(/[$@#&!]+/)) strength++;
    
    if (strength <= 2) return 'weak';
    if (strength <= 4) return 'medium';
    return 'strong';
}

// Add animation to cards on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards
document.querySelectorAll('.feature-card, .history-card, .result-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s, transform 0.5s';
    observer.observe(card);
});

// Add to your main.js
document.addEventListener('DOMContentLoaded', function() {
    const theme = localStorage.getItem('theme') || 'light';
    document.body.classList.toggle('dark-theme', theme === 'dark');
});