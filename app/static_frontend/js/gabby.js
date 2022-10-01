
var currPage = 1;

$(document).ready(function () {
	
	/*
	// Just for testing
	$("#page1").hide();
	$("#page4").show();
	currPage=4;
	$(".btn_restart").css('visibility','visible');
	$("#backButton").css('visibility','visible');
	*/
	
	$("#backButton").on("click", function() {	
		console.log("back clicked");
		switch(currPage){			
			case 2:				
				$("#page2").hide();
				$("#backButton").css('visibility','hidden');
				$("#page1").show();
				currPage=1;
				break;
			case 3:				
				$("#page3").hide();
				$("#page2").show();
				currPage=2;
				break;
			case 4:				
				$("#page4").hide();
				$("#page2").show();
				currPage=2;
				break;		
		}
	});
	
	$(".btn_restart").on("click", function() {	
		window.location.href = '/app';
	});
	
	$(".btn_step2Continue").prop("disabled", true);
	
	$('[data-toggle="buttons"] .attribute_tag').on('click', function () {
		// toggle state
		$(this).toggleClass('active');
		
		// toggle checkbox
		var $chk = $(this).find('[type=checkbox]');
		$chk.prop('checked',!$chk.prop('checked'));
		
		// Keep track of total selected. if >3 can, enable continue button
		if ($(".attribute_tag.active").length >=3) {
			$(".btn_step2Continue").prop("disabled", false);
		} else {
			$(".btn_step2Continue").prop("disabled", true);
		}
		
		return false;
	});

	$(".thumbs_btn").on("click", function() {		
		if ($(this).hasClass("thumbs_up")) {
			if ($(this).hasClass("thumbs_up_inactive")) {
				$(this).addClass("thumbs_up_active");
				$(this).removeClass("thumbs_up_inactive");
				$(this).next().addClass("thumbs_down_inactive");
				$(this).next().removeClass("thumbs_down_active");
			} else {
				$(this).addClass("thumbs_up_inactive");
				$(this).removeClass("thumbs_up_active");
			}
		} else if ($(this).hasClass("thumbs_down")) {	
			if ($(this).hasClass("thumbs_down_inactive")) {
				$(this).addClass("thumbs_down_active");
				$(this).removeClass("thumbs_down_inactive");
				$(this).prev().addClass("thumbs_up_inactive");
				$(this).prev().removeClass("thumbs_up_active");
			} else {
				$(this).addClass("thumbs_down_inactive");
				$(this).removeClass("thumbs_down_active");
			}
		}
		
		// Do logic for saving feedback here.
	});

	$(".product_category").on("click", function() {
		
		var category = $(this).attr("name");
		console.log("getting products for category: " + category);
		
		// Clear all selected attribute tags in case someone has gone backwards
		// to the first screen then forward again.
		$('[data-toggle="buttons"] .attribute_tag').removeClass('active');
		
		// Only monitor
		category = "Monitor";
		
		$("#step2_instruction").html(
			"Choose <b>at least 3 options</b> that matter to you when buying a <b>"+category+"</b>"
		);
		
		reqData = {};
		reqData["category"] =  category;
		
		$.ajax({
			type: 'POST',
			contentType: 'application/json',
			url: '/getAttributes',
			dataType: 'json',
			data: JSON.stringify(reqData),
			success : (data) => {
				//console.log('got response: ');
				//console.log(JSON.stringify(data));
				console.log(data);

				for (var i=0;i < $('#attributes_list label').length;i++) {
					$($('#attributes_list label')[i]).text(data[i]['phrase']);
				}	
				$("#loading_shimmer_attributes_list").css("display", "none");
				$("#attributes_list").css("display", "block");				
			},
			error : (data) => {
				console.log('got error');
				console.log(data)
			}
		});
		
		$("#page1").hide();
		$("#page2").show();
		//window.history.pushState({step: 2},"","?step=2");		
		$("#backButton").css('visibility','visible');
		currPage = 2;
	});
	
	$(".show_more_attributes").on("click", function() {
				
		$("#more_attributes").show();
		$(".show_more_attributes").hide();
	});
	
	$(".btn_step2Continue").on("click", function() {
		//console.log("getting products");
		var reqData = {};
		var chosenAttributes = $('#attributes_list label.active').map(function() {
			return $(this).text();
		}).get();
		reqData["attributes"] = chosenAttributes;
		//console.log(reqData);
		console.log("getting products for attributes: " + chosenAttributes);

		$.ajax({
			type: 'POST',
			contentType: 'application/json',
			url: '/getProducts',
			dataType: 'json',
			data: JSON.stringify(reqData),
			success : (data) => {
				//gProdsResponse = data2;
				//console.log('got response: ');
				//console.log(JSON.stringify(data));
				console.log(data);
				//data = JSON.parse(data2['top10']);
				$('#matchedProducts_count').text( 
						( Math.floor(Math.random() * (7000 - 3000 + 1) ) + 3000 )
						+ " products");

				for (var i=0;i<10;i++) {
					$($('#product_list .product_image img')[i]).attr('src',data[i]['imageURLHighRes'].split(',')[0]);							
					$($('#product_list .product_name')[i]).text(data[i]['title']);
					$($('#product_list .num_reviews')[i]).text("See " + data[i]['num_reviews'] + " reviews");
					$($('#product_list .num_reviews')[i]).attr("data-asin", data[i]['asin']);
					sc = Math.round(data[i]['score']*100);
					if (sc > 85) {
						circle_color_class = "matching_score_high";
					} else if (sc > 50) {
						circle_color_class = "matching_score_med";
					} else {
						circle_color_class = "matching_score_low";
					}
					$('#product_list .matching_score_circle').eq(i).children().eq(0).removeClass('matching_score_high').removeClass('matching_score_med').removeClass('matching_score_low').addClass(circle_color_class);
					
					$($('#product_list .matching_score_num')[i]).text( sc + '%' );
					$($('#product_list .product_link a')[i]).attr("href", "https://www.amazon.com/dp/" + data[i]['asin']);
					$($('#product_list .product_name')[i]).attr("data-asin", data[i]['asin']);
					$($('#product_list .product_name')[i]).attr("data-nreviews", data[i]['num_reviews']);
					
					// we need to find the list of attributes again. unsure if response will be in same order
					var attributes = [];
					var attrscores = [];
					for (var key of Object.keys(data[i])) {
						if (key.endsWith('_score_level') ) {
							attributes.push(key.slice(0, -12));
							attrscores.push(data[i][key]);
						}
					}
					$($('#product_list .matching_score_header img')[i]).attr("data-matchingscore", sc);
					$($('#product_list .matching_score_header img')[i]).attr("data-selectedattributes", attributes.toString());
					$($('#product_list .matching_score_header img')[i]).attr("data-attributescores", attrscores.toString());
				}
				$("#loading_shimmer_product_list").css("display", "none");
				$("#product_list").css("display", "block");
				
			},
			error : (data) => {
				console.log('got error');
				console.log(data)
			}
		});
		
		
		$("#page2").hide();
		$("#page4").show();
		currPage = 4;
		$(".btn_restart").css('visibility','visible');
	});
	
	$('#product_matchingscore_modal').on('show.bs.modal', function (event) {
		var div = $(event.relatedTarget);
		var matchingscore = div.data('matchingscore');
		var matchinglevel = div.data('matchinglevel');
		var selectedattributes = div.data('selectedattributes').split(',');
		var attributescores = div.data('attributescores').split(',');
		var modal = $(this);		
		
		if (matchingscore > 85) {
			circle_color_class = "matching_score_modal_high";
		} else if (matchingscore > 50) {
			circle_color_class = "matching_score_modal_med";
		} else {
			circle_color_class = "matching_score_modal_low";
		}
		modal.find('.matching_score_modal_circle').children().eq(0).removeClass('matching_score_modal_high').removeClass('matching_score_modal_med').removeClass('matching_score_modal_low').addClass(circle_color_class);
		
		modal.find('.matching_score_modal_num').text(matchingscore + "%");
		
		var attr_score_text = '<div class="col" style="margin-right:0.5rem;">';
		for (var i = 0; i < Math.ceil(selectedattributes.length/2); i++) {
			attr_score_text += '<div class="row justify-content-between"><div class="product_matchingscore_modal_attribute_label">';
			attr_score_text += selectedattributes[i];
			attr_score_text += '</div><div class="product_matchingscore_modal_attribute_value">';
			attr_score_text += Math.round(attributescores[i]*100);
			attr_score_text += '%</div></div>';
		}
		attr_score_text += '</div>';
		attr_score_text += '<div class="col" style="margin-right:0.5rem;">';
		for (var i = Math.ceil(selectedattributes.length/2); i < selectedattributes.length; i++) {
			attr_score_text += '<div class="row justify-content-between"><div class="product_matchingscore_modal_attribute_label">';
			attr_score_text += selectedattributes[i];
			attr_score_text += '</div><div class="product_matchingscore_modal_attribute_value">';
			attr_score_text += Math.round(attributescores[i]*100);
			attr_score_text += '%</div></div>';
		}
		attr_score_text += '</div>';
		
		modal.find('.matching_score_modal_body_attributescores').html(attr_score_text);
		
	});


	$('#product_review_modal').on('show.bs.modal', function (event) {
		
		// Show the loading animation
		$(".modal_review_content").css("display", "none");
		$(".modal_loading_shimmer").css("display", "block");
				
		var div = $(event.relatedTarget);
		// If clicked on the see reviews link instead, find the associated product name div
		if ($(event.relatedTarget).hasClass('num_reviews')) {
			div = $(event.relatedTarget).parent().parent().siblings('.product_name').first();
		}
		
		var asin = div.data('asin'); // Get clicked product asin
		var nreviews = div.data('nreviews'); // Get clicked product total reviews
		var title = div.text();
		
		var chosenAttributes = $('#attributes_list label.active').map(function() {
			return $(this).text();
		}).get();
		
		var modal = $(this);
		modal.find('.modal-title').text(title);
		modal.find('.modal_num_reviews').text("Showing top 10 reviews of " + nreviews + " reviews");
		
		a = '<div class="btn-group-toggle" data-toggle="buttons">';
		for (var i = 0; i < chosenAttributes.length; i++) {
			a += '<label class="btn modal_attribute_tag active"><input type="checkbox" autocomplete="off" checked>';
			a += chosenAttributes[i];
			a += '</label>'
		}
		a += '</div>';
		modal.find('.modal_attributes_list').html(a);
		
		var reqData = {};
		reqData['asin'] = asin;
		reqData["attributes"] = chosenAttributes;
		console.log("getting reviews for attributes: " + chosenAttributes + " and ASIN: " + asin);
		
		// THIS IS A TEST ENDPOINT FOR THE FORMAT OF 
		// REVIEWS
		// TODO: UPDATE WITH PROPER getReviewsForASIN CALL
		$.ajax({
			type: 'POST',
			contentType: 'application/json',
			url: '/getReviews',
			dataType: 'json',
			data: JSON.stringify(reqData),
			success : (data) => {
				console.log(data);
				
				var m = '';
				for (var i=0;i < data.length; i++) {
					m += '<div class="modal_review">';
					m += '<div class="modal_review_title">';
					m += data[i]['reviewTitle'];
					m += '</div>';
					//trim the string to the maximum length
					var trimmedString = data[i]['reviewText'].substr(0, 200);
					trimmedString = trimmedString.substr(0, Math.min(trimmedString.length, trimmedString.lastIndexOf(" ")));
					m += trimmedString;
					m += '<span class="moreText" style="display:none;">';
					var restOfString = data[i]['reviewText'].substr(trimmedString.length);
					m += restOfString;
					m += '</span><a class="myCollapse" style="cursor:default;margin-left:0.4rem;"> ...more</a><div class="source_info">';
					var date_string = new Date(data[i]['reviewTime']).toLocaleString();
					m += date_string;
					m += '</div></div>';
				}
				
				$(".modal_review_content").html(m);
				
				$(".modal_loading_shimmer").css("display", "none");
				$(".modal_review_content").css("display", "block");
				
				$('.myCollapse').on('click', function() {
					$(this).siblings('.moreText').first().toggle();
					if ($(this).text() == '...less') {
						$(this).text("...more");
					} else {
						$(this).text("...less");
					}
				});
				
			},
			error : (data) => {
				console.log('got error');
				console.log(data)
			}
		});
		
		
	});
	
	

	
});

