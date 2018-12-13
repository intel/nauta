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

    MadCap.WebHelp.MiniToc = function (runtimeFileType, helpSystem, root) {
        var mSelf = this;
        this._Init = false;
        this._RuntimeFileType = runtimeFileType;
        this._Root = root;
        this._HelpSystem = helpSystem;
        this._TocFile = this._RuntimeFileType == "Toc" ? this._HelpSystem.GetTocFile() : this._HelpSystem.GetBrowseSequenceFile();
        this._TocType = null;
        this._TocPath = null;
        this._TocHref = null;
    }

    var MiniToc = MadCap.WebHelp.MiniToc;

    MiniToc.prototype.Init = function () {
        var $root = $(this._Root);

        this._Depth = $root.attr("data-mc-depth") || "3";
        this._LinkClass = "MiniTOC";


        var mSelf = this;

        $root.attr("data-mc-chunk", "Data/" + this._RuntimeFileType + ".xml");

        this.CreateToc(this._Root, function () {
            mSelf._Init = true;
        });
    };

    MiniToc.prototype.CreateToc = function (root, OnCompleteFunc) {
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
                            self.LoadTocMiniTocChildren(node, $root, 1);

                            if (OnCompleteFunc != null)
                                OnCompleteFunc();
                        }
                    });
                } else {
                    self._HelpSystem.FindTocNode(null, self._TocHref, function (node) {
                        if (node) {
                            self.LoadTocMiniTocChildren(node, $root, 1);

                            if (OnCompleteFunc != null)
                                OnCompleteFunc();
                        }
                    });
                }
            });

        });
    };

    MiniToc.prototype.LoadTocMiniTocChildren = function (node, el, currentLevel) {
        if (currentLevel <= this._Depth) {
            if (node.n) {
                for (var i = 0; i < node.n.length; i++) {
                    var childNode = node.n[i];
                    this.LoadTocMiniToc(childNode, el, currentLevel);
                }
            }
        }
    }

    MiniToc.prototype.LoadTocMiniToc = function (node, el, currentLevel) {
        if (node.i !== undefined) {
            var tocEntry = node.toc.entries[node.i];
            if (tocEntry) {
                var appendTocPath = this._HelpSystem.TopNavTocPath;
                var href = this._HelpSystem.GetTocEntryHref(node, 'Toc', false, appendTocPath);
                
                if (href) {
                    var linkClassLevel = this._LinkClass + currentLevel;
                    var $p = $('<p/>');
                    var $a = $('<a/>');

                    $a.addClass(linkClassLevel);
                    $a.attr('href', MadCap.Utilities.EncodeHtml(href));
                    $a.text(tocEntry.title);
                    $p.append($a);

                    $p.addClass(linkClassLevel + "_0");
                    el.append($p);
                }
            }
        }

        currentLevel++;
        this.LoadTocMiniTocChildren(node, el, currentLevel);
    }

})();