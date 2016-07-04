var current_player = 2;

$(document).ready(function(){

    var ws = new WebSocket("ws://" + location.host + "/ws" + location.pathname + "/" + player_number);

    ws.onmessage = function (msg) {
        var data = JSON.parse(msg.data);
        console.log(data); // for debug
        switch (data.message) {
            case 'connect':
                connect(data);
                break;
            case 'disconnect':
                disconnect(data);
                break;
            case 'initial':
                init_game(data);
                break;
            case 'start':
                start_game();
                break;
            case 'move':
                receive_move(data);
                break;
            case 'finish':
                finish(data);
                break;
            case 'flee':
                flee(data);
                break;
            case 'chat':
                add_chat_message(data);
                break;
            default:
                console.log.error('Unknown message type received!')
                console.log.error(data)
        }

    };
    $(document).on('click', '.tile-button', function(e){
        // TODO
        if (player_number == current_player) {
            var data = {
                message: 'move',
                game: game_id,
                user: player_number,
                cell: e.target.id.split('-')
            };
            ws.send(JSON.stringify(data));
        };
    });
});

function connect(data) {
    // TODO
    console.log(data.user.username + " is now online.")
}

function disconnect(data) {
    // TODO
    console.log(data.user.username + " disconnected.")
}

function init_game(data) {
    // TODO
    console.log("Received initial data.")
}

function start_game() {
    // TODO
    console.log('Game started!');
}

function receive_move(data) {
    // TODO
    console.log('New move received!');
}

function finish(data) {
    // TODO
    console.log('Game finished!');
}

function flee(data) {
    // TODO
    console.log('Flee: ' + data.user.username);
}

function add_chat_message(data) {
    // TODO
    console.log(data.chat.from + ': ' + data.chat.text)
}

