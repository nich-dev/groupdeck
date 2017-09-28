;(function (window, document, $, undefined) {

    var wrapper = $('.cards-wrapper');
    var card = $('.card.front');
    var title = $('.brand-logo');
    var btnDraw = $('#btn-draw');
    var btnRefresh = $('#btn-rfs');
    var key, qs;

    var app = {
        el: {
            wrapper: wrapper,
            card: card,
            title: title,
            btnDraw: btnDraw,
            btnRefresh: btnRefresh
        },
        start: function () {
            app.getRoomSlug();
            app.setRoomTitle();
            app.el.wrapper = $('.cards-wrapper');
            app.el.card = $('.card.front');
            app.el.title = $('.brand-logo');
            app.el.btnDraw = $('#btn-draw');
            app.el.btnRefresh = $('#btn-rfs');
            if (app.slug != '') {
                app.updateDeck();
                app.updateCurrentCard();
                app.buildQs();

                app.attachListeners();
                app.startTimers();
            }
        },
        getRoomSlug: function () {
            var parts = document.location.href.toString().split('/');
            console.log(parts);
            app.slug = parts.pop();
            if (app.slug == '' && parts.length > 6) {
                key = parts.pop();
                app.slug = parts.pop();
                console.log(key);
                console.log(app.slug);
            }
            else {
                app.slug = parts.pop();
            }
        },
        updateDeck: function () {
            app.api.rooms.play_view(app.slug, qs, function (cards) {
                app.cards = cards;
                app.setDiscardPile();
            });
        },
        updateCurrentCard: function () {
                app.api.rooms.get_current_card(app.slug, qs, function (current_card) {
                    if ((app.current_card||{}).pk != current_card.pk) {
                        app.current_card = current_card;
                        app.updateDeck();
                        app.setCard(current_card.text, current_card.flavor_text);
                    }
                });
        },
        drawCard: function () {
            app.api.rooms.draw_card(app.slug, qs, function (new_card) {
                //new_card = app.current_card
                if (new_card.status == 'Deck is empty') {
                    alert('Yarr, ye deck is empty mate!');
                } else {
                    app.setCard(new_card.text, new_card.flavor_text);
                }
            });
        },

        // Functions beginning the `set` prefix are for UI updates
        setCard: function (text, flavor) {
            app.el.wrapper.addClass('switch-pt1');
            setTimeout(function () {
                app.el.card.find('.card-text').text(text);
                app.el.card.find('.card-flavor').text(flavor);
                setTimeout(function () {
                    app.el.wrapper
                    .removeClass('switch-pt1');
                }, 570);
            }, 375);
        },
        setRoomTitle: function () {
            var title = (this.slug + '')
            .replace(/-/g, ' ')
            .replace(/^(.)|\s+(.)/g, function ($1) {
                return $1.toUpperCase();
            });

            app.el.title.text(title);
        },
        setDiscardPile: function () {

        },
        attachListeners: function () {
            app.el.card
            .on('click', app.drawCard);
            app.el.btnDraw
            .on('click', app.drawCard);
            app.el.btnRefresh
            .on('click', app.updateCurrentCard);
        },
        startTimers: function () {
            setInterval(function () {
                app.updateCurrentCard();
            }, 5000);
        },
        buildQs: function () {
            qs = {'key':key};
        },
        readyListeners: [],
        whenReady: function (callback) {
            app.readyListeners.push(callback);
        },
        ready: function () {
            $.each(app.readyListeners, function (key, value) {
                (value||function(){})();
            });
        }
    };
    
    
    app.whenReady(function () {
        app.start();
    });

    window.app = app;
    
})(window, document, jQuery);