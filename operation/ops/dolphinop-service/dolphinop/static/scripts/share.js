var Zepto=function(){function g(a){return a.filter(function(b){return b!==l&&b!==null})}function e(a,b){this.dom=a||[];this.selector=b||""}function c(a,b){return a==document?new e:b!==l?c(b).find(a):new e(g(a instanceof e?a.dom:a instanceof Array?a:a instanceof Element?[a]:d.call(f.querySelectorAll(a))),a)}var d=[].slice,f=document,i={append:"beforeEnd",prepend:"afterBegin",before:"beforeBegin",after:"afterEnd"},h,m,l;if(String.prototype.trim===l)String.prototype.trim=function(){return this.replace(/^\s+/,
"").replace(/\s+$/,"")};e.prototype=c.fn;c.extend=function(a,b){for(h in b)a[h]=b[h]};camelize=function(a){return a.replace(/-+(.)?/g,function(b,j){return j?j.toUpperCase():""})};c.fn={ready:function(a){document.addEventListener("DOMContentLoaded",a,false);return this},compact:function(){this.dom=g(this.dom);return this},get:function(a){return a===l?this.dom:this.dom[a]},remove:function(){return this.each(function(a){a.parentNode.removeChild(a)})},each:function(a){this.dom.forEach(a);return this},
filter:function(a){return c(this.dom.filter(function(b){return d.call(b.parentNode.querySelectorAll(a)).indexOf(b)>=0}))},is:function(a){return this.dom.length>0&&c(this.dom[0]).filter(a).dom.length>0},first:function(){this.dom=g([this.dom[0]]);return this},find:function(a){return c(this.dom.map(function(b){return d.call(b.querySelectorAll(a))}).reduce(function(b,j){return b.concat(j)},[]))},closest:function(a){var b=this.dom[0].parentNode;for(a=d.call(f.querySelectorAll(a));b&&a.indexOf(b)<0;)b=
b.parentNode;return c(b&&b!==f?b:[])},pluck:function(a){return this.dom.map(function(b){return b[a]})},show:function(){return this.css("display","block")},hide:function(){return this.css("display","none")},prev:function(){return c(this.pluck("previousElementSibling"))},next:function(){return c(this.pluck("nextElementSibling"))},html:function(a){return a===l?this.dom.length>0?this.dom[0].innerHTML:null:this.each(function(b){b.innerHTML=a})},attr:function(a,b){return typeof a=="string"&&b===l?this.dom.length>
0?this.dom[0].getAttribute(a)||undefined:null:this.each(function(j){if(typeof a=="object")for(h in a)j.setAttribute(h,a[h]);else j.setAttribute(a,b)})},offset:function(){var a=this.dom[0].getBoundingClientRect();return{left:a.left+f.body.scrollLeft,top:a.top+f.body.scrollTop,width:a.width,height:a.height}},css:function(a,b){if(b===l&&typeof a=="string")return this.dom[0].style[camelize(a)];m="";for(h in a)m+=h+":"+a[h]+";";if(typeof a=="string")m=a+":"+b;return this.each(function(j){j.style.cssText+=
";"+m})},index:function(a){return this.dom.indexOf(c(a).get(0))},bind:function(a,b){return this.each(function(j){a.split(/\s/).forEach(function(n){j.addEventListener(n,b,false)})})},delegate:function(a,b,j){return this.each(function(n){n.addEventListener(b,function(o){for(var k=o.target,p=d.call(n.querySelectorAll(a));k&&p.indexOf(k)<0;)k=k.parentNode;k&&k!==n&&k!==f&&j(k,o)},false)})},live:function(a,b){c(f.body).delegate(this.selector,a,b);return this},hasClass:function(a){return RegExp("(^|\\s)"+
a+"(\\s|$)").test(this.dom[0].className)},addClass:function(a){return this.each(function(b){!c(b).hasClass(a)&&(b.className+=(b.className?" ":"")+a)})},removeClass:function(a){return this.each(function(b){b.className=b.className.replace(RegExp("(^|\\s)"+a+"(\\s|$)")," ").trim()})},trigger:function(a){return this.each(function(b){var j;b.dispatchEvent(j=f.createEvent("Events"),j.initEvent(a,true,false))})}};["width","height"].forEach(function(a){c.fn[a]=function(){return this.offset()[a]}});for(h in i)c.fn[h]=
function(a){return function(b){return this.each(function(j){j["insertAdjacent"+(b instanceof Element?"Element":"HTML")](a,b)})}}(i[h]);e.prototype=c.fn;return c}();"$"in window||(window.$=Zepto);
(function(g){function e(c){var d={},f=c.match(/(Android)\s+([0-9\.]+)/),i=c.match(/(iPhone\sOS)\s([0-9_]+)/),h=c.match(/(iPad).*OS\s([0-9_]+)/);c=c.match(/(webOS)\/([0-9\.]+)/);if(f){d.android=true;d.version=f[2]}if(i){d.ios=true;d.version=i[2].replace(/_/g,".");d.iphone=true}if(h){d.ios=true;d.version=h[2].replace(/_/g,".");d.ipad=true}if(c){d.webos=true;d.version=c[2]}return d}g.os=e(navigator.userAgent);g.__detect=e})(Zepto);
(function(g){g.fn.anim=function(e,c,d){var f=[],i,h;for(h in e)h==="opacity"?i=e[h]:f.push(h+"("+e[h]+")");return this.css({"-webkit-transition":"all "+(c||0.5)+"s "+(d||""),"-webkit-transform":f.join(" "),opacity:i})}})(Zepto);
(function(g){var e={},c;g(document).ready(function(){g(document.body).bind("touchstart",function(d){var f=Date.now(),i=f-(e.last||f);e.target="tagName"in d.touches[0].target?d.touches[0].target:d.touches[0].target.parentNode;c&&clearTimeout(c);e.x1=d.touches[0].pageX;if(i>0&&i<=250)e.isDoubleTap=true;e.last=f}).bind("touchmove",function(d){e.x2=d.touches[0].pageX}).bind("touchend",function(){if(e.isDoubleTap){g(e.target).trigger("doubleTap");e={}}else if(e.x2>0){Math.abs(e.x1-e.x2)>30&&g(e.target).trigger("swipe");
e.x1=e.x2=e.last=0}else if("last"in e)c=setTimeout(function(){c=null;g(e.target).trigger("tap");e={}},250)}).bind("touchcancel",function(){e={}})});["swipe","doubleTap","tap"].forEach(function(d){g.fn[d]=function(f){return this.bind(d,f)}})})(Zepto);
(function(g){function e(c,d,f){var i=new XMLHttpRequest;i.onreadystatechange=function(){if(i.readyState==4){if(i.status==200||i.status==0)f(i.responseText);else f('')}};i.open(c,d,true);i.send(null)}g.get=function(c,d){e("GET",c,d)};g.post=function(c,d){e("POST",c,d)};g.getJSON=function(c,d){g.get(c,function(f){d(JSON.parse(f))})};g.fn.load=function(c,d){var f=this,i=c.split(/\s/),h;if(!this.length)return this;if(i.length>1){c=i[0];h=i[1]}g.get(c,function(m){f.html(h?
g(document.createElement("div")).html(m).find(h).html():m);d&&d()});return this}})(Zepto);(function(g){var e=[],c;g.fn.remove=function(){return this.each(function(d){if(d.tagName=="IMG"){e.push(d);d.src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=";c&&clearTimeout(c);c=setTimeout(function(){e=[]},6E4)}d.parentNode.removeChild(d)})}})(Zepto);

//     Zepto.js
//     (c) 2010, 2011 Thomas Fuchs
//     Zepto.js may be freely distributed under the MIT license.

(function($){
  var touch = {}, touchTimeout;

  function parentIfText(node){
    return 'tagName' in node ? node : node.parentNode;
  }

  function swipeDirection(x1, x2, y1, y2){
    var xDelta = Math.abs(x1 - x2), yDelta = Math.abs(y1 - y2);
    if (xDelta >= yDelta) {
      return (x1 - x2 > 0 ? 'Left' : 'Right');
    } else {
      return (y1 - y2 > 0 ? 'Up' : 'Down');
    }
  }

  var longTapDelay = 750;
  function longTap(){
    if (touch.last && (Date.now() - touch.last >= longTapDelay)) {
      touch.el.trigger('longTap');
      touch = {};
    }
  }

  $(document).ready(function(){
    $(document.body).bind('touchstart', function(e){
      var now = Date.now(), delta = now - (touch.last || now);
      touch.el = $(parentIfText(e.touches[0].target));
      touchTimeout && clearTimeout(touchTimeout);
      touch.x1 = e.touches[0].pageX;
      touch.y1 = e.touches[0].pageY;
      if (delta > 0 && delta <= 250) touch.isDoubleTap = true;
      touch.last = now;
      setTimeout(longTap, longTapDelay);
    }).bind('touchmove', function(e){
      touch.x2 = e.touches[0].pageX;
      touch.y2 = e.touches[0].pageY;
    }).bind('touchend', function(e){
      if (touch.isDoubleTap) {
        touch.el.trigger('doubleTap');
        touch = {};
      } else if (touch.x2 > 0 || touch.y2 > 0) {
        var xDelta = Math.abs(touch.x1 - touch.x2), yDelta = Math.abs(touch.y1 - touch.y2);
        (xDelta > 30 || yDelta > 30) && touch.el.trigger('swipe');
        (xDelta > 30 ^ yDelta > 30) && touch.el.trigger('swipe' + (swipeDirection(touch.x1, touch.x2, touch.y1, touch.y2)));
        touch.x1 = touch.x2 = touch.y1 = touch.y2 = touch.last = 0;
      } else if ('last' in touch) {
        touch.el.trigger('tap');

        touchTimeout = setTimeout(function(){
          touchTimeout = null;
          touch.el.trigger('singleTap');
          touch = {};
        }, 250);
      }
    }).bind('touchcancel', function(){ touch = {} });
  });

  ['swipe', 'swipeLeft', 'swipeRight', 'swipeUp', 'swipeDown', 'doubleTap', 'tap', 'singleTap', 'longTap'].forEach(function(m){
    $.fn[m] = function(callback){ return this.bind(m, callback) }
  });
})(Zepto);

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

// Simple JavaScript Templating
// John Resig - http://ejohn.org/ - MIT Licensed
(function(){
    var cache = {};

    this.tmpl = function tmpl(str, data){
    // Figure out if we're getting a template, or if we need to
    // load the template - and be sure to cache the result.
    var fn = !/\W/.test(str) ?
        cache[str] = cache[str] ||
        tmpl(document.getElementById(str).innerHTML) :
       
        // Generate a reusable function that will serve as a template
        // generator (and which will be cached).
        new Function("obj",
            "var p=[],print=function(){p.push.apply(p,arguments);};" +
         
            // Introduce the data as local variables using with(){}
             "with(obj){p.push('" +
         
            // Convert the template into pure JavaScript
            str.replace(/[\r\t\n]/g, " ")
               .replace(/'(?=[^%]*%>)/g,"\t")
               .split("'").join("\\'")
               .split("\t").join("'")
               .replace(/<%=(.+?)%>/g, "',$1,'")
               .split("<%").join("');")
               .split("%>").join("p.push('")
               + "');}return p.join('');");
     
        // Provide some basic currying to the user
        return data ? fn( data ) : fn;
    };
})(); 
