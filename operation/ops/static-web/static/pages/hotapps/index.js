var pageControl = {
/******************************************tab*********************************/
		//一级导航
	homePiece: null,
	rankPiece: null,
	usePiece: null,
	useAppPiece: null,
	gamePiece: null,
	topicPiece: null,
	searchPiece: null,
		//首页和排行下的二级导航
	homeSubTab: null,
	rankSubTab: null,
		//详细页面的App detail和pic的切换
	tabIntro: null,
	tabPicCut: null,
	intro: null,
	picCut: null,
		//主界面和详细界面
	hotapp: null,
	detail: null,
		//保存进入applist的入口。
	entrance: null,   
	currentShowPage: null,
		//App list ul
	homeAppList: null,
	useAppList: null,
	rankAppList: null,
	searchAppList: null,
		//页面反馈和返回顶部
	footer: null,
/******************************************home pic flash*********************************/
	flashLinks: null,
	focusImg: null,
	startElem: 1,
	picTimeFn: null,
	picMoveD: 0,
	d_adjust: 0,
	startX: null,
	startY: null,
	curX: 0,
	detailCurX: 0,
	detailCurY: 0,
	detailStartX: 0,
	detailStartY: 0,
	detailA: 0,
	imglength: 0,
	picWarp: null,
	touchEffectX: 0,

	screenWidth: 0,
/*****************************************pagecontent**********************************/
	currentLoading: null,
	currentPage: null,
	addmore: null,

	clientid: 0,
	apiObj: {
			jsontype: '',
			clientid: 0,
			start_index: 0,
			count: 15,
			cate_id: 0,
			app_id: 0,
			order: 'downloads',
			keyword: '',
			subject_id: 0,
			fnName: '',
			type: 'bestmatch',
			area: 1
		},
/***************************************storage & track*************************************/
	storageKey: null,
	isModefied: false,
	currentSubCate: '最适合你',
	currentCate: '首页',
	forDetailTrack: true,
	rendered: {},
/***************************************app update info*************************************/
	appUpdate: null,
	appUpdatePage: false, //记录进入更新页的状态
	appUpdateAll: false, //记录是否点击"一键更新"按钮

	init: function() {
		this.focusImg = baina.$('focusImg');

		this.resizeFn();

		var target = this.lhash();//将分类列表页面和详细界面都指定为上一级或者首页
		var killcategory = target.indexOf('category');
		if(killcategory > 0){location.hash = target.substr(0, killcategory);}
		if(target == 'category'){location.hash = 'home';}

		this.updateInfoInit();

		this.picInit();

		this.pageTabInit();

		this.mainTabChange();
		this.pageContentInit();
	},
	updateInfoInit: function() {
		if (window.appupdateinfo) {
			if (window.appupdateinfo.getAppUpdateInfos) {
				var infos = window.appupdateinfo.getAppUpdateInfos();
				this.appUpdate = JSON.parse(infos);
			}
			if (window.appupdateinfo.refreshAppUpdateInfos) {
				window.appupdateinfo.refreshAppUpdateInfos("pageControl.updateCallback");
			}
		} else {
			baina.$('updateEntry').style['display'] = 'none';
		}
	},
	updateCallback: function(data) {
		this.appUpdate = data;
		this.updateNumInit();
		if (this.lhash() === 'update') {
			this.createUpdateList(this.appUpdate);
			this.updateEventInit();
		}
	},
	updateNumInit: function() {
		if (this.appUpdate) {
			var sum = this.appUpdate.apps.length;
			if (sum > 0) {
				baina.$('updateNum').innerText = sum;
				baina.$('updateNum').style['display'] = 'block';
			}
		}
	},
	updateAll: function() {
		if (!pageControl.appUpdateAll) {
			pageControl.appUpdateAll = true;

			var updateLinks = document.querySelectorAll('#updateList > li > a'),
				len = updateLinks.length,
				i = 0;
			pageControl.setTimeDelayed(updateLinks, i, len);
		} else {
			return ;
		}
	},
	// 递归调用：控制一键更新时每个应用的下载间隔
	setTimeDelayed: function(ele, i, len) {
		var that = this;

		if (i >= len) {return false;}
		var evt = document.createEvent('Event');
		evt.initEvent('click', true, true);
		ele[i].dispatchEvent(evt);

		i += 1;
		var interval = 1000;
		var id = setTimeout(function() {
			that.setTimeDelayed(ele, i, len);
		}, interval);
	},
	updateEventInit: function() {
		var updateLinks = document.querySelectorAll('#updateList > li > a'),
			len = updateLinks.length,
			i = 0;
		for (; i < len; i++) {
			baina.addEvent(updateLinks[i], 'click', function() {
				this.innerText = '下载中';
			});
		}
	},
	pageContentInit: function() {
		var that = this;
		baina.addEvent(this.addmore, 'click', function (e) {
			baina.$('addmoremsg').className = 'loading';
			that.apiObj.start_index += that.apiObj.count;
			if(that.currentPage == that.topicPiece){
				that.isModefied = true;
				that.apiObj.fnName = 'createTopic';
				that.getJSONP();
			} else if(that.currentPage != that.searchAppList){
				var curStorage = baina.getStorage(that.storageKey);
				var j = that.apiObj.start_index;
				if(curStorage && curStorage.length > j){
					var curData = [];
					var k = that.apiObj.count;
					k = (k < curStorage.length - j) ? k : (curStorage.length - j);
					for(var i = 0; i < k; i++){
						curData.push(curStorage[i+j]);
					}
					that.createAppList(curData);
				} else{
					that.isModefied = true;
					that.apiObj.fnName = 'createAppList';
					that.getJSONP();
				}				
			} else{
				that.apiObj.fnName = 'createSearchList';
				that.getJSONP();
			}

			var cat = 'loading_' + that.currentCate;
			_ba.track(cat,'loadmore','',1);
		});
		baina.addEvent(window, 'resize', function() {that.resizeFn();});
	},
	resizeFn: function() {
		this.screenWidth = baina.getScreenWidth();
		baina.$('header').style['background-size'] = this.screenWidth + 'px';
		baina.$('detailHead').style['background-size'] = this.screenWidth + 'px';
		baina.$('updateHead').style['background-size'] = this.screenWidth + 'px';
		baina.$('picWarp').style['width'] = this.screenWidth + 'px';
		baina.$('picAppshow').style['width'] = this.screenWidth + 'px';
		baina.$('detailHead').style['background-size'] = this.screenWidth + 'px';
		baina.$('picWarp').style['width'] = this.screenWidth + 'px';
		this.focusImg.style['-webkit-transform'] = 'translate3d(-' + this.picMoveD + 'px,0,0)';
		this.focusImg.style['-webkit-transition'] = '-webkit-transform .1s ease-out';
		if(this.startElem == 0){
			this.movePic(0);
			this.startElem++;
		}
	},
	pageTabInit: function() {		//tab页面切换初始化
		var that = this;
		this.homePiece = baina.$('homePiece');
		this.rankPiece = baina.$('rankPiece');
		this.usePiece = baina.$('usePiece');
		this.useAppPiece = baina.$('useAppPiece');
		this.gamePiece = baina.$('gamePiece');
		this.topicPiece = baina.$('topicPiece');
		this.searchPiece = baina.$('searchPiece');
		this.updatePiece = baina.$('updatePiece');
		this.tabIntro = baina.$('tabIntro');
		this.tabPicCut = baina.$('tabPicCut');
		this.intro = baina.$('intro');
		this.picCut = baina.$('picCut');
		this.hotapp = baina.$('hotapp');
		this.detail = baina.$('detail');
		this.homeAppList = baina.$('homeAppList');
		this.useAppList = baina.$('useAppList');
		this.rankAppList = baina.$('rankAppList');
		this.searchAppList = baina.$('searchAppList');
		this.homeSubTab = baina.$('homeSubTab');
		this.rankSubTab = baina.$('rankSubTab');
		this.topicPiece = baina.$('topicPiece');
		this.footer = baina.$('footer');
		this.addmore = baina.$('addmore');
		this.update = baina.$('update');
		
		baina.addEvent(window, 'hashchange', function() {that.mainTabChange();});

		this.currentShowPage = this.homePiece; // 初始化currentShowPage为home

		baina.addEvent(this.tabIntro, 'click', function (e) {
			if(that.intro && that.intro.style['display'] == 'none'){
				window._ba && _ba.track('detailpage', 'switch', 'screenshot', 1);	
			}
			that.intro2pic(false);
			e.preventDefault();
		});
		baina.addEvent(this.tabPicCut, 'click', function (e) {
			if(that.intro && that.intro.style['display'] == 'block'){
				window._ba && _ba.track('detailpage', 'switch', 'description', 1);
			}
			that.intro2pic(true);
			e.preventDefault();
		});
		baina.addEvent(baina.$('back2app'), 'click', function (e) {
			that.enterDetail(false);
			history.back();
			e.preventDefault();
		});
		baina.addEvent(baina.$('backToApp'), 'click', function (e) {
			history.back();
			this.appUpdatePage = false;
			e.preventDefault();
		});

		baina.addEvent(this.usePiece, 'click', function (e) {that.entrance = that.usePiece;that.enterClass(e);});
		baina.addEvent(this.gamePiece, 'click', function (e) {that.entrance = that.gamePiece;that.enterClass(e);});
		baina.addEvent(this.topicPiece, 'click', function (e) {that.entrance = that.topicPiece;that.enterClass(e);});
		baina.addEvent(baina.$('back2tab'), 'click', function (e) {
			that.apiObj.start_index = 0;
			that.apiObj.count = 15;
			that.entrance.style['display'] = 'block';
			if(that.entrance != that.topicPiece){
				that.addmore.style['display'] = 'none';
				that.footer.style['display'] = 'none';
			}
			that.useAppPiece.style['display'] = 'none';
			history.back();
			e.preventDefault();
		});

		baina.addEvent(baina.$('back2home'), 'click', function (e) {
			that.enterDetail(false);
			that.currentShowPage.style['display'] = 'none';
			that.homePiece.style['display'] = 'block';
			that.currentShowPage = that.homePiece;
			that.useAppPiece.style['display'] = 'none';
			location.hash = 'home';
		});
		baina.addEvent(baina.$('recoApp'), 'click', function (e) {that.changeDetailPage(e);});
		baina.addEvent(baina.$('appTitle'), 'click', function (e) {that.detailDownloadTrack(e);});
		baina.addEvent(baina.$('add4New'), 'click', function (e) {
			window._ba && _ba.track('recommendation', 'switch', '', 1);
			that.change4New();
			e.preventDefault();
		});
		
		baina.addEvent(baina.$('backFromSearch'), 'click', function (e) {
			document.getElementsByClassName('searchForm')[0].className = '';
			baina.$('search').value = '';
			baina.$('mainTab').style.display = 'block';
			
			that.searchPiece.style['display'] = 'none';
			location.hash = 'home';
			e.preventDefault();
		});
		baina.addEvent(baina.$('back2top'), 'click', function (e) {
			window._ba && _ba.track('gototop','click','',1);
			window.scroll(0, -1);
			e.preventDefault();
		});
		baina.addEvent(baina.$('feedback'), 'click',function() {window._ba && _ba.track('feedback','click','',1);});

		
		var appLists = document.getElementsByClassName('appList');
		for(var i = appLists.length;i--;){
			baina.addEvent(appLists[i], 'click', function (e) {that.getDetailPage(e);});
			baina.addEvent(appLists[i], 'click', function (e) {that.listDownloadTrack(e);});
			// baina.addEvent(appLists[i], 'touchstart', function (e) {that.touchEffectStart(e, 'LI');});
			// baina.addEvent(appLists[i], 'touchmove', function (e) {that.touchEffectMove(e);});
			// baina.addEvent(appLists[i], 'touchend', function (e) {that.touchEffectEnd(e, 'LI');});
		}
		
		baina.addEvent(baina.$('search'), 'focus', function() {if(that.currentPage != that.searchPiece){location.hash = 'search';}});
		baina.addEvent(baina.$('search'), 'click', function() {location.hash = 'search';});
		baina.addEvent(baina.$('word'), 'click', function (e) {that.getKeyword(e);e.preventDefault();});
		baina.addEvent(baina.$('newWord'), 'click', function() {that.getSearchPiece();});
		baina.addEvent(baina.$('submit'), 'click', function() {that.getuserInput();});
		baina.addEvent(baina.$('updateEntry'), 'click', function () {location.hash = 'update';});

		//点击效果
		var effects = document.querySelectorAll('.backFromSearch,#submit,#back2app,#back2home,#tabIntro,#tabPicCut,#add4New,#feedback,#back2top,#addmore a,#newWord,#back2tab');
		for(var i = effects.length;i--;){
			baina.addEvent(effects[i], 'touchstart', function (e) {that.touchEffectStart(e, 'A');});
			// baina.addEvent(effects[i], 'touchmove', function (e) {that.touchEffectMove(e, 'A');});
			baina.addEvent(effects[i], 'touchend', function (e) {that.touchEffectEnd(e, 'A');});
		}

		//一键更新
		baina.addEvent(baina.$('updateAll'), 'click', that.updateAll);
	},
	picInit: function() {		//图片切换动画初始化
		var that = this;

		this.picCut = baina.$('picCut');
		this.flashLinks = baina.$('flashchange').getElementsByTagName('span');

		baina.addEvent(this.focusImg, 'touchstart', function (e) {that.touchImgStart(e);});
		baina.addEvent(this.focusImg, 'touchmove', function (e) {that.touchImgMove(e);});
		baina.addEvent(this.focusImg, 'touchend', function (e) {that.touchImgEnd(e);});
		baina.addEvent(this.focusImg, 'click', function (e) {that.getFocusImageDetail(e);});

		baina.addEvent(this.picCut, 'touchstart', function (e) {that.touchPicStart(e);});
		baina.addEvent(this.picCut, 'touchmove', function (e) {that.touchPicMove(e);});
		baina.addEvent(this.picCut, 'touchend', function (e) {that.touchPicEnd(e);});

		this.picTimeFn = setTimeout(function() {that.launchPic(pageControl.startElem);}, 3000);
	},
//JSONP处理跨域问题,修改apiObj，拼接API地址和参数，传入回调函数处理数据。
	getJSONP: function () {
		var url = 'http://estoresrvice7.189store.com/api/';
		//必传部分
		url += this.apiObj.jsontype;
		url += '?clientid=' + this.apiObj.clientid;
		url += '&start_index=' + this.apiObj.start_index;
		url += '&count=' + this.apiObj.count;
		url += '&p_cate_id=' + this.apiObj.p_cate_id;
		if (this.apiObj.cate_id) { url += '&cate_id=' + this.apiObj.cate_id; }
		url += '&order=' + this.apiObj.order;
		url += '&app_id=' + this.apiObj.app_id;
		url += '&type=' + this.apiObj.type;
		url += '&q=' + this.apiObj.keyword;
		url += '&subject_id=' + this.apiObj.subject_id;
		url += '&area=' + this.apiObj.area;
		url += '&callback=pageControl.' + this.apiObj.fnName;

		var jsonID = baina.$('jsonID');
		jsonID && jsonID.parentNode.removeChild(jsonID);
		
		var script = document.createElement("script");
		script.src = url;
		script.id = 'jsonID';
		document.body.appendChild(script);
	},
//根据API生成页面内容,无app信息的时候还是需要显示推荐的App。
	createAppDetail: function (data) {
		if(data.name == undefined){
			this.change4New();
			baina.$('appDetail').style['display'] = 'none';
			return ;
		}

		var date = new Date(data.update_date * 1000);
		var update_date = date.getFullYear() + '年' + (date.getMonth() + 1) + '月' + date.getDate() + '日';  
		var download_url = 'http://estoresrvice7.189store.com/api/app/download/app.json?clientid=' + this.clientid + '&app_id=' + data.id;
		var trackMsg = data.name + '|' + data.id;
		var ihtml = '';
		
		ihtml += '<div class="icon"><img src="' + data.icon_url + '"/><div class="smallLoveLevel">';
		for(var j = 0, m = data.rate;j < m; j++){
			ihtml += '<span></span>';
		}
		for(;j < 5; j++){
			ihtml += '<span class="hatestar"></span>';
		}
		ihtml += '</div></div><div class="about"><h2>' + data.name + '</h2>';
		ihtml += '<p>版本 :<span  id="version">' + data.version + '</span>大小 :<span id="size">' + data.size + '</span></p>';
		ihtml += '<p>上传时间 :<span  id="uploadDate">' + update_date + '</span></p>';
		ihtml += '<p>下载次数 :<span id="downs">' + data.download_count + '次</span></p></div>';
		ihtml += '<a href="' + download_url + '" class="downLink" trackmsg="' + trackMsg + '">免费下载</a>';
		baina.$('appTitle').innerHTML = ihtml;

		baina.$('intro').innerText = data.description;
		var picurls = data.small_preview_icon_urls.split(',');
		var pichtml = '';
		for(i = 0, k = picurls.length; i < k; i++){
			pichtml += '<img src="' + picurls[i] + '" />';
		}
		baina.$('picCut').innerHTML = pichtml;
		this.picCut.style['-webkit-transform'] = 'translate3d(0,0,0)';
		this.intro2pic(false);
		baina.$('detailLoad').style['display'] = 'none';
		baina.$('appTitle').style['display'] = 'block';
		baina.$('appDetail').style['display'] = 'block';
		var label = 'app ' + data.name + '|' + data.id;
		if(this.forDetailTrack){
			window._ba && _ba.track('detailpage', 'loading', label, 1);
			this.apiObj.start_index = Math.floor(Math.random()*80)-4;
		} else{
			window._ba && _ba.track('recommendation', 'loading', label, 1);
		}
		this.change4New();
	},
	createFocusImage: function (data) {
		if(this.isModefied){
			var ihtml = '';
			for(var i = 0, k = data.length; i < k; i++){
				if(data[i].type == 3){
					ihtml += '<a id="' + data[i].attr + '" title="' + data[i].type + '_homePic"><img src="' + data[i].icon_url + '" alt="" /></a>';				
				} else if(data[i].type == 4){
					ihtml += '<a id="subject_' + data[i].attr + '" title="'+ data[i].type +'_精彩推荐"><img src="' + data[i].icon_url + '" alt="" /></a>';
				} else if(data[i].type == 5){
					ihtml += '<div class="pic_' + (i+1) + '" title="'+ data[i].type +'_精彩推荐"><a href="'+ data[i].attr +'"><img src="' + data[i].icon_url + '" alt="" /></a></div>';
				} else{
					ihtml += '<div class="pic_' + (i+1) + '" title="'+ data[i].type +'_精彩推荐"><a href="'+ data[i].attr +'"><img src="' + data[i].icon_url + '" alt="" /></a></div>';
				}
			}
			k -= 1;
			var spans = '<span class="active"></span>';
			for(;k--;){
				spans += '<span></span>'
			}
			this.clearAllNode(this.focusImg);
			this.clearAllNode(baina.$('flashchange'));
			this.focusImg.innerHTML = ihtml;
			baina.$('flashchange').innerHTML = spans;
			baina.setStorage('focusImage',data);
			this.rendered['focusImage'] = true;
			this.isModefied = false;
		}
		var storageData = baina.getStorage(this.storageKey);
		this.clearAllNode(this.currentPage);
		this.currentPage.style['display'] = 'none';
		this.currentLoading.style['display'] = 'block';
		this.apiObj.jsontype = 'app/recommends.json';
		this.apiObj.cate_id = 0;
		this.apiObj.fnName = 'createAppList';
		if(storageData){
			this.createAppList(storageData);
		} else{
			this.isModefied = true;
			this.getJSONP();
		}
	},
	createAppList: function (data) {
		if(!data){return ;}
		var fragment = document.createDocumentFragment();
		var i = 0,
			k = data.length > 15 ? 15 : data.length;
		for (; i < k; i++) {
			var ihtml = "";
			var li = document.createElement('li');
			var trackMsg = data[i].name + '|' + data[i].id;
			var download_url = 'http://estoresrvice7.189store.com/api/app/download/app.json?clientid=' + this.clientid + '&app_id=' + data[i].id;

			ihtml += '<div class="apptitle">';
			ihtml += '<img datasrc="' + data[i].icon_url + '"  src="./image/icon.png" onerror="baina.ErrorImg(this)" />';
			ihtml +='<span class="title">'+data[i].name+'</span><div class="lovelevel">'
			for(var j = 0, m = data[i].rate;j < m; j++){
				ihtml += '<span></span>';
			}
			for(;j < 5; j++){
				ihtml += '<span class="hatestar"></span>';
			}
			ihtml += '</div></div><p class="size">' + data[i].size + '</p>';
			if(data[i].display_download_count){
				ihtml += '<p class="downs">' + data[i].display_download_count + '</p>';
			}
			ihtml += '<a href="' + download_url + '" class="downLink" trackmsg="' + trackMsg + '">免费下载</a>';
			li.innerHTML = ihtml;
			li.id = data[i].id;
			fragment.appendChild(li);
		}
		this.currentPage.appendChild(fragment);
		this.currentLoading.style['display'] = 'none';
		this.currentPage.style['display'] = 'block';
		var that = this;
		setTimeout(function() {
			that.getAppIcon();
		}, 200);
		baina.$('addmoremsg').className = '';
		if(data.length < this.apiObj.count){
			baina.$('addmore').style['display'] = 'none';
		}else{
			baina.$('addmoremsg').className = '';
		}

		if(this.isModefied){
			baina.setStorage(this.storageKey,data);
			this.isModefied = false;
		}
	},
	createUpdateList: function (data) {
		if (!data) {return ;}
		baina.$('updateList').innerHTML = '';

		var fragment = document.createDocumentFragment(),
			apps = data.apps,
			len = apps.length;
		for (var i = 0; i < len; i++) {
			var ihtml = '',
				li = document.createElement('li'),
				trackMsg = apps[i].name + '|' + apps[i].id,
				download_url = 'http://estoresrvice7.189store.com/api/app/download/app.json?clientid=' + this.clientid + '&app_id=' + apps[i].id;

			ihtml += '<div class="apptitle">';
			ihtml += '<img datasrc="' + apps[i].icon_url + '"  src="./image/icon.png" onerror="baina.ErrorImg(this)" />';
			ihtml += '<span class="name">'+apps[i].name+'</span>';
			ihtml += '<span>' + apps[i].local_version + '更新到' + apps[i].version + '</span>';
			ihtml += '<span>' + apps[i].size +'</span></div>';
			ihtml += '<a href="' + download_url + '" class="downLink" trackmsg="' + trackMsg + '">更新</a>';

			li.innerHTML = ihtml;
			li.id = apps[i].id;
			fragment.appendChild(li);
		}
		baina.$('updateList').appendChild(fragment);

		this.currentLoading.style['display'] = 'none';
		this.currentPage.style['display'] = 'block';
		var that = this;
		setTimeout(function() {
			that.getAppIcon();
		}, 200);
	},
	createSearchList: function (data) {
		if(!data){return ;}
		this.footer.style['display'] = 'block';
		data = data.items;
		var newData = [];
		for (var i = 0, k = data.length; i < k; i++) {
			var datamag = JSON.parse(data[i].caption);
			newData.push(datamag);
		}
		this.storageKey = 'searchList';
		this.createAppList(newData);
	},
	createCategory: function (data) {
		var ihtml = '';
		if(!data){return ;}
		if(this.isModefied){
			for (var i = 0, k = data.length; i < k; i++) {
				ihtml += '<a id="category_' + data[i].id + '" title="' + data[i].name + '"><img datasrc="' + data[i].icon_url + '" src="./image/icon.png" /><span>' + data[i].name + '</span></a>';
			}
			this.currentPage.innerHTML = ihtml;
			var that = this;
			setTimeout(function() {
				that.getAppIcon();
			}, 200);
			baina.setStorage(this.storageKey,[true]);
			this.rendered[this.storageKey] = true;
			this.isModefied = false;
		}
	},
	createTopic: function (data) {
		if(!data){return ;}
		if(this.isModefied){
			var fragment = document.createDocumentFragment();
			for (var i = 0, k = data.length; i < k; i++) {
				var ihtml = '';
				var temp_a = document.createElement('a');
				ihtml += '<div><img datasrc="' + data[i].icon_url + '" src="./image/icon.png" /></div>';
				ihtml += '<span class="topicName">' + data[i].name + '</span>';
				ihtml += '<p>' + data[i].description + '</p><i></i>';
				temp_a.id = 'subject_'+ data[i].id;
				temp_a.title = data[i].name;
				temp_a.innerHTML = ihtml;
				fragment.appendChild(temp_a);
			}
			baina.$('topicPiece').appendChild(fragment);
			var that = this;
			setTimeout(function() {
				that.getAppIcon();
			}, 200);

			baina.$('addmoremsg').className = '';
			if(data.length < this.apiObj.count){
				baina.$('addmore').style['display'] = 'none';
			}else{
				baina.$('addmoremsg').className = '';
			}
			baina.setStorage(this.storageKey,data);
			this.rendered[this.storageKey] = true;
			this.isModefied = false;
		}		
	},
	createRecommendWord: function (data) {
		var ihtml = '';
		if(!data){return ;}
		for (var i = 0, k = data.length; i < k; i++) {
			ihtml += '<a id="' + data[i].id + '">' + data[i].keyword + '</a>';
		}
		baina.$('word').innerHTML = ihtml;
		baina.$('word').style['display'] = 'block';
		this.currentLoading.style['display'] = 'none';
	},
	appAdd4New: function (data) {
		if(data.length < 4){
			this.apiObj.start_index = -4;
			this.change4New();
			return ;
		}
		var ihtml = '';
		for (var i = 0, k = data.length; i < k; i++) {
			ihtml += '<a id="' + data[i].id + '"><img datasrc="' + data[i].icon_url + '" src="./image/icon.png" /><span>' + data[i].name + '</span></a>';
		}
		baina.$('recoApp').innerHTML = ihtml;			
		var that = this;
		setTimeout(function() {
			that.getAppIcon(baina.$('recoApp'));
		}, 200);
	},
	//页面控制部分，主要使用了display属性
	mainTabChange: function() {
		var target = this.lhash();
		//做了修改，允许直接访问
		if(target.match(/^detail\d*/g)){
			var app_id = target.slice(6);
			if (app_id){
				this.enterDetail(true);
				baina.$('detailLoad').style['display'] = 'block';
				baina.$('appTitle').style['display'] = 'none';
				baina.$('appDetail').style['display'] = 'none';
				this.apiObj.jsontype = 'app/info.json';
				this.apiObj.app_id = app_id;
				this.apiObj.fnName = 'createAppDetail';
				this.getJSONP();
				this.forDetailTrack = true;
			}
			return;
		}
		if(target.indexOf('category') > 0){
			this.enterDetail(false);
			return ;
		}
		baina.$('searchForm').className = '';
		baina.$('mainTab').style['display'] = 'block';
		this.useAppPiece.style['display'] = 'none';
		this.currentShowPage.style['display'] = 'none';
		this.footer.style['display'] = 'block';
		this.addmore.style['display'] = 'block';
		this.update.style['display'] = 'none';
		this.hotapp.style['display'] = 'block';
		if (window.appupdateinfo) { 
			baina.$('updateEntry').style.display = 'block'; //默认显示更新按钮
		}
		baina.$('backFromSearch').style['display'] = 'none'; //默认隐藏search页回到首页的按钮
		this.enterDetail(false);
		if(target == '' || target == 'home' || target == 'new' || target == 'hot'){
			var switchNum = 'home';
		} else if(target == 'rank' || target == 'userrank' || target == 'gamerank' || target == 'videorank'){
			var switchNum = 'rank';
		} else{
			var	switchNum = target;
		}
		if(switchNum == 'home' || switchNum == 'rank' || switchNum == 'app' || switchNum == 'game' || switchNum == 'topic'){
			baina.$('mainTab').getElementsByClassName('active')[0].className = '';
			baina.$(switchNum+'Tab').className = 'active';
		}
		switch(switchNum){
							//首页，排行，搜索由于分别公用一个div显示，需要重复使用，所以需要重新加载本地缓存
			case 'home':   	this.currentCate = '首页';
							this.subTabChange(target, true);
							this.currentPage = this.homeAppList;
							this.currentShowPage = this.homePiece;
							break;
			case 'rank': 	this.currentCate = '排行';
							this.subTabChange(target, false);
							this.currentPage = this.rankAppList;
							this.currentShowPage = this.rankPiece;
							break;
							//应用，游戏，专题由于是单独的div，不需要重复使用，在第一次加载后，后面就直接切换就可以了。
			case 'app': 	this.currentCate = '应用';
							this.currentPage = this.usePiece;
							this.storageKey = 'appCategories';
							var storageData = baina.getStorage(this.storageKey);
							var cateID = this.currentPage.title;
							this.apiObj.jsontype = 'app/categories.json';
							this.apiObj.p_cate_id = cateID;
							this.apiObj.fnName = 'createCategory';
							if(!this.rendered[this.storageKey]){
								this.isModefied = true;
								this.getJSONP();
							}
							this.footer.style['display'] = 'none';
							this.addmore.style['display'] = 'none';
							this.currentShowPage = this.usePiece;
							break;
			case 'game': 	this.currentCate = '游戏';
							this.currentPage = this.gamePiece;
							this.storageKey = 'gameCategories';
							var storageData = baina.getStorage(this.storageKey);
							var cateID = this.currentPage.title;
							this.apiObj.jsontype = 'app/categories.json';
							this.apiObj.p_cate_id = cateID;
							this.apiObj.fnName = 'createCategory';
							if(!this.rendered[this.storageKey]){
								this.isModefied = true;
								this.getJSONP();
							}
							this.footer.style['display'] = 'none';
							this.addmore.style['display'] = 'none';
							this.currentShowPage = this.gamePiece;
							break;
			case 'topic': 	this.currentCate = '专题';
							this.currentPage = this.topicPiece;
							this.storageKey = 'topicCategories';
							var storageData = baina.getStorage(this.storageKey);
							this.apiObj.jsontype = 'app/subjects.json';
							this.apiObj.fnName = 'createTopic';
							if(!this.rendered[this.storageKey]){
								this.isModefied = true;
								this.getJSONP();
							}
							this.currentShowPage = this.topicPiece;
							break;
			case 'search':  this.currentCate = '搜索';
							this.currentPage = this.searchPiece;
							this.searchAppList.style['display'] = 'none';
							this.addmore.style['display'] = 'none';
							this.footer.style['display'] = 'none';
							baina.$('backFromSearch').style['display'] = 'block';
							baina.$('updateEntry').style['display'] = 'none';
							baina.$('search').value = '';
							baina.$('word').style['display'] = 'block';
							baina.$('newWord').style['display'] = 'block';
							this.apiObj.start_index = Math.floor(Math.random()*80) - 12;
							this.getSearchPiece();
							baina.$('mainTab').style.display = 'none';
							baina.$('searchForm').className = 'searchForm';
							this.currentShowPage = this.searchPiece;
							window._ba && _ba.track('search','loading','',1);
							break;
			case 'update':  this.currentCate = '更新';
							this.currentPage = this.updatePiece;
							this.currentLoading = baina.$('updateLoad');
							//显示逻辑
							this.hotapp.style['display'] = 'none';
							window.scroll(0, -1);
							this.currentPage.style['display'] = 'none';
							this.update.style['display'] = 'block';
							this.appUpdatePage = true;
							//数据加载
							this.createUpdateList(this.appUpdate);
							this.updateEventInit();
							break;
		}
		this.currentShowPage.style['display'] = 'block';
	},
	//首页 & 排行
	getFocusImageDetail: function (e) {
		var targetLink = this.getTarget(e, "A");
		var type = parseInt(targetLink.title)
		if(type == '3'){
			baina.$('detailLoad').style['display'] = 'block';
			baina.$('appTitle').style['display'] = 'none';
			baina.$('appDetail').style['display'] = 'none';
			var appID = targetLink.id;
			this.apiObj.jsontype = 'app/info.json';
			this.apiObj.app_id = appID;
			this.apiObj.fnName = 'createAppDetail';
			this.getJSONP();
			this.forDetailTrack = false;
			this.enterDetail(true);
			var label = 'type:' + type + '-' + appID;
			location.hash = 'detail';
			e.preventDefault();
		} else if(type == '4'){
			var pieceName = baina.$('pieceName');
			this.entrance = this.homePiece;
			this.currentPage = this.useAppList;
			var msg = targetLink.id;
			var msgs = msg.split('_');
			var type = 'app/' + msgs[0] + '/apps.json';
			this.clearAllNode(this.currentPage);
			this.apiObj.jsontype = type;
			this.apiObj.cate_id = msgs[1];
			this.apiObj.subject_id = msgs[1];
			this.apiObj.order = 'downloads';
			this.apiObj.fnName = 'createAppList';
			this.getJSONP();

			var appClassName = targetLink.title.split('_')[1];
			pieceName.innerText = appClassName;
			this.entrance.style['display'] = 'none';
			this.footer.style['display'] = 'block';
			this.useAppPiece.style['display'] = 'block';
			if(location.hash.indexOf('category') < 0){
				location.hash += 'category';				
			}
			var label = 'type:' + type + '-' + msgs[1];
			e.preventDefault();
		}
		this.currentSubCate = '轮转图';
		var cat = 'loading_' + this.currentCate;
		var action = 'loading_' + this.currentSubCate;
		window._ba && _ba.track(cat, action, label, 1);

	},
	subTabChange: function (subType, ishomeSubTab) {
		this.apiObj.start_index = 0;

		if(ishomeSubTab){
			this.currentPage = this.homeAppList;
			this.currentLoading = baina.$('homeLoading');
			if(subType == 'new'){
				var tab = 1;
				this.storageKey = 'newest';
				this.currentSubCate = '最新上架';
			} else if(subType == 'hot'){
				var tab = 2;
				this.storageKey = 'hotest';
				this.currentSubCate = '热门排行';
			} else{
				var tab = 0;
				this.storageKey = 'bestmatch';
				this.currentSubCate = '最适合你';
			}
			this.apiObj.type = this.storageKey;
			var storageData = baina.getStorage('focusImage');
			this.apiObj.jsontype = 'app/category/focus-images.json';
			this.apiObj.cate_id = 14334;
			this.apiObj.fnName = 'createFocusImage';
			if(this.rendered['focusImage']){
				this.createFocusImage(storageData);
			} else{
				this.isModefied = true;
				this.getJSONP();
			}
			this.homeSubTab.getElementsByClassName('active')[0].className = '';
			this.homeSubTab.getElementsByTagName('a')[tab].className = 'active';
		} else{
			this.currentPage = this.rankAppList;
			this.currentLoading = baina.$('rankLoading');
  			if(subType == 'gamerank'){
				var cateID = 14357;
				var tab = 1;
				this.currentSubCate = '游戏排行';
				this.storageKey = 'gamerank';
			} else if(subType == 'videorank'){
				var cateID = 14377;
				var tab = 2;
				this.currentSubCate = '阅读影音';
				this.storageKey = 'videorank';
			} else{
				var cateID = 14334;
				var tab = 0;
				this.currentSubCate = '应用排行';
				this.storageKey = 'apprank';
			}
			var storageData = baina.getStorage(this.storageKey);
			this.clearAllNode(this.currentPage);
			this.currentPage.style['display'] = 'none';
			this.currentLoading.style['display'] = 'block';
			this.apiObj.jsontype = 'app/category/tops.json';
			this.apiObj.cate_id = cateID;
			this.apiObj.fnName = 'createAppList';
			if(storageData){
				this.createAppList(storageData);
			} else{
				this.isModefied = true;
				this.getJSONP();
			}
			this.rankSubTab.getElementsByClassName('active')[0].className = '';
			this.rankSubTab.getElementsByTagName('a')[tab].className = 'active';
		}
		var action = 'tabswitch_' + this.currentCate;
		var label = 'tabswitch_' + this.currentSubCate;
		window._ba && _ba.track('tabswitch', action, label, 1);
	},
	//应用、游戏、专题
	enterClass: function (e) {
		var target = this.getTarget(e, "A");
		var pieceName = baina.$('pieceName');
		
		if(target){
			location.hash += 'category';
			this.currentPage = this.useAppList;
			this.clearAllNode(this.currentPage);
			this.currentLoading = baina.$('useLoading');
			var msg = target.id;
			var msgs = msg.split('_');
			var type = 'app/' + msgs[0] + '/apps.json';
			var appClassName = target.title;
			this.storageKey = appClassName;
			var storageData = baina.getStorage(this.storageKey);

			this.currentPage.style['display'] = 'none';
			this.currentLoading.style['display'] = 'block';
			this.apiObj.start_index = 0;
			this.apiObj.jsontype = type;
			this.apiObj.cate_id = msgs[1];
			this.apiObj.subject_id = msgs[1];
			this.apiObj.order = 'downloads';
			this.apiObj.fnName = 'createAppList';
			if(storageData){
				this.createAppList(storageData);
			} else{
				this.isModefied = true;
				this.getJSONP();
			}

			pieceName.innerText = appClassName;
			this.currentSubCate = appClassName;
			this.entrance.style['display'] = 'none';
			this.footer.style['display'] = 'block';
			this.addmore.style['display'] = 'block';
			this.useAppPiece.style['display'] = 'block';
			var action = 'tabswitch_' + this.currentCate;
			var label = 'tabswitch_' + this.currentSubCate;
			window._ba && _ba.track('tabswitch', action, label, 1);
		}
	},
	//详细界面
	enterDetail: function (isDetail) {
		if(isDetail){
			this.hotapp.style['display'] = 'none';
			this.update.style['display'] = 'none';
			window.scroll(0, -1);
			this.detail.style['display'] = 'block';
		} else {
			this.apiObj.start_index = 0;
			this.apiObj.count = 15;
			this.detail.style['display'] = 'none';
			if (!this.appUpdatePage) {
				this.hotapp.style['display'] = 'block';
			}
		}
	},
	getDetailPage: function (e) {
		var e = e || window.event;
		var target = e.srcElement || e.target;
		if(target.tagName.toUpperCase() == "A"){
			return ;
		}
		location.hash = 'detail';
		target = this.getTarget(e, "LI");
		if(target){
			this.enterDetail(true);
			baina.$('detailLoad').style['display'] = 'block';
			baina.$('appTitle').style['display'] = 'none';
			baina.$('appDetail').style['display'] = 'none';
			var cat = 'loading_' + this.currentCate;
			var action = 'loading_' + this.currentSubCate;
			window._ba && _ba.track(cat, action, target.getElementsByTagName('a')[0].getAttribute('trackmsg'), 1);
			var appID = target.id;
			this.apiObj.jsontype = 'app/info.json';
			this.apiObj.app_id = appID;
			this.apiObj.fnName = 'createAppDetail';
			this.getJSONP();
			this.forDetailTrack = true;
		}
	},
	getAppIcon: function (currentPage) {
		currentPage = currentPage || this.currentPage;
		var imgs = currentPage.getElementsByTagName('img');
		for(var i = 0, k = imgs.length; i < k; i++){
			var image = new Image();
			image.onload = (function (k) {
								imgs[k].src = imgs[k].getAttribute('datasrc');
							})(i);
			image.src = imgs[i].getAttribute('datasrc');
		}
	},
	intro2pic: function (isPic) {
		if(isPic){
			this.intro.style['display'] = 'none';
			this.tabIntro.className = 'notactive';
			this.picCut.style['display'] = '-webkit-box';
			this.tabPicCut.className = '';
		} else {
			this.intro.style['display'] = 'block';
			this.tabIntro.className = '';
			this.picCut.style['display'] = 'none';
			this.tabPicCut.className = 'notactive';
		}
	},
	change4New: function(){
		this.apiObj.jsontype = 'app/recommends.json';
		this.apiObj.cate_id = 0;
		this.apiObj.start_index += 4;
		this.apiObj.count = 4;
		this.apiObj.type = 'hotest';
		this.apiObj.fnName = 'appAdd4New';
		this.getJSONP();
	},
	changeDetailPage: function (e) {
		var target = this.getTarget(e, "A");
		if(target){
			this.enterDetail(true);			
			baina.$('detailLoad').style['display'] = 'block';
			baina.$('appTitle').style['display'] = 'none';
			baina.$('appDetail').style['display'] = 'none';
			this.apiObj.jsontype = 'app/info.json';
			this.apiObj.app_id = target.id;
			this.apiObj.fnName = 'createAppDetail';
			this.getJSONP();
			this.forDetailTrack = false;
		}
	},
	//搜索页面
	getKeyword: function (e) {
		var e = e || window.event;
		var target = e.srcElement || e.target;
		if(target.tagName.toUpperCase() == "A"){
			var keyword = 'word '+ target.innerText;
			baina.$('search').value = target.innerText;
			window._ba && _ba.track('search', 'recommendation', keyword, 1);
			location.hash += 'category';
			this.startSearch(target.innerText);
		}
	},
	getuserInput: function() {
		if(this.currentPage != this.searchPiece){
			location.hash = 'search';
			return;
		}
		var keyword = baina.$('search').value;
		if (keyword == '') {return ;}
		if(this.lhash().indexOf('category') < 0){
			location.hash += 'category';
		}
		window._ba && _ba.track('search', 'userinput', keyword, 1);
		this.startSearch(keyword);
	},
	getSearchPiece: function() {
		this.currentCate = 'search';
		this.currentLoading = baina.$('searchLoading');
		baina.$('word').style['display'] = 'none';
		this.currentLoading.style['display'] = 'block';
		this.apiObj.jsontype = 'app/search/hot-keywords.json';
		this.apiObj.fnName = 'createRecommendWord';
		this.apiObj.count = 12;
		this.apiObj.start_index += this.apiObj.count;
		this.getJSONP();

	},
	startSearch: function (keyword) {
		this.currentPage = this.searchAppList;
		this.clearAllNode(this.currentPage);
		this.currentPage.style['display'] = 'none';
		this.currentLoading.style['display'] = 'block';
		this.apiObj.jsontype = 'search/apps.json';
		this.apiObj.keyword = keyword;
		this.apiObj.fnName = 'createSearchList';
		this.apiObj.count = 15;
		this.apiObj.start_index = 0;
		this.getJSONP();
		this.currentSubCate = 'download';
		baina.$('word').style['display'] = 'none';
		baina.$('newWord').style['display'] = 'none';
		this.addmore.style['display'] = 'block';
		this.searchAppList.style['display'] = 'block';
	},
//share method
	getTarget: function (e, wantName) {
		var e = e || window.event;
		var currentTarget = e.srcElement || e.target;
		for(var i = 3;i--;){
			if((currentTarget.tagName).toUpperCase() == wantName){
				return currentTarget;
			} else {
				currentTarget = currentTarget.parentNode;
			}
		}
		return false;
	},
	clearAllNode: function (parentNode) {
   		while (parentNode.firstChild) {
			var oldNode = parentNode.removeChild(parentNode.firstChild);
			oldNode = null;
    	}
	},
	lhash: function(){
		var lhashText = location.hash;
		return lhashText ? lhashText.slice(1) : '';
	},
	detailDownloadTrack: function (e) {
		var e = e || window.event;
		var target = e.srcElement || e.target;
		if(target.className == 'downLink'){
			if(this.forDetailTrack){
				var cat = 'detaildownload_' + this.currentCate;
				var action = 'detaildownload_' + this.currentSubCate;
				window._ba && _ba.track(cat, action, target.getAttribute('trackmsg'), 1);			
			} else{
				window._ba && _ba.track('recommendation', 'download', target.getAttribute('trackmsg'), 1);
			}
		}
	},
	listDownloadTrack: function (e) {
		var e = e || window.event;
		var target = e.srcElement || e.target;
		if(target.className == 'downLink'){
			var cat = 'listdownload_' + this.currentCate;
			var action = 'listdownload_' + this.currentSubCate;
			window._ba && _ba.track(cat, action, target.getAttribute('trackmsg'), 1);
		}
	},
// 采用长排列，方式。
	launchPic: function (startElem) {
		var that = this;
		var picLists = this.focusImg.getElementsByTagName('a');
		startElem = startElem > picLists.length-1 ? 0 : startElem;
		var showNum = startElem;
		
		this.flashLED(showNum);
		this.movePic(showNum);
		this.startElem = ++startElem ;
		this.picTimeFn = setTimeout(function() {that.launchPic(startElem);}, 3000);
	},
	flashLED: function (showNum) {
		if(baina.$('flashchange').getElementsByClassName('active')[0] == undefined){return ;}
		baina.$('flashchange').getElementsByClassName('active')[0].className = '';
		this.flashLinks[showNum].className = 'active';
	},
	movePic: function (moveNum) {
		this.focusImg.style['-webkit-transition'] = '-webkit-transform .5s ease-out';
		var picLists = this.focusImg.getElementsByTagName('a');
		if(moveNum == 0){
			this.picMoveD = 0;
		} else if(moveNum == picLists.length-1){
			this.picMoveD = picLists.length*320-this.screenWidth;
		} else{
			this.picMoveD += 320;
		}
		this.focusImg.style['-webkit-transform'] = 'translate3d(-' + this.picMoveD + 'px,0,0)';
	},
	touchImgStart: function (e) {
		var target = this.getTarget(e, 'DIV');
		this.curX = 0;
		if(target){
		    this.startX = e.targetTouches[0].pageX;
		    this.startY = e.targetTouches[0].pageY;
			clearTimeout(this.picTimeFn);
		}
	},
	touchImgMove: function (e) {
		var target = this.getTarget(e, 'DIV');
		var picLists = this.focusImg.getElementsByTagName('a');
		var leftElem = this.startElem - 1;
		leftElem = leftElem > picLists.length-1 ? 0 : leftElem;
		var xMove = e.targetTouches[0].pageX - this.startX;
		var yMove = e.targetTouches[0].pageY - this.startY;
		if(Math.abs(xMove) > Math.abs(yMove)){
			e.preventDefault();
			if(target){
			    this.curX = e.targetTouches[0].pageX - this.startX;
				this.focusImg.style['-webkit-transition'] = 'none';
				this.focusImg.style['-webkit-transform'] = 'translate3d(-' + (this.picMoveD-this.curX) + 'px,0,0)';
			}
		}
	},
	touchImgEnd: function (e) {
		var target = this.getTarget(e, 'DIV');
		var picLists = this.focusImg.getElementsByTagName('a');
		var nowNum = this.startElem - 1;
		nowNum = nowNum > picLists.length-1 ? 0 : nowNum;
		if(target){
			if(this.curX > 100){
				var rightNum = nowNum-1;
				if(nowNum == 0){
					this.picMoveD = picLists.length*320-this.screenWidth;
				} else if(nowNum == picLists.length-1){
					this.picMoveD = (picLists.length-2)*320;
				} else{
					this.picMoveD -= 320;					
				}
				rightNum = rightNum < 0 ? picLists.length-1 : rightNum;
				this.focusImg.style['-webkit-transform'] = 'translate3d(-' + this.picMoveD + 'px,0,0)';
				this.focusImg.style['-webkit-transition'] = '-webkit-transform .2s ease-out';
				this.flashLED(rightNum);
				this.startElem = ++rightNum;
			} else if(this.curX < -100){
				var leftNum = nowNum + 1;
				if(nowNum == picLists.length-1){
					this.picMoveD = 0;
				}else if(nowNum == picLists.length-2){
					this.picMoveD = picLists.length*320-this.screenWidth;
				} else{
					this.picMoveD += 320;
				}
				leftNum = leftNum > picLists.length-1 ? 0 : leftNum;
				this.focusImg.style['-webkit-transform'] = 'translate3d(-' + this.picMoveD + 'px,0,0)';
				this.focusImg.style['-webkit-transition'] = '-webkit-transform .2s ease-out';
				this.flashLED(leftNum);
				this.startElem = ++leftNum;
			} else{
				this.focusImg.style['-webkit-transform'] = 'translate3d(-' + this.picMoveD + 'px,0,0)';
				this.focusImg.style['-webkit-transition'] = '-webkit-transform .1s ease-out';
			}
			this.picTimeFn = setTimeout(function() {pageControl.launchPic(pageControl.startElem);}, 4000);
		}
	},
	touchPicStart: function (e) {
		var target = this.getTarget(e, 'DIV');
		if(target){
			this.imglength = target.getElementsByTagName('img').length;
			this.imglength = this.imglength*158 - this.screenWidth;
		    this.detailStartX = e.targetTouches[0].pageX;
		    this.detailStartY = e.targetTouches[0].pageY;
		}
	},
	touchPicMove: function (e) {
		var target = this.getTarget(e, 'DIV');
		var xMove = e.targetTouches[0].pageX - this.detailStartX;
		var yMove = e.targetTouches[0].pageY - this.detailStartY;
		if(Math.abs(xMove) > Math.abs(yMove)){
			if(this.imglength < 0){return ;}
			e.preventDefault();
			if(target){
			    this.detailCurX = xMove + this.detailA;
			    if(this.detailCurX > 0){
			    	this.picCut.style['-webkit-transform'] = 'translate3d(' + (this.detailCurX/3) + 'px,0,0)';
			    }else if(this.detailCurX < -this.imglength){
					this.picCut.style['-webkit-transform'] = 'translate3d(' + (xMove/3 + this.detailA) + 'px,0,0)';
			    }else{
					this.picCut.style['-webkit-transform'] = 'translate3d(' + this.detailCurX + 'px,0,0)';
			    }
			}
		}
	},
	touchPicEnd: function (e) {
		var target = this.getTarget(e, 'DIV');
		if(target){
			if(this.detailCurX < -this.imglength){
				this.picCut.style['-webkit-transform'] = 'translate3d(-' + (this.imglength) + 'px,0,0)';
		    	this.detailA = -this.imglength;    	
		    }else if(this.detailCurX > 0){
		    	this.picCut.style['-webkit-transform'] = 'translate3d(0,0,0)';
		    	this.detailA = 0;
		    } else{
				this.detailA =  this.detailCurX;
		    }
		}
	},
	touchEffectStart: function (e, targetName) {
		var target = this.getTarget(e, targetName);
		var mustkill = document.getElementsByClassName('touchEffect')[0];
		if(mustkill){mustkill.className = '';}
		if(target){
			target.className += " touchEffect";
		}
	},
	touchEffectMove: function (e, targetName){
		var target = this.getTarget(e, targetName);
		if(target){
			var moveX = e.targetTouches[0].pageX - this.touchEffectX;
			if(Math.abs(moveX) > 100){
				e.preventDefault();
				setTimeout(function() {
					target.className = "";
				}, 200);
			}
		}
	},
	touchEffectEnd: function (e, targetName){
		var target = this.getTarget(e, targetName);
		if(target){
			var oldName = target.className;
			var killNum = oldName.indexOf('touchEffect');
			if(killNum >= 0){
				setTimeout(function() {
					target.className = oldName.slice(0, killNum-1);
				}, 100);
			}
			
		}
	}
}
pageControl.init();

baina.addEvent(window.applicationCache,"updateready",function(){
	window.applicationCache.swapCache();
	window.location.reload();  
});
