/* ***************
 *
 * 工具方法集
 *
 * @reuqire ../lib/zepto.min.js
 * @author Qifeng Liu
 * @date 2012/9/12
 *
 * ***************/
(function($, w, d) {
	// 如果 ui 命名空间不存在，则声明
	$.ui || ($.ui = {});
	
	
	$.ui.utils = {
		// 获取屏幕相关信息
		viewData : function() {
			var k = d.documentElement;
			return {
				scrollTop : w.pageYOffset, // 上滚距离
				scrollLeft : w.pageXOffset, // 左滚距离
				documentWidth : d.body.scrollWidth, // 文档宽度
				documentHeight : d.body.scrollHeight, // 文档高度
				viewWidth : k.clientWidth, // 可视区域宽度
				viewHeight : w.innerHeight // 可视区域高度
			}
		}
	};
})(Zepto, window, document);
