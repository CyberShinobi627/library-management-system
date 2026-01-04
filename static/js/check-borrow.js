const bodyColumn = document.querySelector("#body-col");
const tableRows = bodyColumn.children;

for(let row of tableRows){
    const oidColumn = row.children[0];
    const buttonRow = row.children[7].children;
    if(buttonRow.length){
        buttonRow[0].addEventListener("click", () => {
            (async () => {
                const removeUrl = "/user/remove-borrow";
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
}
