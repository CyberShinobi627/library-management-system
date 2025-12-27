const bodyColumn = document.querySelector("#body-col");
const tableRows = bodyColumn.children;
// console.log(bookTable);

for(let row of tableRows){
    const oidColumn = row.children[0];
    const removeBorrow = row.children[6].children[0];
    // console.log(removeBorrow);
    removeBorrow.addEventListener("click", () => {
        // button.innerText = "Add";
        (async () => {
            const removeUrl = "/profile/remove-borrow";
            const removeParams = {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({
                    "oid": oidColumn.innerText
                })
            };

            const removeRes = await fetch(removeUrl, removeParams);
            const removeData = await removeRes.json();
            const isRemoved = removeData["success"];
            if(isRemoved){
                row.remove();
            }
            console.log(tableRows.length);
            if(!tableRows.length){
                const bookTable = document.querySelector("#book-table");
                console.log(bookTable);
                bookTable.remove();
                let emptyMsg = document.querySelector("#empty-msg");
                emptyMsg.innerText = "No borrowed book";
                // document.writeln("Wow such empty");
            }
        })();
    });
}
