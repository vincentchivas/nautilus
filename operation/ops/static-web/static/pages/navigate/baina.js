var baina = {
	//兼顾工具函数、全局管理
	url : "/api/1/navigate.json?pname=com.dolphin.browser.cn",
	wurl:"/service/1/weathers.json",
	app_info : {app_key:"20d9d9c7e9a642cc9d082b3d2a14e707",version:"1.0.0",app_name:"站点导航",chn:"dolphin"},
	dev_info : {res:"320*480",os:"android4.0"},
	outOfDate : 168,//过期时间，单位小时。再次期间，网站、频道列表将使用本地数据localstorage
	$ : function(id){return document.getElementById(id);},
	addEvent : function(obj,eventType,func){obj.addEventListener(eventType,func,false)},
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

	getLocal : function(key,dolphin){
		//获得localStorage里面的值
		var storage = window.localStorage;
		if(window.dolphinLocalStorage && dolphin){
			storage = window.dolphinLocalStorage;
			if(storage.getItem(key) && storage.getItem(key).length>10){
				return storage.getItem(key);
			}else{
				return null;
			}
		}else if(storage.getItem(key)){
			return storage.getItem(key);
		}else{
			return null;
		}
	},
	setLocal : function(key,value,dolphin){
		var storage = window.localStorage;
		if(window.dolphinLocalStorage && dolphin){
			storage = window.dolphinLocalStorage;
		}
		storage.removeItem(key);
		try{
			if(window.dolphinLocalStorage && dolphin){
				return storage.setItem(key,value.toString());
			}else{
				storage.setItem(key,value);
				return "";
			}
		}catch(e){
			//打track这里
			return "error";
		}
	},
	netStat : function(){
		if(window.dolphin && window.dolphin.getActiveNetworkInfo && (window.dolphin.getActiveNetworkInfo()>=1 && window.dolphin.getActiveNetworkInfo()<=15)){
			return 1;//2G情况
		}else if((window.dolphin && !window.dolphin.getActiveNetworkInfo) ||(!window.dolphin && !navigator.onLine)){
			return -1;//非海豚或海豚找不到网络判断函数
		}else{
			return 0;//其余情况，认为是3G
		}
	},
	versionCheck : function(){
		var version = baina.app_info.version;
		//控制版本号，在版本更新时负责调用清理函数清理旧的数据结构，防止对新的结构造成干扰。
		if(!version || (/(^\d+.\d+.\d+(-[1|0][1|0])?$)/i.test(version) ==false &&  /(^0.\d+.0(-b\d+.\d+)?$)/i.test(version) ==false)){
			alert("版本号错误，请检查后重试");
			return false;
		}
		var oldVer;
		if(baina.getLocal("verWebApp")){
			oldVer = baina.getLocal("verWebApp");
		}
		var ver = version;
		if(oldVer !=ver){
			var cacheState = ver.split("-");
			var state = cacheState[1];
			var verCode = cacheState[0].split(".");
			if(cacheState.length == 1|| verCode[0] ==0){
				state = (verCode[0] ==0)?"10":"11";//默认发布版本的缓存状态为10,开发版本的状态为11.
			}
			if(state.charAt(0) == "0"){
				baina.clearUserSettings(); //强制清理掉使用版本控制机制前的一些不再使用的本地存储。
			}else{
				baina.checkUserSettings();
			}
			if(state.charAt(1) == "0"){
				baina.clearUserData(); 
			}else{
				//应该增加版本数据完整性检测的.
				baina.checkUserData();
			}			
			baina.setLocal("verWebApp",version);
		}
		return true;
	},
	clearUserData:function(){
		return true;
	},
	clearUserSettings:function(){
		return true;
	},
	checkUserData:function(){
		return true;
	},
	checkUserSettings:function(){
		return true;
	},	
	clearLocal : function(key,dolphin){
		var storage = window.localStorage;
		if(window.dolphinLocalStorage && dolphin){
			storage = window.dolphinLocalStorage;
		}
		storage.removeItem(key);
	},
	clearLocalAll : function(dolphin){
		var storage = window.localStorage;
		if(window.dolphinLocalStorage && dolphin){
			storage = window.dolphinLocalStorage;
		}
		storage.clear();
	},
	delNode : function(nid){
		//删除某个节点
		if(nid){
			nid.parentNode.removeChild(nid);
		}
	},
	appendClass: function(node,cname){
		if(node){
			node.className += " "+cname; 
		}
	},
	rmClass:function(node,cname){
		if(node){
			var name = node.className;
			if(name.indexOf(" "+cname)!==-1){
				node.className = name.replace(" "+cname,"");
			}
		}
	},
	dayStart : function(tm){
		//计算当前时间，跟上次更新的时间间隔，单位小时
		var day = (tm != undefined)?(new Date(tm)):(new Date());
		var str = day.getFullYear()+"-"+day.getMonth()+"-"+day.getDate()
		day = new Date(str).getTime();
		return day;
	},	

	track : function(category,action,label,value){
		//用于统计
		sdk.sdk_init(baina.app_info,baina.dev_info);
		if(navigator.onLine){
			//有网的情况下才统计
			sdk.track(category,action,label,value);
		}
		return false;
	}
};
baina.addEvent(window.applicationCache,"updateready",function(){
	window.applicationCache.swapCache();
});

var sdk = {
	sdk_version:"JS-0.1",
	mode:"char",//work as char or block device.
	buffer:[],
	app_info:null,
	dev_info:null,
	header:null,
	sdk_init:function(app_info,dev_info){
		if(!sdk.header){
			if(baina.getLocal("track_state") == 1){
				sdk.header = JSON.parse(baina.getLocal("track"));
			}else{
				var hdr = {};
				hdr.isu = Math.floor(Math.random()*1e16) + "" + Date.now();
				var version = navigator.appVersion;
				sdk.app_info = app_info;
				sdk.dev_info = dev_info;
				hdr.app_id = app_info.app_key;
				hdr.appvn = app_info.app_name;
				hdr.appvc = app_info.version;
				hdr.chn = app_info.chn;
				hdr.sdkv = sdk.sdk_version;
				hdr. cc = "cn";
				hdr.res = (document.body.clientWidth)+"*"+(window.innerHeight||document.body.clientHeight);
				hdr.os = "";
				hdr.osv = "";
				hdr.did = "";
				hdr.lon = 0.0;
				hdr.lat = 0.0;
				hdr.model = "";
				hdr.pn = "com.dolphin.browser.cn";
				hdr.cpu = "";
				hdr.lang = navigator.language.split("-")[0];
				hdr.nt = "";
				hdr.no = "";
				baina.setLocal("track",JSON.stringify(hdr));
				baina.setLocal("track_state",1);
				sdk.header = hdr;
			}
		}
	},
	track : function(cat,action,label,value){
		//用于统计
		if(navigator.onLine){
			//有网的情况下才统计
			var url = "http://acn.belugaboost.com/track/1/logs.gif?";
			var msg = {"header":sdk.header,"body":[]};
			if(sdk.mode == "char"){
				msg.body.push({"ctg":cat,"act":action,"lab":label,"val":value,"t":Date.now()});
				url += "l="+encodeURIComponent((JSON.stringify(msg)));
				var timg = new Image();
				timg.src = url;
			}else{
				//块模式，允许将多条信息打包发送。
			}			
		}
		return false;
	}
};
