var current_player = -1;
var $win_label = $('<span class="label label-success result-label">Winner</span>');
var $lose_label = $('<span class="label label-info result-label">Loser</span>');

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
        mark = '<span class="fa fa-times x-mark" id="mark" aria-hidden="true"></span>'
    } else {
        mark = '<span class="fa fa-circle-o o-mark" id="mark" aria-hidden="true"></span>'
    }
    $(tile_id).append(mark);
}

function show_arrow(number) {
    $('.arrow'+number).css({ 'opacity' : 1 });
}

function hide_arrow(number) {
    $('.arrow'+number).css({ 'opacity' : 0 });
}

function show_result(result, player_number) {
    $('#player' + player_number + '>div>div>h3')
        .append((result == player_number) ? $win_label : $lose_label);
}

function show_results(result, players) {
    players.forEach(function(player){
        show_result(result, player);
    });
}

function update_player_status(player) {
    var panel_id = '#player' + player.player_number;
    $(panel_id + '>div>.panel-body').text(player.name ? player.name : '___');
    $(panel_id + '>div>div>h3').text(player.online ? "online" : "offline");
    $(panel_id + '>.player-panel')
        .removeClass('panel-primary panel-danger')
        .addClass(player.online ? "panel-primary" : "panel-danger");

    if ($.inArray(game_result, [1, 2]) >= 0) {
        show_results(game_result, [player.player_number]);
    }
}

function update_spectators_list(user) {
    add_spectator_to_list(user);
}

function draw_line(id1, id2){
        var min_width = 12;
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
        var canvas_width = p.x1 - p.x;
        var canvas_height = p.y1 - p.y;
        canvas_width = (canvas_width > min_width) ? canvas_width : min_width;
        canvas_height = (canvas_height > min_width) ? canvas_height : min_width;
        var c = $('<canvas/>').attr({
            'width': canvas_width,
            'height': canvas_height
        }).css({
            'position': 'absolute',
            'left': p.x,
            'top': p.y,
            'z-index': 1
        }).appendTo($('body'))[0].getContext('2d');

        // draw line
        c.strokeStyle = '#f00';
        c.lineWidth = min_width;
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
    if (data.user.player_number < 3) {
        update_player_status(data.user);
        remove_user_from_list(data.user);
        add_player_to_list(data.user);
    } else {
        add_spectator_to_list(data.user);
        toastr.info(data.user.name + " is watching the game.");
    }
}

function disconnect(data) {
    if (data.user.player_number < 3) {
        update_player_status(data.user);
    }
    remove_user_from_list(data.user);
}

function init_game(data) {
    current_player = data.current_player;
    show_arrow(current_player);

    data.players.forEach(function(player){
        update_player_status(player);
        add_player_to_list(player);
    });

    data.spectators.forEach(function(user_name) {
        update_spectators_list(user_name);
    });

    data.moves.forEach(function(move) {
        draw_tile_mark(move);
    });
}

function start_game() {
    current_player = 1;
    game_state = 1;
    show_arrow(current_player);
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
    hide_arrow(current_player);
    current_player = current_player % 2 + 1;
    show_arrow(current_player);
    if (player_number == current_player) {
        toastr.info("It's your turn now!")
    }
}

function finish(data) {
    game_state = 2;
    game_result = data.finish.result;
    move = data.move;
    draw_tile_mark(move);
    if (data.finish.result != 0) {
        var id1 = "#" + data.finish.win_line[0].x + "-" + data.finish.win_line[0].y;
        var id2 = "#" + data.finish.win_line[1].x + "-" + data.finish.win_line[1].y;
        draw_line(id1, id2);
        toastr.info('Game finished!');
    } else {
        toastr.success('Draw!');
    }
    show_results(data.finish.result, [1, 2]);
    hide_arrow(current_player);
    $('#flee-btn').remove();
    $('.mid-button').wrapInner('<a href="/" class="btn btn-block btn-primary" id="join-btn">BACK</a>');
    current_player = -1;
}

function flee(data) {
    game_state = 2;
    game_result = data.finish.result;
    show_results(data.finish.result, [1, 2]);
    update_player_status(data.user);
    toastr.info('Opponent has left the game. You win!');
}

function get_user_list_item(user) {
    var player_div = document.createElement('div');
    player_div.setAttribute("id", user.player_number);
    player_div.textContent = user.name;
    return player_div;
}

function add_player_to_list(player) {
    $("#players-list").append(get_user_list_item(player));
}

function add_spectator_to_list(player) {
    $("#spectators-list").append(get_user_list_item(player));
}

function remove_user_from_list(user) {
    $('#' + user.player_number).remove();
}

$(document).ready(function(){
    game_result = (game_result == 'None') ? -1 : game_result;

    var ws = new WebSocket("ws://" + location.host + "/ws" + location.pathname + "/" + player_number);
    var $input_message = $("#input-message");
    var $chat_btn = $("#chat-send");

    ws.onmessage = function (msg) {
        var data = JSON.parse(msg.data);
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
        if ((e.target.id != 'mark') && (e.target.innerHTML.length == 0)) {
            if (player_number == current_player) {
            var data = {
                message: 'move',
                game: game_id,
                user: player_number,
                cell: e.target.id.split('-')
            };
            ws.send(JSON.stringify(data));
            }
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

    $(document).on('click', '#flee-btn', function(e){
        var data = {
            message: "flee"
        };
        ws.send(JSON.stringify(data));
        $('#flee-form').submit();
    });

    $(document).on('click', '#join-btn', function(e){
        $('#join-form').submit();
    });
});