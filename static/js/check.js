const bodyColumn = document.querySelector("#body-col");
const tableRows = bodyColumn.children;

for(let row of tableRows){
    const oidColumn = row.children[0];
    const removeBorrow = row.children[6].children[0];
    removeBorrow.addEventListener("click", () => {
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
            if(!tableRows.length){
                const bookTable = document.querySelector("#book-table");
                bookTable.remove();
                let emptyMsg = document.querySelector("#empty-msg");
                emptyMsg.innerText = "No borrowed book";
            }
        })();
    });
}
