const allBooks = document.querySelector(".all-books");
const bookList = document.querySelector("#book-list");

let bookInfo = [];
const searchInput = document.querySelector("#search-input");
searchInput.addEventListener("input", (kw) => {
    const kwVal = kw.target.value.toLowerCase();
    // console.log(bookInfo);
    bookInfo.forEach((book) => {
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
        const button = bookContent.querySelector("button");
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
                    console.log(borrowData);
                })();
            }
            else{
                button.style.backgroundColor = "#04c07b";
                button.innerText = "Add";
            }
        });
        bookName.textContent = book[0];
        bookAuthor.textContent = book[1];
        allBooks.append(bookContent);
        return {"bname": book[0], "bauthor": book[1], "element": bookContent};
    })
    // console.log(users);
})();
