document.addEventListener("DOMContentLoaded", () => {
    console.log("Global library navigation routing active.");

    // Single global listener on the document body handles dynamic components seamlessly
    document.body.addEventListener("click", (event) => {
        
        // 1. CHOOSE ACTION: ISSUE BOOK BUTTON CLICKED
        const issueBtn = event.target.closest(".issue-btn");
        if (issueBtn) {
            // Stop the event from bubbling up to prevent triggering the card click details route
            event.stopPropagation();
            
            const bookId = issueBtn.dataset.id;
            if (bookId && bookId !== "undefined") {
                // Aligns with your custom URL routing rules
                window.location.href = `/issue-book/${bookId}/`;
            } else {
                console.error("Routing Error: Target button missing valid dataset ID.");
            }
            return; // Terminate execution line
        }

        // 2. CHOOSE ACTION: WHOLE BOOK CARD WRAPPER CLICKED
        const bookCard = event.target.closest(".book-card");
        if (bookCard) {
            // Query internal button node structure to parse out the contextual database ID
            const innerBtn = bookCard.querySelector(".issue-btn");
            if (innerBtn) {
                const bookId = innerBtn.dataset.id;
                if (bookId && bookId !== "undefined") {
                    // Aligns with your custom URL routing rules
                    window.location.href = `/book-details/${bookId}/`;
                } else {
                    console.error("Routing Error: Associated card button component missing dataset ID.");
                }
            } else {
                console.error("Routing Error: Clicked card layout does not embed an active action button.");
            }
        }
    });
});