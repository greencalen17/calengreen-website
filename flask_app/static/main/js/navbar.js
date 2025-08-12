document.addEventListener("DOMContentLoaded", function() {
    const menuIcon = document.querySelector('.nav-container menu');
    const navContainer = document.querySelector('.nav-container');
    
    menuIcon.addEventListener('click', function() { // click event
        navContainer.classList.toggle('open');
    });
});
