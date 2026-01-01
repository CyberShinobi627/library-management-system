const forgotId = document.querySelector("#forgot-id");
const bookInfo = document.querySelector(".book-info");

forgotId.addEventListener("click", () => {
    bookInfo.classList.toggle("hide");
});

const fetchId = document.querySelector("#fetch-id");
fetchId.addEventListener("click", () => {
    const bname = document.querySelector("#bname");
    const bauthor = document.querySelector("#bauthor");
    (async () => {
        const url = "/keeper/fetch-id";
        const params = {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": JSON.stringify({
                "bname": bname.value,
                "bauthor": bauthor.value
            })
        };

        const response = await fetch(url, params);
        const jsonData = await response.json();
        const bid = jsonData["bid"];
        console.log(bid);

        if(bid){
            let bidInput = document.querySelector("#bid-input");
            bidInput.value = bid;
        }
        else{
            let showMsg = document.querySelector("#show-msg");
            showMsg.innerText = "Invalid Book name or Author name !!!";
            showMsg.style.color = "red";
        }
    })();
});
