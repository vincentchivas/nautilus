/*
 * tab
 */
;(function($) {
	$.extend($.fn, {
		tab : function(obj) {
			var $self = $(this);
			if ($self.length == 0) {
				// if the selector selects nothing, error happens
				console.error("The selector selects nothing");
				return;
			}
			$self.addClass("android");

			obj = obj == undefined ? {} : obj;

			var dom = {
				bar : $self.find(".z-t-bar").first(),
				wrap : $self.find(".z-t-w").first(),
				shouldRemove : null
			};
			dom.content = dom.wrap.children(".z-t-c");
			dom.tabItems = dom.bar.children(".z-t-bar-i");
			dom.contentItems = dom.content.children(".z-t-c-i");

			var settings = {
				shouldAnimate : obj.animate == undefined ? true : obj.animate,
				currentIndex : obj.index == undefined ? 0 : parseInt(obj.index, 10),
				previousIndex : 0,
				animating : false,
				currentX : 0,
				width : dom.content.width(),
				enableSwipe : obj.swipe == undefined ? false : obj.swipe,
				tabCount : dom.tabItems.length,
				startX : 0,
				startY : 0,
				movingX : false,
				movingY : false
			};
			var funs = {
				init : function(obj) {
					funs.callback = obj.tabChange;
					funs.initUI(obj);
					funs.bindEvent();
				},
				initUI : function(obj) {
					$(dom.tabItems[settings.currentIndex]).addClass("active");
					$(dom.contentItems[settings.currentIndex]).addClass("active");
					dom.content.css("-webkit-transition-property", "-webkit-transform").css("-webkit-transition-timing-function", "cubic-bezier(0.33,0.66,0.66,1)").css("-webkit-transition-duration", "0s");
				},
				bindEvent : function() {
					if (settings.enableSwipe) {
						dom.wrap.on("touchstart", funs.touchStart);
						dom.wrap.on("touchmove", funs.touchMove);
						dom.wrap.on("touchend", funs.touchEnd);
						dom.wrap.on("touchcancel", funs.touchCancel);
					}
					if (settings.shouldAnimate) {
						dom.content.on("webkitTransitionEnd", function() {
							dom.content.css("-webkit-transition-duration", "0s");
							$(dom.shouldRemove).removeClass("active");
							settings.animating = false;
							if (settings.currentIndex != settings.previousIndex) {
								//dom.wrap.css("overflow-x", "hidden");
								//dom.wrap.width($(dom.contentItems[settings.currentIndex]).width());
								//dom.wrap.height($(dom.contentItems[settings.currentIndex]).height());
								if (settings.currentIndex > 0) {
									$(dom.contentItems[settings.currentIndex - 1]).removeClass("active");
								}
								if (settings.currentIndex < settings.tabCount - 1) {
									$(dom.contentItems[settings.currentIndex + 1]).removeClass("active");
								}
								//dom.wrap.css("overflow-x", "hidden");
								window.scrollTo(0, 1);
								if ($.isFunction(funs.callback)) {
									funs.callback(settings.currentIndex, settings.previousIndex);
								}
							}
						});
					}
					dom.tabItems.on("click", function(e) {
						settings.width = dom.content.width();
						var index = dom.tabItems.indexOf(this);
						if (index == settings.currentIndex)
							return;
						if(!$(".z-l-s" ,dom.contentItems[0])[0]){
							//$.ol.loading.show();
						}
						funs.goToTab(index);
					});
				},
				goToTab : function(index) {
					settings.previousIndex = settings.currentIndex;
					if (settings.shouldAnimate) {
						if (settings.animating)
							return;

						dom.content.css("-webkit-transition-duration", "0.2s");
						settings.animating = true;

						// 更改标签头
						$(dom.tabItems[settings.currentIndex]).removeClass("active");
						$(dom.tabItems[index]).addClass("active");

						var willAppear = dom.contentItems[index];
						var willDisappear = dom.contentItems[settings.currentIndex];
						dom.shouldRemove = willDisappear;

						// 进行切换，步骤是1，将即将出现的元素移动到右边（或左边） 2，开始切换
						if (index < settings.currentIndex) {
							willAppear.style["-webkit-transform"] = "translate3d(" + (settings.currentX + settings.width) + "px,0,0)";
							$(willAppear).addClass("active");
							settings.currentX += settings.width;
							setTimeout(function() {
								dom.content[0].style["-webkit-transform"] = "translate3d(" + -settings.currentX + "px,0,0)";
							}, 50);
						} else {
							willAppear.style["-webkit-transform"] = "translate3d(" + (settings.currentX - settings.width) + "px,0,0)";
							$(willAppear).addClass("active");
							settings.currentX -= settings.width;
							setTimeout(function() {
								dom.content[0].style["-webkit-transform"] = "translate3d(" + -settings.currentX + "px,0,0)";
							}, 50);
						}
					} else {
						$(dom.tabItems[settings.currentIndex]).removeClass("active");
						$(dom.tabItems[index]).addClass("active");

						$(dom.contentItems[index]).addClass("active");
						$(dom.contentItems[settings.currentIndex]).removeClass("active");

						if ($.isFunction(funs.callback)) {
							funs.callback(index, settings.currentIndex);
						}
					}
					settings.currentIndex = index;
				},
				touchStart : function(e) {
					settings.startX = e.touches[0].pageX;
					settings.startY = e.touches[0].pageY;

					var previous = settings.currentIndex - 1;
					var next = settings.currentIndex + 1;
					var willAppear;
					if (previous >= 0) {
						willAppear = dom.contentItems[previous];
						willAppear.style["-webkit-transform"] = "translate3d(" + (settings.currentX - settings.width) + "px,0,0)";
						$(willAppear).addClass("active");
					}
					if (next < settings.tabCount) {
						willAppear = dom.contentItems[next];
						willAppear.style["-webkit-transform"] = "translate3d(" + (settings.currentX + settings.width) + "px,0,0)";
						$(willAppear).addClass("active");
					}
				},
				touchMove : function(e) {
					var cX = e.touches[0].pageX;
					var cY = e.touches[0].pageY;

					var dX = cX - settings.startX;
					var dY = cY - settings.startY;

					if (settings.movingX) {
						e.preventDefault();
						var previous = settings.currentIndex - 1;
						var next = settings.currentIndex + 1;
						if (previous < 0 && dX > 0 || next == settings.tabCount && dX < 0) {
							dX = dX / 3;
						} else {
							dX = dX / 1.5;
						}
						dom.content[0].style["-webkit-transform"] = "translate3d(" + (dX - settings.currentX) + "px,0,0)";
					} else {
						if (settings.movingY) {
							settings.movingX = false;
						} else {
							if (Math.abs(dY) <= 5) {
								if (Math.abs(dX) > 10) {
									settings.movingX = true;
									settings.movingY = false;
								}
							} else {
								settings.movingY = true;
							}
						}
					}
				},
				touchEnd : function(e) {
					settings.movingY = false;
					if (settings.movingX) {
						settings.movingX = false;
						var cX = e.changedTouches[0].pageX;
						var dX = cX - settings.startX;
						var previous = settings.currentIndex - 1;
						var next = settings.currentIndex + 1;
						if (previous < 0 && dX > 0 || next == settings.tabCount && dX < 0 || Math.abs(dX) <= 30) {
							dom.content.css("-webkit-transition-duration", "0.2s");
							setTimeout(function() {
								dom.content[0].style["-webkit-transform"] = "translate3d(" + -settings.currentX + "px,0,0)";
							}, 0);
						} else {
							if (dX < 0) {
								funs.goToTab(next);
							} else {
								funs.goToTab(previous);
							}
						}
					}
				},
				touchCancel : function(e) {
					dom.content[0].style["-webkit-transform"] = "translate3d(" + -settings.currentX + "px,0,0)";
				}
			};
			funs.init(obj);

			$self.selectTab = function(index) {
				if (index == settings.currentIndex)
					return $self;
				funs.goToTab(index);
				return $self;
			};

			$self.currentIndex = function() {
				return settings.currentIndex;
			};

			return $self;
		}
	});
})(Zepto);