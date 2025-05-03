document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded successfully');
    
    // Initialize AOS (Animate on Scroll)
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-in-out',
            once: true
        });
    }
    
    // Make sure Bootstrap carousel is active
    const carousel = document.querySelector('#imageCarousel');
    if (carousel) {
        // Make first item active if none is
        if (!carousel.querySelector('.carousel-item.active')) {
            const firstItem = carousel.querySelector('.carousel-item');
            if (firstItem) {
                firstItem.classList.add('active');
            }
        }
        
        // Initialize Bootstrap carousel
        var bsCarousel = new bootstrap.Carousel(carousel, {
            interval: 5000,
            wrap: true
        });
    }
    
    // Contact form validation
    const contactForm = document.querySelector('#contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            if (!contactForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            contactForm.classList.add('was-validated');
        });
    }
    
    // Admin message deletion
    const deleteMessageButtons = document.querySelectorAll('.delete-message');
    if (deleteMessageButtons.length > 0) {
        deleteMessageButtons.forEach(button => {
            button.addEventListener('click', function() {
                const messageId = this.getAttribute('data-id');
                if (confirm('Are you sure you want to delete this message?')) {
                    deleteMessage(messageId);
                }
            });
        });
    }
    
    // Admin project deletion
    const deleteProjectButtons = document.querySelectorAll('.delete-project');
    if (deleteProjectButtons.length > 0) {
        deleteProjectButtons.forEach(button => {
            button.addEventListener('click', function() {
                const projectId = this.getAttribute('data-id');
                if (confirm('Are you sure you want to delete this project?')) {
                    deleteProject(projectId);
                }
            });
        });
    }
    
    // Dark mode toggle
    const darkToggle = document.querySelector('.dark-toggle');
    if (darkToggle) {
        darkToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
        
        // Check for saved dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    }
});

// Function to delete a message
function deleteMessage(messageId) {
    fetch(`/api/delete_message/${messageId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messageElement = document.querySelector(`#message-${messageId}`);
            if (messageElement) {
                messageElement.remove();
            }
        } else {
            alert('Error deleting message');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting message');
    });
}

// Function to delete a project
function deleteProject(projectId) {
    fetch(`/api/delete_project/${projectId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const projectElement = document.querySelector(`#project-${projectId}`);
            if (projectElement) {
                projectElement.remove();
            }
        } else {
            alert('Error deleting project');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting project');
    });
}
