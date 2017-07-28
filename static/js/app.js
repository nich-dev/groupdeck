
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
    $('#content .modal-trigger').leanModal();
    $('.material-tooltip').remove();
    $('.tooltipped').tooltip({delay: 50});
    $('#spinner-load').stop( true, true ).fadeOut(200);
    change_title();
    $('select').material_select();
    Materialize.updateTextFields();
    if ($('.game-wrapper').length > 0) {
        app.ready();
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