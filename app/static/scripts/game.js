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

function draw_tile_mark(move) {
    tile_id = "#" + move.x + "-" + move.y;

    if (move.player == 1){
        mark = '<span class="fa fa-times x-mark" aria-hidden="true"></span>'
    } else {
        mark = '<span class="fa fa-circle-o o-mark" aria-hidden="true"></span>'
    }
    $(tile_id).append(mark);
}

function draw_line(id1, id2){
        var $t1 = $(id1);
        var $t2 = $(id2);

        // find offset positions
        var ot1 = {
            x: $t1.offset().left + $t1.width() / 2,
            y: $t1.offset().top + $t1.height() / 2
        };
        var ot2 = {
            x: $t2.offset().left + $t2.width() / 2,
            y: $t2.offset().top + $t2.height() / 2
        };

        // x,y = top left corner
        // x1,y1 = bottom right corner
        var p = {
            x: ot1.x < ot2.x ? ot1.x : ot2.x,
            x1: ot1.x > ot2.x ? ot1.x : ot2.x,
            y: ot1.y < ot2.y ? ot1.y : ot2.y,
            y1: ot1.y > ot2.y ? ot1.y : ot2.y
        };

        // create canvas between those points
        var c = $('<canvas/>').attr({
            'width': p.x1 - p.x,
            'height': p.y1 - p.y
        }).css({
            'position': 'absolute',
            'left': p.x,
            'top': p.y,
            'z-index': 1
        }).appendTo($('body'))[0].getContext('2d');

        // draw line
        c.strokeStyle = '#f00';
        c.lineWidth = 10;
        c.beginPath();
        c.moveTo(ot1.x - p.x, ot1.y - p.y);
        c.lineTo(ot2.x - p.x, ot2.y - p.y);
        c.stroke();
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
    move = data.move;
    draw_tile_mark(move);
    current_player = current_player % 2 + 1;
    if (player_number == current_player) {
        toastr.info("It's your turn now!")
    }
}

function finish(data) {
    move = data.move;
    draw_tile_mark(move);
    var id1 = "#" + data.finish.win_line[0].x + "-" + data.finish.win_line[0].y;
    var id2 = "#" + data.finish.win_line[1].x + "-" + data.finish.win_line[1].y;
    draw_line(id1, id2);
    current_player = -1;
    toastr.success('Game finished!');
}

function flee(data) {
    // TODO
    toastr.info('Flee: ' + data.user.username);
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