;(function (window, document, $, app, undefined) {

    var api = app.api = function (method, request, data, callback) {
        method = method || 'GET';
        data = data || {};
        request = request || '';
        var response = [];
        var action = "/deck/v2"+request;
        //console.log(document.location.origin.toString()+action);

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
    };

    app.api = $.extend(app.api, {
        cards: {},
        decks: {},
        rooms: {}
    });
    

    $.extend(app.api.cards, {

        // 'GET' on /cards/[pk]/
        get: function (pk, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/cards/'+pk+'/'+qs, null, callback);
        },

        // GET on /cards/
        lookup: function (qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/cards/'+qs, null, (callback||$.noop));
        },

        // 'POST' on /cards/ returns the created card
        create: function (card, qs, callback) {
            qs = tool.arr2qs(qs);
            api('POST', '/cards/'+qs, card, (callback||$.noop));
        }, 

        // 'DELETE' on /cards/[pk]
        delete: function (pk, qs, callback) {
            qs = tool.arr2qs(qs);
            api('DELETE', '/cards/'+pk+'/'+qs, null, (callback||$.noop));
        }, 

        // 'PUT' on /cards/[pk]/ returns the updated card
        update: function (pk, card, qs, callback) {
            qs = tool.arr2qs(qs);
            api('PUT', '/cards/'+pk+'/'+qs, card, (callback||$.noop));
        }, 

        // 'GET' on /cards/[pk]/copy/ returns the copied card
        copy: function (pk, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/cards/'+pk+'/copy/'+qs, null, (callback||$.noop));
        }, 
    });

    $.extend(app.api.decks, {

        // 'GET' on /decks/[slug]/
        get: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/decks/'+slug+'/'+qs, null, callback||$.noop);
        },

        lookup: function (qs, callback) { // GET on /decks/
            qs = tool.arr2qs(qs);
            api('GET', '/decks/'+qs, null, (callback||$.noop));
        },

        create: function (data, callback) { // CREATE
            api('POST', '/decks/', data, (callback||$.noop));
        },

        // 'POST' on /decks/[slug]/add_cards/ returns the deck in simple format.
        // [
        //     {
        //         "card": {
        //             "text":"", 
        //             "flavor_text":"", 
        //             "pk":0
        //         }, 
        //         "count": 2
        //     },
        //     {...}
        // ]
        add_cards: function (slug, cards, qs, callback) {
            qs = tool.arr2qs(qs);
            api('POST', '/decks/'+slug+'/add_cards/'+qs, cards, (callback||$.noop));
        },

        // 'POST' on /decks/[slug]/remove_cards/ returns the deck in simple format.
        // {
        //     "texts": [
        //         "Example text 1",
        //         "Example text 2"
        //     ],
        //     "cards": [
        //         1,
        //         2,
        //         4
        //     ]
        // }
        remove_cards: function (slug, texts, cards, qs, callback) {
            texts = texts || [];
            cards = cards || [];
            qs = tool.arr2qs(qs);
            api('POST', '/decks/'+slug+'/remove_cards/'+qs, { "texts": texts, "cards": cards }, (callback||$.noop));
        },

        // 'POST' on /decks/[slug]/change_count/ returns the deck in simple format.
        // [
        //     {
        //         "card": 3,
        //         "count": 2
        //         "Example text 2"
        //     }
        // ]
        change_count: function (slug, cards, qs, callback) {
            qs = tool.arr2qs(qs);
            api('POST', '/decks/'+slug+'/remove_cards/'+qs, { "texts": texts, "cards": cards }, (callback||$.noop));
        },

        // 'GET' on /decks/[slug]/get_random_card/
        get_random_card: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('POST', '/decks/'+slug+'/get_random_card/'+qs, { "texts": texts, "cards": cards }, (callback||$.noop));
        },

        // 'GET' on /decks/[slug]/play_view/
        play_view: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('POST', '/decks/'+slug+'/play_view/'+qs, null, (callback||$.noop));
        }
    });

    $.extend(app.api.rooms, {

        // 'GET' on /rooms/[slug]/
        get: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/'+qs, { "owner": owner }, callback);
        },

        // 'GET' on /rooms/
        lookup:  function (qs) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+qs, null, (callback||$.noop));
        },

        // 'GET' on /rooms/
        join:  function (key, callback) {
            api('GET', '/rooms/?key='+key, null, (callback||$.noop));
        },

        // 'GET' on /rooms/[slug]/get_current_card/
        // Returns the current displayed card from the deck
        get_current_card: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/get_current_card/'+qs, null, (callback||$.noop));
        },

        // 'GET' on /rooms/[slug]/draw_card/
        // Discards the current card, draws a random card from the deck and sets
        // is as the current displayed card, removes it from the deck, and
        // returns the card.
        draw_card: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/draw_card/'+qs, null, (callback||$.noop));
        },

        // 'GET' on /rooms/[slug]/stop_game/
        // Sets the deck in play. Clears cards_in_deck, cards_in_discard, and
        // card displaed. Explodes all cards (the ones with counts) in the deck,
        // and inserts a temp card for each that it needs for the defined count.
        // 
        // Returns the deck in the 'in game' view.
        //
        // Permissions: User must be owner of room.
        start_game: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/start_game/'+qs, null, callback);
        },

        // Clears cards_in_deck, cards_in_discard, and card displaed. Sets deck as not in play. Returns the game room.
        //
        // Permissions: User must be owner of room.
        stop_game: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/stop_game/'+qs, null, callback);
        },
        // 'GET' on /rooms/[slug]/close_room/
        close_room: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/close_room/'+qs, null, callback);
        },
        // 'GET' on /rooms/[slug]/reset_deck/
        reset_deck: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/reset_deck/'+qs, null, callback);
        },
        // 'GET' on /rooms/[slug]/play_view/
        play_view: function (slug, qs, callback) {
            qs = tool.arr2qs(qs);
            api('GET', '/rooms/'+slug+'/play_view/'+qs, null, callback);
        }
    });

    var tool = {
        argument_to_array: function (args) {
            var args = Array.prototype.slice.call(args);
            return args.sort();
        },
        // simple array to querystring
        arr2qs: function (arr) {
            var key;
            var args = [];
            var qs = '';
            for (key in arr) {
                args.push(encodeURIComponent(key)+'='+encodeURIComponent(arr[key]));
            }

            if (args.length > 0) {
                qs = '?'+(args.join('&'));
            }

            return qs;
        }
    };

})(window, document, jQuery, app);