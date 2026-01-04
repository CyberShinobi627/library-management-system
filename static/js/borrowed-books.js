const borrowBody = document.querySelector("#borrow-body");
const tableRows = borrowBody.children;

for(let row of tableRows){
    const oidColumn = row.children[0];
    const returnButton = row.children[7].children[0];
    const borrowTable = document.querySelector("#borrow-table");
    let emptyMsg = document.querySelector("#empty-msg");
    returnButton.addEventListener("click", () => {
        (async () => {
            const returnUrl = "/keeper/return-book";
            const returnParams = {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({
                    "oid": oidColumn.innerText
                })
            };

            const returnResponse = await fetch(returnUrl, returnParams);
            const returnJson = await returnResponse.json();
            const isReturned = returnJson["success"];
            console.log(isReturned);
            if(isReturned){
                row.remove();
            }
            if(!tableRows.length){
                borrowTable.remove();
                emptyMsg.innerText = "No borrowed books.";
            }
        })();
    });
}
