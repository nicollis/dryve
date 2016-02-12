	//shrink header on scrolling 
	$(document).on("scroll", function(){
		if
      ($(document).scrollTop() > 50){
		  $("header").addClass("shrink");
		}
		else
		{
			$("header").removeClass("shrink");
		}
	});
	
	
	//Toggles mobile nav
	function toggleNav() {
		if($(".nav-collapse").is(":visible")){
			$(".nav-collapse").hide();
		}else{
			$(".nav-collapse").show();
		}
	}