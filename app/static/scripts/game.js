$(document).ready(function(){
    var ws = new WebSocket("ws://" + location.host + "/ws" + location.pathname);
    ws.onmessage = function (msg) {
        var message = JSON.parse(msg.data);
        // TODO
    };
    $(document).on('click', '.tile-button', function(e){
        // TODO
        ws.send(e.target.id);
    });
});

