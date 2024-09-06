// // Get all the div elements with a specific class
// const divs = document.querySelectorAll('.clickable-div');

// // Add a click event listener to each div
// divs.forEach(div => {
//     div.addEventListener('click', () => {
//         // Perform navigation logic here
//         // For example, you can redirect to a new page or update the content dynamically
//         const url = div.dataset.url; // Assuming the URL is stored in a 'data-url' attribute of each div
//         window.location.href = url;
//     });
// });

document.addEventListener('DOMContentLoaded', function() {
    const postCards = document.querySelectorAll('.clickable-post-card');

    postCards.forEach(card => {
        card.addEventListener('click', function(event) {
            // Navigate to the URL specified in the data-url attribute
            const url = this.getAttribute('data-url');
            window.location.href = url;
        });
    });

    // Prevent click events from propagating on interactive elements
    const interactiveElements = document.querySelectorAll('button, a');
    interactiveElements.forEach(element => {
        element.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
});