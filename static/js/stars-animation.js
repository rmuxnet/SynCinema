// Raining Stars Animation for Login Page
(function() {
    'use strict';
    
    // Create stars container immediately
    const starsContainer = document.createElement('div');
    starsContainer.className = 'stars-container';
    
    // Function to create a single star
    function createStar() {
        const star = document.createElement('div');
        star.className = 'star';
        
        // Random size between 3-6px
        const size = Math.random() * 3 + 3;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // Random horizontal position
        star.style.left = `${Math.random() * 100}%`;
        
        // Random animation duration between 4-10 seconds
        const duration = Math.random() * 6 + 4;
        star.style.animationDuration = `${duration}s`;
        
        // Random delay to stagger the stars
        const delay = Math.random() * 3;
        star.style.animationDelay = `${delay}s`;
        
        starsContainer.appendChild(star);
        
        // Remove star after animation completes and create a new one
        setTimeout(() => {
            if (star.parentNode) {
                star.remove();
            }
            createStar();
        }, (duration + delay) * 1000);
    }
    
    // Initialize when DOM is ready
    function init() {
        document.body.insertBefore(starsContainer, document.body.firstChild);
        
        // Create initial set of stars
        const numberOfStars = 60;
        for (let i = 0; i < numberOfStars; i++) {
            setTimeout(() => createStar(), i * 50);
        }
    }
    
    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
