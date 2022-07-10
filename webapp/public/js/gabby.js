


$(document).ready(function () {
	
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
			console.log("clicked thumbs up");			
			$(this).toggleClass('thumbs_up_button, thumbs_up2_button');
		} else if ($(this).hasClass("thumbs_down")) {	
			console.log("clicked thumbs down");
			$(this).toggleClass('thumbs_down_button, thumbs_down2_button');
		}
	});

	$(".product_category").on("click", function() {
		
		var category = $(this).attr("name");
		console.log("clicked " + category);
		
		$("#step2_instruction").html(
		"Choose what matters to you when buying a <b>"+category+"</b>"
		);
		
		$("#page1").hide();
		$("#page2").show();
	});
	
	$(".show_more_attributes").on("click", function() {
		
		
		$("#more_attributes").show();
	});
	
	$(".btn_step2Continue").on("click", function() {
		console.log("clicked continue");
		$("#page2").hide();
		$("#page3").show();
	});
	
	$(".btn_step3Continue").on("click", function() {
		console.log("clicked continue");
		$("#page3").hide();
		$("#page4").show();
	});
	
});

