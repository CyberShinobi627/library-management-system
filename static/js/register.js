const userInput = document.querySelector("#user-input");
const userMsg = document.querySelector("#user-msg");
userInput.addEventListener("input", (event) => {
    const userSearch = event.target.value;
    // console.log(userSearch.length);
    if(userSearch.length < 3){
        userMsg.innerText = "Username must contain minimum 3 characters";
        userMsg.style.color = "red";
    }
    else{
        (async () => {
            const url = "/check-user";
            const params = {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({
                    "userSearch": userSearch
                })
            };
    
            const response = await fetch(url, params);
            const jsonData = await response.json();
            const userExist = jsonData["user_exist"];
            // console.log(userExist);
            if(userExist){
                userMsg.innerText = "Username already exist";
                userMsg.style.color = "red";
            }
            else{
                userMsg.innerText = "Username available";
                userMsg.style.color = "green";
            }
        })();
    }
});

const submitBtn = document.querySelector("#submit-btn");
submitBtn.addEventListener("click", (event) => {
    // console.log(userInput.value);
    const userSearch = userInput.value;
    if(userSearch < 3){
        userMsg.innerText = "Username must contain atleast 3 characters";
        userMsg.style.color = "red";
    }
    else{
        (async () => {
            const url = "/check-user";
            const params = {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": JSON.stringify({
                    "userSearch": userInput.value
                })
            };
            
            const response = await fetch(url, params);
            const jsonData = await response.json();
            const userExist = jsonData["user_exist"];
            // console.log(userExist);
    
            if(userExist){
                const password = document.querySelector("#password");
                password.value = '';
                // console.log(password.value);
            }
            else{
                const registerForm = document.querySelector("#register-form");
                registerForm.submit();
            }
        })();
    }
    event.preventDefault();
});
