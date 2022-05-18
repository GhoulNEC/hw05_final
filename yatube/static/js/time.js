function serverTime($time) {
    $time++;
    var dt = $time - (Math.floor($time / 86400) * 86400);
    var h = Math.floor(dt / 3600);
    var m = Math.floor((dt - h * 3600) / 60);
    var s = Math.floor((dt - h * 3600 - m * 60));
    if (h < 10) h = "0" + h;
    if (m < 10) m = "0" + m;
    if (s < 10) s = "0" + s;
    var obj = document.getElementById("serverTime");
    obj.innerHTML = "Серверное время: " + h + ":" + m + ":" + s;
    setTimeout(function () {
        serverTime($time);
    }, 1000);
}

setTimeout(function () {
    serverTime(Math.round(new Date().getTime()/1000.0) + 10800
);
}, 1000);