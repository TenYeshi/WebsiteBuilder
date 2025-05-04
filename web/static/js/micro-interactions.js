// Micro-interactions JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Set active class on current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar .nav-link');
    
    navLinks.forEach(link => {
        // Get the href attribute and extract the path
        const linkPath = new URL(link.href, window.location.origin).pathname;
        
        // Check if this link's path matches the current path (or if home page and root)
        if (linkPath === currentPath || 
            (linkPath.includes('/index.html') && (currentPath === '/' || currentPath === ''))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Button interactions
    const buttons = document.querySelectorAll('.btn:not(.btn-close)');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
    
    // Feature card interactions
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'rotate(10deg) scale(1.1)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.feature-icon');
            if (icon) {
                icon.style.transform = 'rotate(0) scale(1)';
            }
        });
    });
    
    // Dark mode toggle interaction
    const darkToggle = document.querySelector('.dark-toggle');
    if (darkToggle) {
        darkToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            
            // Save preference
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
            
            // Change toggle icon
            this.innerHTML = isDarkMode ? '☀️' : '🌓';
        });
        
        // Check for saved dark mode preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'enabled') {
            document.body.classList.add('dark-mode');
            darkToggle.innerHTML = '☀️';
        }
    }
    
    // Initialize AOS animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }
    
    // Add ripple effect to buttons
    function createRipple(event) {
        const button = event.currentTarget;
        
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        
        // Position the ripple element
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
        circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
        
        circle.classList.add('ripple');
        
        // Remove existing ripples
        const ripple = button.querySelector('.ripple');
        if (ripple) {
            ripple.remove();
        }
        
        button.appendChild(circle);
    }
    
    // Add the ripple effect to all buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
});