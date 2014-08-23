//GameCenter
function GameCenter(obj){
				this.init(obj);
			}
			GameCenter.prototype = {
				fillInFlag:null, //自动调整定时标志
				outFlag:false, //被拖动元素已经离开标志
				isStayFlag:null, //计算当前位置定时
				isStayPos:null, //判断是否停留位置阀值
				curMoveElem:null, //当前被拖动元素
				moveElems:{}, //缓存的子节点
				parentNode:{}, //父节点
				moveBox:{},//存放元素格子
				boxSizeX:100, //每个元素占空间，X*Y
				boxSizeY:155,
				boxNum:3, //每行放置最大元素数
				touchM:null, //缓存touchMove 对象
				timerFlag:null,//启动sent to desktop定时
				enterFlag:false, //初次进入管理页面阻止触发点击
				sentToDesktopTimer:null,//计时以判断是否要发到桌面
				enTouch:false,   //是否进入管理
				lastPosX:null,  //触摸起点X
				lastPosY:null,	//触摸起点Y
				startPosX:null,//拖动元素位置x
				startPoxY:null,//拖动元素位置y
				clickFlag:null, //区别点击与touch 计时
				changeSwitch:null, 
				localSet:null, //本地存储缓存
				boxState:null,  //ico排列对应gameId
				flagNode:null,  // setToDesktop 标题节点
				sentingFlag:false,
				stopComputePos:false,
				addIco:null,
				tmpBanliang:{},
				init:function(obj){
					
				},
				judgeGesture:function(){
			
				},
				receData:function(obj){
					if(typeof(obj)=='string'||Object.prototype.toString.call(obj)=='[object String]'){
						var length,tmpArr = JSON.parse(obj),tmpItemList=[],tmpSmallItem=[],tmpMiddleItem=[],tmpItems,tmpItem;
						for(var i=0,length = tmpArr.length;i<length;i++){
							tmpItem = this.tidyObject(tmpArr[i]);
							switch(tmpItem.kind){
								case 'large':
									tmpItemList.push(tmpItem);
								break;
								case 'small':
									if(tmpMiddleItem.length<=0){
										tmpSmallItem.push(tmpItem);
									}else{
										tmpItems =[tmpMiddleItem.shift(),tmpItem];
										tmpItemList.push(tmpItems);
									}
								break;
								case 'middle':
									if(tmpSmallItem.length<=0){
										tmpMiddleItem.push(tmpItem);
									}else{
									tmpItems =[tmpItem,tmpSmallItem.shift()];
									tmpItemList.push(tmpItems);
									}	
								break;
								default:
								break;
							}
						}
						this.setLocal('gameCenter',obj);
						return tmpItemList;
					}
				},
				orgamizeHtml:function(obj,start,end,errFun){ //组织页面
					var i=0,reHtml=[],changeFlag=false,firstFlag = true,largetArr=[],smallArr=[],tmpImg={},tmpTit='',tmpSpan='',length,tmpThis=this;
					if(Object.prototype.toString.call(obj)=='[object Array]'){
						for(var j=0,length=obj.length;j<length;j++){
							if(obj[j].kind=='large')
								largetArr.push(obj[j]);
							else
							smallArr.push(obj[j]);
						}
						length=largetArr.length;
						length = ((length>=3)?3:length);
						//for test
						/* for(var i=0;i<length;i++){
						tmpImg+='<a href="detail.html#'+largetArr[i].id+'"><img src="'+largetArr[i].img+'"></a>';
						tmpTit+='tit'+i+'="'+largetArr[i].tit+'" ';
						if(!i)
							tmpSpan+='<span class="on"></span>';
						else
							tmpSpan+='<span></span>';
						}
					reHtml.push('<div id="headItem" class="headP imgHolder"><div len='+length+' id="picHolder">'+tmpImg+'</div><div class="title" id="headTitle" '+tmpTit+' >'+largetArr[0].tit+'</div><div class="itemShadow" >'+tmpSpan+'</div></div>'); */
						tmpImg.arr = [];
						tmpImg.parent = 'picHolder';
						for(var i=0;i<length;i++){
							tmpImg.arr[i]={};
							tmpImg.arr[i].id=largetArr[i].id;
							tmpImg.arr[i].image = largetArr[i].img;
							tmpImg.arr[i].title = largetArr[i].tit;
						}
						setTimeout(function(){tmpThis.slidePic(tmpImg,'falgArea','headTitle')},500);
						reHtml.push('<div id="headItem" class="headP imgHolder"><div id="picHolder"></div><div class="title" id="headTitle" ></div><div class="itemShadow" id="falgArea" ></div></div>');
						j=01,i=0;
						while(1){
							if(j>=largetArr.length&&i>=smallArr.length)
								break;
							if(i<smallArr.length){
								reHtml.push('<a  href="detail.html#'+smallArr[i][1].id+'"><div class="item"><div class="small imgHolder first"><img src="'+smallArr[i][1].img+'"><div class="title">'+((smallArr[i][1].tit.length>14)?(smallArr[i][1].tit.substr(0,7)+'…'):(smallArr[i][1].tit))+'</div><div class="itemShadow"></div></div></a><a href="detail.html#'+smallArr[i][0].id+'"><div class="middle imgHolder second"><img src="'+smallArr[i][0].img+'"><div class="title">'+smallArr[i][0].tit+'</div><div class="itemShadow"></div></div></div></a>');
								i++;
							}
							if(i<smallArr.length){
								reHtml.push('<a href="detail.html#'+smallArr[i][0].id+'"><div class="item"><div class="middle imgHolder first"><img src="'+smallArr[i][0].img+'"><div class="title">'+smallArr[i][0].tit+'</div><div class="itemShadow"></div></div></a><a href="detail.html#'+smallArr[i][1].id+'"><div class="small imgHolder second"><img src="'+smallArr[i][1].img+'"><div class="title">'+((smallArr[i][1].tit.length>14)?(smallArr[i][1].tit.substr(0,7)+'…'):(smallArr[i][1].tit))+'</div><div class="itemShadow"></div></div></div></a>');
								i++;
							}
							if(j<largetArr.length){
								reHtml.push('<div id="largeItem" class="headP imgHolder"><a href="detail.html#'+largetArr[j].id+'"><div id="picHolder"><img src="'+largetArr[j].img+'"><img src="'+largetArr[j].img+'"><img src="'+largetArr[j].img+'"></div><div class="title">'+largetArr[j].tit+'</div></a><div class="itemShadow" ></div></div>');
								j++;
							}
						}
						return reHtml.join("");
					}
					if(errFun != undefined)
						return errFun(arr);
					return null;
				},
				tidyObject:function(tmp){ //打包参数，方便组织页面
					tmpItem = {};
					tmpItem.img = tmp.picture;
					tmpItem.tit = tmp.title;
					tmpItem.id = tmp.id;
					//tmpItem.url = tmp.download_url;
					tmpItem.kind = tmp.pic_kind;
					return tmpItem;
				},
				getId:function(url){  //页面之间传值
					var tmpId = url.substring(url.indexOf('#')+1);
					if(tmpId!=''&&tmpId!=undefined&&url.indexOf('#')!=-1){
						return tmpId;
					}
					return null;
				},
				androidVersion:function(agent){
					if(agent){
						if(nav.indexOf('Android')!=-1){
						return	tmpDolphin = parseInt(nav.substr(nav.indexOf('Android')+8,5));
						}
					}
					return null;
				},
				ajaxGet : function(url,successfn,failfn){  //ajax 请求
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
							}else{
							baina.track("error","ajaxGet",xmlhttp.status,"ajaxUrl",url);
							}
						}else{
							//错误函数
						}
					}
				},
				getLocal:function(key,dolphin){
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
				setLocal:function(key,value,dolphin){
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
				isIos:function(){
					if(/\((iPhone|iPad|iPod)/i.test(navigator.userAgent)){
						return true;
					}else{
						return false;
					}
				},
				iosFixed:function(elem,posi){ //ios fixed适配
					switch(posi){
					case 'top':
						window.addEventListener('scroll',function(){elem.setAttribute('style','position:absolute;top:'+document.body.scrollTop+'px')});
					break;
					case 'bottom':
						window.addEventListener('scroll',function(){elem.setAttribute('style','position:absolute;bottom:auto;top:'+(document.body.scrollTop-50+window.innerHeight)+'px;')});
					break;
					default:
					}
				},
				changePage:function(page,director,width,jumpUrl){
					
					switch(director){
						case 'left':
							speedX = width/32;
							tmpThis.Animation(page,width,0,speedX,0,speedX,0,'xSmall');
						break;
						case 'right':
							speedX = -width/32;
							tmpThis.Animation(curNode,-width,0,speedX,0,speedX,0,'xLarge');
						break;
						default:
						break;
					}
					setTimeout(function(){widow.location.href=jumpUrl},800);
				},
				slidePic:function(pic,flags,tit){
					var tmpThis=this;
					(function(){
					var picParent,flagParent,titParent,picArr=[],flagArr=[],titArr,picNode=[],targetX,judgeReson,speedX,touStartX=0,touMoveFun=function(e){},first=0,second=1,last,next=1,length,enMove=true,turnShow;
					if(!pic||!flags)
						return false;
					length = pic.arr.length;
					last=length-1;
					picNode[0] = document.createElement('div');
					picNode[0].id = 'pic1';
					picNode[1] = document.createElement('div');
					picNode[1].id = 'pic2';
					picParent = document.getElementById(pic.parent);
					flagParent = document.getElementById(flags);
					for(var i=0;i<length;i++){
						picArr[i] = tidy(pic.arr[i]);
						flagArr[i] = document.createElement('span');
						flagArr[i].id = 'flag'+i;
						flagParent.appendChild(flagArr[i]);
					}
					flagArr[0].className = "on";
					picNode[0].setAttribute('posL',0);picNode[0].setAttribute('posT',0);
					picNode[0].innerHTML='<a href="'+((picArr[0].id)?('detail.html#'+picArr[0].id):'#')+'"><img src="'+picArr[0].img+'"></a>';
					if(tit){
						titParent = document.getElementById(tit);
						titParent.innerHTML=picArr[0].tit;
					}	
					picParent.appendChild(picNode[0]);
					picParent.appendChild(picNode[1]);
					picNode[0] = document.getElementById('pic1');
					picNode[1] = document.getElementById('pic2');
					picParent.addEventListener('touchstart',function(e){touS(e)});
					picParent.addEventListener('touchmove',function(e){touMoveFun(e)});
					document.addEventListener('touchend',function(e){touE(e)});
					turnShow = setTimeout(function(){changePic(picNode[first],picNode[second],'left',picArr[next],titParent);changeFlag(flagArr,next);last=(last+1+length)%length;next=(next+1+length)%length;touStartX = 0;first=(++first)%2;second=(++second)%2;},10000);
					function touS(e){
						if(!touStartX&&e.target.nodeName.toLowerCase()=='img'){
							touStartX = e.touches[0].pageX;
							touMoveFun=touM;
						}
						
						return true;
					}
					function touM(e){
						if(!touStartX)
							return false;
						if((parseInt(e.touches[0].pageX)-parseInt(touStartX))>0){
							changePic(picNode[first],picNode[second],'right',picArr[last],titParent);changeFlag(flagArr,last);last=(last-1+length)%length;next=(next-1+length)%length;
						}else{
							changePic(picNode[first],picNode[second],'left',picArr[next],titParent);changeFlag(flagArr,next);last=(last+1+length)%length;next=(next+1+length)%length;
						}
						touStartX = 0;
						first=(++first)%2;
						second=(++second)%2;
					}
					function changeFlag(tmpFlag,onId){
						for(var i=0,length=tmpFlag.length;i<length;i++){
							tmpFlag[i].className = "";
						}
						tmpFlag[onId].className="on";
					}
					function touE(){
						if(touStartX){touStartX=0;touMoveFun=function(){};enMove = true;}
					}
					function tidy(tmp){
						var retmp = {};
						retmp.id = tmp.id;
						retmp.img = tmp.image;
						retmp.tit = tmp.title;
						return retmp;
					}
					function changePic(curNode,lastNode,method,info,titNode){
						var tmpWidth = parseInt(curNode.offsetWidth);
						switch(method){
							case 'left':
								targetX = -tmpWidth;
								sourceX = tmpWidth;
								judgeReson = 'xSmall';
								speedX = -(tmpWidth/32);
							break;
							case 'right':
								targetX = tmpWidth;
								sourceX = -tmpWidth;
								judgeReson = 'xLarge';
								speedX = tmpWidth/32;
							break;
							default:
							break;
						}
						if(titNode){
							titNode.innerHTML = info.tit;
						}
						lastNode.setAttribute('style','-webkit-transform: translate3d('+sourceX+'px,0,0);');
						lastNode.innerHTML = '<a href="'+((info.id)?('detail.html#'+info.id):'#')+'"><img src="'+info.img+'"></a>';
						lastNode.setAttribute('posL',sourceX);lastNode.setAttribute('posT',0);
						setTimeout(function(){tmpThis.Animation(curNode,targetX,0,speedX,0,speedX,0,judgeReson);},25);
						setTimeout(function(){tmpThis.Animation(lastNode,0,0,speedX,0,(sourceX+speedX),0,judgeReson);},25);
						clearTimeout(turnShow);
						turnShow = setTimeout(function(){changePic(picNode[first],picNode[second],'left',picArr[next],titParent);changeFlag(flagArr,next);last=(last+1+length)%length;next=(next+1+length)%length;touStartX = 0;first=(++first)%2;second=(++second)%2;},10000);
					}})();
				},
				localSys:function(page){
					var saveFlag=true,saveItem={},reObj;
					switch(page){
						case 'index':
							
						break;
						case 'featured':
						break;
						case 'detail':
						break;
					}
					if(saveFlag){
						for(var i in saveItem)
						this.setLocal(i,saveItem[i]);
					}
					return reObj;
				},
				initDrag:function(obj,tmpLocalSet,tmpBoxState){
					var tmpThis = this,tmpParent,d=document,w=window,tmpBox,i,objLength;
					this.localSet = tmpLocalSet;this.boxState = tmpBoxState;
					if(!obj.parent||obj.parent==''){
						throw new Error('父元素不能为空');
					}
					this.flagNode = document.getElementById('sentToTopBar');
					tmpParent = d.getElementById(obj.parent)||(this.errLog('父元素获取失败！'));
					tmpBox = [];
					for(i=0,objLength=obj.child.length;i<objLength;i++){
						tmpBox[i] = {};
						tmpBox[i].id=i;
						tmpBox[i].left = i%this.boxNum*this.boxSizeX;
						tmpBox[i].top = Math.floor(i/this.boxNum)*this.boxSizeY;
						this.moveElems[obj.child[i]]={belongBox:tmpBox[i]};
						tmpBox[i].target = d.getElementById(obj.child[i]);
					}
					this.addIco = document.getElementById('addIco');
					this.moveElems.length = objLength;
					this.changeSwitch = d.getElementById('changeState');
					this.moveBox.box = tmpBox;
					this.moveBox.empty = objLength; 
					tmpBox = [];
					this.addEvent(tmpParent,'touchstart',function(e){tmpThis.touchStartFun(e);window.console.log('1')});
					this.addEvent(tmpParent,'touchmove',function(e){tmpThis.touchMoveFun(e);window.console.log('2')});
					this.addEvent(tmpParent,'click',function(e){tmpThis.clickFun(e)})
					this.addEvent(d,'touchend',function(e){tmpThis.touchEndFun(e);window.console.log('3')});
					/* this.addEvent(tmpParent,'mousedown',function(e){tmpThis.touchStartFun(e)});
					this.addEvent(tmpParent,'mousemove',function(e){tmpThis.touchMoveFun(e)});
					this.addEvent(d,'mouseup',function(e){tmpThis.touchEndFun(e)},false); */
					this.addEvent(d.getElementById('returnBtn'),'click',function(){tmpThis.exitEnter('exit')});
				},
				showAnounce:function(){
					var date=new Date(),month = date.getMonth(),day = date.getDay(),now = month*30+day,last,dialogNode;
					for(var i=0,length=this.moveElems.length;i<length;i++){
						if(last = this.moveBox.box[i].target.getAttribute('lastOpen')){
							last = parseInt(last);
							if((now-last)>18){
								dialogNode = document.createElement('div');
								dialogNode.className = "dA";
								dialogNode.setAttribute('animation','dialogshow');
								dialogNode.innerHTML="<p>Don't you love me?</p>";
								this.moveBox.box[i].target.appendChild(dialogNode);
							}
						}
					}
				},
				exitEnter:function(method){
					switch(method){
						case 'exit':
							this.enTouch=false;this.changeSwitch.className="showCabinet";this.saveBox();this.addIco.style.display='';
						break;
						case 'enter':
							this.enTouch=true;this.changeSwitch.className="hideCabinet";this.addIco.style.display='none';;
						break;
						default:
						return false;
					}
					return true;
				},
				saveBox:function(){
					var tmpArr=[];
					for(var i=0,tmpLength=this.moveElems.length;i<tmpLength;i++){
						tmpArr[i]=this.boxState[this.moveBox.box[i].target.id.replace('ico','')];
					}
					this.localSet.boxSave = tmpArr;
					this.setLocal('localSave',JSON.stringify(this.localSet));
					this.addIco.style.left = this.moveElems.length%3*100+'px';
					this.addIco.style.top = Math.floor(this.moveElems.length/3)*155+'px';
					//this.addIco.setAttribute('style','left:'+(this.moveElems.length%3)*100+'px,'+Math.floor(this.moveElems.length/3)*155+'px,0);');
				},
				clickFun:function(e){
					var pNode = e.target.parentNode;
					if(!this.enterFlag){
						this.enterFlag=true;
						return false;
					}
					if((pNode.id in this.moveElems)){
						if(this.enTouch){
							//if(e.target.className=='deleIco')
							if(pNode.id in this.moveElems)
								this.deleIco(pNode);
						}else{
							var date=new Date(),month = date.getMonth(),day = date.getDay(),now = month*30+day,tmpUrl = pNode.getAttribute('url'),tmpTit=pNode.getAttribute('tit'),tmpJump = 'loading.html#';
							this.localSet.readedGame[this.boxState[e.target.parentNode.id.replace('ico','')]].lastOpen = now;
							this.setLocal('localSave',JSON.stringify(this.localSet));
							e.target.setAttribute('animation','showClick');setTimeout(function(){e.target.setAttribute('animation','');if(tmpUrl&&tmpUrl!='undefined'){tmpJump+=tmpUrl+'&'+tmpTit}else{tmpJump+=("http://www.phoboslab.org/xtype")};window.location.href=tmpJump},500);
						}
					}
				},
				sentToDesktop:function(node,e){
					var tmpThis=this,tmpIco,tmpMessage = document.getElementById('userMessage'),tmpInfo;
					tmpInfo = this.localSet.readedGame[this.boxState[node.id.replace('ico','')]];
					this.flagNode.style.borderColor='red';
					if(!tmpInfo.isSent){
						clearTimeout(this.sentToDesktopTimer);
						this.sentToDesktopTimer = setTimeout(function(){
							var gameSiteUrl,iconFileUrl,shortcutName = node.getAttribute('tit'),sentCall=false;
							tmpThis.tmpBanliang.enable=true;
							//enable=confirm("您确定要将"+shortcutName+'发送到桌面？');
							if(tmpThis.tmpBanliang.enable){
								tmpThis.tmpBanliang.enable = false;
								gameSiteUrl=node.getAttribute('url');
								//iconFileUrl='http://'+document.domain+'/'+node.getAttribute('ico');
								iconFileUrl=node.getAttribute('ico');
								sentCall = dolphinGameCenter.createGameShortcut(shortcutName,gameSiteUrl,iconFileUrl,1000);
								setTimeout(function(){if(sentCall){tmpInfo.isSent=true;tmpMessage.innerHTML="";tmpThis.touchEndFun(e);tmpThis.flagNode.style.borderColor='';}else{tmpInfo.isSent=false;tmpMessage.innerHTML="发送失败，"+shortcutName+"&"+gameSiteUrl+"&"+iconFileUrl+"可能您的lancher不支持！"}tmpMessage.setAttribute('animation','dialogshow');setTimeout(function(){tmpMessage.setAttribute('animation','')},2000);tmpThis.tmpBanliang.enable = true;},1000);
								tmpThis.sentingFlag = false;
							}
						},3000);
					}else{
						tmpMessage.innerHTML='您已经发送过该游戏了！';
						tmpMessage.setAttribute('animation','dialogshow');
						setTimeout(function(){tmpMessage.setAttribute('animation','')},2000);
					}
				},
				deleIco:function(node){
					var tmplist,removeId,tmploca,tempThis=this,tmpLeft=node.getAttribute('posL'),tmpTop=node.getAttribute('posT');
					removeId = this.moveElems[node.id].belongBox.id;
					node.setAttribute('animation','removeShow');
					node.style.cssText='left:'+tmpLeft+'px;top:'+tmpTop+'px';
					setTimeout(function(){node.parentNode.removeChild(node);tempThis.fillIn(removeId);tempThis.moveElems.length-=1;tempThis.localSet.readedGame[tempThis.localSet.boxSave[removeId]].isAdd=false;tempThis.localSet.readedGame[tempThis.localSet.boxSave[removeId]].isSent=false},1000);
				},
				touchStartFun:function(e){
					var tmpThis=this;
					if((e.target.parentNode.id in this.moveElems)){
						this.clickFlag = setTimeout(function(){e.preventDefault();tmpThis.clickFlag=null;if(!tmpThis.enTouch){tmpThis.touchMoveFun=function(){clearTimeout(tmpThis.timerFlag);clearTimeout(tmpThis.clickFlag);}}},50);
						if(!this.enTouch){
						clearTimeout(this.timerFlag);
						this.timerFlag = setTimeout(function(){e.preventDefault();tmpThis.exitEnter('enter')},300);
						return false;
						}
						var touE,node;
						node = e.target.parentNode;
						this.curMoveElem = node;
						//window.console.log(node);
						touE = (e.touches&&e.touches[0])||e;
						this.lastPosX = touE.pageX;
						this.lastPosY = touE.pageY;
						this.firstPosX = parseInt(node.getAttribute('posL'))||0;
						this.firstPosY = parseInt(node.getAttribute('posT'))||0;
						this.touchMoveFun = this.moveElem;
						//this.fillInFlag = setTimeout(function(){tmpThis.fillIn();},250);
					}
				},
				touchMoveFun:function(e){
				e.preventDefault();
				},
				moveElem:function(e){
					var node,touE,curPosX,tmpThis=this;
					e.preventDefault();
					if(!(node = this.curMoveElem))
						return false;
					touE = (e.touches&&e.touches[0])||e;
					touX = touE.pageX;touY =touE.pageY;
					curPosX = touX-this.lastPosX+this.firstPosX;
					curPosY = touY-this.lastPosY+this.firstPosY;
					//window.console.log(touY);
					if(touY<70&&!this.sentingFlag){
						this.sentingFlag = true;
						this.sentToDesktop(node,e);
					}	
					if(touY>70&&this.sentingFlag){
						this.sentingFlag = false;
						clearTimeout(this.sentToDesktopTimer);
						this.flagNode.style.borderColor='';
					}
					node.setAttribute('style','-webkit-transform: translate3d('+curPosX+'px,'+curPosY+'px,0);');
					if(!this.outFlag&&this.isLeave(node,curPosX,curPosY)){
						this.outFlag =true;
						//window.console.log('moveout'+tmpBoxId);
					}else{
						clearTimeout(this.isStayFlag);
						this.isStayFlag = setTimeout(function(){if(!this.stopComputePos){tmpThis.computePos(curPosX,curPosY)}},200);
					}
				},
				touchEndFun:function(e){
					clearTimeout(this.timerFlag);
					clearTimeout(this.isStayFlag);
					this.touchMoveFun = function(){};
					if(this.clickFlag){
						clearTimeout(this.clickFlag);
						return false;
					}
					if(!this.enTouch)
						return false;
					var node,touE;
					node = this.curMoveElem;
					touE =(e.changedTouches&&e.changedTouches[0])||(e.touches&&e.touches[0])||e;
					if(node&&(node.id in this.moveElems)){
							var tmpBox = this.moveBox.box[parseInt(node.id.replace('ico',''))];
							node.setAttribute('posL',(touE.pageX-this.lastPosX+this.firstPosX));
							node.setAttribute('posT',(touE.pageY-this.lastPosY+this.firstPosY));
							//window.console.log('posL'+(touE.pageX-this.lastPosX+this.firstPosX)+'posT'+(touE.pageY-this.lastPosY+this.firstPosY));
							this.returnBack(node);
							this.firstPosX = null;this.firstPosY=null;
							this.curMoveElem=null;
							this.touchMoveFun = function(){};
					}
				},
				computePos:function(x,y){
					var whichBox;
					if(this.stopComputePos){
						return false;
					}
					this.stopComputePos = true;
					whichBox = Math.floor(x/this.boxSizeX)+Math.floor(y/this.boxSizeY)*this.boxNum;
					if(whichBox <this.moveElems.length&&0<=whichBox){
						this.fillOut(whichBox);
					}else{
						this.stopComputePos = false;
					}
				},
				isLeave:function(curElem,x,y){
					var tmpBox = this.moveElems[curElem.id].belongBox;
					if(Math.abs(x-tmpBox.left)>this.boxSizeX||Math.abs(y - tmpBox.top)>this.boxSizeY){
						this.moveElems[curElem.id].belongBox = null;
						this.fillIn(tmpBox.id);
						return true;
					}
					else
						return false;
				},
				updateEmpty:function(kind,boxId){
					switch(kind){
						case 'returnBack':
							this.moveBox.empty = this.moveElems.length;
						break;
						case 'fillOut':
						case 'fillIn' :
							this.moveBox.empty = boxId;
							//this.showBoxL();
						break;
						default:
					}
				},
				fillOut:function(boxId){
					var tmpThis = this,icoNum = this.moveElems.length,tmpTBox,tmpSBox,bottomBox;
					bottomBox = icoNum-1;
					for(var i=bottomBox;i>boxId;i--){
						tmpSBox = this.moveBox.box[i-1];
						if(tmpSBox&&tmpSBox.target){
							this.moveTo(tmpSBox.target,i);
							//window.console.log(i+tmpSBox.target.id);
						}else{
							
							break;
						}
					}
					//window.console.log(i+'&');
					this.moveElems[this.curMoveElem.id].belongBox = this.moveBox.box[boxId];
					this.moveBox.box[boxId].target=this.curMoveElem;
					this.outFlag = false;
					setTimeout(function(){this.stopComputePos = false;},500);
					return true;
				},
				fillIn:function(boxId){
					var tmpThis = this,icoNum = this.moveElems.length,tmpSBox;
					for(var j=boxId;j<icoNum-1;j++){
						//window.console.log('fillIn'+j)
						tmpSBox = this.moveBox.box[j+1];
						if(tmpSBox&&tmpSBox.target){
							//window.console.log('fillIn'+tmpSBox.target.id)
							this.moveTo(tmpSBox.target,j);
						}else{
							//if(this.moveBox.box[i]){this.moveBox.box[i].target = null;}
							break;
						}
					}
					//window.console.log('fillIn'+i);
					this.updateEmpty('fillIn',j);
					return true;
				},
				returnBack:function(curElem){
					var tmpBox = this.moveElems[curElem.id].belongBox,tmpEmpty,tmpLength =this.moveElems.length;
					//window.console.log(tmpBox.target.id+'&&'+tmpBox.id+'&&'+curElem.id+"&&"+tmpEmpty);
					tmpEmpty = ((this.moveBox.empty>=tmpLength)?(tmpLength-1):this.moveBox.empty)
					if(tmpBox){
						this.moveTo(curElem,tmpBox.id,true);
					}else{
						this.moveTo(curElem,tmpEmpty);
					}
					this.updateEmpty('returnBack');
					this.outFlag = false;
					this.stopComputePos = false;
					clearTimeout(this.sentToDesktopTimer);
				},
				moveTo:function(curElem,boxId){  //移至某一位置
					var tmpThis = this,judgeReson,left = parseInt(curElem.getAttribute('posL'))||0,top = parseInt(curElem.getAttribute('posT'))||0,speedX,speedY,tmpBox=this.moveBox.box[boxId],x=(tmpBox&&tmpBox.left)||(boxId%this.boxNum*this.boxSizeX),y=(tmpBox&&tmpBox.top)||(Math.floor(boxId/this.boxNum)*this.boxSizeY);
					//window.console.log(top+'&&'+left+'&&'+tmpBox.id+'&&'+curElem.id);
					this.moveBox.box[boxId].target = curElem;
					this.moveElems[curElem.id].belongBox = this.moveBox.box[boxId];
					if(x>left){judgeReson = 'xLarge'}
					else if(x<left){judgeReson = 'xSmall'}
					else if(y>top){judgeReson = 'yLarge'}
					else if(y<top){judgeReson = 'ySmall'}
					else{return false;}
					speedX = (x-left)/16;
					speedY = (y-top)/16;
					setTimeout(function(){tmpThis.Animation(curElem,x,y,speedX,speedY,(left+speedX),(top+speedY),judgeReson);},25);
				},
				Animation:function(curElem,endX,endY,speedX,speedY,x,y,judgeReson){ //移动动画，改进流畅度
					if(curElem==undefined){
						throw(new Error('动画对像为空！'));
						return false;
					}
					var tmpThis = this,exitFlag = false;
					x +=speedX;
					y +=speedY;
					curElem.setAttribute('style','-webkit-transform: translate3d('+x+'px,'+y+'px,0);');
					switch(judgeReson){
						case 'xLarge': if(x>=endX){exitFlag=true;}; break;case 'xSmall':if(x<=endX){exitFlag=true;}; break;case 'yLarge':if(y>=endY){exitFlag=true;}; break;case 'ySmall':if(y<=endY){exitFlag=true;}; break;default:return false;
					}
					if(exitFlag){
						curElem.setAttribute('style','-webkit-transform: translate3d('+endX+'px,'+endY+'px,0);');
						curElem.setAttribute('posL',endX);
						curElem.setAttribute('posT',endY);
						//window.console.log(endX+'&&'+endY);
						return true;
					}else{
						setTimeout(function(){tmpThis.Animation(curElem,endX,endY,speedX,speedY,x,y,judgeReson)},25);
					}
				},
				addEvent:function(elem,event,func,other){
					if(other==undefined)
						other = true;
					elem.addEventListener(event,func,other);
				},
				showBoxL:function(){
					var tmpBox;
					for(var i=0,tmpLength=this.moveElems.length;i<tmpLength;i++){
						tmpBox = this.moveBox.box[i];
						window.console.log("id:"+tmpBox.id+"&target:"+tmpBox.target.id+"&targetBox:"+this.moveElems[tmpBox.target.id].belongBox.id);
					}
				},
				testLog:function(){  //输出测试信息接口
					text = "&";
					for(var i=0;i<arguments.length;i++){
						text+=arguments[i]+"&";
					}
					document.getElementById('show').innerHTML = text;
				}
			}