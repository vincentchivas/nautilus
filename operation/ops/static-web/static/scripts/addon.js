var loadApps = null;
var vote = null;
var track = null;
var addslashes = null;
var shortNum = null;
var showpop = null;


(function ($) {
    var isAjaxCompleted = true;

    var columnName = '';
    var categoryId = '';
    var categoryTitle = null;

    var columnPage = [];
    var columnContent = [];
    var columnWrap = [];
    var columnTab = [];
    var appLoad = [];
    var pageLoad = null;

    var orientation = 0;
    var timeInt = null;

    var tabs = new Array("left", "middle", "right", "cateapps", "details", "search");

    // dolphin tracking
    var trackHost = 'http://track.dolphin-browser.com/track/site.gif?';

    // related apps
    var relatedUrl = './relevant.html?os=' + platform + '&l=' + lang + '&id=';

    // voting url
    var votingUrl = './lovecount?os=' + platform + '&l=' + lang + '&id=';

    // app details url
    var detailsUrl = './detail.html?os=' + platform + '&l=' + lang + '&id=';

    //search url
    var searchUrl = "./search?os=" + platform + "&l=" + lang + "&title=";
    var keyword = "";

    // screen shot
    var prev_image = null;
    var next_image = null;

    function initial() {

        for (i in tabs)
        {
            var tab = tabs[i];
            
            columnPage[tab] = 1;
            columnContent[tab] = $('#' + tab + '_content');
            columnWrap[tab] = $('#' + tab + '_wrap');
            columnTab[tab] = $('#' + tab + '_tab');
            appLoad[tab] = null;
        }

        pageLoad = $('#page_load');

        categoryTitle = $('#cateapps_title');
    }

    loadApps = function(columnName) {

        loading(columnName);

        var localData = null;
        var storageKey = product;
        var pageNum = columnPage[columnName];

        // only cache the first page
        if (pageNum == 1) {
            storageKey += (":" + columnName);

            if (columnName == "cateapps") {
                storageKey += (":" + categoryId);
            }

            localData = localStorage.getItem(storageKey);
        }

        var url = getLoadingPath() + '&page=' + pageNum;

        $.get(url, function (data) {

            // only cache the first page
            if (pageNum == 1) {
                if (data && data != localData) {
                    localData = null;
                    localStorage.setItem(storageKey, data);

                    // clear and reset the old content
                    columnContent[columnName].html('');
                    columnPage[columnName] = 1;
                    loadTemplate(data, columnName);
                }
            } else {
                loadTemplate(data, columnName);
            }
        });

        if (localData) {
            loadTemplate(localData, columnName);
        }
    }

    vote = function(element, name, id) {
        var span = $('span', element);
        var loveCount = parseInt(span.html());
        if (!isNaN(loveCount)) {
            span.html(loveCount + 1);
        }
        span.addClass('like');
        $.get(votingUrl + id);

        track(element, 'like', name , id);
    }

    function loadSearch(){
        if(keyword === ""){
            columnContent["search"].html('');
            return;
        }
        columnContent["search"].html('<div class="searching">Search...</div>');
        var url = searchUrl + keyword;
        $.get(url, function(data){
            columnContent["search"].html('');
            try{
                data = JSON.parse(data);
            }catch(e){
                data = [];
            }

            if(data.length === 0){
                columnContent["search"].html('<div class="no_result">sorry, no tags match</div>');
                return;
            }

            columnContent.search.append(tmpl('left_tmpl', data));
            $('img.lazy').lazyload();
            $('img.lazy').removeClass('lazy');
        });
    }

    function loading(columnName) {
        var pagination = $('.loading_more a', columnWrap[columnName]);
        var loading = $('.loading_more label', columnWrap[columnName]);
        var footer = $('.loading_more .footer', columnWrap[columnName]);

        pagination.hide();
        footer.hide();
        loading.show();
    }

    function loadTemplate(resData, columnName) {

        var pagination = $('.loading_more a', columnWrap[columnName]);
        var loading = $('.loading_more label', columnWrap[columnName]);
        var footer = $('.loading_more .footer', columnWrap[columnName]);

        var data = JSON.parse(resData);

        loading.hide();
        if ( !data || data.length < 24) {
            footer.show();
        } else {
            pagination.show();
        }

        if (data) {
            columnContent[columnName].append(tmpl(columnName + '_tmpl', data));

            columnPage[columnName]++;

            $('img.lazy').lazyload();
            $('img.lazy').removeClass('lazy');
            
            if (columnName == 'middle') {
                autoScroll();
            }
        }
    }

    function loadRelatedApps(appId) {

        var url = relatedUrl + appId;

        $.get(url, function (resData) {
            if (resData != '' || resData != '[]') {
                var data = JSON.parse(resData);
                $("#app_content").append(tmpl('related_tmpl', data));
                
                $('img.lazy').lazyload($.load);
                $('img.lazy').removeClass('lazy');
            }
        });
    }

    function registerDetailsEvents() {
        var wrapper = $('#details');

        $('.more_btn').bind('click', function () {
            var btn = $(this);
            if (btn.hasClass("more")) {
                wrapper.css('height', 'auto');
                btn.removeClass("more");
                btn.html(strings.LESS);
            } else {
                wrapper.css('height', '140px');
                btn.addClass("more");
                btn.html(strings.MORE);
            }
        });
    }
    
    function registerEvents() {
        // search dom
        var searchBar = $("#search_bar");
        var searchBtn = $("#search_btn");
        var clearInputBtn = $("span.clear_input_btn");
        var searchForm = $("#search_form");
        var searchBox = $("#search_form input");
        var searchWrap = $("#search_wrap");
        var content = $("div.content");

        window.addEventListener("resize", checkOrientation, false);
        window.addEventListener("orientationchange", checkOrientation, false);

        window.addEventListener('hashchange', function () {
            var hash = window.location.hash;
            var newColumnName = "left";
            searchBar.show();
            content.show();
            searchWrap.hide();

            if (hash != '') {
                if (hash.substr(0, 10) == "#cateapps:") {
                    searchBar.hide();
                    newColumnName = "cateapps";

                    categoryId = hash.slice(10);
                    categoryTitle.html(localStorage.getItem("cate:" + categoryId));

                    columnPage[newColumnName] = 1;
                    columnContent[newColumnName].html('');

                } else if (hash.substr(0, 9) == "#details:") {
                    // no paging or loading is required
                    // render the details page directly
                    searchBar.hide();
                    newColumnName = "details";
                    columnPage[newColumnName] = 0;

                    var appId = hash.slice(9);
                    var appContent = sessionStorage.getItem("addon:" + appId);
                    
                    if ( appContent ) {
                        loadAppDetails(appContent);
                    } else {
                        $.get(detailsUrl + appId, function (data) {
                            loadAppDetails(data);
                        });
                    }
                }else if(hash == "#search"){
                    newColumnName = "search";
                    content.hide();
                    searchWrap.show();
                    return;
                }else{
                    var name = hash.slice(1);
                    if (columnTab[name]) {
                        newColumnName = name;
                    }
                }
            }

            searchBox.dom[0].value = "";//clear the input when history back
            switchTabs(newColumnName);
        });

        searchBtn.bind("click", function(){
            location.hash = "search";
            setTimeout(function(){ //200ms is hashchange event handler
                keyword = searchBox.dom[0].value;
                loadSearch();
            }, 200);
        });

        searchForm.bind("submit", function(e){
            location.hash = "search";
            setTimeout(function(){ //200ms is hashchange event handler
                keyword = searchBox.dom[0].value;
                loadSearch();
            }, 200);
            e.preventDefault(); //this version of zepto does not support "return false"
            return false;
        });

        clearInputBtn.bind("click", function(){
            searchBox.dom[0].value = "";
        });
    }

    function loadAppDetails(appContent) {

        var appData = JSON.parse(appContent);

        if (appData) {
            columnContent["details"].html(tmpl('details_tmpl', appData));

            registerDetailsEvents();
            $('img.lazy').lazyload();
            $('img.lazy').removeClass('lazy');

            loadRelatedApps(appData.id);
        } else {
            window.location.hash = "";
        }
    }

    function checkOrientation() {
        if (orientation != window.orientation) {
            orientation = window.orientation;
            
            var body = $('body');
            if (orientation % 180 != 0) {
                body.addClass('horizontal');
            } else {
                body.removeClass('horizontal');
            }

            if ($("#pop_wrapper").dom[0].clientWidth > 0) {
                setTimeout(adjust_pop, 500);
            }
        }
    }

    function switchTabs(newColumnName) {

        if (columnTab[newColumnName]
            && columnName != newColumnName) {
            
            // columnName is '' in first loading
            if (columnName) {
                columnTab[columnName].removeClass('active');
                columnWrap[columnName].hide();
            }

            columnName = newColumnName;

            columnTab[columnName].addClass('active');
            columnWrap[columnName].show();

            if (columnPage[columnName] == 1) {
                loadApps(columnName);
            }
        }

        window.scrollTo(0, 1);


        // hide the pop image
        if ($("#pop_wrapper").dom[0].clientWidth > 0) {
            $('#pop_wrapper').hide();
        }
    }

    function getLoadingPath() {

        var path = null;

        switch (columnName) {
        case "left": path = './hoting.html'; break;
        case "middle": path = './feature.html'; break;
        case "right": path = './category.html'; break;
        case "cateapps": path = './cateapps.html'; break;
        }

        var parameter = '?os=' + platform + '&l=' + lang + '&format=json';

        if (columnName == 'cateapps') {
            parameter += ('&id=' + categoryId);
        }

        return path + parameter;
    }

    function autoScroll() {

        var counter = 1;
        var count = $('.slice').dom.length / 2;
        var container = $('.image_scrollbox');
        var scrollview = $('.image_scroll');
        var scrollbar = $('.image_scrollbar span');

        if (timeInt) {
            clearInterval(timeInt);
        }

        timeInt = setInterval(function () {

            if (columnName == 'middle') {

                var width = container.dom[0].clientWidth - 20;
                scrollview.css('-webkit-transition', '-webkit-transform .3s linear');
                scrollview.css('-webkit-transform', 'translate3d(' + -width + 'px, 0, 0)');
                
                setTimeout(function () {
                    var first = $('.slice').dom[0];
                    var second = $('.slice').dom[1];

                    // move the first element to the last
                    scrollview.append(first.outerHTML);
                    scrollview.append(second.outerHTML);

                    scrollview.dom[0].removeChild(first);
                    scrollview.dom[0].removeChild(second);

                    scrollview.css('-webkit-transition', 'none');
                    scrollview.css('-webkit-transform', 'translate3d(0, 0, 0)');

                    // adjust the scroll bar
                    scrollbar.removeClass('active');
                    scrollbar.dom[counter++].setAttribute('class', 'active');
                    
                    if (counter == count) {
                        counter = 0;
                    }

                }, 400);
            }
        }, 5000);
    }

    track = function (element, type, name, url) {

        var event = null;
        var value = url ? (name + ':' + url) : name;

        event = columnName + '_' + type;
        
        if (columnName == "cateapps") {
            event = categoryTitle.html() + '_' + type;
        }else if (columnName == "details") {
            event = name +'_'  + type;
        }

        _gaq.push(['_trackEvent', columnName, event, value]);

        // dolphin tracking
        var trackUrl = trackHost + 't=0&v=' + version + '&l=' + lang + '&p=' + product + '_' + platform
                            + '&w=' + element.offsetLeft + '&h=' + element.offsetTop
                            + '&col=' + columnName + '&item=' + event + '&src=' + encodeURIComponent(value);
        $.get(trackUrl);
    }

    addslashes = function ( str ) {  
        return (str+'').replace(/([\\"'])/g, "\\$1").replace(/\0/g, "\\0");  
    }

    shortNum = function ( number) {
        if (number >= 10000) {
            return ">" + Math.floor(number/1000) +"k";
        }
        return number;
    }

    showpop = function(current, len) {
        var wrapper = $('#pop_wrapper');
        wrapper.css('height', $('body').height()+'px');
        wrapper.show();

        var pop_image = $('#pop_wrapper img');
        var thumb_image = $('.screenshots img').dom[current];

        pop_image.attr('src', thumb_image.attributes['src'].value);
        adjust_pop();

        pop_image.attr('src', thumb_image.attributes['data-url'].value);

        if (current > 0) {
            $('.prev_button').show();
            prev_image = function() {
                showpop(current-1,len);
            }
        } else {
            $('.prev_button').hide();
        }
        
        if (current < len - 1) {
            $('.next_button').show();
            next_image = function() {
                showpop(current+1,len);
            }
        } else {
            $('.next_button').hide();
        }
    }

    function adjust_pop() {
        var content = $('.pop_content');
        var image = $('#pop_wrapper img');

        content.css('top', document.body.scrollTop + document.body.clientHeight/2);
        content.css('margin-top', '-' + image.height() / 2 +'px'); 
        content.css('margin-left', '-' + image.width() / 2 +'px');
    }

    function pop_init() {
        $('#pop_wrapper').bind('touchmove', function (e) {
            e.preventDefault();
        });

        $('#pop_wrapper img').bind('load', adjust_pop);

        $('.prev_button').bind('click', function() {
            if (prev_image) prev_image();
        });

        $('.next_button').bind('click', function() {
            if (next_image) next_image();
        });
    }

    $(document).ready(function () {

        initial();

        window.scrollTo(0, 1);

        registerEvents();

        pop_init();

        /* Force initial hash change for loading */
        var event = document.createEvent("Events");
        event.initEvent("hashchange", true, false);
        window.dispatchEvent(event);

    });
})(Zepto);
