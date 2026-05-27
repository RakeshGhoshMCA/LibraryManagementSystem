const cards = document.querySelectorAll(".book-card");
const issueBtns = document.querySelectorAll(".issue-btn");


cards.forEach((card)=>{
    card.addEventListener("click",()=>{

        const id = card.dataset.id;
        window.location.href = `/book-details/${id}/`;
    });
});



issueBtns.forEach((button)=>{
    button.addEventListener("click",(event)=>{

        event.stopPropagation();
        const id = button.dataset.id;
        window.location.href = `/issue-book/${id}/`;
    });
});