// Edunify Global Javascript

document.addEventListener("DOMContentLoaded", function() {
    // Dynamic styling changes on scroll
    const navbar = document.querySelector(".glass-nav");
    if (navbar) {
        // Run once on load to catch current position
        if (window.scrollY > 30) {
            navbar.classList.add("scrolled");
        }
        
        window.addEventListener("scroll", function() {
            if (window.scrollY > 30) {
                navbar.classList.add("scrolled");
            } else {
                navbar.classList.remove("scrolled");
            }
        });
    }

    // Auto dismiss alert messages after 5 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll(".alert");
        alerts.forEach(function(alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Theme toggler logic
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const themeToggleIcon = document.getElementById("themeToggleIcon");

    if (themeToggleBtn && themeToggleIcon) {
        // Set initial icon based on active theme
        function updateToggleIcon(theme) {
            // Remove any inline style that might override classes
            themeToggleIcon.removeAttribute('style');
            if (theme === 'dark') {
                themeToggleIcon.className = "bi bi-sun-fill fs-5";
                themeToggleIcon.style.color = "#fbbf24";
            } else {
                themeToggleIcon.className = "bi bi-moon-stars fs-5";
                themeToggleIcon.style.color = "var(--text-muted)";
            }
        }

        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        updateToggleIcon(currentTheme);

        themeToggleBtn.addEventListener("click", function() {
            const activeTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleIcon(newTheme);
        });
    }
});
