$("body").bind("touchstart",function(){});//用于激活元素的:active

var themeUtils = {
	//皮肤的工具函数
	saveTabStatus : function(key, index){
		this.setSession(key, index);
	},
	loadTabStatus : function(key){
		var index = this.getSession(key);
		return index ? index : 0;
	},
	errorPic : function(pic){
		//图片出错的时间，图片img删掉
		if(pic && pic.nodeName && pic.parentNode){
			pic.parentNode.removeChild(pic);
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
	getSession : function(key){
		//获得localStorage里面的值
		var storage = window.sessionStorage;
		if(storage.getItem(key)){
			return storage.getItem(key);
		}else{
			return null;
		}
	},
	setSession : function(key,value){
		var storage = window.sessionStorage;
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
	delNode : function(nid){
		//删除某个节点
		if(nid && nid.nodeName && nid.parentNode){
			nid.parentNode.removeChild(nid);
		}
	},
	showToast : function(toastNode, context){
		var vW = document.documentElement.clientWidth;
		var vH = document.documentElement.clientHeight;

		toastNode.html(context);

		//调整toast的尺寸，首先显示出来才能方便获取高度
		toastNode.show();
		//30为confirm的高
		toastNode.css("left", 20);
		//减去底部菜单栏高度，底部边距，以及自身高度。
		toastNode.css("top", vH - 60);
		//触发淡入动画
		toastNode.css("opacity", 1);

		setTimeout(function(){
			//淡入动画需要1秒，再停留1秒
			toastNode.css("opacity", 0);
		}, 2000);
		setTimeout(function(){
			//以免页面冗余，完全透明后还是隐藏。淡出动画需要1秒。
			toastNode.hide();
			toastNode.html("");
		}, 3000);
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
	 /**
	  * 获取参数列表，优先从query字符串获取，如果没有就取hash值里面的，根据需求调整
	  * @return {Object} [description]
	  */
	getMatchParams : function(){//用于获取app_id或者subject_id等
		var _hash = this.getHashParams(),
			_query = this.getQueryParams();
		return $.extend(_hash, _query);
	},
	 /**
	  * 获取查询参数
	  * @return {[type]} [description]
	  */
	getQueryParams:function(){
		var queryStr = window.location.search.slice(1);
		return this.getStringParams(queryStr);
	},
	 /**
	  * 获取hash值的对象
	  * @return {Object} 
	  */
	getHashParams:function(){
		return this.getStringParams(this.lhash());
	},
	 /**
	  * 序列化字符串值
	  * @param {String} str 需要序列号的值
	  * @return {Object} hash对象
	  */
	getStringParams:function(str){
		var _input = "string" === typeof str ? str : '',
			_paras = _input.split('&'),
			result={};
		var i, l, tmp;
		for(i=0,l=_paras.length; i<l; i++){
			tmp = _paras[i].split('=');
			result[tmp[0]] = tmp[1] || '';
		}
		return result;
	}
}