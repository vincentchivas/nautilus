var track = null;
var showDetails = null;
var showNext = null;
var hideDetails = null;

(function ($) {
    var isAjaxCompleted = true;
    var columnName = 'trending';
    var columnEndFlag = [];
    var columnPage = [];
    var columnContent = [];
    var columnWrap = [];
    var columnTab = [];
    var appLoad = [];
    var pageLoad = null;

    var lastOffset = 0;
    var orientation = -1;
    var lastPosition = 0;
    var timeInt = null;

    var tabs = new Array("trending","featured","games", "applications");

    // dolphin tracking
    var trackHost = 'http://track.dolphin-browser.com/track/site.gif?';
    
    function initial() {

        if (lang != 'zh_CN') {
            columnName = 'featured';
            tabs = new Array("featured","games", "applications");
        }   

        for (i in tabs)
        {
            var tab = tabs[i];
            
            columnEndFlag[tab] = false;
            columnPage[tab] = 1;
            columnContent[tab] = $('#' + tab + '_content');
            columnWrap[tab] = $('#' + tab + '_wrap');
            columnTab[tab] = $('#' + tab + '_tab');
            appLoad[tab] = null;
        }

        pageLoad = $('#page_load');
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
        pageLoad.css('visibility', 'visible');
    }

    function loadTemplate(resData, columnName) {

        pageLoad.css('visibility', 'hidden');
        
        if (resData.replace(/(^\s*)|(\s*$)/g, '') == '') {
            columnEndFlag[columnName] = true;
            return;
        }

        if (columnName == 'trending' && trendApi) {
           // var data = eval('(' + resData + ')');
           // columnContent[columnName].append(tmpl('trending_tmpl', data));
        } else {
            columnContent[columnName].append(resData);
        }
        columnPage[columnName]++;
        
        $('img.lazy').lazyload();
        $('img.lazy').removeClass('lazy');
    }

    function registerEvents() {

        // submit the default search query
        $('#submit').bind('click', function () {
            var input = $('#keyword');

            if (input.dom[0].value == '') {
                input.dom[0].value = keyword;
            }
        });

        var container = $('#container');
        var scrollarea = $('#scrollarea');
    
        var startY, endY, offset, maxOffset = null;
        var speed, lastTime, slowTime = null;
        var loadApps = false;
        
        container.bind('touchstart', function (e) {
            speed = 0;
            offset = lastOffset;
            maxOffset = scrollarea.height() - parseInt(container.css('height'));
            lastTime = e.timeStamp;
            endY = startY = e.touches[0].pageY;
            scrollarea.css('-webkit-transition', 'none');
        });

        container.bind('touchmove', function (e) {
            e.preventDefault();
            speed = (e.touches[0].pageY - endY) / (e.timeStamp - lastTime);
            lastTime = e.timeStamp;
            endY = e.touches[0].pageY;

            offset = lastOffset + endY - startY;
            
            if (offset > 0) {
                offset = 0;
            } else if (offset < -maxOffset) {
                offset =  (offset + maxOffset) / 2 - maxOffset;
            }
            
            scrollarea.css('-webkit-transform', 'translate3d(0, ' + offset + 'px, 0)');
        });

        container.bind('touchend', function (e) {
            if (offset < -maxOffset) {
                slowTime = 300;
                lastOffset = -maxOffset;
            } else {
                var accelerate = speed > 0 ? 0.0025 : -0.0025;
                slowTime = speed / accelerate;
                var distance = 0.5 * accelerate * slowTime * slowTime;
                var diffTime = 0;
                
                lastOffset = offset + distance;

                if (lastOffset > 0) {
                    diffTime = Math.sqrt(1.5 * lastOffset / accelerate);
                    lastOffset = 0;
                } else if (lastOffset < -maxOffset) {
                    diffTime = Math.sqrt(1.5 * (lastOffset  + maxOffset) / accelerate);
                    lastOffset =  - maxOffset ;
                }

                slowTime -= diffTime;
            }

            if (lastOffset + maxOffset < 100) {
                loadApps = true;
            }

            autoScroll(lastOffset, slowTime);

            setTimeout(function () {
                var event = document.createEvent("Events");
                event.initEvent("scroll", true, false);
                window.dispatchEvent(event);
            }, slowTime);
        });

        function autoScroll(offset, time) {
            scrollarea.css('-webkit-transition', '-webkit-transform ' + time/1000 + 's cubic-bezier(0.33, 0.66, 0.66, 1)');					
            scrollarea.css('-webkit-transform', 'translate3d(0, ' + offset + 'px, 0)');
        }

        window.addEventListener("resize", checkOrientation, false);
        window.addEventListener("orientationchange", checkOrientation, false);

        window.addEventListener('scroll', function (e) {
            if (loadApps && !columnEndFlag[columnName]) {
                loadApps = false;
                var url = getLoadingPath() + '&page=' + columnPage[columnName];
                loadContent(url, columnName);
                return;
            }
        }, false);

        window.addEventListener('hashchange', function () {
            var hash = window.location.hash;
            if (hash != '#cateapps' || columnPage.cateapps > 1) {
                if (lang == 'zh_CN') {
                    switchTabs(hash != '' ? hash.slice(1) : 'trending');
                }
                else {
                    switchTabs(hash != '' ? hash.slice(1) : 'featured');
                }
            }
        });

        document.addEventListener('touchmove', function (e) {
            e.preventDefault();
        }, false);
    }


    function checkOrientation() {

        var width = $('body').width();
        
        if (width < 1000) {
            $('#container').css('height', '845px');
            if (columnName == 'featured') {
                $('#contents').addClass('withads');
                $('#ads').show();
            } else {
                $('#contents').removeClass('withads');
                $('#ads').hide();
            }
            $('#popup').removeClass('landscape');
        } else {
            $('#container').css('height', '590px');
            $('#contents').removeClass('withads');
            $('#popup').addClass('landscape');
            $('#ads').show();
        }

        if (columnName == "trending") {
            $('#contents').removeClass('withads');
            $('#ads').hide();
            
            $("#contents").addClass("withifr");
        }
        else {
            $("#contents").removeClass("withifr");
        }
    }

    function switchTabs(newColumnName) {

        
        if (columnTab[newColumnName] 
            && columnName != newColumnName) {

            columnTab[columnName].removeClass('active');
            columnWrap[columnName].hide();

            columnName = newColumnName;

            if (columnName == 'featured') {
                $('#promotions').show();
            } else {
                $('#promotions').hide();
            }

            lastOffset = 0;
            $('#scrollarea').css('-webkit-transition', 'none');
            $('#scrollarea').css('-webkit-transform', 'translate3d(0, 0, 0)');

            checkOrientation();
                
            columnTab[columnName].addClass('active');
            columnWrap[columnName].show();

            if (columnPage[columnName] == 1) {
                var url = getLoadingPath() + '&page=1';
                loadContent(url, columnName);
            }
        }
    }

    showDetails = function (element, type, appId, appName) {
        track(element, type, appName, appId);
        
        $('#details_wrap').show();

        var url = './details.html?os=' + platform + '&l=' + lang + '&id=' + appId;
        $.get(url, function (data) {
            if (data != '') {
                $('#details_content').html(data);
                initDetailsView();
            }
        });
    }

    hideDetails = function () {
        $('#details_wrap').hide();
        $('#details_content').html('');
    }

    function getLoadingPath() {

        var path = null;
        var parameter = '?os=' + platform + '&l=' + lang;

        switch (columnName) {
        case "featured": path = './featured.html'; break;
        case "trending": path = trendApi ? './trendapi' : './trend.html'; break;
        case "games": 
            path = './typeapps.html'; 
            parameter += '&type=game'; 
            break;
        case "applications": 
            path = './typeapps.html'; 
            parameter += '&type=app'; 
            break;
        }

        if (path == './trendapi'){
            parameter = '?type=' + platform.toLowerCase() + '&l=' + lang;
        }
        return path + parameter;
    }

    function initDetailsView() {
        $('.screenshots img.lazy').lazyload();
        $('.screenshots img.lazy').removeClass('lazy');

        var container = $('.scrollview');
        var scrollarea = $('.scroll');

        var start, end, offset, maxOffset, lastOffset = 0;
        var speed, lastTime, slowTime = null;
        var loadApps = false;

        container.bind('touchstart', function (e) {
            scrollWidth = 0;
            var slices = $('.screenshots .slice');
            slices.each(function(e) {
                scrollWidth += e.scrollWidth;
            });

            maxOffset = scrollWidth - container.width() - 20;
            if (maxOffset < 0) maxOffset = 0;

            speed = 0;
            offset = lastOffset;
            lastTime = e.timeStamp;
            end = start = e.touches[0].pageX;
            scrollarea.css('-webkit-transition', 'none');
        });

        container.bind('touchmove', function (e) {
            e.preventDefault();
            speed = (e.touches[0].pageX - end) / (e.timeStamp - lastTime);
            lastTime = e.timeStamp;
            end = e.touches[0].pageX;

            offset = lastOffset + end - start;

            if (offset > 0) {
                offset = offset / 2;
            } else if (offset < -maxOffset) {
                offset = (offset + maxOffset) / 2 - maxOffset;
            }

            scrollarea.css('-webkit-transform', 'translate3d(' + offset + 'px, 0, 0)');
        });

        container.bind('touchend', function (e) {
            if (offset > 0) {
                slowTime = 300;
                lastOffset = 0;
            } else if (offset < -maxOffset) {
                slowTime = 300;
                lastOffset = -maxOffset;
            } else {
                var accelerate = speed > 0 ? 0.0025 : -0.0025;
                slowTime = speed / accelerate;
                var distance = 0.5 * accelerate * slowTime * slowTime;
                var diffTime = 0;

                lastOffset = offset + distance;

                if (lastOffset > 0) {
                    diffTime = Math.sqrt(1.5 * lastOffset / accelerate);
                    lastOffset = 0;
                } else if (lastOffset < -maxOffset) {
                    diffTime = Math.sqrt(1.5 * (lastOffset  + maxOffset) / accelerate);
                    lastOffset =  - maxOffset ;
                }

                slowTime -= diffTime;
            }
            autoScroll(lastOffset, slowTime);
        });

        function autoScroll(offset, time) {
            scrollarea.css('-webkit-transition', '-webkit-transform ' + time/1000 + 's cubic-bezier(0.33, 0.66, 0.66, 1)');					
            scrollarea.css('-webkit-transform', 'translate3d(' + offset + 'px, 0, 0)');
        }
    }


    function initPromotionView() {

        var isTransitionCompleted = true;
        var scrollview = $('.showcontrol');

        var showLink = $('.front a');
        var frontImg = $('.front img');

        // bind scroll related event
        var offset, lastOffset = 0, endX, endY = null;
        var count = $('.showcontrol li').dom.length;
        var height = $('.showcontrol li').dom[0].clientHeight;

        scrollview.bind('swipeUp', function (e) {
            alert(startY);
            if (startY - endY < height / 2) {

                scroll(-height);

            }
        });

        scrollview.bind('swipeDown', function (e) {
            alert(startY);
            if (endY - startY < height / 2) {
                scroll(height);
            }
        });

        scrollview.bind('touchstart', function (e) {
            offset = lastOffset;
            height = $('.showcontrol li').dom[0].clientHeight;
            endY = startY = e.touches[0].pageY;
            scrollview.css('-webkit-transition', 'none');
        });

        scrollview.bind('touchmove', function (e) {
            e.preventDefault();
            e.stopPropagation();
            endY = e.touches[0].pageY;
            offset = lastOffset + endY - startY;
            scrollview.css('-webkit-transform', 'translate3d(0, ' + offset + 'px, 0)');
        });

        scrollview.bind('touchend', function (e) {
            
            lastOffset = offset;
            scroll(0);
        
        });

        function scroll(offset) {

            var maxPosition = $('.showcontrol li').dom.length - $('#promotions').height() / height;
            
            var position = Math.round((lastOffset + offset) / height);

            if (position > 0) position = 0;
            if (position < -maxPosition) position = -maxPosition; 

            lastOffset = position * height;

            scrollview.css('-webkit-transition', '-webkit-transform 0.3s cubic-bezier(0.33, 0.66, 0.66, 1)');					
            scrollview.css('-webkit-transform', 'translate3d(0, ' + lastOffset + 'px, 0)');

        }

        showNext = function (element) {

            var clickElement = $('img', element);

            if (showLink.attr('href') != clickElement.attr('data-href')
                && isTransitionCompleted)
            {
                isTransitionCompleted = false;

                showLink.attr('href', clickElement.attr('data-href'));
                showLink.attr('onclick', clickElement.attr('data-click'));
                frontImg.css('opacity', 0);

                var img = document.createElement('img');
                $(img).bind("load", function() {
                    frontImg.attr('src', clickElement.attr('data-src'));
                    frontImg.css('opacity', 1);
                    isTransitionCompleted = true;
                }).attr("src", clickElement.attr('data-src'));
            }
        }

        showNext(scrollview);
    }

    track = function (element, type, name, url) {

        var event = columnName + '_' + type;
        var value = url ? (name + ':' + url) : name;

        if (type == 'search') {
            // make the 'search' independent to each column
            _gaq.push(['_trackEvent', type, columnName, value]);
        } else {
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

        checkOrientation();

        // load the feature scrollview
        //var url = './topfeatured.html?os=' + platform + '&l=' + lang;
        //$.get(url, function (data) {
        //   if (data != '') {
        //      $('#promotions').html(data);
        initPromotionView();

        $('img.lazy').lazyload();
        $('img.lazy').removeClass('lazy');
        //  }
        //});

        url = './ads.html?os=' + platform + '&l=' + lang;
        $.get(url, function (data) {
            if (data != '') {
                $('#ads').html(data);
            }
        });

        var hash = window.location.hash;

        if (hash != '' && hash.slice(1) != columnName) {
            switchTabs(hash.slice(1));
        }

        // the first page has already included
        columnPage["featured"] ++;

        //else {
            // load the feature page first
        //    url = getLoadingPath() + '&page=' + columnPage[columnName];
        //    loadContent(url, columnName);
        //}
    });
})(Zepto);