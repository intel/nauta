/// <reference path="../../Scripts/jquery.js" />
/// <reference path="../../Scripts/MadCapGlobal.js" />
/// <reference path="../../Scripts/MadCapUtilities.js" />
/// <reference path="../../Scripts/MadCapDom.js" />
/// <reference path="../../Scripts/MadCapXhr.js" />
/// <reference path="../../Scripts/MadCapTextEffects.js" />
/// <reference path="MadCapHelpSystem.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */


(function () {
    if (!MadCap.Utilities.HasRuntimeFileType("TriPane"))
        return;

    MadCap.WebHelp = MadCap.CreateNamespace("WebHelp");

    MadCap.WebHelp.IndexPane = function (helpSystem) {
        var mSelf = this;
        this._Init = false;
        this._ContainerEl = null;
        this._HelpSystem = helpSystem;
        this._EntryHeight = -1;
        this._IndexEntryCount = 0;
        this._IndexEntries = Object.create(null);
        this._IndexDivs = new Array();
        this._XmlDoc = null;
        this._Chunks = null;
        this._AlphaMap = new MadCap.Utilities.Dictionary();
        this._LiCached = null;
        this._SeePrefix = null;
        this._SeeAlsoPrefix = null;

        this.GetPath = function (root, url) {
            return MadCap.String.IsNullOrEmpty(root) ?
                new MadCap.Utilities.Url(url).ToRelative('/Content/').FullPath :
                '../' + new MadCap.Utilities.Url(root + url).FullPath;
        }

        this.LoadRootEntry = function (li, OnCompleteFunc) {
            var $li = $(li);
            var rootEntry = $li.data('entry');

            mSelf._HelpSystem.LoadRootIndexEntry(rootEntry, function (entry) {
                // Load sub entries
                if (entry.e && !entry.childrenLoaded) {
                    var $ul = $('<ul/>');
                    $ul.addClass('tree inner');

                    mSelf.LoadEntries($ul, entry.e);

                    $li.append($ul);

                    mSelf._Terms = mSelf._Terms.add($('.IndexEntry a', $ul));
                }

                entry.childrenLoaded = true;
                $li.data('entry', entry);

                if (OnCompleteFunc)
                    OnCompleteFunc(entry, $li);
            });
        }

        this.LoadEntries = function (el, entries) {
            var self = this;

            if (!$.isArray(entries)) { // if unordered, sort
                var sortedEntries = [];

                $.each(entries, function (term, entry) {
                    if (!entry.t)
                        entry.t = term;
                    sortedEntries.push(entry);
                });
                sortedEntries.sort(function (entry1, entry2) {
                    var term1 = (entry1.s || entry1.t).toLowerCase();
                    var term2 = (entry2.s || entry2.t).toLowerCase();

                    return MadCap.String.LocaleCompare(term1, term2, mSelf._HelpSystem.LanguageCode);
                });

                entries = sortedEntries;
            }

            $.each(entries, function (index, entry) {
                var $li = $('<li/>');
                $li.addClass('IndexEntry tree-node tree-node-collapsed');

                var term = entry.t;
                var see = entry.r == 'See';
                var seeAlso = entry.r == 'SeeAlso';

                var $term = $('<div/>');
                $term.addClass('IndexTerm');

                var $label = $('<span/>').addClass('label');
                $term.append($label);

                var appendTerm = true;

                if (see) {
                    term = self._SeePrefix + ': ' + entry.f; // reference link
                    $term.addClass('see');
                    entry.seeAlsoLinks = [entry.f];
                }
                else if (seeAlso) {
                    term = self._SeeAlsoPrefix + ': ';
                    entry.seeAlsoLinks = [];

                    seeAlsoLinks = entry.f.split('; ');
                    if (seeAlsoLinks.length > 1) {
                        var $a = $('<a/>').text(term);
                        $label.append($a);

                        for (var i = 0; i < seeAlsoLinks.length; i++) {
                            var seeAlsoLink = seeAlsoLinks[i];

                            var $seeAlsoLink = $('<a/>').addClass('seeAlsoLink').text(seeAlsoLink);
                            $label.append($seeAlsoLink);

                            entry.seeAlsoLinks.push(seeAlsoLink);

                            if (i < seeAlsoLinks.length - 1)
                                $label.append('; ');
                        }

                        appendTerm = false;
                    }
                    else {
                        term += entry.f;
                        entry.seeAlsoLinks.push(entry.f);
                    }

                    $term.addClass('see-also');
                }

                if (appendTerm) {
                    var $a = $('<a/>').text(term);
                    $label.append($a);
                }

                $li.append($term);

                entry.isRoot = typeof entry.$ !== 'undefined';

                if (entry.e) {
                    var $ul = $('<ul/>');
                    $ul.addClass('tree inner');

                    self.LoadEntries($ul, entry.e);

                    $li.append($ul);
                }
                else if (entry.$ === 1 || !entry.isRoot) {
                    $li.removeClass("tree-node-collapsed");
                    $li.addClass("tree-node-leaf");
                }

                el.append($li);

                entry.el = $li[0];

                $li.data('entry', entry);

                if (!see && !seeAlso) {
                    if (typeof self._IndexEntries[term] == 'undefined') {
                        self._IndexEntries[term] = [entry];
                    }
                    else {
                        self._IndexEntries[term].push(entry);
                    }
                }
            });
        };

        this.FindEntry = function (terms, onCompleteFunc) {
            mSelf._HelpSystem.FindIndexEntry(terms, function (rootEntry, entry) {
                if (!entry)
                    return;

                mSelf.LoadRootEntry(rootEntry.el, function () {
                    if (onCompleteFunc)
                        onCompleteFunc(entry);
                });
            });
        }

        this.SelectEntry = function (e, entry, $li, $this, expand) {
            $('.tree-node-selected', mSelf._ContainerEl).removeClass('tree-node-selected');
            $li.addClass('tree-node-selected');

            if (!entry) {
                $('body').removeClass('active');
                return;
            }

            MadCap.TextEffects.RemoveLinkListTrees();

            var top = e.pageY - $this.offset().top;
            var left = e.pageX - $this.offset().left;
            var isWeb = !this._HelpSystem.IsTabletLayout() || !this._HelpSystem.IsResponsive;

            if (entry.r && !expand) {
                var index = $('.seeAlsoLink', $li).index(e.target);
                var seeLink = entry.seeAlsoLinks[0];

                if (index >= 0)
                    seeLink = entry.seeAlsoLinks[index];

                seeLink = seeLink.replace(', ', ':');

                this.FindEntry(seeLink, function (entry) {
                    $li = $(entry.el);
                    $container = isWeb ? $(mSelf._ContainerEl).parent() : $("#navigation");

                    mSelf._UnhideNode($li[0]);
                    mSelf.SelectEntry(e, entry, $li, $this, true);

                    $container.animate({ scrollTop: $container.scrollTop() + $li.offset().top - $container.offset().top });
                });

                return;
            }
            else if (entry.linkList && entry.linkList.length > 1 && !expand) {
                if (isWeb)
                    MadCap.TextEffects.CreateLinkListPopup(entry.linkList, mSelf._ContainerEl, top, left, $this, '#');
                else {
                    MadCap.TextEffects.CreateLinkListTree(entry.linkList, $li, $this, '#', function (e) {
                        mSelf.TreeNode_Click(e);
                        MadCap.TextEffects.Item_Click.call($(e.currentTarget), [e]);
                    });
                }

                MadCap.Utilities.PreventDefault(e);
                e.stopPropagation();
            }
            else if (entry.linkList && entry.linkList.length == 1) {
                $('body').removeClass('active');
                document.location.href = '#' + entry.linkList[0].Link;
            }

            if ($li.hasClass("tree-node-expanded") && !expand) {
                $li.removeClass("tree-node-expanded");
                $li.addClass("tree-node-collapsed");
            }
            else if ($li.hasClass("tree-node-collapsed")) {
                $li.removeClass("tree-node-collapsed");
                $li.addClass("tree-node-expanded");
            }
        }

        this.TreeNode_Click = function (e) {
            var li = MadCap.Dom.GetAncestorNodeByTagName(e.target, "li");

            if (li == null)
                return;

            if ($(e.target).closest('.link-list-popup').length > 0)
                return;

            var $this = $(this);
            var $li = $(li);

            MadCap.Utilities.PreventDefault(e);

            var entry = $li.data('entry');

            if (!$li.hasClass("IndexEntryLink") && (!entry || entry.isRoot)) {
                mSelf.LoadRootEntry(li, function (entry, $li) {
                    mSelf.SelectEntry(e, entry, $li, $this);
                });
            }
            else {
                mSelf.SelectEntry(e, entry, $li, $this);
            }
        };

        this.Search = function () {
            var query = this.value.toLowerCase();

            mSelf._Terms.each(function () {
                var $term = $(this);
                var found = mSelf._HelpSystem.IndexPartialWordSearch ?
                    $term.text().toLowerCase().indexOf(query) != -1 :
                    MadCap.String.StartsWith($term.text(), query, false);

                $term.css('display', found ? 'block' : 'none');

                // only highlight if partial word search
                if (mSelf._HelpSystem.IndexPartialWordSearch) {
                    $term.removeHighlight('highlightIndex');

                    if (found) {
                        $term.highlight(query, 'highlightIndex');
                    }
                }
            });
        };
    };

    var IndexPane = MadCap.WebHelp.IndexPane;

    IndexPane.prototype.Init = function (containerEl, OnCompleteFunc) {
        if (this._Init) {
            if (OnCompleteFunc != null)
                OnCompleteFunc();

            return;
        }

        var self = this;

        self._ContainerEl = containerEl;

        var $containerParent = $(this._ContainerEl.parentNode);
        this._SeePrefix = $containerParent.attr("data-see-prefix") || "See";
        this._SeeAlsoPrefix = $containerParent.attr("data-see-also-prefix") || "See Also";

        self._HelpSystem.LoadIndex(function (index, args) {
            var $ul = $('<ul/>');
            $ul.addClass('tree');

            self.LoadEntries($ul, index.terms);

            var $container = $(self._ContainerEl);
            $container.click(self.TreeNode_Click);
            $container.append($ul);

            var $search = $('#search-index');
            $search.bind('keyup', self.Search);
            $('#responsive-search-index').bind('keyup', self.Search);

            self._Terms = $('.IndexEntry a', this._ContainerEl);
            self._Init = true;

            if (OnCompleteFunc != null)
                OnCompleteFunc();
        }, null);
    };

    IndexPane.prototype._UnhideNode = function (node) {
        var parentNode = MadCap.Dom.GetAncestorNodeByTagName(node, "li", this._ContainerEl);

        while (parentNode != null) {
            var $parentNode = $(parentNode);
            $parentNode.removeClass("tree-node-collapsed");
            $parentNode.addClass("tree-node-expanded");

            parentNode = MadCap.Dom.GetAncestorNodeByTagName(parentNode, "li", this._ContainerEl);
        }
    };
})();
