var baina = {
	//兼顾工具函数、全局管理
	url : "/vw2/",///vw2/",
	ver : "20121228",//强制版本检查使用
	outOfDate : 168,//过期时间，单位小时。在此期间，网站、频道列表将使用本地数据localstorage
	$ : function(id){return document.getElementById(id);},
	addEvent : function(obj,eventType,func){
		if(navigator.msPointerEnabled){
			//ms pad
			switch (eventType){
				case "touchstart":
					eventType = "MSPointerDown";
					break;
				case "touchmove":
					eventType = "MSPointerMove";
					break;
				case "touchend":
					eventType = "MSPointerUp";
					break;
			}
		}
		if(window.addEventListener){
			obj.addEventListener(eventType,func,false);
		}else{
			obj.attachEvent("on" + eventType, func); 
		}
	},
	delEvent : function(obj,eventType,func){obj.removeEventListener(eventType,func,false)},
	viewData : function(){
		var W=0, H=0, SL=0, ST=0, SW=0, SH=0;
		var w=window, d=document, dd=d.documentElement;	
		W=dd.clientWidth||d.body.clientWidth;
		H=w.innerHeight||dd.clientHeight||d.body.clientHeight;
		ST=d.body.scrollTop||dd.scrollTop||w.pageYOffset;
		SL=d.body.scrollLeft||dd.scrollLeft||w.pageXOffset;
		SW=Math.max(d.body.scrollWidth, dd.scrollWidth ||0);
		SH=Math.max(d.body.scrollHeight,dd.scrollHeight||0, H);
		return {
			"scrollTop":ST,
			"scrollLeft":SL,
			"documentWidth":SW,
			"documentHeight":SH,
			"viewWidth":W,
			"viewHeight":H
		};
	},
	ajaxGet : function(url,successfn,failfn){
		var xmlhttp;
		if (window.XMLHttpRequest){
			xmlhttp=new XMLHttpRequest();
		}else{
			xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		}
		xmlhttp.open("GET",url,true);
		xmlhttp.send();
		xmlhttp.onreadystatechange=function(){
			if(xmlhttp.readyState==4){
				if(xmlhttp.status==200 && successfn!=undefined){
					successfn(xmlhttp.responseText);
				}else if(failfn != undefined){
					//alert("status:" + xmlhttp.status + " url:"+url);
					failfn(xmlhttp.responseText);
				}
			}else{
				//错误函数
			}
		}
	},
	ajaxPost : function(url,data,successfn,failfn){
		var xmlhttp;
		if (window.XMLHttpRequest){
			xmlhttp=new XMLHttpRequest();
		}else{
			xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
		}
		xmlhttp.open("POST",url);
		xmlhttp.send(JSON.stringify(data));
		xmlhttp.onreadystatechange=function(){
			if(xmlhttp.readyState==4){
				if(xmlhttp.status==200 && successfn!=undefined){
					successfn(xmlhttp.responseText);
				}else if(failfn != undefined){
					//alert("status:" + xmlhttp.status + " url:"+url);
					failfn(xmlhttp.responseText);
				}
			}else{
				//错误函数
			}
		}
	},
	lhash : function(){
		//返回hash，不包括“#”
		var lhash = location.hash;
		if(lhash){
			lhash = lhash.slice(1);
		}else{
			lhash = "";
		}
		return lhash;
	},
	timeLast : function(){
		//计算当前时间，跟上次更新的时间间隔，单位小时
		if(baina.getLocal("refreshTime")){
			var now = Date.now();
			var lastTime = new Date(parseInt(baina.getLocal("refreshTime")));
			return parseInt((now - lastTime)/3600000);
		}else{
			return 8760; //365*24;
		}
	},
	getLocal : function(key){
		//获得localStorage里面的值
		var storage = window.localStorage;
		if(storage.getItem(key)){
			return storage.getItem(key);
		}else{
			return null;
		}
	},
	setLocal : function(key,value){
		var storage = window.localStorage;
		storage.removeItem(key);
		try{
			storage.setItem(key,value);
			return "";
		}catch(e){
			//打track这里
			return "error";
		}
	},
	clearLocal : function(key){
		var storage = window.localStorage;
		storage.removeItem(key);
	},
	clearLocalAll : function(){
		var storage = window.localStorage;
		storage.clear();
	},
	delNode : function(nid){
		//删除某个节点
		if(nid && nid.nodeName){
			nid.parentNode.removeChild(nid);
		}
	},
	subs : function(s,endindex,addDot){
		//对s字符串，截取endindex长度的字节数。addDot表示是否需要加上...在后面
		var r = /[^\x00-\xff]/g;
		if(!s || s.replace(r,"mm").length <= endindex){
			return s;
		}
		var m = Math.floor(endindex/2);
		for(var i=m,k=s.length;i<k;i++){
			if(s.substr(0,i).replace(r,"mm").length>=endindex){
				if(addDot){
					return s.substr(0,i-1) + "...";
				}else{
					return s.substr(0,i);
				}
			}
		}
		return s;   
	},
	manageDate : function(date,isOffset){
		//格式化时间，将时间转化为文字描述
		var result = "";
		if(isOffset==undefined){
			//不显示差量的情况
			var tempT = new Date(date);
			result = tempT.getFullYear() + "-" + (tempT.getMonth()+1) + "-" + tempT.getDate() + ", ";
			if(tempT.getHours()<12){
				result += "上午"+tempT.getHours();
			}else{
				if(tempT.getHours()==12){
					result += "下午12";
				}else{
					result += "下午"+(tempT.getHours()-12);
				}
			}
			result += ":";
			if(tempT.getMinutes()<10){
				result += "0";
			}
			result += "" + tempT.getMinutes();
			return result;
		}
		var offset = parseInt(new Date().getTime() - date);
		if(offset>=0){
			if(offset<59000){
				result = parseInt(offset/1000) + "秒前";
			}else if(offset<3600000){
				result = parseInt(offset/60000) + "分钟前";
			}else if(offset<86400000){
				result = parseInt(offset/3600000) + "小时前";
			}else{
				result = parseInt(offset/86400000) + "天前";
			}
		}else{
			var tempOffset = Math.abs(offset);
			if(tempOffset<59000){
				result = parseInt(tempOffset/1000) + "秒后";
			}else if(tempOffset<3600000){
				result = parseInt(tempOffset/60000) + "分钟后";
			}else if(tempOffset<86400000){
				result = parseInt(tempOffset/3600000) + "小时前后";
			}else{
				result = parseInt(tempOffset/86400000) + "天前";
			}
		}
		return result;
	},
	adjustListPic : function(pic){
		//图片加载成功后，调整尺寸(list)
		//被调整过一次以后，图片的尺寸就不准了，需要重新获取，所以要new一个image对象
		var tempImg = new Image();
		tempImg.src = pic.src;
		var w = pic.parentNode.offsetWidth;
		var h = pic.parentNode.offsetHeight;
		tempImg.onload = function(){
			var originalRatio = tempImg.width/tempImg.height;
			setTimeout(function(){
				if(w/h >= originalRatio){
					pic.style["width"] = w + "px";
					pic.style["height"] = parseInt(w/originalRatio) + "px";
				}else{
					pic.style["height"] = h + "px";
					pic.style["width"] = parseInt(h*originalRatio) + "px";
				}
				baina.showCommonPic(pic);
			},20);
		}
	},
	errorPic : function(pic,bgcolor){
		//图片出错的时间，图片img删掉，换成黑色
		var pNode = pic.parentNode;
		baina.delNode(pic);
		if(bgcolor){
			pNode.style["background"] = "#"+bgcolor+" url(images/dolphin_b.png) no-repeat center center";
		}else{
			pNode.style["background"] = "#666 url(images/dolphin_b.png) no-repeat center center";
		}
		pNode.style["background-size"] = "25px";
	},
	adjustNewsPic : function(pic){
		//图片加载成功后，调整尺寸(detail)
		//被调整过一次以后，图片的尺寸就不准了，需要重新获取，所以要new一个image对象
		var tempImg = new Image();
		tempImg.src = pic.src;
		tempImg.onload = function(){
			var oriW = tempImg.width;//原始图片的高宽
			var oriH = tempImg.height;
			var w = pic.parentNode.offsetWidth;
			var h = parseInt(oriH/oriW*w);
			setTimeout(function(){
				//需要延时一下，否则android比较垃圾，多了就处理不过来了
				if(w < oriW){
					pic.style["width"] = w + "px";
					pic.style["height"] = h + "px";
				}else{
					pic.style["width"] = oriW + "px";
					pic.style["height"] = oriH + "px";
				}
				baina.showDetailPic(pic);
			},50);
		}
	},
	adjustAlbumPic : function(pic){
		//图片加载成功后，调整图片尺寸（图集的detail）
		var tempImg = new Image();
		tempImg.src = pic.src;
		tempImg.onload = function(){
			//判断一下tempImg.width，保证这个属性存在。这个主要是刷新的时候，图片没load，这个属性是0，导致计算错误
			oriW = tempImg.width;
			oriH = tempImg.height;
			var originalRatio = oriW/oriH;
			var returnW,returnH;
			var vW = baina.viewData().viewWidth;
			var vH = baina.viewData().viewHeight
			if(vW/vH >= originalRatio){
				returnH = vH;
				returnW = parseInt(vH*originalRatio);
			}else{
				returnW = vW;
				returnH = parseInt(vW/originalRatio);
			}
			pic.style["width"] = returnW + "px";
			pic.style["height"] = returnH + "px";
			baina.showCommonPic(pic);
		}
	},
	showDetailPic : function(pic){
		//新闻详情页面的图片获取之前尺寸未知，所以它的父元素div事先设置了一个默认高度值，
		//在图片onload后将高度变成auto以适应其中的图片
		pic.parentNode.style["height"] = "auto";
		pic.parentNode.style["background-color"] = "rgba(0, 0, 0, 0)";
		pic.style["display"] = "block";
	},
	showCommonPic : function(pic){
		pic.style["display"] = "block";
	},
	refreshT : function(){
		//参数t。为了让后端api做缓存，t不能随机取，就0~4
		var ajaxT = 0;
		if(baina.getLocal("webzine-ajaxT")){
			ajaxT = parseInt(baina.getLocal("webzine-ajaxT"));
			if(ajaxT < 0){
				ajaxT = 0;
			}else{
				ajaxT = (++ajaxT)%5;
			}
		}
		baina.setLocal("webzine-ajaxT",ajaxT);
		return ajaxT;
	},
	netWorkType : function(qMark){
		//海豚浏览器独有函数，检测网络的情况
		/*
		public static final int NETWORK_TYPE_DISCONNECT =-1;
		public static final int NETWORK_TYPE_WIFI =10000;
		public static final int NETWORK_TYPE_UNKNOWN = 0;
		public static final int NETWORK_TYPE_GPRS = 1;
		public static final int NETWORK_TYPE_EDGE = 2;
		public static final int NETWORK_TYPE_UMTS = 3;
		public static final int NETWORK_TYPE_CDMA = 4;
		public static final int NETWORK_TYPE_EVDO_0 = 5;
		public static final int NETWORK_TYPE_EVDO_A = 6;
		public static final int NETWORK_TYPE_1xRTT = 7;
		public static final int NETWORK_TYPE_HSDPA = 8;
		public static final int NETWORK_TYPE_HSUPA = 9;
		public static final int NETWORK_TYPE_HSPA = 10;
		public static final int NETWORK_TYPE_IDEN = 11;
		public static final int NETWORK_TYPE_EVDO_B = 12;
		public static final int NETWORK_TYPE_LTE = 13;
		public static final int NETWORK_TYPE_EHRPD = 14;
		public static final int NETWORK_TYPE_HSPAP = 15;
		*/
		if(window.dolphin && window.dolphin.getActiveNetworkInfo){
			if(qMark){
				//问号
				return "?nt=" + window.dolphin.getActiveNetworkInfo();
			}else{
				return "&nt=" + window.dolphin.getActiveNetworkInfo();
			}
		}else{
			return "";
		}
	},
	track : function(action_type,item_type,item_self,reference_item_type,reference_item,position){
		//用于统计
		if(navigator.onLine){
			//有网的情况下才统计
			var url = "http://a.dolphin-browser.com/track/t.gif?";
			url += "t=" + Date.now();
			url += "&src=dolphin-reader";
			if(baina.getLocal("deviceid")){
				//如果有uid了，则把uid发送给服务器，作为用户的标识
				url += "&did=" + baina.getLocal("deviceid");
			}else{
				//否则随机生成一个，记录在storage中
				var did = Math.floor(Math.random()*1e16) + "" + Date.now();
				baina.setLocal("deviceid",did);
				url += "&did=" + did;
			}
			if(navigator.platform){
				url += "&dt=" + navigator.platform;//device_type
			}
			if(screen.width){
				url += "&re=" + screen.width + "*" + screen.height;//resolution
			}
			if(window.dolphin && window.dolphin.getActiveNetworkInfo){
				url += "&nt=" + window.dolphin.getActiveNetworkInfo();//network_type
			}else{
				url += "&nt=unknown";
			}
			url += "&at=" + action_type;
			url += "&it=" + item_type;
			url += "&i=" + item_self;
			if(reference_item_type!=undefined){
				url += "&rit=" + reference_item_type;
			}
			if(reference_item!=undefined){
				url += "&ri=" + reference_item;
			}
			if(position!=undefined){
				url += "&p=" + position;
			}
			var timg = new Image();
			timg.src = encodeURI(url);
		}
		return false;
	},
	touchSet : function(obj){
		//y方向简单滑动控件。不带任何回调，没有特殊控制（例如下拉刷新等）
		this.author = "zengshun";
		this.email = "isaacshun@gmail.com";
		this.weibo = "http://weibo.com/isaacshun";
		this.init(obj);
	},
	setTransition : function(obj,string){
		//做一下兼容性，IE10用的是transition。但发现在一些android机器上会导致-webkit-transition失效，从而动画失效，所以统一把transition写在-webkit-transition的前面
		obj.style["transition"] = string.replace(/-webkit-transform/g,"transform");
		obj.style["-webkit-transition"] = string;
	},
	setTransform : function(obj,x,y){
		//做一下兼容性，IE10用的是transform
		obj.style["transform"] = "translate3d("+x+"px,"+y+"px,0)";
		obj.style["-webkit-transform"] = "translate3d("+x+"px,"+y+"px,0)";
	},
	touchX : function(e){
		//做一下兼容性，IE10用的e.pageX
		if(e.touches){
			return e.touches[0].pageX;
		}else{
			return e.pageX;
		}
	},
	touchY : function(e){
		//做一下兼容性，IE10用的e.pageY
		if(e.touches){
			return e.touches[0].pageY;
		}else{
			return e.pageY;
		}
	},
	setAnimation : function(obj,string){
		//设置animation属性，做兼容性
		obj.style["animation"] = string;
		obj.style["-webkit-animation"] = string;
	},
	supportScroll : function(){
		//是否是android 4 或者 ios 5以上
		//return navigator.userAgent.match(/(Android 4)|(CPU iPhone OS [56])/i);
		return navigator.userAgent.match(/CPU iPhone OS [56]/i);
	},
	createStyle : function(filename,fileid){
		//创建CSS样式表，插入<style>标签
		if(!baina.$(fileid)){
			var tLink = document.createElement("link");
			tLink.rel = "stylesheet";
			tLink.type = "text/css";
			tLink.href = filename;
			tLink.id = fileid;
			document.getElementsByTagName("head")[0].appendChild(tLink);
		}
	},
	strIconPage : function(page){
		//当iconPage<10时，需要在其前面加上0
		if(page<10){
			return "0" + page;
		}else{
			return page;
		}
	},
	addClass : function(elem, value){
		if (!elem) {
			return false;
		}
		var classNames = value.split(" ");
		if (elem.nodeType === 1) {
			if (!elem.className && classNames.length === 1) {
				elem.className = value;
			} else {
				var setClass = " " + elem.className + " ";
				for (var c = 0, cl = classNames.length; c < cl; c++) {
					if (!~setClass.indexOf(" " + classNames[c] + " ")) {
						setClass += classNames[c] + " ";
					}
				}
				elem.className = setClass.replace(/^\s+|\s+$/g,"");
			}
		}
	}
};
baina.touchSet.prototype = {
	tTarget : null,//移动的对象
	cY : 0,//移动的总位置，是morechannel_的缩写
	lastcY : 0,//上一个move事件的时候移动的总位置
	lastY : 0,//上一个触点的位置
	startX : 0,
	startY : 0,//开始的位置
	distanceX : 0,//水平方向移动的距离
	distanceY1 : 0,
	distanceY : 0,//y方向上，end之后缓冲的距离
	hasmove : false,//是否有移动
	outerH : null,//计算availbleH使用的，包裹的div
	scrollToTop : false,//触碰滑动区域的时候，时候需要隐藏浏览器顶部的地址栏
	availbleH : 0,
	slowTimeY : 0,//缓冲所用的时间
	speedY : 0,//速度
	lastTime : 0,//时间戳
	borderStartY : false,//是否本身就在边界上，例如顶部或者底部
	borderOutBlank : false,//滑动到上下边界之后是否可以拉出空白
	init : function(obj){
		var tempThis = this;
		this.tTarget = obj.tTarget;
		this.outerH = obj.outerH;
		this.borderOutBlank = obj.borderOutBlank ? true : false;
		if(obj.scrollToTop){
			this.scrollToTop = obj.scrollToTop;
		}
		baina.addEvent(this.tTarget,"touchstart",function(e){tempThis._TouchStart(e);});
		baina.addEvent(this.tTarget,"touchmove",function(e){tempThis._TouchMove(e);});
		baina.addEvent(this.tTarget,"touchend",function(e){tempThis._TouchEnd(e);});
		baina.addEvent(this.tTarget,"click",function(e){tempThis._click(e);});
		//对于外层需要阻止一下，主要是当内层的高度比外层还要矮的时候，会拖动外层。这时，外层不能乱动
		baina.addEvent(this.outerH,"touchmove",function(e){e.preventDefault();e.stopPropagation();});
		baina.addEvent(window,"resize",function(){tempThis.rotateAdjust();});
		baina.addEvent(window,"orientationchange",function(){tempThis.rotateAdjust();});
	},
	_TouchStart : function(e){
		if(e.touches && e.touches.length>1){
			//这里只允许单指操作
			return false;
		}
		if(this.scrollToTop && baina.viewData().scrollTop!=1){
			//触碰了滑动区域，如果浏览器的地址栏没有收起来，则让它收起来
			window.scrollTo(0,1);
		}
		//如果y方向上在缓冲，再touchstart的时候，需要停下来
		var style = document.defaultView.getComputedStyle(this.tTarget, null);
		// Computed the transform in a matrix object given the style.
		var transform;
		if(window.MSCSSMatrix){
			transform = new MSCSSMatrix(style.transform);
		}else if(window.WebKitCSSMatrix){
			transform = new WebKitCSSMatrix(style.webkitTransform);
		}
		// Clear the active transition so it doesn’t apply to our next transform.
		baina.setTransition(this.tTarget,"");
		// Set the element transform to where it is right now.
		this.cY = transform.m42;
		baina.setTransform(this.tTarget,0,this.cY);
		this.startX = baina.touchX(e);
		this.lastY = this.startY = baina.touchY(e);
		this.hasmove = false;
		this.lastcY = this.cY;
		this.distanceY = this.distanceY1 = 0;
		this.availbleH = this.tTarget.offsetHeight - this.outerH.offsetHeight;//在横竖屏转换时，这个值会发生变化唉，所以需要处理
		if(this.availbleH<0){
			this.availbleH = 0;
		}
		baina.setTransition(this.tTarget,"");
		this.lastTime = e.timeStamp;
		this.slowTimeY = 0;
		if(this.cY>=0 || Math.abs(this.cY)>=this.availbleH){
			this.borderStartY = true;
		}else{
			this.borderStartY = false;
		}
	},
	_TouchMove : function(e){
		e.preventDefault();
		if(e.touches && e.touches.length>1){
			//这里只允许单指操作
			return false;
		}
		var currentX = baina.touchX(e);	
		var currentY = baina.touchY(e);	
		this.cY = this.lastcY + currentY - this.lastY;
		if(this.cY >=0 || Math.abs(this.cY)>=this.availbleH){
			//最顶上往下移动，最底部往上移动，则根据borderOutBlank的值来判断是速度减半拉出空白还是不滑动
			this.cY = this.borderOutBlank ? (this.lastcY + (currentY- this.lastY)/2) : this.lastcY;
		}
		this.speedY = (currentY - this.lastY)/(e.timeStamp - this.lastTime);
		var acceleration = this.speedY > 0 ? -0.001 : 0.001;//加速度常量，可根据喜好适当调整。减速运动，所以方向跟速度是相反的。
		this.slowTimeY = -parseInt(this.speedY/acceleration);
		this.distanceY = -parseInt(0.5*acceleration*Math.pow(this.slowTimeY,2));//根据速度，计算此时松手滑行的距离。
		this.lastcY = this.cY;
		this.lastY = currentY;
		this.lastTime = e.timeStamp;
		this.distanceY1 = currentY - this.startY;
		this.distanceX = currentX - this.startX;
		baina.setTransform(this.tTarget,0,this.cY);
		if(Math.abs(this.distanceX)>10 || Math.abs(this.distanceY1)>10){
			this.hasmove = true;//有移动
		}
	},
	_TouchEnd : function(e){
		if(e.touches && e.touches.length>0){
			//这里只允许单指操作。注意touchend的时候，如果是单指，已经没有手指了，就是0。这个跟start、move都不一样
			return false;
		}
		var tempThis = this;
		if(Math.abs(this.distanceY1)>10){
			//有些浏览器的bug，光在touchmove阻止不行。但是完全阻止，又会影响click，所以只能自己判断
			e.preventDefault();
		}
		var tempCY = this.cY;
		this.cY = this.lastcY + this.distanceY;
		if(this.cY>0 || Math.abs(this.cY)>this.availbleH){
			//出界的情况
			if(this.cY>0){
				this.cY = 0;
				//因为路程短了，根据速度重新计算时间
				this.slowTimeY = Math.abs(tempCY/this.speedY);
			}else if(Math.abs(this.cY)>this.availbleH){
				this.cY = -this.availbleH;
				this.slowTimeY = Math.abs((this.availbleH-Math.abs(tempCY))/this.speedY);
			}
			if(this.borderStartY){
				//如果一开始就在边界，出界了则规定时间滑动回来
				this.autoMoveTo(this.tTarget,0,this.cY,500,"ease");
			}else{
				this.autoMoveTo(this.tTarget,0,this.cY,this.slowTimeY,"ease");
			}
		}else{
			this.autoMoveTo(this.tTarget,0,this.cY,this.slowTimeY);
		}
	},
	_click : function(e){
		//主要是处理ie10不能正确的阻止点击事件
		if(this.hasmove){
			e.returnValue = false;
			e.preventDefault();
			return false;
		}
	},
	autoMoveTo : function(target,posX,posY,time,timingfunc){
		if(timingfunc != undefined){
			baina.setTransition(target,"-webkit-transform " + time/1000 + "s " + timingfunc);
		}else{
			baina.setTransition(target,"-webkit-transform " + time/1000 + "s cubic-bezier(0.33, 0.66, 0.66, 1)");
		}
		baina.setTransform(target,posX,posY);
	},
	rotateAdjust : function(){
		//横竖转换的时候，会存在出界的情况，需要处理
		this.availbleH = this.tTarget.offsetHeight - this.outerH.offsetHeight;
		if(this.availbleH<0){
			this.availbleH = 0;
		}
		if(Math.abs(this.cY)>this.availbleH){
			this.cY = -this.availbleH;
			baina.setTransform(this.tTarget,0,this.cY);
		}
	},
	setcy : function(cy){
		//给外部使用的，设置滑动到的位置
		this.cY = cy;
		baina.setTransform(this.tTarget,0,this.cY);
	}
};
baina.addEvent(window.applicationCache,"updateready",function(){
	window.applicationCache.swapCache();
	window.location.reload();  
});