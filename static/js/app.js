var instrument_page = 1;
var scrollTriggered = false;
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
	$('.parallax').parallax();
    $('#content .modal-trigger').leanModal();
    init_forms();
    $(window).off("scroll", inst_loading_scroll);
    if($('#instrument-cards').length > 0){
    	instrument_page = 1;
    	$(window).scroll(inst_loading_scroll);
    }
    $('.material-tooltip').remove();
    $('.tooltipped').tooltip({delay: 50});
    if($('#obj-plant').length > 0){
    	init_savereport_table();
    } 
    $('#spinner-load').stop( true, true ).fadeOut(200);
}

var initialize_first = function(){
	$(".dropdown-button").dropdown({ hover: false });
	$('.button-collapse').sideNav({
	      menuWidth: 240, // Default is 240
	      edge: 'left', // Choose the horizontal origin
	      closeOnClick: false // Closes side-nav on <a> clicks, useful for Angular/Meteor
	    });
    $('.parallax').parallax();
    $('.modal-trigger').leanModal();
    init_forms();
    $(window).off("scroll", inst_loading_scroll);
    if($('#instrument-cards').length > 0){
    	instrument_page = 1;
    	$(window).scroll(inst_loading_scroll);
    }   
    $('.tooltipped').tooltip({delay: 50});
    if($('#obj-plant').length > 0){
    	init_savereport_table();
    } 
    $('#spinner-load').stop( true, true ).fadeOut(200);
}

var spinner = '<div class="preloader-wrapper x-small active">\
    <div class="spinner-layer spinner-green-only">\
      <div class="circle-clipper left">\
        <div class="circle" style="left:0;height:15px;width:15px;"></div>\
      </div><div class="gap-patch">\
        <div class="circle" style="left:0;height:15px;width:15px;"></div>\
      </div><div class="circle-clipper right">\
        <div class="circle" style="left:0;height:15px;width:15px;"></div>\
      </div>\
    </div>\
  </div>';

var progress = '<div class="progress icon">\
      <div class="indeterminate"></div>\
  </div>';

var show_spinner = function() {
	$('#spinner-load').fadeIn();
}

var hide_spinner = function() {
	$('#spinner-load').fadeOut();
}

var grab_models = function(){
	$('#id_model').select2({
		  ajax: {
		    url: "/v2/modelsjs",
		    dataType: 'json',
		    delay: 250,
		    data: function (params) {
		      return {
		        q: params.term, // search term'
		        limit:50,
		        offset: params.page
		      };
		    },
		    processResults: function (data, params) {
		      // parse the results into the format expected by Select2
		      // since we are using custom formatting functions we do not need to
		      // alter the remote JSON data, except to indicate that infinite
		      // scrolling can be used
		      params.page = params.page || 1;
		      console.log(data.results);
		      return {
		        results: $.map(data.results, function (item){
		        	return {
		        		text: item.model_number + " ("+item.type+") by "+item.manufacturer,
		        		id: item.pk
		        	}
		        }),
		        pagination: {
		          more: (params.page * 50) < data.total_count
		        }
		      };
		    },
		    cache: true
		  },
		  escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
		  minimumInputLength: 1
		});
}

var grab_locations = function(ps, ls){
	var url = "/v2/locations/?limit=2000&plant="+ps.val();
	$.ajax({
    	type: "GET",
    	url: url,
    	dataType: 'json',
    	timeout: 5000,
    	success: function(data){
    		ls.find('option').remove().end();
    		for(i=0; i < data.results.length; i++){
    			ls.append('<option value="'+data.results[i].pk+'">'+data.results[i].name+'</option>')    			
    		}
    		if($('#init-location').length > 0){
    			ls.val($('#init-location').data('pk'));
    		}
    		ls.material_select();
    	}, error: function(data){
    		console.log(data);
    		Materialize.toast(data, 5000);
    	}, fail: function (data){
    		console.log(data);
    		Materialize.toast(data, 5000);
    	}        	
    });
}

var init_createinstrument = function(){
	var $c = $('#calibrationfreq-form');
	var $l = $('#location-form');
	$l.find('select').material_select();
	var $m = $('#instrumentmodel-form');
	$m.find('select').material_select();
	var $t = $('#type-form');
	var $f = $('#manufacturer-form');
	
	$c.on('submit', function(e) {
        e.preventDefault();  //prevent form from submitting
        var url = '/v2/calibfreqs/';
        $.ajax({
        	type: "POST",
        	url: url,
        	dataType: 'json',
        	data: $c.serialize(),
        	success: function(data){
        		console.log(data);
        		$('#id_calibration_frequency').append($('<option>', {value:data.pk, text:data.name}));
        		$('#id_calibration_frequency').val(data.pk);
        		$('#id_calibration_frequency').material_select();
        		$c.find("input[type=text], textarea").val("");
        		$('#frequency-modal').closeModal();
        		Materialize.toast("Calibration Frequency '"+data.name+"' Added", 4000);
        	}, error: function(data){
        		$c.find('h4').removeClass('blue').addClass('red');
        		$c.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}, fail: function (data){
        		$c.find('h4').removeClass('blue').addClass('red');
        		$c.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}        	
        });
    });
	
	$l.on('submit', function(e) {
        e.preventDefault();  //prevent form from submitting
        var url = '/v2/locations/';
        $.ajax({
        	type: "POST",
        	url: url,
        	dataType: 'json',
        	data: $l.serialize(),
        	success: function(data){
        		console.log(data);
        		$('#id_location').append($('<option>', {value:data.pk, text:data.name}));
        		$('#id_location').val(data.pk);
        		$('#id_location').material_select();
        		$l.find("input[type=text], textarea").val("");
        		$('#location-modal').closeModal();
        		Materialize.toast("Location '"+data.name+"' Added", 4000);
        	}, error: function(data){
        		$l.find('h4').removeClass('blue').addClass('red');
        		$l.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}, fail: function (data){
        		$l.find('h4').removeClass('blue').addClass('red');
        		$l.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}        	
        });
    });
	
	$m.on('submit', function(e) {
        e.preventDefault();  //prevent form from submitting
        var url = '/v2/models2/';
        console.log($m.serialize());
        $.ajax({
        	type: "POST",
        	url: url,
        	dataType: 'json',
        	data: $m.serialize(),
        	success: function(data){
        		console.log(data);
        		$('#id_model').append($('<option>', {value:data.pk, text:data.model_number}));
        		$('#id_model').val(data.pk);
        		$("#select2-id_model-container").text(data.model_number);
        		$('#model-modal').closeModal();
        		Materialize.toast("Model '"+data.model_number+"' Added", 4000);
        	}, error: function(data){
        		$m.find('h4').removeClass('blue').addClass('red');
        		$m.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}, fail: function (data){
        		$m.find('h4').removeClass('blue').addClass('red');
        		$m.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}        	
        });
    });
	
	$t.on('submit', function(e) {
        e.preventDefault();  //prevent form from submitting
        var url = '/v2/types/';
        console.log($t.serialize());
        $.ajax({
        	type: "POST",
        	url: url,
        	dataType: 'json',
        	data: $t.serialize(),
        	success: function(data){
        		console.log(data);
        		$('#id_type').append($('<option>', {value:data.pk, text:data.name}));
        		$('#id_type').val(data.pk);
        		$('#id_type').material_select();
        		$t.find("input[type=text], textarea").val("");
        		$('#type-modal').closeModal();
        		Materialize.toast("Instrument Type '"+data.name+"' Added", 4000);
        	}, error: function(data){
        		$t.find('h4').removeClass('blue').addClass('red');
        		$t.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}, fail: function (data){
        		$t.find('h4').removeClass('blue').addClass('red');
        		$t.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}        	
        });
    });
	
	$f.on('submit', function(e) {
        e.preventDefault();  //prevent form from submitting
        var url = '/v2/manufacturers/';
        console.log($f.serialize());
        $.ajax({
        	type: "POST",
        	url: url,
        	dataType: 'json',
        	data: $f.serialize(),
        	success: function(data){
        		console.log(data);
        		$('#id_manufacturer').append($('<option>', {value:data.pk, text:data.name}));
        		$('#id_manufacturer').val(data.pk);
        		$('#id_manufacturer').material_select();
        		$f.find("input[type=text], textarea").val("");
        		$('#manufacturer-modal').closeModal();
        		Materialize.toast("Manufacturer '"+data.name+"' Added", 4000);
        	}, error: function(data){
        		$f.find('h4').removeClass('blue').addClass('red');
        		$f.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}, fail: function (data){
        		$f.find('h4').removeClass('blue').addClass('red');
        		$f.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}        	
        });
    });
	$('#id_calibration_frequency').material_select();
	$('#id_plant').material_select();
	grab_locations($('#id_plant'), $('#id_location'));
	$('#id_plant').change(function () {
		grab_locations($(this), $('#id_location'));
	});
	grab_models();
	if($('#init-model').length > 0){
		$("#select2-id_model-container").text($('#init-model').data('name'));
	}
}

var init_createtask = function(){
	var $c = $('#cat-form');
	$c.on('submit', function(e) {
        e.preventDefault();  //prevent form from submitting
        var url = '/v2/taskcategories/';
        $.ajax({
        	type: "POST",
        	url: url,
        	dataType: 'json',
        	data: $c.serialize(),
        	success: function(data){
        		console.log(data);
        		$('#id_category').append($('<option>', {value:data.pk, text:data.name}));
        		$('#id_category').val(data.pk);
        		$('#id_category').material_select();
        		$c.find("input[type=text], textarea").val("");
        		$('#cat-modal').closeModal();
        		Materialize.toast("Category '"+data.name+"' Added", 4000);
        	}, error: function(data){
        		$c.find('h4').removeClass('blue').addClass('red');
        		$c.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}, fail: function (data){
        		$c.find('h4').removeClass('blue').addClass('red');
        		$c.find('.error-msg').text(data.statusText);
        		Materialize.toast(data.statusText, 5000);
        	}        	
        });
    });
	var $u = $('#id_users');
	$('.users-select').on('click', function() {
		$u.val('');
		console.log($(this).data('users'));
		var users = $(this).data('users').substring(0, $(this).data('users').length-1);
		$.each(users.split(","), function(i,e){
		    $("#id_users option[value='" + e + "']").prop("selected", true);
		}); $u.material_select();
	});
}

var add_calib_point = function(){
	var $p = $('.calibration-add').prev();
	var num = $p.find('input').data('num') + 1;
	var field = '<div class="col s12 m6 input-field calibration-input">\
							<input id="calibraiton-point-'+num+'" type="text" data-num="'+num+'" class="validate calibration-point">\
					        <label for="calibraiton-point-'+num+'" data-num="'+num+'">Calibration Point '+num+'</label>\
						</div>';
	$p.after($(field));
}

var fetch_calib_json = function(modal){
	var checked = false;
	if (modal.find('#completed').is(":checked")){
		checked = true;
	}
	var points = [];
	modal.find('.calibration-point').each(function () {
		if ($(this).val() != null && $(this).val() != "" && $(this).val() != " "){
			points.push({"number": $(this).data("num"), "value": $(this).val(), "pk": $(this).data("pk")});
		}
	});
	var calibration = {"alarm": modal.find('#alarm_trigger_points').val(),
			"comments": modal.find('#comments').val(),
			"issues": modal.find('#issues').val(),
			"completed": checked,
			"points": JSON.stringify(points),
			"instrument": modal.find('.modal-content').data("inst"),
			"pk": modal.find('.modal-content').data("pk")
	};
	return calibration;
}

var submit_calibration = function(button, pk) {
	button.find('i').text('donut_large').addClass('cube-animation');
	var json = fetch_calib_json($('#calibration'+pk+'-modal'));
	console.log(json);
	$.ajax({
    	type: "POST",
    	url: '/v2/upcalib/?format=json',
    	dataType: 'json',
    	data: json,
    	success: function(data){
    		console.log(data);
    		button.find('i').text('send').removeClass('cube-animation');
    		$('#calibration'+pk+'-modal').find('.modal-content').data("pk", data.pk);
    		if(data.error){
    			Materialize.toast(data.error, 5000);
    		} else { Materialize.toast("Calibration saved", 5000); }    		
    		if(data.completed && $('.collection').length > 0){
    			$('#calibration'+pk+'-modal').closeModal();
    			$('#instrument-issue-'+pk).fadeOut();
    		}
    	}, error: function(data){
    		button.find('i').text('send').removeClass('cube-animation');
    		Materialize.toast(data.statusText, 5000);
    		console.log(data);
    	}, fail: function (data){
    		button.find('i').text('send').removeClass('cube-animation');
    		Materialize.toast(data.statusText, 5000);
    		console.log(data);
    	}        	
    });
}

var fetch_calib_form = function(obj){
	var pk = obj.data('pk');
	if ($('#calibration'+pk+'-modal').html() == ""){
		var url = "/calibration/"+pk+"/";
		var copy = obj.find('i').clone();
		console.log(copy);
		obj.html(progress);
		$.ajax({
	    	type: "GET",
	    	url: url,
	    	dataType: 'text',
	    	timeout: 5000,
	    	success: function(data){
	    		$('#calibration'+pk+'-modal').html(data);
	    		Materialize.updateTextFields();
	    		$('#calibration'+pk+'-modal').find('.modal-close').on('click', function() {
	    			$('#calibration'+pk+'-modal').closeModal();
	    		});
	    		$('#calibration'+pk+'-modal').find('.calibration-add-btn').on('click', function(){
	    			add_calib_point();
	    		});
	    		$('#calibration'+pk+'-modal').find('.submit-btn').on('click', function(){
	    			submit_calibration($(this), pk);
	    		});
	    		$('#calibration'+pk+'-modal').openModal();
	    		obj.html(copy);
	    		obj.find('i').data('pk', pk);
	    	}, error: function(data){
	    		console.log(data);
	    		Materialize.toast(data.statusText, 5000);
	    		obj.html(copy);
	    	}, fail: function (data){
	    		console.log(data);
	    		Materialize.toast(data.statusText, 5000);
	    		obj.html(copy);
	    	}        	
	    });
	}	else {
		$('#calibration'+pk+'-modal').openModal();
	}
}

var submit_task = function(pk, cleared) {
	var json = { 'pk':pk, 'cleared':cleared};
	console.log(json);
	$.ajax({
    	type: "PUT",
    	url: '/v2/tasks/'+pk+'/?format=json',
    	dataType: 'json',
    	data: json,
    	success: function(data){
    		console.log(data);
    		if(data.error){
    			Materialize.toast(data.error, 5000);
    		} else { Materialize.toast("Calibration saved", 5000); }    		
    		if($('.collection').length > 0){
    			$('#calibration_t'+pk+'-modal').closeModal();
    			$('#instrument-issue-t'+pk).fadeOut();
    		}
    	}, error: function(data){
    		Materialize.toast(data.statusText, 5000);
    		console.log(data);
    	}, fail: function (data){
    		Materialize.toast(data.statusText, 5000);
    		console.log(data);
    	}        	
    });
}

var locations = [];
var limit_location_select = function(ps, ls){
		if (locations.length < 1){
			ls.children().each(function(){
				locations.push($(this));
			});
		}
        if (ps.val() != "Any"){
        	ls.find('option').remove().end().append('<option value="Any">Any</option>');
        	for (i = 0; i < locations.length; i++){
        		if(parseInt(locations[i].data('plant')) == parseInt(ps.val())){
        			ls.append(locations[i]);
        		}
        	}
        	ls.val('Any'); ls.material_select();
        } else {
        	ls.find('option').remove().end();
        	for (i = 0; i < locations.length; i++){
        		ls.append(locations[i]);
        	}
        	ls.val('Any'); ls.material_select();
        }
}

var init_forms = function(){
	$('#id_next_calibration').pickadate({
	    selectMonths: true, // Creates a dropdown to control month
	    selectYears: 10,
	    format: 'yyyy-mm-dd',
	    formatSubmit: 'yyyy-mm-dd',
	    hiddenSuffix: ' 01:00:00',
	    min: new Date()
	  });
	
	$('#date_report').pickadate({
	    selectMonths: true, // Creates a dropdown to control month
	    selectYears: 15,
        closeOnSelect: true,
	    format: 'mm-dd-yyyy',
	    max: new Date()
	  });
    $('#date_report2').pickadate({
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 15,
        closeOnSelect: true,
        format: 'mm-dd-yyyy',
        max: new Date()
      });
	if($('.task-done').length >0){
		$('.task-done').on('click', function() {
			var nowInMillis = Date.now();
			submit_task($(this).data('pk'), nowInMillis);
		});
	}
	$('textarea').addClass('materialize-textarea');
	if($('#expand-fab').length > 0){
		$('#hidden-btn').click(function() {
			$('.hidden-info').toggle();
		});
	}
	if($('#instrument-form').length > 0){
		init_createinstrument();
	} else {
		$('select').material_select();
		if($('#cat-form').length > 0){
			init_createtask();
		}
	}
	if($('#search_inst').length > 0){
		$('#id_plant').change(function () {
			limit_location_select($(this), $('#id_location'));
		});
	}
	$('#search-button').on('click', function () {
    	$('#filter-block').slideToggle(100);
    });
	$('.calibration-add-btn').on('click', function(){
		add_calib_point();
	});
	$('.calib-pop').on('click', function(){
		fetch_calib_form($(this));
	});
	
	if($('#collection').length > 0){
		Sortable.create(document.getElementById("collection"));
	}
    Materialize.updateTextFields();  
}

var load_instruments = function(){
	$('#spinner-load').stop( true, true ).delay(100).fadeIn(300);
	var url = window.location.pathname;
	if(window.location.search.length > 0){
		var url = url + window.location.search+"&offset="+instrument_page;
	} else {
		url = url+"?offset="+instrument_page;
	}
	$.ajax({
    	type: "GET",
    	url: url,
    	dataType: 'html',
    	timeout: 5000,
    	success: function(data){
    		instrument_page = instrument_page + 1;
    		$("#instrument-cards").append(data);
    		$('.tooltipped').tooltip({delay: 50});
    		$('.calib-pop').off('click');
    		$('.calib-pop').on('click', function(){
    			fetch_calib_form($(this));
    		});
    		$('.calibration-add-btn').off('click');
    		$('.calibration-add-btn').on('click', function(){
    			add_calib_point();
    		});
    		$('#spinner-load').stop( true, true ).delay(50).fadeOut(300);
    	}, error: function(data){
    		console.log(data);
    		Materialize.toast(data, 5000);
    		$('#spinner-load').stop( true, true ).fadeOut(600);
    	}, fail: function (data){
    		console.log(data);
    		Materialize.toast(data, 5000);
    		$('#spinner-load').stop( true, true ).fadeOut(600);
    	}        	
    });
}

var scrollTimer = null;
var inst_loading_scroll = function(){
	if (!scrollTriggered){
		if($(window).scrollTop() > $(document).height() - $(window).height()-$('.page-footer')[0].scrollHeight) {
			scrollTriggered = true;
			scrollTimer = null;
			setTimeout(function() {
				scrollTriggered=false;
			}, 500);
			load_instruments();
		}
	}
}

var init_savereport_table = function(){
	var filetitle = 'CITI '+$('#obj-plant').data('name')+' Export';
	var tt = $('#report-table').DataTable({
			scrollX: true,
	        dom: '<Bf<t>lip>',
	        nowrap: false,
	        "lengthMenu": [[10, 50, 100, -1], [10, 50, 100, "All"]],
	        buttons: 
	        	[
	             {
	                 extend: 'excelHtml5',
	                 title: filetitle
	             },
	             {
	                 extend: 'csvHtml5',
	                 title: filetitle
	             },
	             {
	                 extend: 'pdfHtml5',
	                 title: filetitle
	             },
	             'colvis'
	         ],
	        stateSave: true,
	        colReorder: true,
	        "iDisplayLength": 10,
		});
}