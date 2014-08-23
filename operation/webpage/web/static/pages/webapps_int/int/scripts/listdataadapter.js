/* ***************
 *
 * data adapter for list,paginglist,indexbarlist,pullrefreshlist
 *
 * @require ../lib/zepto.min.js
 * @author Qifeng Liu
 * @date 2012/9/20
 *
 * ***************/

;(function($, w, d) {
	// 如果 ui 命名空间不存在，则声明
	$.ui || ($.ui = {});
	
	
	$.ui.data = {
			/*
			 * like ["a","b","c"]
			 */
			simpleAdapter : function(data) {
				var result = {};
				result._title = null;
				result._items = [];
				$.each(data, function(index, item) {
					result._items.push({
						_text : item
					});
				});
				return [result];
			},
			
			/*
			 * like [{name:"a"},{name:"b"},{name:"c"}]
			 */
			objectAdapter : function(data, adapter) {
				var result = {};
				result._title = null;
				result._items = [];
				var obj;
				$.each(data, function(index, item) {
					obj = {};
					obj._text = item[adapter.property];
					$.extend(obj, item);
					result._items.push(obj);
				});
				return [result];
			},
			
			/*
			 * like [{name:"a",items:["a.1","a.2"]},{name:"b",items:["b.1","b.2"]},{name:"b",items:["c.1","c.2"]}]
			 */
			groupAdapter : function(data, adapter) {
				var result = [];
				var obj, ary;
				$.each(data, function(index, item) {
					obj = {};
					obj._title = item[adapter.property];
					$.extend(obj, item);
					obj._items = [];
					ary = item[adapter.children];
					if (ary) {
						obj._items = $.ui.data[adapter.adapter.type+"Adapter"](ary, adapter.adapter)[0]._items;
					}
					result.push(obj);
				});
				return result;
			}
	};
})(Zepto, window, document);