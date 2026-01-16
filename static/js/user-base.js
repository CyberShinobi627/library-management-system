const navLeft = document.querySelector(".nav-left");
const navs = navLeft.children;
const navPath = location.pathname;
for(const nav of navs){
    nav.classList.toggle("active", (navPath === nav.pathname) || (navPath === "/user/" && nav.pathname === "/user/profile/"));
}
