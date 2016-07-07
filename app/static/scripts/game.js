var current_player = -1;

toastr.options = {
  "closeButton": true,
  "debug": false,
  "newestOnTop": false,
  "progressBar": false,
  "positionClass": "toast-top-right",
  "defaultPositionClass": "toast-top-right",
  "preventDuplicates": false,
  "onclick": null,
  "showDuration": "300",
  "hideDuration": "1000",
  "timeOut": "8000",
  "extendedTimeOut": "1000",
  "showEasing": "swing",
  "hideEasing": "linear",
  "showMethod": "fadeIn",
  "hideMethod": "fadeOut"
};

function build_chat_row(name, text) {
    var chat_row = document.createElement("div");
    chat_row.className = "chat-row";

    var chat_row_name = document.createElement("span");
    chat_row_name.className = "chat-row-name";
    chat_row_name.textContent = name + ": ";

    var chat_row_text = document.createElement("span");
    chat_row_text.className = "chat-row-text";
    chat_row_text.textContent = text;

    chat_row.appendChild(chat_row_name);
    chat_row.appendChild(chat_row_text);
    return chat_row;
}

function add_chat_message(data) {
    var new_row = build_chat_row(data.chat.from, data.chat.text);
    $("#chat").prepend(new_row);
}

function send_chat_message(socket, text) {
    var data = {
        message: "chat",
        text: text
    };
    socket.send(JSON.stringify(data));
}

$(document).ready(function(){

    var ws = new WebSocket("ws://" + location.host + "/ws" + location.pathname + "/" + player_number);
    var $input_message = $("#input-message");
    var $chat_btn = $("#chat-send");

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
                console.log.error('Unknown message type received!');
                console.log.error(data);
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
        }
    });

    $input_message.keyup(function(event){
        if(event.keyCode == 13){
            $chat_btn.click();
        }
    });

    $(document).on('click', '#chat-send', function(e){
        if ($input_message.val()) {
            send_chat_message(ws, $input_message.val());
            $input_message.val("");
        }
    });
});

function connect(data) {
    // TODO
    toastr.info(data.user.username + " is now online.");
}

function disconnect(data) {
    // TODO
    toastr.warning(data.user.username + " disconnected.");
}

function init_game(data) {
    // TODO
    console.log("Received initial data.");
}

function start_game() {
    console.log('Game started!');
    current_player = 1;

    toastr.success("Game started!");
    if (player_number == current_player) {
        toastr.success("It's your turn.");
    } else {
        toastr.success("It's opponent's turn. Please, wait.");
    }
}

function receive_move(data) {
    // TODO
    console.log('New move received!');
}

function finish(data) {
    // TODO
    toastr.success('Game finished!');
}

function flee(data) {
    // TODO
    toastr.info('Flee: ' + data.user.username);
}
