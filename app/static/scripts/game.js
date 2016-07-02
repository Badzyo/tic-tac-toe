$(document).ready(function(){
    var ws = new WebSocket("ws://" + location.host + "/ws" + location.pathname + "/" + player_number);
    ws.onmessage = function (msg) {
        var message = JSON.parse(msg.data);
        console.log(message);
        // TODO
    };
    $(document).on('click', '.tile-button', function(e){
        // TODO
        ws.send(e.target.id);
    });
});

