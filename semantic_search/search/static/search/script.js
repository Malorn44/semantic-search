
// For fixing some choppy animation loading
window.onload = function() {
    var slider = document.querySelector('.slider');
    slider.classList.add('transition');
};

// for fixing the behavior of the semantic search slider
// Enter should be used to toggle, not submit the form when slider is focused
window.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector('.switch input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.click();
        }
    });
});
