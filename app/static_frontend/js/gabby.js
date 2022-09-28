
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
		console.log("clicked " + category);
		
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
				console.log('got response: ');
				console.log(JSON.stringify(data));		

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
	
	/*$(".btn_step2Continue").on("click", function() {
		console.log("getting reviews");
		var reqData = {};
		var chosenAttributes = $('#attributes_list label.active').map(function() {
			return $(this).text();
		}).get();
		reqData["attributes"] = chosenAttributes;
		console.log(reqData);
		
		$.ajax({
			type: 'POST',
			contentType: 'application/json',
			url: '/getReviews',
			dataType: 'json',
			data: JSON.stringify(reqData),
			success : (data) => {
				console.log('got response: ');
				console.log(JSON.stringify(data));	
								
				// Populate review cards with data
				//var review = data[0];
				//var r = '';
				//r += '<div class="review_card"><div class="row"><div class="col-6"><div class="review_text">';
				//r += review['reviewText'];
				//r += '</div><div class="source_info">';
				//r += review['reviewTime']; //date
				//r += '</div></div><div class="col-3"><div class="attribute_header">matching words</div><div class="matching_words">'
				//r += review['phrase']; //matching phrases
				//r += '</div></div><div class="col-3"><div class="helpful_header">Resonates?</div><button class="btn thumbs_btn thumbs_up thumbs_up_button"></button><button class="btn thumbs_btn thumbs_down thumbs_down_button"></button></div></div></div>';
				
				//$('#review_list').html(r);
				
				for (var i=0;i<5;i++) {
					$($('#review_list .review_text')[i]).html(data[i]['reviewText']);
					var d = new Date(data[i]['reviewTime']);		
					$($('#review_list .source_info')[i]).html(d.toLocaleString());
					$($('#review_list .matching_words')[i]).html(data[i]['phrase']);
				}
				
			},
			error : (data) => {
				console.log('got error');
				console.log(data)
			}
		});
		
		
		$("#page2").hide();
		$("#page4").show();
		//window.history.pushState({step: 3},"","?step=3");
		currPage = 4;
	});*/
	
	$(".btn_step2Continue").on("click", function() {
		console.log("getting products");
		var reqData = {};
		var chosenAttributes = $('#attributes_list label.active').map(function() {
			return $(this).text();
		}).get();
		reqData["attributes"] = chosenAttributes;
		console.log(reqData);

		$.ajax({
			type: 'POST',
			contentType: 'application/json',
			url: '/getProducts',
			dataType: 'json',
			data: JSON.stringify(reqData),
			success : (data) => {
				console.log('got response: ');
				console.log(JSON.stringify(data));		

				for (var i=0;i<10;i++) {
					$($('#product_list .product_image img')[i]).attr('src',data[i]['imageURLHighRes'].split(',')[0]);							
					$($('#product_list .product_name')[i]).text(data[i]['title']);
					$($('#product_list .num_reviews')[i]).text(data[i]['num_reviews'] + " reviews");
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
	
});

