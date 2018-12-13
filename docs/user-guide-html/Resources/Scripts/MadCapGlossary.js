/// <reference path="../../Scripts/jquery.js" />
/// <reference path="../../Scripts/require.js" />
/// <reference path="../../Scripts/MadCapGlobal.js" />
/// <reference path="../../Scripts/MadCapUtilities.js" />
/// <reference path="../../Scripts/MadCapDom.js" />
/// <reference path="../../Scripts/MadCapXhr.js" />
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

    MadCap.WebHelp.GlossaryPane = function (helpSystem) {
        var mSelf = this;
        this._Init = false;
        this._ContainerEl = null;
        this._HelpSystem = helpSystem;

        MadCap.Utilities.CrossFrame.AddMessageHandler(this.OnMessage, this);

        this.TreeNode_Click = function (e) {
            var li = MadCap.Dom.GetAncestorNodeByTagName(e.target, 'li');

            if (li == null)
                return;

            var $li = $(li);
            var $a = $('a', $li);
            var term = $a.text();
            var c = $li.attr('data-chunk');
            var chunkPath = mSelf._HelpSystem.Glossary.chunks[c].path;
            var helpSystemRoot = new MadCap.Utilities.Url(chunkPath).ToFolder().ToFolder();

            MadCap.Utilities.PreventDefault(e);

            // Load chunk
            require([chunkPath], function (chunk) {
                var entry = chunk[term];

                $('.tree-node-selected', mSelf._ContainerEl).removeClass('tree-node-selected');
                $li.addClass('tree-node-selected');

                var $term = $('.GlossaryPageTerm', li);

                // Load definition (if exists)
                if (!MadCap.String.IsNullOrEmpty(entry.d) && !$term.hasClass('MCDropDownHead')) {
                    $term.addClass('MCDropDownHead MCDropDownHotSpot');

                    var $def = $('<div/>');

                    $def.addClass('GlossaryPageDefinition MCDropDownBody');
                    $def.append(entry.d);

                    $li.addClass('MCDropDown');
                    $li.append($term);
                    $li.append($def);

                    var dropDown = new MadCap.TextEffects.DropDownControl($li[0]);
                    dropDown.Init(false);
                    dropDown.Open(true);
                }

                // Load link (if exists)
                if (!MadCap.String.IsNullOrEmpty(entry.l)) {
                    var href = $a.attr('href');

                    if (MadCap.String.IsNullOrEmpty(href)) {
                        var path = helpSystemRoot.CombinePath(entry.l).ToRelative(mSelf._HelpSystem.GetContentPath()).FullPath;
                        href = encodeURI(path);

                        $a.attr('href', href);
                    }

                    document.location.href = '#' + href;
                }
                else {
                    // Expand/collapse node
                    if ($li.hasClass('tree-node-expanded')) {
                        $li.removeClass('tree-node-expanded');
                        $li.addClass('tree-node-collapsed');
                    }
                    else if ($li.hasClass('tree-node-collapsed')) {
                        $li.removeClass('tree-node-collapsed');
                        $li.addClass('tree-node-expanded');

                        // If expanding the last node, scroll list to bottom
                        if ($('li', $li.parent()).last()[0] == $li[0]) {
                            var $container = $(mSelf._ContainerEl);
                            $container.animate({ scrollTop: $container[0].scrollHeight }, 500);
                        }
                    }
                }
            });
        };

        this.Search = function () {
            var query = this.value.toLowerCase();

            mSelf._Terms.each(function () {
                var $term = $(this);
                var entry = $term.closest("li");
                var found = mSelf._HelpSystem.GlossaryPartialWordSearch ?
                    $term.text().toLowerCase().indexOf(query) != -1 :
                    MadCap.String.StartsWith($term.text(), query, false);

                entry.css('display', found ? 'block' : 'none');

                // only highlight if partial word search
                if (mSelf._HelpSystem.GlossaryPartialWordSearch) {
                    $term.removeHighlight('highlightGlossary');

                    if (found) {
                        $term.highlight(query, 'highlightGlossary');
                    }
                }
            });
        };
    };

    var GlossaryPane = MadCap.WebHelp.GlossaryPane;

    GlossaryPane.prototype.OnMessage = function (message, dataValues, responseData) {
        var returnData = { Handled: false, FireResponse: true };

        return returnData;
    };

    GlossaryPane.prototype.Init = function (containerEl, OnCompleteFunc) {
        if (this._Init) {
            if (OnCompleteFunc != null)
                OnCompleteFunc();

            return;
        }

        var mSelf = this;

        mSelf._ContainerEl = containerEl;

        mSelf._HelpSystem.LoadGlossary(function (glossary, args) {
            var $ul = $('<ul/>');
            $ul.addClass('tree');
            var sortedTerms = glossary.terms.sort(function (a, b) {
                return MadCap.String.LocaleCompare(a.s || a.t, b.s || b.t, mSelf._HelpSystem.LanguageCode);
            });
            for (var i = 0; i < sortedTerms.length; i++) {
                var entry = sortedTerms[i];

                var $li = $('<li/>');
                $li.addClass('GlossaryPageEntry tree-node tree-node-collapsed');
                $li.attr('data-chunk', entry.c);

                var $term = $('<div/>');
                $term.addClass('GlossaryPageTerm');
                $term.append('<span class="label"><a>' + entry.t + '</a></span>');

                $li.append($term);

                $ul.append($li);
            }

            var $container = $(mSelf._ContainerEl);
            $container.click(mSelf.TreeNode_Click);
            $container.append($ul);

            var $search = $('#search-glossary');
            $search.bind('keyup', mSelf.Search);
            $('#responsive-search-glossary').bind('keyup', mSelf.Search);

            mSelf._Terms = $('.GlossaryPageTerm a', mSelf._ContainerEl);

            mSelf._Init = true;

            if (OnCompleteFunc != null)
                OnCompleteFunc();
        }, null);
    };

    GlossaryPane.prototype._SelectNode = function (node) {
        $(".tree-node-selected", this._ContainerEl).removeClass("tree-node-selected");
        $(node).addClass("tree-node-selected");
    };
})();
