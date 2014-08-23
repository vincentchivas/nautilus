/*
 * carousel
 */
;(function($) {
	$.extend($.fn, {
		carousel : function(obj) {
			this.each(function(){
				// 当前Zepto对象
				var $self = $(this);

				var dom = {
					wrap : $self.find(".z-c-w"),
					items : $self.find(".z-c-i"),
					pageControl : null,
					pageItems : null
				};
				var settings = {
					width : dom.wrap.width(),
					count : dom.items.size(),
					index : 0,
					startX : 0,
					startY : 0,
					movingX : false,
					movingY : false,
					distance : 0,
					pageControl : obj ? (obj.showControl ? true : false) : true,
					autoScroll : obj ? (obj.autoScroll ? true : false) : false
				};
				var funs = {
					init : function() {
						funs.initUI();
						funs.bindEvent();
						if (settings.autoScroll) {
							settings.interval = setInterval(funs.autoScroll, 5000);
						}
					},
					bindEvent : function() {
						dom.wrap.off().on({
							"touchstart" : function(e) {
								//e.stopPropagation();
								settings.width = dom.wrap.width();
								settings.distance = settings.width / 4;
								
								settings.startX = e.touches[0].pageX;
								settings.startY = e.touches[0].pageY;

								if (settings.autoScroll){
									clearInterval(settings.interval);
									//隐藏最后一个循环页
									dom.dupItem.css("visibility", "hidden");
								}
							},
							"touchmove" : function(e) {
								//e.stopPropagation();
								var currentX = e.touches[0].pageX;
								var currentY = e.touches[0].pageY;
								var dX = currentX - settings.startX;
								var dY = currentY - settings.startY;

								if (settings.movingX) {
									e.stopPropagation();
									e.preventDefault();
									var x = 0;
									if (settings.index == 0 && dX > 0 || settings.index == settings.count - 1 && dX < 0) {
										x = -settings.index * settings.width + dX / 3;
									} else {
										x = -settings.index * settings.width + dX;
									}
									dom.wrap.css("-webkit-transform", "translate3d(" + x + "px,0,0)");
								} else if (!settings.movingY) {
									e.stopPropagation();
									var dX = Math.abs(dX);
									var dY = Math.abs(dY);
									if (dX > 10 && dX/dY > 1) {
										settings.movingX = true;
										settings.movingY = false;
									} else if(dY > 10 && dX/dY < 1) {
										settings.movingY = true;
										settings.movingX = false;
									}
								}
							},
							"touchend" : function(e) {
								//e.stopPropagation();
								settings.movingY = false;
								if (settings.movingX) {
									settings.movingX = false;
									var currentX = e.changedTouches[0].pageX;
									var distance = currentX - settings.startX;
									if (Math.abs(distance) >= settings.distance) {
										settings.index = settings.index - Math.abs(distance) / distance;
										settings.index = settings.index < 0 ? 0 : (settings.index > (settings.count - 1) ? (settings.count - 1) : settings.index);
									}
									funs.continueMove();
								}
								if (settings.autoScroll) {
									settings.interval = setInterval(funs.autoScroll, 5000);
									setTimeout(function(){
										dom.dupItem.css("visibility", "visible");
									},250);
								}
							},
							"webkitTransitionEnd" : function() {
								dom.wrap.removeClass("transitionable");
								if(settings.index >= settings.count){
									settings.index %= settings.count;
									dom.wrap.css("-webkit-transform", "translate3d(" + -settings.index * settings.width + "px,0,0)");
								}
							}
						});
						dom.pageControl.off().on("touchstart", function(e) {
							settings.width = dom.wrap.width();
							settings.distance = settings.width / 4;
							
							var touchX = e.touches[0].pageX;
							var currentX = $(dom.pageItems[settings.index]).offset().left;
							if (touchX > currentX && settings.index < (settings.count - 1)) {
								settings.index += 1;
								funs.continueMove();
							} else if (touchX < currentX && settings.index > 0) {
								settings.index -= 1;
								funs.continueMove();
							}
						});
						$(window).on({
							"resize" : function() {
								funs.adjustPOS();
							},
							"orientationchange" : function() {
								funs.adjustPOS();
							}
						});
					},
					adjustPOS : function() {
						settings.width = dom.wrap.width();
						settings.distance = settings.width / 5;
						dom.wrap.css("-webkit-transform", "translate3d(" + -settings.index * settings.width + "px,0,0)");
					},
					continueMove : function() {
						dom.wrap.addClass("transitionable");
						dom.pageItems.removeClass("active");
						$(dom.pageItems[settings.index % settings.count]).addClass("active");
						dom.wrap.css("-webkit-transform", "translate3d(" + -settings.index * settings.width + "px,0,0)");
					},
					initUI : function() {
						settings.distance = settings.width / 4;
						if (settings.pageControl) {
							$self.append(funs.createPageDOM());
						}
						dom.pageControl = $self.find(".z-c-p");
						dom.pageItems = $self.find(".z-c-p>span");

						if(settings.autoScroll){
							//重复第一个页面用作尾部的循环
							funs.dupFirstItem();
						}
					},
					dupFirstItem : function() {
						dom.dupItem = $self.find(".z-c-i:first-child").clone();
						$(dom.wrap).append(dom.dupItem);
					},
					createPageDOM : function() {
						var pageControlToRemove = $self.find(".z-c-p");
						if (pageControlToRemove.length) {
							pageControlToRemove.remove();
						}
						var pageFragment = document.createDocumentFragment();
						var pageDiv = document.createElement("div");
						pageDiv.setAttribute("class", "z-c-p");
						pageFragment.appendChild(pageDiv);
						var pageItemSpan = document.createElement("span");
						pageItemSpan.setAttribute("class", "active");
						pageDiv.appendChild(pageItemSpan);
						for (var i = 1; i < settings.count; i++) {
							pageItemSpan = document.createElement("span");
							pageDiv.appendChild(pageItemSpan);
						}
						return pageFragment;
					},
					clear : function() {
						var pageControlToRemove = $self.find(".z-c-p");
						if (pageControlToRemove.length) {
							pageControlToRemove.remove();
						}
						dom.wrap.empty().css("-webkit-transform", "translate3d(0,0,0)");
					},
					autoScroll : function() {
						if(dom.wrap.width() > 0 && dom.items.width() > 0){
							settings.index++;
							settings.width = dom.wrap.width();
							funs.continueMove(settings.index);
						}
					} 
				};

				funs.init();

				$self.clear = funs.clear;
			});

			return this;
		}
	});
})(Zepto);