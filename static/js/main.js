// main.js — students will add JavaScript here as features are built

// Wait for the DOM to be fully loaded before accessing elements
document.addEventListener('DOMContentLoaded', function() {
    // Get the modal
    var modal = document.getElementById("how-it-works-modal");

    // Get the button that opens the modal
    var btn = document.getElementById("see-how-it-works");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close-modal")[0];

    // Check if elements exist before adding event listeners
    if (modal && btn && span) {
        // When the user clicks the button, open the modal
        btn.onclick = function(event) {
            event.preventDefault(); // Prevent default link behavior
            modal.style.display = "block";
        }

        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
            modal.style.display = "none";
            // Stop the YouTube video when closing the modal
            var iframe = modal.querySelector("iframe");
            if (iframe) {
                iframe.src = ""; // Stop the video by clearing the src
            }
        }

        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
                // Stop the YouTube video when clicking outside
                var iframe = modal.querySelector("iframe");
                if (iframe) {
                    iframe.src = ""; // Stop the video by clearing the src
                }
            }
        }
    }
});
