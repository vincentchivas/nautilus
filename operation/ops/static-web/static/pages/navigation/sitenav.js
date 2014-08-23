function setLocal(key,value){
	var storage = window.localStorage;
	if(window.dolphinLocalStorage){
		//storage = window.dolphinLocalStorage;
	}
	storage.removeItem(key);
	storage.setItem(key,value.toString());
}
 function getLocal(key,dolphin){
	//���localStorage�����ֵ
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
}	
function track(action_type,item_type,item_self,reference_item_type,reference_item,position){
	//����ͳ��
	if(navigator.onLine){
		//����������²�ͳ��
		var url = "http://a.dolphin-browser.com/track/t.gif?";
		url += "t=" + Date.now();
		if(getLocal("deviceid")){
			//�����uid�ˣ����uid���͸�����������Ϊ�û��ı�ʶ
			url += "&did=" + getLocal("deviceid");
		}else{
			//�����������һ������¼��storage��
			var did = Math.floor(Math.random()*1e16) + "" + Date.now();
			setLocal("deviceid",did);
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
		url += "&src=siteNavigation";
		var timg = new Image();
		timg.src = encodeURI(url);
	}
	return false;
}