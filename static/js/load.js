document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const btn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('loadingSpinner');

            // Prevent double submission if already loading
            if (btn.disabled) {
                e.preventDefault();
                return;
            }

            // Set loading state
            btn.disabled = true;
            btn.classList.remove('hover:from-blue-500', 'hover:to-indigo-500', 'active-scale');
            spinner.classList.remove('hidden');
            btnText.textContent = 'Entering Cinema...';
        });
    }
});