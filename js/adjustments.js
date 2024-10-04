
function loadGameUrl() {
    var game = decodeURIComponent(location.hash);
    if (game) {
        sabaki.loadContent(game.substring(1), "sgf", {suppressAskForSave: true})
        .then( () => { sabaki.goToEnd() });
    }
}
sabaki.events.on("ready", loadGameUrl);
addEventListener("hashchange", loadGameUrl);

//    function updateGameUrl() {
//            var game = window.sabaki.getSGF();
//            window.location.hash = game;
//    }
//    window.sabaki.events.on("moveMake", updateGameUrl);
//    window.sabaki.events.on("toolUse", updateGameUrl);
//    window.sabaki.events.on("modeChange", updateGameUrl);

function copyMove() {
    var goban = document.getElementById("goban");
    html2canvas(goban, {
        windowWidth: 500,
        windowHeight: 500,
    }).then(canvas => {
        var moveName = document.querySelector("#properties div.inner p.header span").innerText;
        var gameTree = sabaki.state.gameTrees[sabaki.state.gameIndex];
        var gameName = sabaki.getGameInfo(gameTree).gameName || "";
        if (gameName == moveName) {
            moveName = "";
        } else if (gameName && moveName) {
            moveName = " - " + moveName;
        }

        const blob = new Blob(
            [`<b>${gameName}</b><i>${moveName}</i><img src="${canvas.toDataURL()}"><hr><code>${sabaki.getSGF()}</code>`],
            {type:"text/html"}
        );
        navigator.clipboard.write([
            new ClipboardItem({
                "text/html": blob
            })
        ]).then( () => {alert("Copied");});
    });
};


function copyImage() {
    var goban = document.getElementById("goban");
    html2canvas(goban, {
        windowWidth: 1000,
        windowHeight: 1000,
    }).then(canvas => {
        canvas.toBlob(blob => {
            navigator.clipboard.write([
                new ClipboardItem({
                    "image/png": blob
                })
            ]).then( () => {alert("Copied");});
        });
    });
};
