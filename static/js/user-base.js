const navLeft = document.querySelector(".nav-left");
const navs = navLeft.children;
const urlPath = location.pathname;
for(const nav of navs){
    nav.classList.toggle("active", (urlPath === nav.pathname) || (urlPath === "/user/" && nav.pathname === "/user/profile/"));
}
