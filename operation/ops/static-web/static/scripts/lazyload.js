/*
 * Lazy Load - jQuery plugin for lazy loading images
 *
 * Copyright (c) 2007-2011 Mika Tuupola
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 * Project home:
 *   http://www.appelsiini.net/projects/lazyload
 *
 * Version:  1.6.0-dev
 *
 */
(function($) {

    $.fn.lazyload = function() {
        /* default behavior is preload */
        var loadfunc = arguments[0] || $.preload;
                
        /* Fire one scroll event per scroll. Not one scroll event per image. */
        var elements = this;
        
        window.addEventListener('scroll', function(event) {
            var counter = 0;
            elements.each(function(e) {
                if ($.abovethetop(e) ||
                    $.leftofbegin(e)) {
                        /* Nothing. */
                } else if (!$.belowthefold(e) &&
                    !$.rightoffold(e)) {
                        $(e).trigger("appear");
                }
            });

            /* Remove image from array so it is not looped next time. */
            var temp = [];
            for ( var i = 0, length = elements.dom.length; i < length; i++ ) {
                if ( !elements.dom[ i ].loaded) {
                    temp.push( elements.dom[ i ] );
                }
            }
            elements = $(temp);
        });
        
        this.each(function(e) {
            var self = e;            
            self.loaded = false;
            
            /* When appear is triggered load original image. */
            $(self).bind("appear", function() {
                if (!e.loaded) {
                    loadfunc(self);
                };
            });
        });
        
        /* Force initial check if images should appear. */
        var event = document.createEvent("Events");
        event.initEvent("scroll", true, false);
        window.dispatchEvent(event);
        
        return this;

    };

    /* Convenience methods in jQuery namespace.           */
    /* Use as  $.belowthefold(element, {threshold : 100, container : window}) */

    $.belowthefold = function(element) {
        var fold = window.innerHeight + window.scrollY;
        return fold <= $(element).offset().top;
    };
    
    $.rightoffold = function(element) {
        var fold = window.innerWidth + window.scrollX;
        return fold <= $(element).offset().left;
    };
        
    $.abovethetop = function(element) {
        var fold = window.scrollY;
        return fold >= $(element).offset().top  + $(element).height();
    };
    
    $.leftofbegin = function(element) {
        var fold = window.scrollX;
        return fold >= $(element).offset().left + $(element).width();
    };
    
    $.preload = function(element) {
        var img = document.createElement('img');
        $(img)
            .bind("load", function() {
                $(element)
                    .hide()
                    .attr("src", $(element).attr('data-original'))
                    .show();
                element.loaded = true;
            })
            .attr("src", $(element).attr('data-original'));		
    };

    $.load = function(element) {
        $(element).attr("src", $(element).attr('data-original'));
        element.loaded = true;
    };
})(Zepto);
