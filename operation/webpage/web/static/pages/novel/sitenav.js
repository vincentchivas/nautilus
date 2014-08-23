var store = {
	//baseurl:"data.php?add=novels.html&pn=com.dolphin.browser.cn&src=ofw",
	baseurl:"/api/1/novels.html?pn=com.dolphin.browser.cn&src=ofw",
	addEvent : function(obj,eventType,func){obj.addEventListener(eventType,func,false)},
	height: window.innerHeight||document.documentElement.clientHeight||document.body.clientHeight,
	width:window.innerWidth||document.documentElement.clientWidth||document.body.clientWidth,
	getListData:function(nm,fn,efn)
	{
		var url = this.baseurl;
		var tempThis = this;
		if(navigator.onLine)
		{
			url += "&title="+ nm;
			this.ajaxGet(encodeURI(url),
				function(text){tempThis.handleNovelData(text,fn);},
				function(text){tempThis.handleAjaxErr(text,efn);});				
		}
	},
	handleAjaxErr:function(text,fn)
	{
		fn(text);
		return false;
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
	testServerText:function(text)
	{
		if(!text)
		{
			return null;
		}
		if(typeof text=="string" && (text.slice(0,10).toLowerCase().match("<html") || text.slice(0,10).toLowerCase().match("<!doctype"))){
			return null;
		}
		var r = JSON.parse(text);
		if(!r || r.items.length == 0)
		{
			return null;
		}
		return r;
	},
	handleNovelData:function(text,fn)
	{
		r = this.testServerText(text);
		if(r != null)
		{
			fn(r);
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
		storage.setItem(key,value.toString());
	},
	track:function(action_type,item_type,item_self,reference_item_type,reference_item,position){
	//用于统计
		if(navigator.onLine){
			//有网的情况下才统计
			var url = "http://a.dolphin-browser.com/track/t.gif?";
			url += "t=" + Date.now();
			if(this.getLocal("deviceid")){
				//如果有uid了，则把uid发送给服务器，作为用户的标识
				url += "&did=" + this.getLocal("deviceid");
			}else{
				//否则随机生成一个，记录在storage中
				var did = Math.floor(Math.random()*1e16) + "" + Date.now();
				this.setLocal("deviceid",did);
				url += "&did=" + did;
			}
			if(navigator.platform){
				url += "&dt=" + navigator.platform;//device_type
			}
			if(navigator.language){
				url += "&os=" + navigator.language;//os
			}
			if(screen.width){
				url += "&re=" + screen.width + "*" + screen.height;//resolution
			}
			if(window.dolphin && window.dolphin.getActiveNetworkInfo){
				url += "&nt=" + window.dolphin.getActiveNetworkInfo();//network_type
			}
			url += "&at=" + action_type;
			url += "&it=" + item_type;
			url += "&i=" + item_self;
			if(reference_item_type!=undefined){
				url += "&rt=" + reference_item_type;
			}
			if(reference_item!=undefined){
				url += "&ri=" + reference_item;
			}
			if(position!=undefined){
				url += "&p=" + position;
			}
			url += "&src=novelRank";
			var timg = new Image();
			timg.src = encodeURI(url);
		}
		return false;
	},
	createStyle:function(filename,fileid){
		//创建CSS样式表，插入<style>标签
		if(!document.getElementById(fileid)){
			var tLink = document.createElement("link");
			tLink.rel = "stylesheet";
			tLink.type = "text/css";
			tLink.href = filename;
			tLink.id = fileid;
			document.getElementsByTagName("head")[0].appendChild(tLink);
		}
	}
}