;(function (window, document, $, app, undefined) {

    var api = app.api = function (method, request, data, callback) {
        method = method || 'GET';
        data = data || {};
        request = request || '';
        var response = [];
        var action = "/deck/v2"+request;
        console.log(document.location.origin.toString()+action);

        // construct an HTTP request
        var xhr = new XMLHttpRequest();
        xhr.open(method, document.location.origin.toString()+action, true);
        xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

        xhr.onloadend = function () {
            // Todo: Check for server errors 5XX
            callback(JSON.parse(xhr.responseText), xhr);
        };

        // send the collected data as JSON
        xhr.send(JSON.stringify(data));

        /* Out with the old
        $.getJSON($.extend(true, {}, args, {
            "url": "http://45.55.209.220/deck/v2"+request,
            "method": method,
            "beforeSend": function(xhr){
                xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
            },
            "complete": function (xhr,) {
                var json = JSON.parse(xhr.responseText);
                callback(json, xhr, statusText);
            }
        }));
        */
    };

    app.api = $.extend(app.api, {
        cards: {},
        decks: {},
        rooms: {}
    });
    

    $.extend(app.api.cards, {
        // 'GET' on /cards/[pk]/
        get: function (pk, owner, callback) {
            var qs = '?';
            owner = !!owner;
            if (owner === false) {
                qs += '&owner=false';
            }
            api('GET', '/cards/'+pk+'/'+qs, { "owner": owner }, callback);
        },
        // GET on /cards/
        lookup: function (search, owner, since, callback) {
            var qs = '?';
            owner = !!owner;
            if (search.length > 0) {
                qs += '&search='+search;
            }
            if (owner === false) {
                qs += '&owner=false';
            }
            api('GET', '/cards/'+qs, null, (callback||$.noop));
        },
        // 'POST' on /cards/ returns the created card
        create: function (card, callback) {
            api('POST', '/cards/', [card], (callback||$.noop));
        }, 
        // 'DELETE' on /cards/[pk]
        delete: function (pk) {
            api('POST', '/cards/'+pk+'/', null, (callback||$.noop));
        }, 
        // 'PUT' on /cards/[pk]/ returns the updated card
        update: function (pk, card, callback) {
            api('POST', '/cards/'+pk+'/', null, (callback||$.noop));
        }, 
        // 'GET' on /cards/[pk]/copy/ returns the copied card
        copy: function (pk, callback) {}, 
    });

    $.extend(app.api.decks, {
        // 'GET' on /decks/[slug]/
        get: function (slug, owner, callback) {
            var qs = '?';
            owner = !!owner;
            if (owner === false) {
                qs += '&owner=false';
            }
            api('GET', '/decks/'+slug+'/'+qs, { "owner": owner }, callback);
        },
        lookup: function (search, owner, since, in_play) { // GET on /decks/
            var qs = '?';
            owner = !!owner;
            if (search.length > 0) {
                qs += '&search='+search;
            }
            if (owner === false) {
                qs += '&owner=false';
            }
            api('GET', '/decks/'+qs, null, (callback||$.noop));
        },
        // 'POST' on /decks/[slug]/add_cards/ returns the deck in simple format.
        add_cards: function (cards) {

        },
        // 'POST' on /decks/[slug]/remove_cards/ returns the deck in simple format.
        remove_cards: function (slug, callback) {

        },
        // 'POST' on /decks/[slug]/change_count/ returns the deck in simple format.
        change_count: function (slug, callback) {

        },
        // 'GET' on /decks/[slug]/get_random_card/
        get_random_card: function (slug, callback) {

        },
        // 'GET' on /decks/[slug]/play_view/
        play_view: function (slug, callback) {

        }
    });

    $.extend(app.api.rooms, {
        // 'GET' on /rooms/[slug]/
        get: function (slug, owner, callback) {
            var qs = '?';
            owner = !!owner;
            if (owner === false) {
                qs += '&own=false';
            }
            api('GET', '/rooms/'+slug+'/'+qs, { "owner": owner }, callback);
        },
        // 'GET' on /rooms/
        lookup:  function (owner, since) {
            var qs = '?';
            owner = !!owner;
            if (owner === false) {
                qs += '&own=false';
            }
            api('GET', '/rooms/'+qs, null, (callback||$.noop));
        },
        // 'GET' on /rooms/
        join:  function (key, callback) {
            api('GET', '/rooms/?key='+key, null, (callback||$.noop));
        },
        // 'GET' on /rooms/[slug]/get_current_card/
        // Returns the current displayed card from the deck
        get_current_card: function (slug, callback) {
            api('GET', '/rooms/'+slug+'/get_current_card/', null, (callback||$.noop));
        },
        // 'GET' on /rooms/[slug]/draw_card/
        // Discards the current card, draws a random card from the deck and sets
        // is as the current displayed card, removes it from the deck, and
        // returns the card.
        draw_card: function (slug, callback) {
            api('GET', '/rooms/'+slug+'/draw_card/', null, (callback||$.noop));
        },
        // 'GET' on /rooms/[slug]/stop_game/
        // Sets the deck in play. Clears cards_in_deck, cards_in_discard, and
        // card displaed. Explodes all cards (the ones with counts) in the deck,
        // and inserts a temp card for each that it needs for the defined count.
        // 
        // Returns the deck in the 'in game' view.
        //
        // Permissions: User must be owner of room.
        start_game: function (slug) {

        },
        // Clears cards_in_deck, cards_in_discard, and card displaed. Sets deck as not in play. Returns the game room.
        //
        // Permissions: User must be owner of room.
        stop_game: function (slug) {

        },
        // 'GET' on /rooms/[slug]/close_room/
        close_room: function (slug) {

        },
        // 'GET' on /rooms/[slug]/reset_deck/
        reset_deck: function (slug) {

        },
        // 'GET' on /rooms/[slug]/play_view/
        play_view: function (slug, callback) {
            api('GET', '/rooms/'+slug+'/play_view/', null, callback);
        }
    });

    var tool = {
        argument_to_array: function (args) {
            var args = Array.prototype.slice.call(args);
            return args.sort();
        }
    };

})(window, document, jQuery, app);