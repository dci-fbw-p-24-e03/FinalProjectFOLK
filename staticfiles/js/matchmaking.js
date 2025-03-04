document.addEventListener("htmx:afterRequest", function(event) {
    let response = event.detail.xhr.responseText;
    try {
        let data = JSON.parse(response);
        if (data.status === "matched") {
            // Redirect immediately to the game room.
            window.location.href = "/game-room/" + data.room_id + "/";
        } else if (data.status === "waiting") {
            // Redirect to waiting room.
            window.location.href = data.redirect;
        }
    } catch (error) {
        console.error("Could not parse response:", response);
    }
});