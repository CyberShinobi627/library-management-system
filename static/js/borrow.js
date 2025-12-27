const allBooks = document.querySelector(".all-books");
const bookList = document.querySelector("#book-list");

let bookInfo = [];
const searchInput = document.querySelector("#search-input");
searchInput.addEventListener("input", (searchKey) => {
    const searchValue = searchKey.target.value.toLowerCase();
    bookInfo.forEach((book) => {
        const isVisible = book["bname"].toLowerCase().includes(searchValue) || book["bauthor"].toLowerCase().includes(searchValue);
        book["element"].classList.toggle("hide", !isVisible);
    });
});

(async () => {
    const url = "/profile/borrow-book";
    const params = {
        "method": "POST",
        "headers": {"Content-Type": "application/json"}
    };
    
    const response = await fetch(url, params);
    const jsonData = await response.json();
    const books = jsonData["books"];
    const borrowBids = jsonData["borrow_bids"];
    bookInfo = books.map((book) => {
        const bookContent = bookList.content.cloneNode(true).children[0];
        let bookName = bookContent.querySelector("#book-name");
        let bookAuthor = bookContent.querySelector("#book-author");
        let button = bookContent.querySelector("button");
        let stock_msg = bookContent.querySelector("#stock-msg");
        bookName.textContent = book[1];
        bookAuthor.textContent = book[2];

        if(borrowBids.includes(book[0])){
            button.disabled = true;
            button.style.opacity = 0.6;
            button.style.cursor = "not-allowed";
            button.innerText = "Borrowed";
        }
        else if(!book[3]){
            button.remove();
            stock_msg.innerText = "Item out of stock";
        }

        button.addEventListener("click", () => {
            // button.style.backgroundColor = "red";
            button.disabled = true;
            button.style.opacity = 0.6;
            button.style.cursor = "not-allowed";
            button.innerText = "Borrowed";
            (async () => {
                const borrowUrl = "/profile/add-borrow";
                const borrowParams = {
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "body": JSON.stringify({
                        "bookName": book[1],
                        "bookAuthor": book[2]
                    })
                };

                const borrowRes = await fetch(borrowUrl, borrowParams);
                const borrowData = await borrowRes.json();
                const isAdded = borrowData["success"];
                // console.log(isAdded);
            })();
        });
        
        allBooks.append(bookContent);
        return {
            "bname": book[1],
            "bauthor": book[2],
            "element": bookContent
        };
    })
})();
