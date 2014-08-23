/* ***************
 *
 * button control
 *
 * @reuqire ../lib/zepto.min.js
 * @author Qifeng Liu
 * @date 2012/9/12
 *
 * ***************/

;(function($) {
    $.extend($.fn, {
        list : function(obj) {
            // Zepto Object
            var $self = $(this);
            if ($self.length == 0) {
                // if the selector selects nothing, error happens
                console.error("The selector selects nothing");
                return;
            }
            // data vars
            var listData = {
                dataSource : obj.dataSource,
                data : null
            };

            // settings
            var settings = {
                type : obj.type || "plain",  // list display style : plain | group
                editStyle : obj.editStyle || "none" // list edit style : none | delete | reorder
            };
            
            // functions
            var funs = {
                delegate : obj.delegate, // delegate for custom style and event handle
                
                init : function(obj) {
                    funs.bindEvent();
                    funs.beginData();
                },
                
                bindEvent : function() {
                    $self.on({
                        "touchstart" : function(e) {
                            $(e.target).addClass("fake-active");
                        },
                        "touchcancel" : function(e) {
                            $(e.target).removeClass("fake-active");
                        },
                        "touchend" : function(e) {
                            $(e.target).removeClass("fake-active");
                        },
                        "touchmove" : function(e) {
                            $(e.target).removeClass("fake-active");
                        },
                        "click" : function(e) {
                            e.stopPropagation();
                            if (funs.delegate) {
                                if ($.isFunction(funs.delegate.clickOnRow)) {
                                    var row = $(this).index();
                                    var section = $(this).parent().parent().index();
                                    funs.delegate.clickOnRow({
                                        section : section,
                                        row : row
                                    }, listData.data[section]._items[row], e);
                                }
                            } else{
                                //$self.off({"click", ".z-l-r"});
                                e.preventDefault();
                            }
                            return false;
                        }
                    }, ".z-l-r");
                    $self.on({
                        "click" : function(e) {
                            e.stopPropagation();
                            if (funs.delegate) {
                                if ($.isFunction(funs.delegate.clickOnHeader)) {
                                    var section = $(this).parent().index();
                                    funs.delegate.clickOnHeader({
                                        section : section
                                    }, listData.data[section]);
                                }
                            }
                            return false;
                        }
                    }, ".z-l-h");
                    $self.on({
                        "click" : function(e) {
                            e.stopPropagation();
                            if (funs.delegate) {
                                if ($.isFunction(funs.delegate.clickOnFooter)) {
                                    var section = $(this).parent().index();
                                    funs.delegate.clickOnFooter({
                                        section : section
                                    }, listData.data[section]);
                                }
                            }
                            return false;
                        }
                    }, ".z-l-f");
                },
                
                // resolve the data with data adapter
                beginData : function() {
                    var data = listData.dataSource.data;
                    var adapter = listData.dataSource.adapter;
                    if ($.isFunction(adapter)) { // custom adapter
                        listData.data = adapter(data);
                    } else { // system adapter
                        listData.data = $.ui.data[adapter.type+"Adapter"](data, adapter);
                    }
                    funs.initUI();
                },
                
                initUI : function() {
                    // style
                    $self.addClass("l-s-" + settings.type.substring(0, 1));
                    
                    var fragment = funs.createFragment();
                    $self.append(fragment);
                },
                createFragment : function() {
                    var fragment = document.createDocumentFragment();
                    $.each(listData.data, function(index, data) {
                        fragment.appendChild(funs.createSection(data, index));
                    });
                    return fragment;
                },
                createSection : function(data, section) {
                    var section = document.createElement("div");
                    section.className = "z-l-s";
                    if (funs.delegate) {
                        if ($.isFunction(funs.delegate.headerDOM)) {
                            var headerDIV = funs.delegate.headerDOM({
                                section : section
                            }, data);
                            headerDIV.className = headerDIV.className + " z-l-h";
                            section.appendChild(headerDIV);
                        } else {
                            if (settings.type == "group") {
                                var headerDIV = document.createElement("div");
                                headerDIV.className = "z-l-h";
                                headerDIV.innerHTML = data._title;
                                section.appendChild(headerDIV);
                            }
                        }
                    }
                    var sectionContent = document.createElement("div");
                    sectionContent.className = "z-l-s-c";
                    section.appendChild(sectionContent);
                    $.each(data._items, function(index, item) {
                        sectionContent.appendChild(funs.createRow(item, index, section));
                    });
                    if (funs.delegate) {
                        if ($.isFunction(funs.delegate.footerDOM)) {
                            var footerDIV = funs.delegate.footerDOM({
                                section : section
                            }, data);
                            footerDIV.className = footerDIV.className + " z-l-f";
                            section.appendChild(footerDIV);
                        }
                    }
                    return section;
                },
                createRow : function(data, row, section) {
                    var rowDOM;
                    if (funs.delegate && $.isFunction(funs.delegate.rowDOM)) {
                        rowDOM = funs.delegate.rowDOM({
                            section : section,
                            row : row
                        }, data);
                    } else {
                        rowDOM = document.createElement("div");
                        rowDOM.innerHTML = data._text;
                    }
                    rowDOM.className = rowDOM.className + " z-l-r";
                    return rowDOM;
                }
            };

            funs.init(obj);
            
            /**
             * @param section : the position to insert at
             * @param data : the data to insert
             * 
             * @return Zepto object
             */
            $self.appendSection = function(data){
                var adapter = listData.dataSource.adapter;
                var newData = $.ui.data[adapter.type + "Adapter"](data,adapter)[0];
                listData.data.push(newData);
                var sectionDOM = funs.createSection(newData);
                $self.append(sectionDOM);
                return $self;
            };
            /**
             * @param section : the position to insert at
             * @param data : the data to insert
             * 
             * @return Zepto object
             */
            $self.insertSectionAtSection = function(section,data){
                var $sections = $self.find(".z-l-s");
                if(section < 0 || section > $sections.length){
                    throw new Error("插入的位置不正确");
                } else {
                    var adapter = listData.dataSource.adapter;
                    var newData = $.ui.data[adapter.type + "Adapter"](data,adapter)[0];
                    listData.data.splice(section,0,newData);
                    var sectionDOM = funs.createSection(newData);
                    if($sections.length == 0){
                        $self.append(sectionDOM);
                    } else {
                        if(section == 0){
                            $($sections[0]).before(sectionDOM);
                        } else {
                            $($sections[section - 1]).after(sectionDOM);
                        }
                    }
                }
                return $self;
            };
            
            $self.removeSection = function(section){
                var $sections = $self.find(".z-l-s");
                if(section >= $sections.length || section < 0){
                    throw new Error("删除的位置不对");
                } else {
                    listData.data.splice(section,1);
                    $($sections[section]).remove();
                }
                return $self;
            };

            /**
             * @param indexPath : the position to insert at
             * @param data : the data to insert, must the same format with init data
             * 
             * @return Zepto Object
             */
            $self.insertAtIndexPath = function(indexPath, data) {
                var $sections = $self.find(".z-l-s");
                if (indexPath.section >= 0 && indexPath.section <= $sections.length - 1) {
                    var $rows = $($sections[indexPath.section]).find(".z-l-r");
                    if (indexPath.row < 0) {
                        throw new Error("插入的位置不正确");
                    } else if (indexPath.row <= $rows.length) {
                        var adapter = listData.dataSource.adapter;
                        var newData = $.ui.data[adapter.type+"Adapter"]([data], adapter);
                        var toInsertData = newData[0]._items;
                        var rowDOM;
                        var fn = null;
                        var fix = 0;
                        if($rows.length == 0){
                            listData.data[indexPath.section]._items.splice(0, 0, toInsertData[0]);
                            rowDOM = funs.createRow(toInsertData[0], 0, 0);
                            $($sections[indexPath.section]).find(".z-l-s-c").append(rowDOM);
                        } else {
                            indexPath.row == $rows.length ? ( fn = "after", fix = 1) : fn = "before";
                            for (var i = 0, l = toInsertData.length; i < l; i++) {
                                listData.data[indexPath.section]._items.splice(indexPath.row + i, 0, toInsertData[i]);
                                rowDOM = funs.createRow(toInsertData[i], indexPath.row + i, indexPath.section);
                                $($rows[indexPath.row - fix])[fn](rowDOM);
                            }
                        }
                    } else {
                        throw new Error("插入的位置不正确");
                    }
                }
                return $self;
            };

            
            /**
             * @param indexPath : the position to remove
             * 
             * @return Zepto Object
             */
            $self.removeAtIndexPath = function(indexPath) {
                var sectionData = listData.data[indexPath.section];
                var $sections;
                var rowData;
                var $rows;
                if (sectionData) {
                    rowData = sectionData._items[indexPath.row];
                    if (rowData) {
                        sectionData._items.splice(indexPath.row, 1);
                        $sections = $self.find(".z-l-s");
                        $rows = $($sections[indexPath.section]).find(".z-l-r");
                        $($rows[indexPath.row]).remove();
                    }
                }
                return $self;
            };

            $self.updateAtIndexPath = function(indexPath, data) {
                return $self;
            };

            /**
             * recreate the ui with new dataSource
             * 
             * @return Zepto Object
             */
            $self.reset = function(dataSource) {
                $self.empty();
                listData.dataSource = dataSource;
                funs.beginData();
                return $self;
            };

            return $self;
        }
    })
})(Zepto);