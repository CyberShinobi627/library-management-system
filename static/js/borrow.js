const allBooks = document.querySelector(".all-books");
const bookList = document.querySelector("#book-list");

let bookInfo = [];
const searchInput = document.querySelector("#search-input");
searchInput.addEventListener("input", (kw) => {
    const kwVal = kw.target.value.toLowerCase();
    // console.log(bookInfo);
    bookInfo.forEach((book) => {
        // console.log(book["qty"]);
        const isVisible = book["bname"].toLowerCase().includes(kwVal) || book["bauthor"].toLowerCase().includes(kwVal);
        book["element"].classList.toggle("hide", !isVisible);
        // console.log(temp);
    });
});

(async () => {
    const url = "/profile/borrow-book";
    const params = {
        "method": "POST",
        "headers": {"Content-Type": "application/json"}
    };
    
    let response = await fetch(url, params);
    let jsonData = await response.json();
    const books = jsonData["books"];
    // console.log(books);
    bookInfo = books.map((book) => {
        const bookContent = bookList.content.cloneNode(true).children[0];
        let bookName = bookContent.querySelector("#book-name");
        let bookAuthor = bookContent.querySelector("#book-author");
        let button = bookContent.querySelector("button");
        let stock_msg = bookContent.querySelector("#stock-msg");
        button.addEventListener("click", () => {
            if(button.innerText == "Add"){
                button.style.backgroundColor = "red";
                button.innerText = "Remove";
                (async () => {
                    const borrowUrl = "/profile/add-borrow";
                    const borrowParams = {
                        "method": "POST",
                        "headers": {"Content-Type": "application/json"},
                        "body": JSON.stringify({
                            "bookName": book[0],
                            "bookAuthor": book[1]
                        })
                    };
                    let borrowRes = await fetch(borrowUrl, borrowParams);
                    let borrowData = await borrowRes.json();
                    let qty = borrowData["qty"];
                    if(!qty){
                        console.log(qty);
                        button.remove();
                        stock_msg.innerText = "Item out of stock";
                    }
                    // console.log(book[2]);
                })();
            }
            else{
                button.style.backgroundColor = "#04c07b";
                button.innerText = "Add";
            }
        });
        bookName.textContent = book[0];
        bookAuthor.textContent = book[1];
        if(!book[2]){
            console.log(book[2]);
            button.remove();
            stock_msg.innerText = "Item out of stock";
        }
        allBooks.append(bookContent);
        return {"bname": book[0],
            "bauthor": book[1],
            // "qty": book[2],
            "element": bookContent
        };
    })
    // console.log(users);
})();
