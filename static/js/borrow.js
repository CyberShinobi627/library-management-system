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
    const url = "/user/borrow-book";
    const params = {
        "method": "POST",
        "headers": {"Content-Type": "application/json"}
    };
    
    const response = await fetch(url, params);
    const jsonData = await response.json();
    const books = jsonData["books"];
    const bids = jsonData["bids"];
    const statuses = jsonData["statuses"];
    bookInfo = books.map((book) => {
        const bookContent = bookList.content.cloneNode(true).children[0];
        let bookName = bookContent.querySelector("#book-name");
        let bookAuthor = bookContent.querySelector("#book-author");
        let button = bookContent.querySelector("button");
        let stock_msg = bookContent.querySelector("#stock-msg");
        bookName.textContent = book[1];
        bookAuthor.textContent = book[2];

        if(bids.includes(book[0])){
            const status = statuses[bids.indexOf(book[0])];
            console.log(book[0], status);
            if(status == 1){
                button.style.backgroundColor = "red";
                button.innerText = "Remove";
            }
            else if(status == 2){
                button.disabled = true;
                button.style.opacity = 0.6;
                button.style.cursor = "not-allowed";
                button.innerText = "Borrowed";
            }
        }
        else if(!book[3]){
            button.remove();
            stock_msg.innerText = "Item out of stock";
        }

        button.addEventListener("click", () => {
            if(button.innerText == "Add"){
                button.style.backgroundColor = "red";
                button.innerText = "Remove";
                (async () => {
                    const borrowUrl = "/user/add-borrow";
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
            }
            else{
                button.style.backgroundColor = "#04c07b";
                button.innerText = "Add";
                (async () => {
                    const removeUrl = "/user/remove-borrow";
                    const removeParams = {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "body": JSON.stringify({
                            "bookName": book[1],
                            "bookAuthor": book[2]
                        })
                    };

                    const removeRes = await fetch(removeUrl, removeParams);
                    const removeData = await removeRes.json();
                    const isRemoved = removeData["success"];
                    // console.log(isRemoved);
                })();
            }
        });
        
        allBooks.append(bookContent);
        return {
            "bname": book[1],
            "bauthor": book[2],
            "element": bookContent
        };
    })
})();
