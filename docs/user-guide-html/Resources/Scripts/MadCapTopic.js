/// <reference path="../../Scripts/jquery.js" />
/// <reference path="../../Scripts/MadCapGlobal.js" />
/// <reference path="../../Scripts/MadCapUtilities.js" />
/// <reference path="../../Scripts/MadCapDom.js" />
/// <reference path="../../Scripts/MadCapXhr.js" />
/// <reference path="../../Scripts/MadCapFeedback.js" />
/// <reference path="../../Scripts/MadCapEffects.js" />
/// <reference path="../Scripts/MadCapHelpSystem.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */

(function () {
    /* Note: Check changeset 44920: [Flare 8] 
    Fixed CSH bug where MadCapAll.js was loading code from MadCapTopic.js into non-topic files. 
    Needed to add a runtime-file-type check. This was breaking the CSH tester in Chrome because the MadCapTopic.js 
    code would attempt to load the Help system which would try to load HelpSystem.xml in the current directory. The 
    CSH tester is copied to the temp folder so this file doesn't exist. This only affected Chrome because it used HelpSystem.js 
    rather than .xml. The other browsers catch the missing XML file and continue. */
    if (!MadCap.Utilities.HasRuntimeFileType("Topic"))
        return;

    MadCap.CreateNamespace("Topic");

    var Topic = MadCap.Topic;
    var TextEffects = MadCap.TextEffects;
    var isTriPane = MadCap.Utilities.HasRuntimeFileType("TriPane");

    // Statics

    Topic.Expand = function (el) {
        var control = new TextEffects.ExpandingControl(el.parentNode);

        control.Toggle();
    };

    Topic.DropDown = function (el) {
        var control = new TextEffects.DropDownControl(el.parentNode.parentNode);

        control.Toggle();
    };

    Topic.Toggle = function (el) {
        var control = new TextEffects.TogglerControl(el);

        control.Toggle();
    };

    Topic.ThumbPopup_Click = function (e) {
        var popupEl = Topic.ShowThumbnailPopup(e, this, "click");

        if (e.preventDefault)
            e.preventDefault(); // prevents link from navigating
    };

    Topic.ThumbPopup_Hover = function (e) {
        var popupEl = Topic.ShowThumbnailPopup(e, this, "mouseleave");
    };

    Topic.ShowThumbnailPopup = function (e, aEl, showType) {
        var CONTAINER_MARGIN = 10;
        var CONTAINER_BORDER_WIDTH = 1;
        var IMAGE_PADDING = 10;
        var thumbEl = $(aEl).children("img")[0];
        var fullImageWidth = parseInt(MadCap.Dom.Dataset(thumbEl, "mcWidth"));
        var fullImageHeight = parseInt(MadCap.Dom.Dataset(thumbEl, "mcHeight"));
        var hwRatio = fullImageHeight / fullImageWidth;
        var maxWidth = document.documentElement.clientWidth - ((CONTAINER_MARGIN + CONTAINER_BORDER_WIDTH + IMAGE_PADDING) * 2);
        var maxHeight = document.documentElement.clientHeight - ((CONTAINER_MARGIN + CONTAINER_BORDER_WIDTH + IMAGE_PADDING) * 2);

        if (fullImageHeight > maxHeight) {
            fullImageHeight = maxHeight;
            fullImageWidth = fullImageHeight / hwRatio;
        }

        if (fullImageWidth > maxWidth) {
            fullImageWidth = maxWidth;
            fullImageHeight = fullImageWidth * hwRatio;
        }

        //

        var documentUrl = new MadCap.Utilities.Url(document.location.href);

        var thumbTop = $(thumbEl).offset().top;
        var thumbLeft = $(thumbEl).offset().left;

        var fullImageSrc = MadCap.Dom.GetAttribute(aEl, "href");

        var fullImageAlt = MadCap.Dom.GetAttribute(aEl, "data-mc-popup-alt");
        var containerHeight = fullImageHeight + ((CONTAINER_BORDER_WIDTH + IMAGE_PADDING) * 2);
        var containerWidth = fullImageWidth + ((CONTAINER_BORDER_WIDTH + IMAGE_PADDING) * 2);
        var containerTop = (thumbTop + (thumbEl.offsetHeight / 2)) - (containerHeight / 2);
        var containerLeft = (thumbLeft + (thumbEl.offsetWidth / 2)) - (containerWidth / 2);

        // Keep within viewable area

        var scrollPosition = MadCap.Dom.GetScrollPosition();
        var clientTop = scrollPosition.Y;
        var clientBottom = clientTop + document.documentElement.clientHeight;
        var clientLeft = scrollPosition.X;
        var clientRight = clientLeft + document.documentElement.clientWidth;
        var minTop = clientTop + CONTAINER_MARGIN;
        var minLeft = clientLeft + CONTAINER_MARGIN;
        var maxBottom = clientBottom - CONTAINER_MARGIN;
        var maxRight = clientRight - CONTAINER_MARGIN;

        if (containerTop < minTop)
            containerTop = minTop;

        if (containerLeft < minLeft)
            containerLeft = minLeft;

        if (containerTop + containerHeight > maxBottom)
            containerTop = maxBottom - containerHeight;

        if (containerLeft + containerWidth > maxRight)
            containerLeft = maxRight - containerWidth;

        //

        if ($(".title-bar.sticky.is-stuck")) {
            if (containerTop < $(".title-bar.sticky.is-stuck").innerHeight()) {
                containerTop += $(".title-bar.sticky.is-stuck").innerHeight() - containerTop + CONTAINER_MARGIN;
            }
        }

        //

        var $containerEl = $("<div></div>");
        $containerEl.addClass("MCPopupContainer");

        var fullImageEl = document.createElement("img");
        $(fullImageEl).addClass("MCPopupFullImage");
        fullImageEl.setAttribute("src", fullImageSrc);
        fullImageEl.setAttribute("alt", fullImageAlt); // Fix for bug #46031 - HTML5 output
        fullImageEl.setAttribute("tabindex", "0");

        $containerEl.bind(showType, function () {
            MadCap.DEBUG.Log.AddLine(showType);
            $containerEl.animate(
            {
                top: topStart,
                left: leftStart
            }, 200, function () {
                $containerEl.remove();
            });

            $(fullImageEl).animate(
            {
                width: thumbEl.offsetWidth,
                height: thumbEl.offsetHeight
            }, 200);

            $(bgTintEl).animate(
            {
                opacity: 0
            }, 200, function () { MadCap.TextEffects.RemoveBackgroundTint(); });
        });

        $containerEl.bind("keydown", function (e) {
            var e = e || window.event;
            if (e.keyCode != 27 && e.keyCode != 13) // Escape and enter key support to close thumbnail popup
                return;

            $containerEl.remove();
            MadCap.TextEffects.RemoveBackgroundTint();
        });

        $containerEl.append(fullImageEl);
        document.body.appendChild($containerEl[0]);

        // Animate it

        var topStart = thumbTop - (CONTAINER_BORDER_WIDTH + IMAGE_PADDING);
        var leftStart = thumbLeft - (CONTAINER_BORDER_WIDTH + IMAGE_PADDING);

        if (MadCap.IsIBooks()) {
            $idealContainer = $(aEl).parentsUntil("body").last();
            fullImageWidth = $idealContainer[0].offsetWidth * 0.9;
            fullImageHeight = fullImageWidth * hwRatio;
            containerLeft = $idealContainer.offset().left;
        $containerEl.css({ top: topStart, left: leftStart }).animate(
        {
            top: containerTop,
               left: containerLeft,
               width: fullImageWidth,
               height: fullImageHeight
           }, 200);

        } else {

            $containerEl.css({ top: topStart, left: leftStart }).animate(
            {
                top: containerTop,
                left: containerLeft
        }, 200);
        }

        $(fullImageEl).css({ width: thumbEl.offsetWidth, height: thumbEl.offsetHeight }).animate(
        {
            width: fullImageWidth,
            height: fullImageHeight
        }, 200);

        // Add the background tint and animate it
        var bgTintEl = MadCap.TextEffects.AddBackgroundTint(null, document.body);

        $(bgTintEl).animate(
        {
            opacity: 0.5
        }, 200);

        fullImageEl.focus();
    };

    Topic.HelpControl_Click = function (e) {
        var aEl = this;

        Topic.GetHelpControlLinks(this, function (topics) {
            // Make the links relative to the current topic
            var url = new MadCap.Utilities.Url(document.location.href);

            for (var i = topics.length - 1; i >= 0; i--) {
                var topic = topics[i];
                topic.Title = "t" in topic ? topic.t : "Title" in topic ? topic.Title : null;

                var link = "Url" in topic ? topic.Url : "Link" in topic ? topic.Link : null;
                if (link != null && typeof link != "string") {
                    if (link.FullPath == url.FullPath)
                        topics.Remove(i);

                    link = link.ToRelative(url);

                    topic.Link = link.FullPath;
                }
            }

            // Sort them by title
            if (!$(aEl).hasClass("MCHelpControl-Related")) {
                topics.sort(function (a, b) {
                    return a.Title.localeCompare(b.Title);
                });
            }

            // Remove duplicates
            var map = new MadCap.Utilities.Dictionary();

            for (var i = topics.length - 1; i >= 0; i--) {
                var currTopic = topics[i];
                var link = currTopic.Link;

                if (map.GetItem(link)) {
                    topics.Remove(i);
                    continue;
                }

                map.Add(currTopic.Link, true);
            }


            // Create the list
            TextEffects.CreateLinkListPopup(topics, document.body, e.pageY, e.pageX, aEl);

        }, null);

        e.preventDefault();
        e.stopPropagation();
    };

    Topic.GetHelpControlLinks = function (node, callbackFunc) {
        var links = new Array();
        var $node = $(node);

        if (_HelpSystem && !_HelpSystem.InPreviewMode) {
            if (IsEmbeddedTopic()) {
                //                if (_HelpSystem.IsMerged()) {
                var indexKeywords = $node.attr("data-mc-keywords");

                if (indexKeywords != null) {
                    if (indexKeywords == "")
                        callbackFunc(links);

                    var keywords = indexKeywords.split(";");

                    MadCap.Utilities.AsyncForeach(keywords, function (keyword, callback) {
                        _HelpSystem.FindIndexEntry(keyword, function (rootEntry, entry) {
                            if (entry != null && entry.linkList) {
                                links = links.concat(entry.linkList);
                            }

                            callback();
                        });
                    },
                        function () {
                            callbackFunc(_HelpSystem.SortLinkList(links));
                        });

                    return;
                }
                else {
                    var concepts = $node.attr("data-mc-concepts");

                    if (concepts != null) {
                        _HelpSystem.GetConceptsLinks(concepts).then(callbackFunc);

                        return;
                    }
                }
            }
        }

        var topics = $node.attr("data-mc-topics");

        if (topics != null) {
            topicPairs = topics.split("||");

            if (topicPairs == "") {
                callbackFunc(links);
            }

            for (var i = 0, length = topicPairs.length; i < length; i++) {
                var topicAndPath = topicPairs[i].split("|");

                links[links.length] = { Title: topicAndPath[0], Link: topicAndPath[1] };
            }
        }

        callbackFunc(links);
    };

    Topic.Hyperlink_Onclick = function (e) {
        var $this = $(this);

        if ($this.hasClass("MCTopicPopup") || $this.hasClass("MCPopupThumbnailLink") || $this.hasClass("MCHelpControl") || $this.hasClass("reply-comment-button"))
            return;

        var href = MadCap.Dom.GetAttribute(this, "href");

        if (href == null || MadCap.String.StartsWith(href, "http:") || MadCap.String.StartsWith(href, "https:"))
            return;

        var target = MadCap.Dom.GetAttribute(this, "target");

        if (target != null)
            return;

        if (IsEmbeddedTopic()) {
            var url = new MadCap.Utilities.Url(document.location.href);

            if (MadCap.String.StartsWith(href, '#')) {
                url = new MadCap.Utilities.Url(url.PlainPath + href);
            }
            else if (MadCap.String.Contains(href, "javascript:void(0)")) {
                return;
            }
            else {
                url = url.ToFolder().CombinePath(href);
            }

            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "navigate-topic", [url.FullPath], null);

            e.preventDefault(); // prevents link from navigating
        }
        else {
            MadCap.Utilities.Url.OnNavigateTopic.call($this, e);
        }
    };

    Topic.ScrollToBookmark = function (id) {
        id = decodeURI(id).replace(/([ #;?%&,.+*~\':"!^$[\]()=>|\/@])/g, '\\$1'); // escape invalid jquery characters

        if (!id) { return; }

        var $target = $("#" + id);
        if ($target.length == 0)
            $target = $("[name = '" + id + "']");

        if ($target.length > 0) {
            Unhide($target[0], false);
            var $menus = $("ul[data-mc-toc]");
            var menusLoaded = 0;
            if ($menus.length > 0) {
                $menus.each(function () {
                    if (!this.innerHTML.replace(/\s/g, '').length) { // menu not loaded yet
                        $(this).on("loaded", function () {
                            menusLoaded++;
                            if (menusLoaded == $menus.length)
                                ScrollToOffset($target.offset().top);
                        });
                    } else {
                        menusLoaded++;
                        if (menusLoaded == $menus.length)
                            ScrollToOffset($target.offset().top);
                    }
                });
            } else {
                ScrollToOffset($target.offset().top);
            }
        }
    };

    function ScrollToOffset(targetOffset) {
        var $scrollContainer = $(".sidenav-container").is(":visible") ? $(".body-container") : $("html, body");
        var computedOffset = $(".title-bar.sticky.is-stuck").length > 0 || $(".sidenav-container").is(":visible") ? targetOffset - $(".title-bar").innerHeight() : targetOffset;
        
        $scrollContainer.scrollTop(computedOffset);
    }

    $(function (e) {
        MadCap.Utilities.LoadHandlers["MadCapTopic"] = Topic.Init;

        Window_Onload(e);
    });

    function Window_OnResize(e) {
        ShowFeedback();
    }

    function ShowFeedback() {
        var $feedbackWrapper = $(".feedback-comments-wrapper");
        if (_HelpSystem && _HelpSystem.IsResponsive && parent != window) {
            $feedbackWrapper.addClass("feedback-embedded");
            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "get-parent-window-width", null, function (data) {
                var width = parseInt(data[0]);

                if (_HelpSystem.IsTabletLayout(width)) {
                    if (!$feedbackWrapper.hasClass("responsive"))
                        $feedbackWrapper.addClass("responsive");
                }
                else {
                    if ($feedbackWrapper.hasClass("responsive"))
                        $feedbackWrapper.removeClass("responsive");
                }
            });
        }
        else {
            if ($feedbackWrapper.hasClass("responsive"))
                $feedbackWrapper.removeClass("responsive");
        }
    }

    function Window_Onload(e) {
        $(window).on('resize', Window_OnResize);
        $(window).on('hashchange', Window_Onhashchange);

        Topic.Init(document);
    }

    Topic.Init = function (context) {
        // Apply placeholder polyfill
        $("input, textarea", context).placeholder();

        // if embedded topic or topic popup, hide any MCWebHelpFramesetLinks
        if (IsEmbeddedTopic() || IsTopicPopup()) {
            $(".MCWebHelpFramesetLink", context).hide();
        }

        // Handle clicks to anchors using event delegation. This way, anchors added dynamically (via help controls, etc.) will be handled without needing to attach the handler then.
        $(context).on("click", "a, area", MadCap.Topic.Hyperlink_Onclick);

        // Set up thumbnail popups and hovers
        $(".MCPopupThumbnailPopup", context).on('click', MadCap.Topic.ThumbPopup_Click);
        $(".MCPopupThumbnailHover", context).on('mouseover', MadCap.Topic.ThumbPopup_Hover);

        $("a.MCHelpControl", context).on('click', MadCap.Topic.HelpControl_Click);

        // Set up buttons
        $(".print-button", context).on('click', function (e) {
            window.print();
        });

        $(".expand-all-button", context).on('click', function (e) {
            var $this = $(this);

            if ($this.hasClass("expand-all-button"))
                MadCap.TextEffects.TextEffectControl.ExpandAll("open");
            else if ($this.hasClass("collapse-all-button"))
                MadCap.TextEffects.TextEffectControl.ExpandAll("close");

            MadCap.Utilities.ToggleButtonState(this);
        });
        $(".remove-highlight-button", context).on('click', function (e) {
            RemoveHighlight();
        });

        $(".previous-topic-button", context).on('click', function (e) {
            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "navigate-previous");
        });

        $(".next-topic-button", context).on('click', function (e) {
            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "navigate-next");
        });


        //
        if (MadCap.String.Contains(navigator.userAgent, "iphone", false)) {
            window.scrollTo(0, 1);
        }

        // iPad scrolling issue with iframe. The iframe contents that aren't visible don't render after scrolling.
        // http://stackoverflow.com/questions/10805301/how-can-i-scroll-an-iframe-in-ios-4-with-2-fingers/10807318#10807318
        if (MadCap.IsIOS() && isTriPane) {
            // Can't use jQuery here because append() will cause any inline <script> to be executed again.
            //var $wrapperDiv = $("<div id='ios-wrapper'></div>");
            //$wrapperDiv.append($(document.body).children()).appendTo(document.body);
            var $wrapperDiv = $("<div id='ios-wrapper'></div>").appendTo(document.body);
            var wrapperDiv = $wrapperDiv[0];

            for (var i = document.body.childNodes.length - 2; i >= 0; i--) {
                var child = document.body.childNodes[i];

                wrapperDiv.insertBefore(child, wrapperDiv.firstChild);
            }
        }

        HighlightSearchTerms();

        //

        var homeFrame = parent;

        if (IsTopicPopup())
            homeFrame = parent.parent;

        var pathToHelpSystem = $(document.documentElement).attr('data-mc-path-to-help-system');
        var helpSystemPath = "Data/HelpSystem.xml";

        if (pathToHelpSystem)
            helpSystemPath = pathToHelpSystem + helpSystemPath;

        var url = new MadCap.Utilities.Url(helpSystemPath);

        MadCap.WebHelp.HelpSystem.LoadHelpSystem(url.FullPath).done(function (helpSystem) {
            _HelpSystem = helpSystem;

            OnHelpSystemLoaded();
        });
    }

    function LoadMenus() {
        var $tocUls = $("ul[data-mc-toc]");
        var tocData;
        if (!isTriPane) {
            tocData = LoadTocDatafromQuery();
        }

        $tocUls.each(function () {
            var self = this;
            var tocPane = new MadCap.WebHelp.TocPane("Toc", _HelpSystem, this, true);

            tocPane._TocType = tocData.TocType;
            tocPane._TocPath = tocData.TocType == 'Toc' ? tocData.TocPath : tocData.BrowseSequencesPath;
            tocPane._TocHref = tocData.Href;
            tocPane.Init(function () {
                // if dynamically generate top nav title menu then fire window resize event
                // to force sticky title to resize
                if (MadCap.Dom.GetAttributeBool(self, "data-mc-top-nav-menu", false)) {
                    $(window).trigger('resize');
                }

                var e = jQuery.Event("loaded");
                $(self).trigger(e);
            });
        });
    }

    function LoadBreadcrumbs() {
        var $tocBreadcrumbs = $("div.breadcrumbs[data-mc-toc]");
        var tocData;
        if (!isTriPane) {
            tocData = LoadTocDatafromQuery();
        }

        $tocBreadcrumbs.each(function () {
            var breadcrumbs = new MadCap.WebHelp.Breadcrumbs("Toc", _HelpSystem, this, true);

            breadcrumbs._TocType = tocData.TocType;
            breadcrumbs._TocPath = tocData.TocType == 'Toc' ? tocData.TocPath : tocData.BrowseSequencesPath;
            breadcrumbs._TocHref = tocData.Href;
            breadcrumbs.Init();
        });
    }

    function LoadMiniTocs() {        
        var $miniTocs = $("div.miniToc[data-mc-toc]");
        var tocData;        
        if (!isTriPane && $miniTocs.length > 0) {
            tocData = LoadTocDatafromQuery();
            
            // adjust tocpath for subproject topics in html5 output
            // build new tocpath based on current subproject root node title
            _HelpSystem.FindNodeInToc("Toc", tocData.TocPath, tocData.Href, function(node) {
                if (node) {
                    var newTocPath = "";
                    var entryHref = _HelpSystem.GetTocEntryHref(node, tocData.TocType, false, true);
                    if (IsEmbeddedTopic())
                        entryHref = decodeURIComponent(entryHref);
                    var currTocData = _HelpSystem.GetTocData(new MadCap.Utilities.Url(entryHref));
                    var needsNewTocPath = tocData[tocData.TocType + "Path"] != currTocData[tocData.TocType + "Path"];
                    
                    if (needsNewTocPath) {
                        var title = node.toc.entries[node.i].title;
                        var splitPath = tocData[tocData.TocType + "Path"].split('|');
                        for (var i = 0; i < splitPath.length; i++) {
                            var step = splitPath[i];
                            if (step == title || newTocPath) {
                                newTocPath += (i == splitPath.length - 1) ? step : (step + "|");
                            }
                        }
                                
                        tocData[tocData.TocType + "Path"] = newTocPath;
                    }
                }
                    
                InitMiniToc(tocData);
            }, null, false);
                
            return;
        }

        InitMiniToc(tocData);
    }

    function InitMiniToc(tocData) {
        var $miniTocs = $("div.miniToc[data-mc-toc]");
        $miniTocs.each(function () {
            var miniToc = new MadCap.WebHelp.MiniToc("Toc", _HelpSystem, this);

            miniToc._TocType = tocData.TocType;
            miniToc._TocPath = tocData.TocType == 'Toc' ? tocData.TocPath : tocData.BrowseSequencesPath;
            miniToc._TocHref = tocData.Href;
            miniToc.Init();
        });
    }

    function LoadTocDatafromQuery() {
        var helpSystem = _HelpSystem.GetMasterHelpsystem();
        var contentFolder = helpSystem.GetContentPath();
        var current = new MadCap.Utilities.Url(document.location.href);
        if (current.IsFolder) {
            var ext = new MadCap.Utilities.Url(helpSystem.DefaultStartTopic).Extension;
            current = current.AddFile("default." + ext);  // if current path is folder, check for default.htm
        }
        var contentPath = current.ToFolder().CombinePath(contentFolder);
        var href = current.ToRelative(contentPath);

        return _HelpSystem.GetTocData(new MadCap.Utilities.Url(href.FullPath));
    }

    function OnHelpSystemLoaded() {
        var hash = MadCap.Utilities.Url.CurrentHash();
        if (hash.length > 0) {
            var href = new MadCap.Utilities.Url(hash.substring(1));
            ProcessBookmark(href.ToNoQuery().FullPath);
            if (!$("html").hasClass("pulseTopic")) {
                $(window).trigger("hashchange");
            }
        }

        UpdateCurrentTopicIndex();

        LoadMenus();
        LoadBreadcrumbs();
        LoadMiniTocs();

        if (_HelpSystem && _HelpSystem.LiveHelpEnabled) {
            _FeedbackController = MadCap.WebHelp.LoadFeedbackController(_HelpSystem.LiveHelpServer);
            _FeedbackController.Init(function () {
                if (_FeedbackController.FeedbackActive) {
                    // Request the CSHID from the parent frame
                    MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "get-csh-id", null, function (data) {
                        var cshid = data != null ? data[0] : null;

                        if (_TopicID != null) {
                            $(document.documentElement).addClass('has-topic');

                            // Log the topic view
                            _FeedbackController.LogTopic(_TopicID, cshid, function () {
                                var $feedbackWrapper = $(".feedback-comments-wrapper");

                                if (!IsTopicPopup() && !IsTemplateTopic() && !IsCommunityDisabled()) {
                                    if (!_FeedbackController.PulseEnabled) { // using Feedback Server
                                        $feedbackWrapper.removeClass("hidden");

                                        _CommentLengthExceededMessage = $("#new-comment-form").attr("data-comment-length-exceeded-message")
                                            || "The maximum comment length was exceeded by {n} characters.";

                                        // If anonymous comments are enabled, the username field will be displayed.
                                        _FeedbackController.GetAnonymousEnabled(_HelpSystem.LiveHelpOutputId, function (anonEnabled) {
                                            _AnonymousCommentsEnabled = anonEnabled;

                                            if (anonEnabled)
                                                $(document.documentElement).addClass("feedback-anonymous-enabled");
                                        });

                                        var username = MadCap.Utilities.Store.getItem("LiveHelpUsername");
                                    $(".username").val(username);

                                        // Hook up the comment submit button handler
                                    $(".comment-submit").click(CommentSubmit_Click);

                                        // Hook up the reply comment button handler (using event delegation)
                                    $(".feedback-comments-wrapper .comments").on("click", ".reply-comment-button", ReplyComment_Click);

                                        // Get topic comments
                                        RefreshComments();
                                    }
                                    else if (_FeedbackController.PulseActive) {
                                        GetPulsePath(function (path) {
                                            if (path) {
                                                var src = _FeedbackController.PulseServer + path;
                                                SetPulseFrameSrc(src);
                                            }
                                            else {
                                                _FeedbackController.GetPulseStreamID(_TopicID, function (streamID) {

                                                    if (streamID == "00000000-0000-0000-0000-000000000000") {
                                                        return;
                                                    }
                                                    var src = _FeedbackController.PulseServer + "streams/" + streamID + "/activities?frame=stream";
                                                    SetPulseFrameSrc(src);
                                                });
                                            }
                                        });

                                        var serverUrl = new MadCap.Utilities.Url(_FeedbackController.PulseServer);
                                        MadCap.Utilities.CrossFrame.AddVerifiedOrigin(serverUrl.Origin);
                                    }
                                }
                            });
                        }
                    });
                }
            });
            ShowFeedback();
        }
    }

    function Window_Onhashchange(e) {
        var url = new MadCap.Utilities.Url(document.location.href);

        if (!MadCap.String.IsNullOrEmpty(url.Fragment)) {
            var id = url.Fragment.substring(1);
            id = MadCap.Utilities.Url.StripInvalidCharacters(id);

            Topic.ScrollToBookmark(id);
        }
    }

    function ProcessBookmark(bookmarkName) {
        bookmarkName = MadCap.Utilities.Url.StripInvalidCharacters(bookmarkName);

        var el = $("[name='" + bookmarkName + "']");

        if (el.length > 0) {
            Unhide(el[0], false);
        }
    }

    function IsEmbeddedTopic() {
        return window.name == "topic" && !MadCap.Utilities.HasRuntimeFileType("Default");
    }

    function IsTopicPopup() {
        return window.name == "MCPopup" && !MadCap.Utilities.HasRuntimeFileType("Default");
    }

    function IsTemplateTopic() {
        return $('html').hasClass('templateTopic');
    }

    function IsCommunityDisabled() {
        var communityFeatures = $(document.documentElement).attr('data-mc-community-features');
        return communityFeatures && communityFeatures.toLowerCase() == "disabled";
    }

    function UpdateCurrentTopicIndex() {
        MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "get-href", null, function (data) {
            if (data) {
                var url = new MadCap.Utilities.Url(data[0]);

                var href = new MadCap.Utilities.Url(url.Fragment.substring(1));
                var bsPath = url.QueryMap.GetItem('BrowseSequencesPath');

                _HelpSystem.SetBrowseSequencePath(bsPath, href);
            }
        });
    }

    function CommentSubmit_Click(e) {
        var $form = $(this).closest(".comment-form-wrapper");
        var userGuid = null;
        var username = $form.children(".username-field").val();
        var subject = $form.children(".subject-field").val();
        var comment = $form.find(".body-field").val();
        var parentCommentID = null;
        var $formParent = $form.parent();

        if ($formParent.hasClass("comment"))
            parentCommentID = $formParent.attr("data-mc-comment-id");

        AddComment(username, subject, comment, parentCommentID);
    }

    function AddComment(username, subject, comment, parentCommentID) {
        if (_AnonymousCommentsEnabled) {
            MadCap.Utilities.Store.setItem("LiveHelpUsername", username);

            try {
                _FeedbackController.AddComment(_TopicID, null, username, subject, comment, parentCommentID, RefreshComments);
            }
            catch (ex) {
                var message = _CommentLengthExceededMessage.replace(/{n}/g, ex.Data.ExceedAmount);
                alert(message);
            }
        }
        else {
            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "login-user", null, function (data) {
                var userGuid = data[0];

                if (userGuid != null) {
                    try {
                        _FeedbackController.AddComment(_TopicID, userGuid, username, subject, comment, parentCommentID, RefreshComments);
                    }
                    catch (ex) {
                        var message = _CommentLengthExceededMessage.replace(/{n}/g, ex.Data.ExceedAmount);
                        alert(message);
                    }
                }
            });
        }
    }

    function ReplyComment_Click(e) {
        e.preventDefault();

        var $formParent = $(this).closest(".comment");

        if ($formParent.children(".comment-form-wrapper")[0] != null)
            return;

        // create a copy of the new comment form and append it to the end of the current comment

        var $newForm = $("#new-comment-form").clone();
        $newForm.attr("id", null);
        $newForm.children(".comment-submit").click(CommentSubmit_Click);
        $formParent.children(".buttons").after($newForm);
        $newForm.hide().slideDown();
    }

    function RefreshComments() {
        MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "get-user-guid", null, function (data) {
            var userGuid = data[0];

            _FeedbackController.GetTopicComments(_TopicID, userGuid, null, function (commentsXml) {
                var xmlDoc = MadCap.Utilities.Xhr.LoadXmlString(commentsXml);
                var $comments = $(".comments");
                $comments.children().not(".mc-template").remove();

                BuildComments(xmlDoc.documentElement, $comments);
            });
        });
    }

    function BuildComments(xmlNode, htmlContainerNode) {
        var $xmlCommentNodes = $(xmlNode).children("Comment");
        var $commentTemplate = $(".comments .comment.mc-template");

        for (var i = 0, length = $xmlCommentNodes.length; i < length; i++) {
            var $xmlCommentNode = $($xmlCommentNodes[i]);
            var xmlUsername = $xmlCommentNode.attr("User");
            var xmlTimestamp = $xmlCommentNode.attr("DateUTC") || $xmlCommentNode.attr("Date"); // Feedback V1 used "Date", V2 uses "DateUTC". We could do a version check, but simply checking for the attribute is easier.
            var xmlSubject = $xmlCommentNode.attr("Subject");
            var xmlCommentID = $xmlCommentNode.attr("CommentID");
            var xmlBody = $xmlCommentNode.children("Body").text();

            var $commentNode = $commentTemplate.clone();
            $commentNode.removeClass("mc-template");

            $commentNode.attr("data-mc-comment-id", xmlCommentID);
            $(".username", $commentNode).text(xmlUsername);
            $(".timestamp", $commentNode).text(xmlTimestamp);
            $(".subject", $commentNode).text(xmlSubject);
            $(".body", $commentNode).text(xmlBody);

            $(htmlContainerNode).append($commentNode);

            BuildComments($xmlCommentNode.children("Comments")[0], $commentNode);
        }
    }

    function GetPulsePath(onComplete) {
        MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "get-href", null, function (data) {
            var pulsePath = null;

            if (data) {
                var url = new MadCap.Utilities.Url(decodeURIComponent(data[0]));

                var href = new MadCap.Utilities.Url(url.Fragment.substring(1));
                pulsePath = url.QueryMap.GetItem('PulsePath');
            }

            onComplete(pulsePath);
        });
    }

    function SetPulseFrameSrc(src) {
        var $feedbackWrapper = $(".feedback-comments-wrapper");
        $feedbackWrapper.empty();

        var $pulseIframe = $("<iframe name='topiccomments-html5' class='pulse-frame pulse-loading' title='Topic Comments' frameborder='0'></iframe>");
        $pulseIframe.appendTo($feedbackWrapper);
        $pulseIframe.attr("onload", "this.className='pulse-frame';");
        $pulseIframe.attr("src", src);

        if (!_HideComments)
            $feedbackWrapper.removeClass("hidden");
    }

    function RemoveHighlight() {
        for (var index = 1; index <= 10; index++) {
            $('body').removeHighlight('SearchHighlight' + index);
        }
    }

    function HighlightSearchTerms() {
        function findNextSibling(child) {
            if (typeof child.nextElementSibling == 'undefined') {
                return child.nextSibling == null || child.nextSibling.nodeType == 1 ? child.nextSibling : findNextSibling(child.nextSibling);
            } else {
                return child.nextElementSibling;
            }
        };
        MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "get-href", null, function (data) {
            if (data) {
                var url = new MadCap.Utilities.Url(data[0]);
                var highlight = url.QueryMap.GetItem("Highlight");

                if (MadCap.String.IsNullOrEmpty(highlight)) {
                    return;
                }

                var phrases = highlight.match(/"[^"]*"/g);
                if (phrases != null) {
                    for (var phrase = 0; phrase < phrases.length; phrase++) {
                        highlight = highlight.replace(phrases[phrase], "");
                    }
                }
                var terms = highlight.replace('"', "").split(" ");
                for (var term = 0; term < terms.length; term++) {
                    if (terms[term] == "") {
                        terms.splice(terms[term], 1);
                        term--;
                    }
                }

                if (phrases != null) {
                    for (var phrase = 0; phrase < phrases.length; phrase++) {
                        terms.push(phrases[phrase].replace(/"/g, ""));
                    }
                }

                for (var term = 0; term < terms.length; term++) {
                    if ($.inArray(terms[term].toLowerCase(), MadCap.Utilities.StopWords) != -1) {
                        terms.splice(term, 1);
                        term--;
                    }
                }

                for (var index = 0; index < terms.length; index++) {
                    var termElements = Array("*[class*='MCExpandingBody']", "*[class*='MCDropDownHotSpot']", "*[data-mc-target-name]");
                    for (var termElement = 0; termElement < termElements.length; termElement++) {
                        var elems = $(termElements[termElement]);
                        for (var elem = 0; elem < elems.length; elem++) {

                            var nextParentSibling = findNextSibling(elems[elem].parentElement);
                            if ((elems[elem].textContent != null && elems[elem].textContent.toLowerCase().indexOf(terms[index].toLowerCase()) >= 0) ||
                                (nextParentSibling != null && nextParentSibling.textContent != null &&
                                nextParentSibling.textContent.toLowerCase().indexOf(terms[index].toLowerCase()) >= 0)) {
                                Unhide(termElement != 2 ? elems[elem] : elems[elem].firstChild);
                            }
                        }
                    }
                    $('body').highlight(terms[index], 'SearchHighlight SearchHighlight' + (index + 1));
                }
            }
        });
    }

    function Highlight(term, color, caseSensitive, searchType) {
        if (term == "") {
            return;
        }

        ApplyHighlight(document.body, term, color, caseSensitive, searchType);

        // Scroll to first highlighted term

        if (_FirstHighlight && _FirstHighlight.offsetTop > document.documentElement.clientHeight) {
            document.documentElement.scrollTop = _FirstHighlight.offsetTop;
        }
    }

    function MergeTextNodes(node) {
        for (var i = node.childNodes.length - 1; i >= 1; i--) {
            var currNode = node.childNodes[i];
            var prevNode = currNode.previousSibling;

            if (currNode.nodeType == 3 && prevNode.nodeType == 3) {
                prevNode.nodeValue = prevNode.nodeValue + currNode.nodeValue;
                node.removeChild(currNode);
            }
        }

        for (var i = 0; i < node.childNodes.length; i++) {
            MergeTextNodes(node.childNodes[i]);
        }
    }

    function ApplyHighlight(root, term, color, caseSensitive, searchType) {
        var re = null;

        if (searchType == "NGram") {
            re = new RegExp(term, "g" + (caseSensitive ? "" : "i"));
        }
        else {
            var escTerm = term.replace(/([*^$+?.()[\]{}|\\])/g, "\\$1"); // Escape regex

            re = new RegExp("(^|\\s|[.,;!#$/:?'\"()[\\]{}|=+*_\\-\\\\])" + escTerm + "($|\\s|[.,;!#$/:?'\"()[\\]{}|=+*_\\-\\\\])", "g" + (caseSensitive ? "" : "i"));
        }

        for (var i = root.childNodes.length - 1; i >= 0; i--) {
            var node = root.childNodes[i];

            ApplyHighlight(node, term, color, caseSensitive, searchType);

            if (node.nodeType != 3 || node.parentNode.nodeName == "SCRIPT") {
                continue;
            }

            var currNode = node;
            var text = currNode.nodeValue;

            for (var match = re.exec(text); match != null; match = re.exec(text)) {
                var pos = match.index + (searchType == "NGram" ? 0 : match[1].length);
                var posEnd = pos + term.length;
                var span = document.createElement("span");

                span.className = "highlight";
                span.style.fontWeight = "bold";
                span.style.backgroundColor = color.split(",")[0];
                span.style.color = color.split(",")[1];

                var span2 = document.createElement("span");

                span2.className = "SearchHighlight" + (_ColorIndex + 1);
                span2.appendChild(document.createTextNode(text.substring(pos, posEnd)));

                span.appendChild(span2);

                currNode.nodeValue = text.substring(0, pos);
                currNode.parentNode.insertBefore(span, currNode.nextSibling);
                currNode.parentNode.insertBefore(document.createTextNode(text.substring(posEnd, text.length)), span.nextSibling);

                currNode = currNode.nextSibling.nextSibling;
                text = currNode.nodeValue;

                //

                if (_FirstHighlight == null || span.offsetTop < _FirstHighlight.offsetTop) {
                    _FirstHighlight = span;
                }

                //

                Unhide(span);
            }
        }
    }

    function Unhide(el, animate) {
        if (typeof animate == 'undefined')
            animate = true;

        var didOpen = false;

        for (var currNode = el.parentNode; currNode.nodeName != "BODY"; currNode = currNode.parentNode) {
            var $currNode = $(currNode);

            if ($currNode.hasClass("MCExpanding")) {
                var control = TextEffects.TextEffectControl.FindControl($currNode[0]);
                if (control == null) {
                    control = new MadCap.Topic.ExpandingControl(currNode);
                }
                control.Open(animate);
                didOpen = true;
            }
            else if ($currNode.hasClass("MCDropDown")) {
                var control = TextEffects.TextEffectControl.FindControl($currNode[0]);
                if (control == null) {
                    control = new MadCap.Topic.DropDownControl(currNode);
                }
                control.Open(animate);
                didOpen = true;
            }
            else {
                var targetName = $(currNode).attr("data-mc-target-name");

                if (targetName != null) {
                    var togglerNodes = MadCap.Dom.GetElementsByClassName("MCToggler", null, document.body);

                    for (var i = 0, length = togglerNodes.length; i < length; i++) {
                        var targets = $(togglerNodes[i]).attr("data-mc-targets").split(";");
                        var found = false;

                        for (var j = 0; j < targets.length; j++) {
                            if (targets[j] == targetName) {
                                found = true;

                                break;
                            }
                        }

                        if (!found)
                            continue;

                        var control = TextEffects.TextEffectControl.FindControl(togglerNodes[i]);
                        if (control == null) {
                            control = new MadCap.Topic.TogglerControl(togglerNodes[i]);
                        }
                        control.Open(animate);
                        didOpen = true;

                        break;
                    }
                }
            }
        }

        return didOpen;
    }

    MadCap.Utilities.CrossFrame.AddMessageHandler(function (message, dataValues, responseData) {
        var returnData = { Handled: false, FireResponse: true };

        if (message == "print") {
            window.focus();
            window.print();

            returnData.Handled = true;
        }
        else if (message == "expand-all") {
            MadCap.TextEffects.TextEffectControl.ExpandAll("open");

            returnData.Handled = true;
        }
        else if (message == "collapse-all") {
            MadCap.TextEffects.TextEffectControl.ExpandAll("close");

            returnData.Handled = true;
        }
        else if (message == "get-topic-id") {
            responseData[responseData.length] = _TopicID;

            returnData.Handled = true;
        }
        else if (message == "get-topic-url") {
            responseData[responseData.length] = document.location.href;

            returnData.Handled = true;
        }
        else if (message == "remove-highlight") {
            RemoveHighlight();
            returnData.Handled = true;
        }
        else if (message == "get-bs-path") {
            var url = new MadCap.Utilities.Url(document.location.href);
            var bsPath = url.QueryMap.GetItem("BrowseSequencePath");

            if (bsPath == null)
                bsPath = MadCap.Dom.Dataset(document.documentElement, "mcBrowseSequencePath");

            responseData[responseData.length] = bsPath;
            responseData[responseData.length] = url.FullPath;

            //

            returnData.Handled = true;
        }
        else if (message == "reload-pulse") {
            MadCap.Utilities.CrossFrame.PostMessageRequest(frames["topiccomments-html5"], "reload");

            //

            returnData.Handled = true;
        }
        else if (message == "logout-complete") {
            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "logout-complete");

            returnData.Handled = true;
        }
        else if (message == "set-pulse-login-id") {
            if (_FeedbackController != null)
                _FeedbackController.PulseUserGuid = dataValues[0];

            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "set-pulse-login-id", dataValues);

            returnData.Handled = true;
        }
        else if (message == "resize-pulse") {
            var $pulseFrame = $('.pulse-frame');
            $pulseFrame.attr('scrolling', 'no');
            $pulseFrame.css('overflow', 'hidden');
            $pulseFrame.height(dataValues[1]);

            returnData.Handled = true;
        }
        else if (message == "show-comments") {
            _HideComments = false;
            returnData.Handled = true;
        }
        else if (message == "hide-comments") {
            _HideComments = true;
            returnData.Handled = true;
        }

        return returnData;
    }, null);

    var _ColorTable = new Array("#ffff66,#000000",
								"#a0ffff,#000000",
								"#99ff99,#000000",
								"#ff9999,#000000",
								"#ff66ff,#000000",
								"#880000,#ffffff",
								"#00aa00,#ffffff",
								"#886800,#ffffff",
								"#004699,#ffffff",
								"#990099,#ffffff");
    var _ColorIndex = 0;
    var _FirstHighlight = null;
    var _HelpSystem = null;
    var _FeedbackController = null;
    var _HideComments = true;
    var _AnonymousCommentsEnabled = false;
    var _TopicID = MadCap.Dom.Dataset(document.documentElement, "mcLiveHelp");
    var _CommentLengthExceededMessage = null;
})();
