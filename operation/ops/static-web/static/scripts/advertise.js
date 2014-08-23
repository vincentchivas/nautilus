
var Advertise = function(obj){
	this.author = "ypqi";
	this.email = "yanpqi@gmail.com";
	this.init(obj);
};
Advertise.prototype = {
	expire:3600000,//广告过期时间
	advsdisplay:false,//是否已经显示了广告
	advsPos:[],
	length:0,
	posname:"pt_advs",//广告位的类名
	init : function(obj){
		this.cid = obj.cid;
		this.expire = obj.expire?obj.expire:this.expire;
		this.posname = obj.classname?obj.classname:this.posname;
		this.advsPostion();
		this.initAdvertise();
	},
	initAdvertise : function(){
		var tempThis = this;
		var advsList = null;
		//var url = "http://172.16.9.144:8990/ad?cid=8";
		//var url = "/api/1/adverts.json?cid=8";
		var url = "http://opscn.dolphin-browser.com/api/1/adverts.json?cid=" + this.cid;
		if(window.dolphin && window.dolphin.dolphinadvert){
			url += "&" + window.dolphin.dolphinadvert();
		}
		if(!this.getSLocal("advs") || !(advsList = JSON.parse(this.getSLocal("advs"))) || Date.now()-advsList.tm >= tempThis.expire){
			this.ajaxGet(encodeURI(url),function(text){tempThis.manageAdvs(text);},function(text){tempThis.manageAdvs(text);});
		}else{
			this.showAdvs(advsList.data);
		}
	},
	manageAdvs : function(text){
		var aResponse,weight= 0;
		if(typeof text=="string" && (text.slice(0,10).toLowerCase().match("<html") || text.slice(0,10).toLowerCase().match("<!doctype")) ){
			return false;
		}
		if(!(aResponse = JSON.parse(text)) && typeof aResponse != "array"){
			return false;
		}
		for(var i=0;i<aResponse.length;i++){
			weight = 0;
			var newPicList=[],isPic = false,pos_data = aResponse[i].data;
			//过滤每个位置的数据，将其处理成只包含图片广告或文字广告。
			for(var j=0;j<pos_data.length;j++){
				if(pos_data[j].images.length ==0){
					continue;
				}else{
					newPicList.push(pos_data[j]);
					isPic = true;
				}
			}
			if(isPic){
				pos_data = newPicList;//只保留unshift到首部的图片数据。
				aResponse[i].mode = "imag";
			}else{
				aResponse[i].mode = "text";
			}
			//对这个位置的广告数据计算权重。
			for(var j=0;j<pos_data.length;j++){
				var temp = weight;
				weight += (pos_data[j].weight>0)?pos_data[j].weight:1;
				pos_data[j].weight = temp;
			}
			//将总权重记录下来，保证随机时可以随机到一个正确的范围。
			aResponse[i].tweight = weight;
			aResponse[i].data = pos_data;
		}
		var store = {tm:Date.now(),data:aResponse};
		this.setSLocal("advs",JSON.stringify(store));
		this.showAdvs(store.data);
	},
	showAdvs : function(data){
		if(this.advsdisplay){
			//已经显示了广告,直接退出.
			return true;
		}

		var tempThis = this;
		var elem,dom,cycleShow = [],idx,idx_adv;
		for(var i=0;i<data.length;i++){
			pos_data = data[i].data;
			if(data[i].mode == "imag"){
				//构造一个随机数，根据随机数确定哪个广告的哪张图片要被显示。
				var pos = this.strategyPicture(data[i].tweight,post_data);
				//取得要显示图片广告的位置，建立一个IMG元素，并将选定的图片url赋值给img的src。
				dom = this.advsPos[iid];
				if(!dom){
					continue;
				}
				var img = document.createElement("img");
				img.className="advpic";				
				dom.style["display"] = "block";
				img.style["max-width"] = dom.clientWidth +"px";
				img.src = show[pos[1]];
				dom.href = pos_data[pos[0]].url;
				dom.appendChild(img);
			}else{
				//对于文字广告，将其放入一个任务表中。
				cycleShow.push(data[i]);
			}
		}

		if(cycleShow.length > 0){
			//循环地从任务表中选择一个广告显示在对应的位置上。
			cycleText();
			setInterval(function(){
				cycleText();
			},10000);
		}
		function cycleText(){
			tempThis.advsdisplay = true;
			for(var i=0;i<cycleShow.length;i++){
				var pos_data = cycleShow[i];
				var dom = tempThis.advsPos[cycleShow[i].iid];
				if(!dom){
					continue;
				}
				var idx_adv = Math.floor((Math.random()*100)%pos_data.tweight);
				rdata = pos_data.data;
				for(var j= rdata.length-1;j>=0;j--){
					if(rdata[j].weight <= idx_adv){
						dom.style["display"] = "block";
						dom.href = rdata[j].url;
						dom.innerHTML = rdata[j].title;
						break;
					}
				}
			}
		}
	},
	resetAdvs : function(){
		//重置已经显示的广告,页面不切换而显示内容切换的情况下需要进行此操作.
		for(var i=0;i<this.length;i++){
			if(this.advsPos[i]){
				this.advsPos[i].innerHTML = "";
				this.advsPos[i].style["display"] = "none";
			}
		}
		this.advsdisplay = false;
	},
	strategyPicture:function(max,data){
		var idx,idx_adv,wt_adv = Math.floor((Math.random()*100)%weight);

		for(var j= data.length-1;j>=0;j--){
			if(data[j].weight <= wt_adv){
				idx_adv = j;
				break;
			}
		}
		var show = data[idx_adv].images;
		idx = Math.floor((Math.random()*100)%show.length);
		return [idx_adv,idx];//返回要显示的图片系列和系列中的图片位置.
	},
	strategyText:function(){

	},
	advsPostion:function(){
		//扫描页面上的广告位,将之放入表中.
		this.advsPos = [];
		var posList = document.getElementsByClassName(this.posname);
		for(var i=0,len=posList.length;i<len;i++){
			if(iid = posList[i].getAttribute("iid")){
				this.advsPos[iid] = posList[i]
			}
		}
		this.length = this.advsPos.length;
	},
	getSLocal : function(key,dolphin){
		//获得sessionStorage里面的值
		var storage = window.sessionStorage;
		if(storage.getItem(key)){
			return storage.getItem(key);
		}else{
			return null;
		}
	},
	setSLocal : function(key,value,dolphin){
		var storage = window.sessionStorage;
		storage.removeItem(key);
		storage.setItem(key,value);
		return "";
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
};
