const bodyColumn = document.querySelector("#body-col");
const tableRows = bodyColumn.children;

for(let row of tableRows){
    const oidColumn = row.children[0];
    // console.log(oidColumn);
    const acceptButton = row.children[4].children[0];
    // console.log(acceptButton);
    acceptButton.addEventListener("click", () => {
        (async () => {
            const acceptUrl = "/keeper/accept-order";
            const acceptParams = {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({
                    "oid": oidColumn.innerText
                })
            };

            const acceptResponse = await fetch(acceptUrl, acceptParams);
            const acceptJson = await acceptResponse.json();
            const isAccepted = acceptJson["success"];
            console.log(isAccepted);
            if(isAccepted){
                row.remove();
            }
        })();
        // console.log(row);
    });

    const rejectButton = row.children[5].children[0];
    // console.log(rejectButton);
    rejectButton.addEventListener("click", () => {
        (async () => {
            const rejectUrl = "/keeper/reject-order";
            const rejectParams = {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({
                    "oid": oidColumn.innerText
                })
            };

            const rejectResponse = await fetch(rejectUrl, rejectParams);
            const rejectJson = await rejectResponse.json();
            const isRejected = rejectJson["success"];
            console.log(isRejected);
            if(isRejected){
                row.remove();
            }
        })();
    });
}
