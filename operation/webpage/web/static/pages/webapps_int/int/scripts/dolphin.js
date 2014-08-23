var dolphin = {
	addToHome : function(name, url, icon){
		alert(name + "已添加到桌面");
	},
	isHomeAdded : function(url){
		return Math.random() > 0.5 ? true : false;
	},
	showNativeAddPage : function(){
		alert("此处弹出客户端添加界面");
	}
};