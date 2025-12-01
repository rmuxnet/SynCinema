(function() {
    'use strict';

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (prefersReducedMotion.matches) return;
    
    const snowContainer = document.createElement('div');
    snowContainer.className = 'snow-container';
    
    const snowSymbols = ['❄', '❅', '❆', '•', '·', '*'];

    function createSnowflake() {
        if (document.hidden) {
            setTimeout(createSnowflake, 100);
            return;
        }

        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';
        
        const span = document.createElement('span');
        const symbol = snowSymbols[Math.floor(Math.random() * snowSymbols.length)];
        span.innerHTML = symbol;
        snowflake.appendChild(span);
        
        const size = Math.random() * 1.5 + 0.8; 
        snowflake.style.fontSize = `${size}rem`;
        snowflake.style.left = `${Math.random() * 100}%`;
        
        let opacity;
        if (size < 1.2) {
            opacity = Math.random() * 0.3 + 0.2; 
            snowflake.style.zIndex = 0;
        } else {
            opacity = Math.random() * 0.4 + 0.6; 
            snowflake.style.zIndex = 1;
        }
        snowflake.style.setProperty('--opacity-target', opacity);

        const fallDuration = Math.random() * 5 + 7; 
        const swayDuration = Math.random() * 2 + 2; 
        const swayAmount = Math.random() * 100 - 50; 
        const spinDuration = Math.random() * 5 + 3; 
        const spinDeg = (Math.random() > 0.5 ? 360 : -360) * (Math.random() + 0.5); 
        
        snowflake.style.setProperty('--sway-amount', `${swayAmount}px`);
        snowflake.style.setProperty('--rotate-deg', `${spinDeg}deg`);
        
        snowflake.style.animation = `
            fall ${fallDuration}s linear infinite, 
            sway ${swayDuration}s ease-in-out infinite alternate
        `;
        span.style.animation = `spin ${spinDuration}s linear infinite`;
        
        const delay = Math.random() * 5;
        snowflake.style.animationDelay = `${delay}s, ${delay}s`;
        span.style.animationDelay = `${delay}s`; 
        
        snowContainer.appendChild(snowflake);
        
        setTimeout(() => {
            if (snowflake.parentNode) snowflake.remove();
            createSnowflake(); 
        }, (fallDuration + delay) * 1000);
    }
    
    function init() {
        document.body.insertBefore(snowContainer, document.body.firstChild);
        
        const isMobile = window.innerWidth < 768;
        const numberOfFlakes = isMobile ? 50 : 150;
        
        for (let i = 0; i < numberOfFlakes; i++) {
            setTimeout(() => createSnowflake(), i * 30);
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();