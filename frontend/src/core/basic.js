export function basicLogout(c) {
    var a;
    var b = "You should be logged out now.";
    try {
        a = document.execCommand("ClearAuthenticationCache");
    } catch (d) {}

    if (!a) {
        if (window.XMLHttpRequest) {
            a = new window.XMLHttpRequest();
            a.open(
                "HEAD",
                c || window.location.href,
                true,
                "logout",
                new Date().getTime().toString()
            );
            a.send("");
            a = true;
        } else {
            // eslint-disable-next-line no-undef
            if (window.ActiveXObject) {
                // eslint-disable-next-line no-undef
                a = new ActiveXObject("Microsoft.XMLHTTP");
            } else {
                a = undefined;
            }
        }
    }

    if (!a) {
        b = "Your browser is too old or too weird to support log out functionality. Close all windows and restart the browser.";
    }
    alert(b);
}
