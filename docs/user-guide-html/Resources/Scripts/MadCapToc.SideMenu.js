/// <reference path="../../Scripts/MadCapGlobal.js" />
/// <reference path="../../Scripts/MadCapUtilities.js" />
/// <reference path="../../Scripts/MadCapDom.js" />
/// <reference path="MadCapHelpSystem.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */


(function () {

    var TocPane = MadCap.WebHelp.TocPane;

    TocPane.prototype.TocNodeMenuCallback = function (node, el, toc, OnCompleteFunc) {
        if (this._IsContextSensitive) {
            if (node) {
                this.LoadTocMenu(node, el, this._MaxDepth, OnCompleteFunc);
            } else {
                $(el).remove();

                if (OnCompleteFunc != null)
                    OnCompleteFunc();
            }
        } else {
            this.LoadTocMenuFromRoot(toc.tree, node, el, this._MaxDepth, OnCompleteFunc);
        }
    }

    TocPane.prototype.LoadTocMenuFromRoot = function (rootNode, currNode, el, depth, OnCompleteFunc) {
        if (rootNode.n && depth != 0) {
            var loaded = 0;
            var length = rootNode.n.length;

            if (length == 0) {
                if (OnCompleteFunc != null)
                    OnCompleteFunc();
            }

            depth--;
            for (var i = 0; i < length; i++) {
                var childNode = rootNode.n[i];
                var $li = $('<li/>');
                el.append($li);
                var self = this;
                this.LoadTocNode(childNode, $li, function (workingNode) {
                    var $liChild = self._NodeElMap[self.GetNodeHash(workingNode)];
                    if (workingNode == currNode) {
                        self.SetTocMenuItemSelected($liChild);
                    }
                    if (workingNode.n) {
                        var $ul = $('<ul/>');
                        $ul.attr("class", "sub-menu");
                        $liChild.append($ul);
                        $liChild.attr("class", "has-children");
                        self.LoadTocMenuFromRoot(workingNode, currNode, $ul, depth, function () {
                            loaded++;
                            if (loaded == length) {
                                if (OnCompleteFunc != null)
                                    OnCompleteFunc();
                            }
                        });
                    } else {
                        loaded++;
                        if (loaded == length) {
                            if (OnCompleteFunc != null)
                                OnCompleteFunc();
                        }
                    }

                });
            }
        }
    }

    TocPane.prototype.LoadTocMenu = function (node, el, depth, OnCompleteFunc) {
        if (this._IncludeParent && node.parent.c !== undefined) {
            var $li = $('<li/>');
            el.append($li);
            var self = this;
            this.LoadTocNode(node.parent, $li, function () {
                var $ul = $('<ul/>');
                $li.append($ul);
                $li.attr("class", "has-children");
                $ul.attr("class", "sub-menu");
                if (self._IncludeSiblings) {
                    self.LoadTocMenuSiblings(node, $ul, depth, OnCompleteFunc);
                } else {
                    self.LoadTocSelectedMenu(node, $ul, depth, OnCompleteFunc);
                }
            });
        } else if (this._IncludeSiblings) {
            this.LoadTocMenuSiblings(node, el, depth, OnCompleteFunc);
        } else {
            this.LoadTocSelectedMenu(node, el, depth, OnCompleteFunc);
        }
    }

    TocPane.prototype.LoadTocSelectedMenu = function (node, el, depth, OnCompleteFunc) {
        var $li = $('<li/>');
        el.append($li);
        var self = this;
        this.LoadTocNode(node, $li, function () {
            self.SetTocMenuItemSelected($li);
            self.AddTocMenuChildren(node, $li, depth, OnCompleteFunc);
        });
    }

    TocPane.prototype.LoadTocMenuSiblings = function (node, el, depth, OnCompleteFunc) {
        var length = node.parent.n.length;
        var loaded = 0;
        for (var i = 0; i < node.parent.n.length; i++) {
            var childNode = node.parent.n[i];
            var $li = $('<li/>');
            el.append($li);

            var self = this;
            this.LoadTocNode(childNode, $li, function (workingNode) {
                if (workingNode == node) {
                    var $liChild = self._NodeElMap[self.GetNodeHash(node)];
                    self.SetTocMenuItemSelected($liChild);
                    self.AddTocMenuChildren(node, $liChild, depth, function () {
                        loaded++;
                        if (loaded == length) {
                            if (OnCompleteFunc)
                                OnCompleteFunc();
                        }
                    });
                } else {
                    loaded++;
                    if (loaded == length) {
                        if (OnCompleteFunc)
                            OnCompleteFunc();
                    }
                }
            });
        }
    }

    TocPane.prototype.AddTocMenuChildren = function (node, el, depth, OnCompleteFunc) {
        if (this._IncludeChildren && node.n) {
            depth--;
            var $ul = $('<ul/>');
            el.append($ul);
            el.attr("class", "has-children");
            this.LoadTocMenuChildren(node, $ul, depth, OnCompleteFunc);
            $ul.attr("class", "sub-menu");
        } else {
            if (OnCompleteFunc)
                OnCompleteFunc();
        }
    }

    TocPane.prototype.LoadTocMenuChildren = function (node, el, depth, OnCompleteFunc) {
        var length = node.n.length;
        var loaded = 0;
        if (length == 0) {
            if (OnCompleteFunc)
                OnCompleteFunc();
        }

        for (var i = 0; i < length; i++) {
            var childNode = node.n[i];
            var $li = $('<li/>');
            el.append($li);

            var self = this;
            this.LoadTocNode(childNode, $li, function (workingNode) {
                if (depth != 0) {
                    var $liChild = self._NodeElMap[self.GetNodeHash(workingNode)];
                    self.AddTocMenuChildren(workingNode, $liChild, depth, function () {
                        loaded++;
                        if (loaded == length) {
                            if (OnCompleteFunc)
                                OnCompleteFunc();
                        }
                    });
                } else {
                    loaded++;
                    if (loaded == length) {
                        if (OnCompleteFunc)
                            OnCompleteFunc();
                    }
                }
            });
        }
    }

    TocPane.prototype.SetTocMenuItemSelected = function (el) {
        var $a = $(el).find("a");
        $a.addClass("selected");
    }

})();