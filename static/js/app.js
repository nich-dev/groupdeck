
function getCookie(name)
{
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?

            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
var first = true;
var initialize_generic = function(){
    if(first){
        first = false;
    } else {
        $('.button-collapse').sideNav('hide');
    }
    $(".dropdown-button").dropdown({ hover: false });
    //broken with jquery 3, wait til next release
    //$('.parallax').parallax();
    $('.lean-overlay').hide();
    $('#content .modal-trigger').leanModal();
    $('.material-tooltip').remove();
    $('.tooltipped').tooltip({delay: 50});
    $('#spinner-load').stop( true, true ).fadeOut(200);
    change_title();
    init_forms();
    $('select').material_select();
    Materialize.updateTextFields();
    if ($('.game-wrapper').length > 0) {
        app.ready();
    }
    if($('.manage-deck').length > 0){
        manage_deck.init();
    }
}

var initialize_first = function(){
    $('.button-collapse').sideNav({
          menuWidth: 240, // Default is 240
          edge: 'left', // Choose the horizontal origin
          closeOnClick: false // Closes side-nav on <a> clicks, useful for Angular/Meteor
    });
    
    initialize_generic();
}


var change_title = function(){
    if ($('#title-change').length > 0) {
        var text = $('#title-change').text();
        document.title = text;
        $('#logo-container').text(text);
    };
}

var init_forms = function(){
    if ($('#card-list').length > 0) {
        var list = document.getElementById('card-list');
        var cardList = Sortable.create(list);
    };
    if ($('#deck-card-list').length > 0) {
        var list = document.getElementById('deck-card-list');
        var cardList = Sortable.create(list, {
            filter: '.js-remove',
            onFilter: function (evt) {
                var el = cardList.closest(evt.item);
                el && el.parentNode.removeChild(el);
            }
        });
    };
}

var isEmptyOrSpaces = function (str){
    return str === null || str.match(/^ *$/) !== null;
}

var card_html = '<li class="collection-item col s12 m6 l4" data-card="{{ pk }}"> \
    <div class="card"> \
        <div class="card-content"> \
            <span class="card-title">{{ text }}</span> <br> \
            <span class="blue white-text text-darken-2">&nbsp;{{ count }}&nbsp;</span> \
            <span>&nbsp;{{ flavor_text }}&nbsp;</p> \
            <i class="material-icons action blue-text text-darken-1 activator">edit</i> \
            <i class="material-icons js-remove action blue-text text-darken-1">delete</i> \
        </div> \
        <div class="card-reveal"> \
            <span class="card-title arrow-down"><i class="material-icons right">keyboard_arrow_down</i></span> \
            <input type="text" name="text" required="" value="{{ text }}" id="id_text" maxlength="255" placeholder="Text"> \
            <input type="text" name="flavor_text" required="" value="{{ flavor_text }}" id="id_text" maxlength="255" placeholder="Flavor Text"> \
            <input type="number" name="count" required="" value="{{ count }}" id="id_text" maxlength="255" placeholder="Count" defaultValue="1"> \
        </div> \
    </div> \
</li>';

var manage_deck = {
    deck: null,
    field: null,
    results_list: null,
    clear_button: null,
    save_button: null,
    changed: [],
    added: [],
    flag: false,
    typingTimer: null,  //timer identifier
    doneTypingInterval: 700,  //time in ms, 1s
    init: function(){
        if ($('.deck-delete').length > 0) {
            app.api.decks.get($('.deck-delete').data('slug'), null, function(result){
                manage_deck.deck = result;
            });
        };
        manage_deck.field = $('#autocomplete-input-search');
        manage_deck.results_list = $('#autocomplete-results ul');
        manage_deck.clear_button = $('#autocomplete-results-close');
        manage_deck.save_button = $('.fixed-action-btn a');
        //listen for clicks
        manage_deck.clear_button.on('click', manage_deck.wipe);
        manage_deck.save_button.on('click', manage_deck.save);
        $('#create-card-form').on('submit', function(e) {
            e.preventDefault();
            manage_deck.create_card();
        });
        //on keyup, start the countdown
        manage_deck.field.on('keyup', function () {
          clearTimeout(manage_deck.typingTimer);
          manage_deck.typingTimer = setTimeout(manage_deck.search, manage_deck.doneTypingInterval);
        });
        //on keydown, clear the countdown 
        manage_deck.field.on('keydown', function () {
          clearTimeout(manage_deck.typingTimer);
        });
    },
    search: function() {
        if (manage_deck.field.val() == null ||
            manage_deck.field.val() == ''){
            manage_deck.wipe();
        } else {
            app.api.cards.lookup({'search': manage_deck.field.val()}, manage_deck.display);
        }      
    },
    display: function(result) {
        manage_deck.wipe();
        result.results.forEach(function(card) {
            var $option = $("<li data-pk='"+card.pk +"'><span class='title'>"
                +card.text+"</span><i>&nbsp;"+card.flavor_text+"</i></li>")
            .appendTo(manage_deck.results_list);
            $option.on('click', function(){
                app.api.cards.get($option.data('pk'), null, manage_deck.add_to_deck);
            });
        });
        manage_deck.clear_button.show();
    },
    wipe: function() {
        manage_deck.clear_button.hide();
        manage_deck.results_list.empty();
    },
    create_card: function(){
        if (!manage_deck.flag) {
            manage_deck.flag = true; return;
        };
        var card = {
            "text": $('#id_text_add').val(),
            "flavor_text": $('#id_flavor_text_add').val(),
            "pk": 0
        };
        var count = $('#id_amount_add').val();
        if (isEmptyOrSpaces(card.text) || count == null || count < 1) {
            Materialize.toast('Finish all required fields first', 1500);
        } else {
            document.getElementById("create-card-form").reset();
            manage_deck.add_to_deck(card, count);
            $('#modal-create-card').closeModal();
        }
    },
    add_to_deck: function(element, count = 1){
        var new_card = {"card": {"text": element.text, 
                    "flavor_text": element.flavor_text, "pk": element.pk}, "count": count};
        //check if deck is created, if not just visually add card
        if (manage_deck.deck == null) {
            manage_deck.display_to_deck(element, count);
            manage_deck.added.push(new_card);
            manage_deck.save();
        }
        //check if card already in deck
        else if (manage_deck.is_in_deck(element.pk)) {
            Materialize.toast('This card is already in your deck!', 1500);
        } else { //add that sucker for real
            app.api.decks.add_cards(manage_deck.deck.slug, [new_card], 
                null, function(result) {
                    manage_deck.display_to_deck(element, count);
                    manage_deck.deck.cards.push(new_card);
                }
            );
        }        
    },
    display_to_deck: function(card, count = 1){
        var new_card = card_html
                        .replace('{{ text }}', card.text)
                        .replace('{{ text }}', card.text)
                        .replace('{{ count }}', count)
                        .replace('{{ count }}', count)
                        .replace('{{ flavor_text }}', card.flavor_text)
                        .replace('{{ flavor_text }}', card.flavor_text)
                        .replace('{{ pk }}', card.pk);
        $(new_card).appendTo('#deck-card-list');
    },
    save: function(){
        if (isEmptyOrSpaces($('#id_name').val())) {
            Materialize.toast('Cannot save without a name', 2000);
            return;
        };
        //check if new save, and create
        if (manage_deck.deck.slug == null) {
            app.api.decks.create({'name': $('#id_name').val()}, manage_deck.new_save);
        }
        //iterate through changed cards, update to the server
        else{
            //add new cards to the deck
            app.api.decks.add_cards(manage_deck.deck.slug, manage_deck.added, 
                null, function(result) {
                    manage_deck.deck.cards = manage_deck.added;
                    manage_deck.added = [];
                }
            );
            //update details of each card
        }
    },
    new_save: function(deck){
        manage_deck.deck = deck;
        Materialize.toast('Created your new deck "' + deck.name +'"', 1500);
        $('.pagetitle').text('Manage Deck: '+deck.name);
        manage_deck.save();
    },
    is_in_deck: function(pk){
        manage_deck.deck.cards.forEach(function(c) {
            if (c.pk == pk) {return true};
            return true;
        });
        return false;
    }
};
