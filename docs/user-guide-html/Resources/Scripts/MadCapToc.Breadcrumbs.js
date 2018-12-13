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
    MadCap.WebHelp = MadCap.CreateNamespace("WebHelp");

    var previewMode = window.external && window.external.attached && window.external.attached(); // Previewing style changes in the skin editor

    MadCap.WebHelp.Breadcrumbs = function (runtimeFileType, helpSystem, root, canSync) {
        var mSelf = this;
        this._Init = false;
        this._RuntimeFileType = runtimeFileType;
        this._Root = root;
        this._CanSync = canSync;
        this._HelpSystem = helpSystem;
        this._TocFile = this._RuntimeFileType == "Toc" ? this._HelpSystem.GetTocFile() : this._HelpSystem.GetBrowseSequenceFile();
        this._TocType = null;
        this._TocPath = null;
        this._TocHref = null;
    }

    var Breadcrumbs = MadCap.WebHelp.Breadcrumbs;

    Breadcrumbs.prototype.Init = function () {
        var $root = $(this._Root);

        this._MaxLevel = $root.attr("data-mc-breadcrumbs-count") || "3";
        this._Divider = $root.attr("data-mc-breadcrumbs-divider") || " > ";
        this._LinkClass = "MCBreadcrumbsLink";
        this._SelfClass = "MCBreadcrumbsSelf";
        this._DividerClass = "MCBreadcrumbsDivider";


        var mSelf = this;

        $root.attr("data-mc-chunk", "Data/" + this._RuntimeFileType + ".xml");

        this.CreateToc(this._Root, function () {
            mSelf._Init = true;
        });
    };

    Breadcrumbs.prototype.CreateToc = function (root, OnCompleteFunc) {
        var hasToc = true;

        if (this._RuntimeFileType == "Toc")
            hasToc = this._HelpSystem.HasToc;
        else
            hasToc = this._HelpSystem.HasBrowseSequences;

        if (!hasToc) {
            if (OnCompleteFunc != null)
                OnCompleteFunc();

            return;
        }

        var self = this;

        self._HelpSystem.LoadToc([this._RuntimeFileType, null]).then(function (toc) {
            var $root = $(root);

            var tocDeferred = [];
            for (var i = 0; i < toc.chunks.length; i++) {
                if (!toc.chunks[i].loaded)
                    tocDeferred.push(self._HelpSystem.LoadTocChunk(toc, i));
            }

            // finish loading all tocChunks
            $.when.apply(this, tocDeferred).done(function () {
                // search for start node in toc
                if (self._TocType) {
                    self._HelpSystem.FindNode(self._TocType, self._TocPath, self._TocHref, function (node) {
                        if (node) {
                            self.LoadTocBreadcrumbs(node, $root);

                            if (OnCompleteFunc != null)
                                OnCompleteFunc();
                        }
                    });
                } else {
                    self._HelpSystem.FindTocNode(null, self._TocHref, function (node) {
                        if (node) {
                            self.LoadTocBreadcrumbs(node, $root);

                            if (OnCompleteFunc != null)
                                OnCompleteFunc();
                        }
                    });
                }
            });
        });
    };

    Breadcrumbs.prototype.LoadTocBreadcrumbs = function (node, el) {
        var tocNodes = [];
        var workingNode = node.parent;
        var nodeDepth = this._HelpSystem.NodeDepth(node);
        tocNodes.push(node);
        nodeDepth -= 2;

        if (workingNode) {
            for (var i = nodeDepth; i >= 0; i--) {
                if ((this._MaxLevel < nodeDepth && i <= this._MaxLevel) ||
                     this._MaxLevel >= nodeDepth) {

                    tocNodes.unshift(workingNode);
                }

                if (!workingNode.parent) {
                    break;
                }

                workingNode = workingNode.parent;
            }
        }

        for (var k = 0; k < tocNodes.length; k++) {
            var tocNode = tocNodes[k];
            if (tocNode.i !== undefined) {
                var tocEntry = tocNode.toc.entries[tocNode.i];
                if (tocEntry) {
                    if (tocNode == node) {
                        var $nodeSpan = $('<span/>');
                        $nodeSpan.text(tocEntry.title);
                        $nodeSpan.addClass(this._SelfClass);
                        el.append($nodeSpan);
                    } else if (tocNode.n) {
                        var $a = $('<a/>');
                        var $dividerSpan = $('<span/>');
                        var appendTocPath = this._HelpSystem.TopNavTocPath;
                        var href = this._HelpSystem.GetTocEntryHref(tocNode, 'Toc', false, appendTocPath);

                        if (href) {
                            $a.attr('href', MadCap.Utilities.EncodeHtml(href));
                            $a.text(tocEntry.title);
                            $a.addClass(this._LinkClass);
                            el.append($a);
                        } else {
                            var $span = $('<span/>');
                            $span.text(tocEntry.title);
                            $span.addClass(this._SelfClass);
                            el.append($span);
                        }

                        $dividerSpan.text(this._Divider);
                        $dividerSpan.addClass(this._DividerClass);
                        el.append($dividerSpan);
                    }
                }
            }
        }
    }

})();