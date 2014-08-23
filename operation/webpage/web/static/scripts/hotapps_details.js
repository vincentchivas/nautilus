var track = null;

(function ($) {
	var orientation = 0;
	var lastPosition = 0;

	var trackHost = 'http://track.dolphin-browser.com/track/site.gif?';

	function initScrollView()
	{
		var container = $('.scrollview');
		var scrollview = $('.scroll');

		var left = null;
		var startX = null;
		var startY = null;
		var endX = null;
		var endY = null;
		var count = $('.slice').dom.length;

		scrollview.css('width', Math.ceil(count / 2) * 100 + '%');
		$('.slice').css('width', 0.5 / Math.ceil(count / 2) * 100 + '%');
		
		$('.scrollbar img').dom[0].src = staticPath + 'image/pages/hotapps/bpoint.png';
		
		container.bind('swipeLeft', function(e){
			e.stopPropagation();

			var width = container.dom[0].clientWidth;
			if (startX - endX < width/2)
			{
				scroll(scrollview, -width);
			}
		});

		container.bind('swipeRight', function(e){
			e.stopPropagation();

			var width = container.dom[0].clientWidth;
			if (endX - startX < width/2)
			{l
				scroll(scrollview, width);
			}
		});

		container.bind('touchstart', function(e){
			left = parseInt(scrollview.css('left'));
			startX = e.touches[0].pageX;
			startY = e.touches[0].pageY;
		});

		container.bind('touchmove', function(e){
			endX = e.touches[0].pageX;
			endY = e.touches[0].pageY;
			if (Math.abs(endX - startX) > Math.abs(endY - startY))
			{
				e.preventDefault();
				scrollview.css('left', left + endX - startX);
			}
		});

		container.bind('touchend', function(e){		
			scroll(scrollview, 0);
		});
	}

	function scroll(element, offset)
	{
		var width = $('.scrollview').dom[0].clientWidth;

		var originalX = parseInt(element.css('left'));
		var position = Math.round((originalX + offset) / width);
		var count = Math.ceil($('.slice').dom.length / 2) - 1;

		if (position > 0) position = 0;
		if (position < -count) position = -count; 

		var targetX =  position * width;

		element.css('-webkit-transition', 'left .3s linear');
		element.css('left', targetX);

		if (lastPosition != -position)
		{
			var barItems = $('.scrollbar img').dom;
			position %= barItems.length;

			barItems[lastPosition].src = staticPath + 'image/pages/hotapps/wpoint.png';
			barItems[-position].src = staticPath + 'image/pages/hotapps/bpoint.png';

			lastPosition = -position;
		}
	}
	
	function checkOrientation() {

		if (orientation != window.orientation) {
			orientation = window.orientation;
			
			var body = $('#body');
			if (orientation % 180 != 0) {
				body.css('width', '65%');
			} else {
				body.css('width', '100%');
			}
		}
	}

	track = function (element, name, url) {

		var category = 'subpage';
		var event =  'item';

		var value = url ? (name + ':' + url) : name;
		_gaq.push(['_trackEvent', category, event, value]);

		// dolphin tracking
		var trackUrl = trackHost + 't=0&v=' + version + '&l=' + lang + '&p=' + product + '_' + platform
							+ '&w=' + element.offsetLeft + '&h=' + element.offsetTop
							+ '&col=' + category + '&item=' + event + '&src=' + encodeURIComponent(value);
		$.get(trackUrl);
	}
	
	function initialize()
	{
		initScrollView();

		var wrapper = $('.wrapper');
		var content = $('.content');
		
		$('.more').bind('click', function () {
			if (parseInt(wrapper.css('height')) == content.dom[0].scrollHeight)
			{
				wrapper.css('height', '60px');
				this.innerHTML = toggleStrings[0];
			}
			else
			{
				wrapper.css('height', content.dom[0].scrollHeight);
				this.innerHTML = toggleStrings[1];
			}
		});
		
		window.addEventListener("resize", checkOrientation, false);
		window.addEventListener("orientationchange", checkOrientation, false);

		$('img.lazy').lazyload();
		$('img.lazy').removeClass('lazy');
	}


	$(document).ready(function() {
		
		window.scrollTo(0, 1);
		initialize();

	});
})(Zepto);