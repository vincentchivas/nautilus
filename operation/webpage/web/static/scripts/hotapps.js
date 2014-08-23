var loadCategoryApps = null;
var track = null;
var parseAds = null;

(function ($) {
    var isAjaxCompleted = true;

    var columnName = 'featured';
    var categoryId = '';
    var categoryTitle = null;

    var columnEndFlag = [];
    var columnPage = [];
    var columnContent = [];
    var columnWrap = [];
    var columnTab = [];
    var appLoad = [];
    var pageLoad = null;

    var orientation = 0;
    var lastPosition = 0;
    var timeInt = null;

    // dolphin tracking
    var trackHost = 'http://track.dolphin-browser.com/track/site.gif?';
    
    // ad tracking
    var adHost = 'http://www.belugaboost.com/stats/ask.jsonp?';

    function initial() {

        columnEndFlag.featured = false;
        columnEndFlag.trending = false;
        columnEndFlag.categories = true; // category does not scroll loading
        columnEndFlag.cateapps = false;

        columnPage.featured = 2;
        columnPage.trending = 1;
        columnPage.categories = 1;
        columnPage.cateapps = 1;

        columnContent.featured = $('#feature_content');
        columnContent.trending = $('#trend_content');
        columnContent.categories = $('#category_content');
        columnContent.cateapps = $('#cateapps_content');

        columnWrap.featured = $('#feature_wrap');
        columnWrap.trending = $('#trend_wrap');
        columnWrap.categories = $('#category_wrap');
        columnWrap.cateapps = $('#cateapps_wrap');

        columnTab.featured = $('#feature_tab');
        columnTab.trending = $('#trend_tab');
        columnTab.categories = $('#category_tab');
        columnTab.cateapps = $('#category_tab'); // cateapps share the same tab with category

        pageLoad = $('#page_load');

        appLoad.featured = $('#feature_load');
        appLoad.trending = $('#trend_load');
        // appLoad.categories = $('#category_load'); category has no loading
        appLoad.cateapps = $('#cateapps_load');

        categoryTitle = $('#cateapps_title');
    }

    function loadContent(url, columnName) {

        if (!isAjaxCompleted) return;

        isAjaxCompleted = false;
        loading(columnName);

        $.get(url, function (data) {
            loadTemplate(data, columnName);
            isAjaxCompleted = true;
        });
    }

    function loading(columnName) {

        if (columnPage[columnName] > 1) {
            appLoad[columnName].css('display', 'inline-block');
        } else {
            pageLoad.css('display', 'block');
        }
    }

    function loadTemplate(resData, columnName) {

        if (columnPage[columnName] > 1) {
            appLoad[columnName].css('display', 'none');
        } else {
            pageLoad.css('display', 'none');
        }

        if (resData == '') {
            columnEndFlag[columnName] = true;
            $('.bottom', columnWrap[columnName]).hide();
            return;
        }

        if (columnName == 'trending' && trendApi) {
            var data = eval('(' + resData + ')');
            columnContent[columnName].append(tmpl('trending_tmpl', data));
        } else {
            columnContent[columnName].append(resData);
        }

        columnPage[columnName]++;

        loadAdTracking();

        $('img.lazy').lazyload();
        $('img.lazy').removeClass('lazy');
    }

    function loadAdTracking() {
        var ads = $('img.loadtrack');
        
        if (ads.dom.length > 0) {
            var parameters = ('p=' + adPublisherId);
            ads.each(function(e) {
                parameters += ('&adId=' + $(e).attr('data-id'));
            });
            parameters += '&callback=parseAds';
            
            var url = adHost + parameters;
            $('#jsonp').attr('src', url);

            ads.removeClass('loadtrack');
        }
    }

    parseAds = function(ads) {
        for (var i = 0; i< ads.length; ++i) {
            var id = ads[i].ad_id;
            
            var app = $('#ad_' + id);
            app.attr('href', ads[i].click_url);
            
            var impress = $('.track', app);
            impress.attr('data-original', ads[i].impress_url);
            impress.addClass('lazy');
        }
        
        $('img.lazy').lazyload($.load);
        $('img.lazy').removeClass('lazy');
    }

    function registerEvents() {

        $('#submit').bind('click', function () {

            var input = $('#keyword');

            if (input.dom[0].value == '') {
                input.dom[0].value = keyword;
            }
        });

        /*
        $('#feature').bind('click', function () {
            switchTabs('featured');
        });

        $('#trend').bind('click', function () {
            switchTabs('trending');
        });

        $('#category').bind('click', function () {
            switchTabs('categories');
        });
        */

        /* disabled by design in short term
        if (touchSupport)
        {
            $('#contents').bind('swipeLeft', function(){
                swipeTabs('left');
            });

            $('#contents').bind('swipeRight', function(){
                swipeTabs('right');
            });
        }
        */

        window.addEventListener("resize", checkOrientation, false);
        window.addEventListener("orientationchange", checkOrientation, false);

        window.addEventListener('scroll', function () {

            var isBottom = (window.scrollY + window.innerHeight + 200) >= document.documentElement.scrollHeight;

            if (isBottom && !columnEndFlag[columnName]) {
                var url = getLoadingPath() + '&page=' + columnPage[columnName];
                loadContent(url, columnName);
                return;
            }
        }, false);

        window.addEventListener('hashchange', function () {
            var hash = window.location.hash;
            if (hash != '#cateapps' || columnPage.cateapps > 1) {
                switchTabs(hash != '' ? hash.slice(1) : 'featured');
            }
        });
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

    function swipeTabs(direction) {

        if (direction == 'right') {
            switch (columnName) {
            case 'featured': return switchTabs('categories');
            case 'trending': return switchTabs('featured');
            case 'categories':
            case 'cateapps': return switchTabs('trending');
            }
        } else if (direction == 'left') {
            switch (columnName) {
            case 'featured': return switchTabs('trending');
            case 'trending': return switchTabs('categories');
            case 'categories':
            case 'cateapps': return switchTabs('featured');
            }
        }
    }

    function switchTabs(newColumnName) {

        if (columnTab[newColumnName]
            && columnName != newColumnName) {

            if (columnPage[columnName] == 1) {
                pageLoad.css('display', 'none');
            }

            columnTab[columnName].removeClass('active');
            columnWrap[columnName].hide();

            //window.scrollTo(0, 1);
            columnName = newColumnName;

            columnTab[columnName].addClass('active');
            columnWrap[columnName].show();

            if (columnPage[columnName] == 1) {
                var url = getLoadingPath() + '&page=1';
                loadContent(url, columnName);
            }
        }
    }

    loadCategoryApps = function (element, type, cateId, cateName) {

        categoryId = cateId;
        categoryTitle.html(cateName);

        // click tracking function
        track(element, type, cateName, cateId);

        var columnName = 'cateapps';
        columnPage[columnName] = 1;
        columnEndFlag[columnName] = false;
        columnContent[columnName].html('');
        $('.bottom', columnWrap[columnName]).show();
        appLoad[columnName].css('display', 'none');

        switchTabs(columnName);
    }

    function getLoadingPath() {

        var path = null;

        switch (columnName) {
        case "featured": path = './featured.html'; break;
        case "trending": path = trendApi ? './trendapi' : './trend.html'; break;
        case "categories": path = './categories.html'; break;
        case "cateapps": path = './cateapps.html'; break;
        }

        var parameter = '?os=' + platform + '&l=' + lang;

        if (path == './trendapi'){
            parameter = '?type=' + platform.toLowerCase() + '&l=' + lang;
        }

        if (columnName == 'cateapps') {
            parameter += ('&id=' + categoryId);
        }

        return path + parameter;
    }

    function initScrollView() {

        var container = $('#scrollview_container');
        var scrollview = $('.scroll');

        var left, startX, startY, endX, endY = null;
        var count = $('.slice').dom.length;

        scrollview.css('width', count * 100 + '%');
        $('.slice').css('width', 1 / count * 100 + '%');
        $('.slice').css('display','block');

        //$('.scrollbar img').dom[0].src = staticPath + 'image/pages/hotapps/bpoint.png';
	
        autoScroll();

        // bind scroll related event
        if (touchSupport) {

            container.bind('swipeLeft', function (e) {
                e.stopPropagation();

                var width = container.dom[0].clientWidth;
                if (startX - endX < width / 2) {
                    scroll(scrollview, -width);
                }
            });

            container.bind('swipeRight', function (e) {
                e.stopPropagation();

                var width = container.dom[0].clientWidth;
                if (endX - startX < width / 2) {
                    scroll(scrollview, width);
                }
            });

            container.bind('touchstart', function (e) {
                clearInterval(timeInt); // cancel the auto scrolling

                left = parseInt(scrollview.css('left'));
                startX = e.touches[0].pageX;
                startY = e.touches[0].pageY;
            });

            container.bind('touchmove', function (e) {
                endX = e.touches[0].pageX;
                endY = e.touches[0].pageY;

                if (Math.abs(endX - startX) > Math.abs(endY - startY)) {
                    e.preventDefault();
                    scrollview.css('left', left + endX - startX);
                }
            });

            container.bind('touchend', function () {
                scroll(scrollview, 0);
                autoScroll(); // restart the auto scrolling
            });
        }
    }

    function autoScroll() {

        var container = $('#scrollview_container');
        var scrollview = $('.scroll');
        var slices = $('.slice');
        var count = slices.dom.length;

        timeInt = setInterval(function () {

            if (columnName == 'featured') {
                var width = container.dom[0].clientWidth;

                if (lastPosition != count - 1) {
                    scroll(scrollview, -width);
                } else {
                    // adjust the width settings for appending
                    // use absolute width to avoid shaking
                    scrollview.css('width', (count + 1) * width);
                    slices.css('width', width);

                    // add the first slice to the end
                    // after scrolling, reset to the beginning
                    scrollview.append(slices.dom[0].outerHTML);
                    scroll(scrollview, -width);

                    setTimeout(function () {
                        scrollview.css('-webkit-transition', 'none');
                        scrollview.css('left', 0);
                        
                        // restore the width settings
                        scrollview.css('width', count * 100 + '%');
                        slices.css('width', 1 / count * 100 + '%');
                        scrollview.dom[0].removeChild($('.slice').dom[count]);
                    }, 300);
                }
            }
        }, 9000);
    }

    function scroll(element, offset) {

        var width = $('#scrollview_container').dom[0].clientWidth;

        var originalX = parseInt(element.css('left'));
        var position = Math.round((originalX + offset) / width);
        var count = $('.slice').dom.length - 1;

        if (position > 0) position = 0;
        if (position < -count) position = -count; 

        var targetX = position * width;

        element.css('-webkit-transition', 'left .3s linear');
        element.css('left', targetX);

        if (lastPosition != -position) {
            var barItems = $('.scrollbar div').dom;
            position %= barItems.length;

            //barItems[lastPosition].src = staticPath + 'image/pages/hotapps/wpoint.png';
            //barItems[-position].src = staticPath + 'image/pages/hotapps/bpoint.png';

            $(barItems[lastPosition]).removeClass("black");
            $(barItems[-position]).addClass("black");

            lastPosition = -position;
        }
    }

    track = function (element, type, name, url) {

        var event = null;
        var value = url ? (name + ':' + url) : name;

        if (type == 'search') {
            // make the 'search' independent to each column
            _gaq.push(['_trackEvent', type, columnName, value]);
        } else {

            switch (columnName) {
            case "featured":
            case "trending":
            case "categories": event = columnName + '_' + type; break;
            default: event = categoryTitle.html() + '_' + type; break;
            }

            _gaq.push(['_trackEvent', columnName, event, value]);
        }

        // dolphin tracking
        var trackUrl = trackHost + 't=0&v=' + version + '&l=' + lang + '&p=' + product + '_' + platform
                            + '&w=' + element.offsetLeft + '&h=' + element.offsetTop
                            + '&col=' + columnName + '&item=' + event + '&src=' + encodeURIComponent(value);
        $.get(trackUrl);
    }

    $(document).ready(function () {

        initial();

        window.scrollTo(0, 1);

        registerEvents();

        if (top.location != self.location) {
            top.location = self.location.href;
        }

        setTimeout(function () {
            // load the feature scrollview
            //var url = './topfeatured.html?os=' + platform + '&l=' + lang;
            //$.get(url, function (data) {
            //    if (data != '') {
             //       $('#scrollview_container').html(data);
                initScrollView();
        $('img.lazy').lazyload();
        $('img.lazy').removeClass('lazy');
            //    }
            //});

            var hash = window.location.hash;

            if (hash != '' && hash != '#cateapps' 
                && hash.slice(1) != columnName) {
                switchTabs(hash.slice(1));
            } 
		//else {
                 //load the feature page first
                //url = getLoadingPath() + '&page=' + columnPage[columnName];
                //loadContent(url, columnName);
            //}
        }, 800);
    });
})(Zepto);
