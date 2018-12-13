/// <reference path="jquery.js" />
/// <reference path="MadCapGlobal.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */

(function () {
    MadCap.CreateNamespace("TextEffects");

    var TextEffects = MadCap.TextEffects;

    TextEffects.Init = function (context) {
        TextEffects.ExpandingControl.Load(context);
        TextEffects.DropDownControl.Load(context);
        TextEffects.TogglerControl.Load(context);
        TextEffects.TextPopupControl.Load(context);
        TextEffects.TopicPopupControl.Load(context);
    };

    TextEffects.Dispose = function (context) {
        TextEffects.ExpandingControl.UnLoad(context);
        TextEffects.DropDownControl.UnLoad(context);
        TextEffects.TogglerControl.UnLoad(context);
        TextEffects.TextPopupControl.UnLoad(context);
        TextEffects.TopicPopupControl.UnLoad(context);
    };

    $(function () {
        MadCap.Utilities.LoadHandlers["MadCapTextEffects"] = TextEffects.Init;

        TextEffects.Init(document);
    });

    // TextEffectControl

    TextEffects.TextEffectControl = function (el, className) {
        if (this._rootEl == null) {
            this._rootEl = el;
        }

        this._hotSpotEl = null;
        this._bodyEls = null;
        this._className = className;

        TextEffects.TextEffectControl.Controls[TextEffects.TextEffectControl.Controls.length] = this;

        var _self = this;

        (function () {
            _self._hotSpotEl = MadCap.Dom.GetElementsByClassName(_self._className + "HotSpot", null, _self._rootEl)[0];
            _self._bodyEls = MadCap.Dom.GetElementsByClassName(_self._className + "Body", null, _self._rootEl);

            var hotSpots = MadCap.Dom.GetElementsByClassName(_self._className + "HotSpot", null, _self._rootEl);

            for (var i = hotSpots.length - 1; i >= 0; i--) {
                var parent = hotSpots[i].parentNode;
                while (parent != null) {
                    if ($(parent).hasClass(_self._className)) {
                        if (parent == _self._rootEl) {
                            $(hotSpots[i]).click(function (e) { _self.Toggle.call(_self); });
                        }
                        else {
                            break;
                        }
                    }
                    
                    parent = parent.parentNode;
                }
            };
        })();
    };

    TextEffects.UnbindTextEffectControl = function (el, className) {
        if (this._rootEl == null) {
            this._rootEl = el;
        }

        this._hotSpotEl = null;
        this._bodyEls = null;
        this._className = className;

        var _self = this;

        (function () {
            _self._hotSpotEl = MadCap.Dom.GetElementsByClassName(_self._className + "HotSpot", null, _self._rootEl)[0];

            var hotSpots = MadCap.Dom.GetElementsByClassName(_self._className + "HotSpot", null, _self._rootEl);

            for (var i = hotSpots.length - 1; i >= 0; i--) {
                var parent = hotSpots[i].parentNode;
                while (parent != null) {
                    if ($(parent).hasClass(_self._className)) {
                        if (parent == _self._rootEl) {
                            $(hotSpots[i]).unbind();
                        }
                        else {
                            break;
                        }
                    }

                    parent = parent.parentNode;
                }
            };

            $(_self._hotSpotEl).unbind();
        })();
    };

    // Statics

    TextEffects.TextEffectControl.Controls = new Array();

    TextEffects.TextEffectControl.FindControl = function (el) {
        for (var i = 0; i < TextEffects.TextEffectControl.Controls.length; i++) {
            if (TextEffects.TextEffectControl.Controls[i]._rootEl == el) {
                return TextEffects.TextEffectControl.Controls[i];
            }
        }

        return null;
    };

    TextEffects.TextEffectControl.ExpandAll = function (swapType) {
        for (var i = 0, length = TextEffects.TextEffectControl.Controls.length; i < length; i++) {
            var control = TextEffects.TextEffectControl.Controls[i];

            if (swapType == "open")
                control.Open(false);
            else if (swapType == "close")
                control.Close(false);
        }
    };

    // Functions

    TextEffects.TextEffectControl.prototype.Open = function () {
        var $rootEl = $(this._rootEl);
        if ($rootEl.hasClass("MCToggler")){
            $rootEl = $(this._rootEl.parentNode).find("a.MCToggler");
            //$rootEl = $(this._rootEl.parentNode.children[0]);
        }
        $rootEl.removeClass(this._className + "_Closed");
        $rootEl.addClass(this._className + "_Open");

        var imgClass = null;
        if ($rootEl.hasClass("MCToggler")) {
            imgClass = $(".MCToggler_Image_Icon");
        }
        else if ($rootEl.hasClass("MCDropDown")) {
            imgClass = $(".MCDropDown_Image_Icon");
        }
        else if ($rootEl.hasClass("MCExpanding")) {
            imgClass = $(".MCExpanding_Image_Icon");
        }

        var $img = $rootEl.find(imgClass);
        this.ToggleAltText($img[0], $rootEl, "closed");

        $rootEl.attr("data-mc-state", "open");
    };

    TextEffects.TextEffectControl.prototype.Close = function () {
        var $rootEl = $(this._rootEl);
        if ($rootEl.hasClass("MCToggler")) {
            $rootEl = $(this._rootEl.parentNode).find("a.MCToggler");
            //$rootEl = $(this._rootEl.parentNode.children[0]);
        }
        $rootEl.removeClass(this._className + "_Open");
        $rootEl.addClass(this._className + "_Closed");

        var imgClass = null;
        if ($rootEl.hasClass("MCToggler")) {
            imgClass = $(".MCToggler_Image_Icon");
        }
        else if ($rootEl.hasClass("MCDropDown")) {
            imgClass = $(".MCDropDown_Image_Icon");
        }
        else if ($rootEl.hasClass("MCExpanding")) {
            imgClass = $(".MCExpanding_Image_Icon");
        }

        var $img = $rootEl.find(imgClass);
        this.ToggleAltText($img[0], $rootEl, "open");

        $rootEl.attr("data-mc-state", "closed");
    };

    TextEffects.TextEffectControl.prototype.ToggleAltText = function (imgEl, rootEl, state) {
        if (imgEl != null) {
            var $imgEl = $(imgEl);

            var alt2 = $imgEl.attr("data-mc-alt2");
            var alt = $imgEl.attr("alt");

            if (rootEl != null && rootEl.attr("data-mc-state") == state) {
                $imgEl.attr("alt", alt2);
                $imgEl.attr("data-mc-alt2", alt);
            }
        }
    }

    TextEffects.TextEffectControl.prototype.Toggle = function () {
        var $rootEl = $(this._rootEl);

        if ($rootEl.hasClass("MCToggler")) {
            $rootEl = $(this._rootEl.parentNode).find("a.MCToggler");
            //$rootEl = $(this._rootEl.parentNode.children[0]);
        }

        var state = $rootEl.attr("data-mc-state") || "closed";
        var newState = null;

        if (state == "open") {
            this.Close(true);
        }
        else if (state == "closed") {
            this.Open(true);
        }

        $($rootEl.find("a")[0]).focus();
    };

    TextEffects.TextEffectControl.prototype.ResizeSlideshow = function (el, open) {

        if (el) {
            var $el = $(el);
            var $slideshow = $el.closest('div[class^="mc-viewport"]');
            if ($slideshow) {

                var newHeight = 0;
                $el.children().each(function () {
                    newHeight = newHeight + $(this).outerHeight();
                });

                if (open)
                    newHeight = $slideshow.height() + Math.max(newHeight, $el.outerHeight());
                else
                    newHeight = $slideshow.height() - Math.max(newHeight, $el.outerHeight());

                $slideshow.animate({ height: newHeight });
            }
        }
    }

    // ExpandingControl

    TextEffects.ExpandingControl = function (el) {
        TextEffects.TextEffectControl.call(this, el, "MCExpanding");
    };

    MadCap.Extend(TextEffects.TextEffectControl, TextEffects.ExpandingControl);

    TextEffects.ExpandingControl.Load = function (context) {
        var expandings = $(".MCExpanding", context);

        for (var i = 0, length = expandings.length; i < length; i++) {
            var expandingEl = expandings[i];
            var expanding = new TextEffects.ExpandingControl(expandingEl);
            expanding.Init();
        }
    };

    TextEffects.ExpandingControl.UnLoad = function (context) {
        var expandings = $(".MCExpanding", context);

        for (var i = 0, length = expandings.length; i < length; i++)
            TextEffects.UnbindTextEffectControl(expandings[i]);
    };

    TextEffects.ExpandingControl.prototype.Init = function () {
        this.Close(false);
    };

    TextEffects.ExpandingControl.prototype.Open = function (shouldAnimate) {
        this.base.Open.call(this);
        var $bodyEls = $(this._bodyEls[0]);

        this.ResizeSlideshow($bodyEls, true);

        $bodyEls.show();
        $bodyEls.css("display", "inline");

        $(window).trigger('resize');
    };

    TextEffects.ExpandingControl.prototype.Close = function (shouldAnimate) {
        $(this._bodyEls[0]).hide();
        $(window).trigger('resize');
        this.base.Close.call(this);
    };

    // DropDownControl

    TextEffects.DropDownControl = function (el) {
        TextEffects.TextEffectControl.call(this, el, "MCDropDown");
    };

    MadCap.Extend(TextEffects.TextEffectControl, TextEffects.DropDownControl);

    TextEffects.DropDownControl.Load = function (context) {
        var dropDowns = $(".MCDropDown", context);

        for (var i = 0, length = dropDowns.length; i < length; i++) {
            var dropDownEl = dropDowns[i];
            var dropDown = new TextEffects.DropDownControl(dropDownEl);
            dropDown.Init(false);
        }
    };

    TextEffects.DropDownControl.UnLoad = function (context) {
        var dropDowns = $(".MCDropDown", context);

        for (var i = 0, length = dropDowns.length; i < length; i++)
            TextEffects.UnbindTextEffectControl(dropDowns[i]);
    };

    TextEffects.DropDownControl.prototype.Init = function () {
        this.Close(false);
    };

    TextEffects.DropDownControl.prototype.Open = function (shouldAnimate) {
        this.base.Open.call(this);
        var $bodyEl = $(this._bodyEls[0]);

        var $sticky = $bodyEl.find('div.sticky');
        if ($sticky.length > 0) {
            $bodyEl.slideDown(function() {
                $(window).trigger('resize');
            });

            $sticky.foundation('_calc', true);
            return;
        }

        if (shouldAnimate) {
            $bodyEl.hide().slideDown(function () {
                $(window).trigger('resize');
            });
        } else {
            $bodyEl.show();
            $(window).trigger('resize');
        }
        
        this.ResizeSlideshow($bodyEl, true);
    };

    TextEffects.DropDownControl.prototype.Close = function (shouldAnimate) {
        var $bodyEl = $(this._bodyEls[0]);
        if (!shouldAnimate) {
            var $sticky = $bodyEl.find('div.sticky');
            if ($sticky.length > 0)
                $sticky.foundation('_calc', true);

            $bodyEl.hide();
            this.base.Close.call(this);
            $(window).trigger('resize');

            return;
        }

        var self = this;

        this.ResizeSlideshow(this._bodyEls[0], false);

        $(this._bodyEls[0]).slideUp(function () {
            self.base.Close.call(self);
            $(window).trigger('resize');
        });

    };

    // TogglerControl

    TextEffects.TogglerControl = function (el) {
        this._rootEl = el;
        this._hotSpotEl = el;
        this._bodyEls = new Array();
        this._className = "MCToggler";

        TextEffects.TextEffectControl.Controls[TextEffects.TextEffectControl.Controls.length] = this;

        var _self = this;

        (function () {
            var targetsVal = MadCap.Dom.Dataset(_self._rootEl, "mcTargets");
            var targets = targetsVal.split(";");

            for (var i = 0, length = targets.length; i < length; i++) {
                var target = targets[i];
                var els = MadCap.Dom.GetElementsByAttribute("data-mc-target-name", target, null, document.body);

                _self._bodyEls = _self._bodyEls.concat(els);
            }

            $(_self._hotSpotEl).click(function (e) { _self.Toggle.call(_self); });
        })();
    };

    MadCap.Extend(TextEffects.TextEffectControl, TextEffects.TogglerControl);

    TextEffects.TogglerControl.Load = function (context) {
        var togglers = $(".MCToggler", context);

        for (var i = 0, length = togglers.length; i < length; i++) {
            var togglerEl = togglers[i];
            var toggler = new TextEffects.TogglerControl(togglerEl);
            toggler.Init();
        }
    };

    TextEffects.TogglerControl.UnLoad = function (context) {
        var togglers = $(".MCToggler", context);

        for (var i = 0, length = togglers.length; i < length; i++)
            TextEffects.UnbindTextEffectControl(togglers[i]);
    };

    TextEffects.TogglerControl.prototype.Init = function () {
        this.Close(false);
    };

    TextEffects.TogglerControl.prototype.Open = function (animate) {
        this.base.Open.call(this);
       
        for (var i = 0, length = this._bodyEls.length; i < length; i++) {
            if (animate) {
                $(this._bodyEls[i]).css({ opacity: 0, display: "" });
                $(this._bodyEls[i]).animate(
                    {
                        opacity: 1
                    },
                    200, function() {
                        $(window).trigger('resize');
                    });
            }
            else {
                $(this._bodyEls[i]).css({ opacity: 1, display: "" });
                $(window).trigger('resize');
            }
        }

        this.ResizeSlideshow(this._bodyEls[0], true);
    };

    TextEffects.TogglerControl.prototype.Close = function (animate) {
        this.base.Close.call(this);

        this.ResizeSlideshow(this._bodyEls[0], false);

        function HideEl(el) {
            $(el).css("display", "none");
        }

        for (var i = 0, length = this._bodyEls.length; i < length; i++) {
            var self = this;

            if (animate) {
                $(this._bodyEls[i]).animate(
                {
                    opacity: 0
                },
                200,
                function () {
                    HideEl(this);
                    $(window).trigger('resize');
                });
            }
            else {
                HideEl(this._bodyEls[i]);
                $(window).trigger('resize');
            }
        }
    };

    // TextPopupControl

    TextEffects.TextPopupControl = function (el) {
        this._rootEl = el;
        this._hotSpotEl = el;
        this._bodyEls = null;
        this._className = "MCTextPopup";

        var _self = this;

        (function () {
            _self._bodyEls = $("." + _self._className + "Body", _self._rootEl).toArray();

            // fix for popups on touch devices
            if (MadCap.Utilities.IsTouchDevice()) {
                $(_self._hotSpotEl).click(function (e) {
                    if ($(this).attr('data-mc-state') === "closed")
                        _self.Open();
                    else
                        _self.Close();
                });
            } else {
                $(_self._hotSpotEl).on('mouseover', function (e) { _self.Open(); });
                $(_self._hotSpotEl).on('mouseleave', function (e) { _self.Close(); });
            }

        })();
    };

    MadCap.Extend(TextEffects.TextEffectControl, TextEffects.TextPopupControl);

    TextEffects.TextPopupControl.Load = function (context) {
        var textPopups = $(".MCTextPopup", context);

        for (var i = 0, length = textPopups.length; i < length; i++) {
            var textPopupEl = textPopups[i];
            var textPopup = new TextEffects.TextPopupControl(textPopupEl);
            textPopup.Init();
        }
    };

    TextEffects.TextPopupControl.UnLoad = function (context) {
        var textPopups = $(".MCTextPopup", context);

        for (var i = 0, length = textPopups.length; i < length; i++)
            TextEffects.UnbindTextEffectControl(textPopups[i]);
    };

    TextEffects.TextPopupControl.prototype.Init = function () {
        this.Close(false);
    };

    TextEffects.TextPopupControl.prototype.Open = function () {
        this.base.Open.call(this);

        var $popupSpot = $(this._rootEl);
        var $popupBodyEl = $(this._bodyEls[0]);
        var $popupArrowEl = $(".MCTextPopupArrow", $popupSpot);
        var $fixedHeader = $(".title-bar.sticky");
        var $win = $(window);

        $popupBodyEl.css("top", "0");
        $popupBodyEl.css("left", "0");

        // reset the height that may have been set when previously opening the text popup if it didn't fit
        $popupBodyEl.css("height", "auto");

        // Place the popup body centered below/above the text
        var ARROW_HEIGHT = 13;
        var offsetRootTop = $popupBodyEl.offset().top;
        var offsetRootLeft = $popupBodyEl.offset().left;
        var offsetTop = $popupSpot.offset().top - offsetRootTop;
        var offsetLeft = $popupSpot.offset().left - offsetRootLeft;
        var bottom = offsetTop + this._rootEl.offsetHeight;
        var popupWidth = $popupBodyEl[0].offsetWidth;
        var popupHeight = $popupBodyEl[0].offsetHeight;
        var middle = offsetLeft + ($popupSpot[0].offsetWidth / 2);
        var left = middle - (popupWidth / 2);
        var right = left + popupWidth;
        var top = bottom + ARROW_HEIGHT;
        var scrollTop = $win.scrollTop();
        var scrollLeft = $win.scrollLeft();
        var arrowMarginLeft = -$popupArrowEl[0].offsetWidth / 2;
        var outerWidth = $win.width();

        var heightBelow = scrollTop + $win.height() - bottom;

        if ($fixedHeader.length > 0)
            scrollTop += $fixedHeader.innerHeight();

        if ((popupHeight + ARROW_HEIGHT) > heightBelow) // can't fit below
        {
            var heightAbove = offsetTop - scrollTop;

            if ((popupHeight + ARROW_HEIGHT) > heightAbove) // can't fit above
            {
                top = bottom; // in this case place the popup immediately below the popup text so the user can move the mouse into it to scroll without it disappearing
                var borderTop = parseInt($popupBodyEl.css("border-top-width"));
                var borderBottom = parseInt($popupBodyEl.css("border-bottom-width"));
                var paddingTop = parseInt($popupBodyEl.css("padding-top"));
                var paddingBottom = parseInt($popupBodyEl.css("padding-bottom"));
                $popupBodyEl.css("height", (heightBelow - borderTop - borderBottom - paddingTop - paddingBottom) + "px");
                $popupBodyEl.css("overflow", "auto");
            }
            else {
                $popupBodyEl.addClass("MCTextPopupBodyBottom");

                top = offsetTop - popupHeight - ARROW_HEIGHT;
            }
        }
        else {
            $popupBodyEl.removeClass("MCTextPopupBodyBottom");
        }

        $popupBodyEl.css("top", top + "px");

        if (right >= outerWidth + scrollLeft)
            arrowMarginLeft += (right - outerWidth - scrollLeft);

        if (left < scrollLeft)
            arrowMarginLeft += (left - scrollLeft);

        left = Math.min(left, scrollLeft + outerWidth - popupWidth);
        left = Math.max(left, scrollLeft);

        var $body = $popupSpot.closest("body");
        //beyond the first page of an epub, coordinates need to be adjusted left-wise by scrollWidth
        if (MadCap.HasEpubReadingSystem()) {
            left = $popupSpot.offset().left;
            arrowMarginLeft = -(($popupBodyEl[0].offsetWidth / 2) - ($popupArrowEl[0].offsetWidth / 2));
        }

        $popupBodyEl.css("left", left + "px");
        $popupBodyEl.css("zIndex", 1);
        $popupArrowEl.css("margin-left", arrowMarginLeft + "px");

        // Animate it
        $popupBodyEl.animate(
        {
            opacity: 1
        }, 200);
    };

    TextEffects.TextPopupControl.prototype.Close = function () {
        this.base.Close.call(this);

        var $popupBodyEl = $(this._bodyEls[0]);
        $popupBodyEl.css("opacity", 0);
    };

    // TopicPopupControl

    TextEffects.TopicPopupControl = function (el) {
        this._rootEl = el;
        this._hotSpotEl = el;
        this._bodyEls = null;
        this._className = "MCTopicPopup";

        var _self = this;

        (function () {
            _self._bodyEls = $("." + _self._className + "Body", _self._rootEl).toArray();

            $(_self._hotSpotEl).click(function (e) {
                _self.Open();

                $(document.documentElement).click(function (e) {
                    _self.Close();

                    $(document.documentElement).off("click", arguments.callee);
                });

                e.stopPropagation(); // Adding the event listener above will cause the current click to also fire the above handler. Call e.stopPropagation() to prevent that.

                MadCap.Utilities.PreventDefault(e); // prevents link from navigating
            });
        })();
    };

    MadCap.Extend(TextEffects.TextEffectControl, TextEffects.TopicPopupControl);

    TextEffects.TopicPopupControl.Load = function (context) {
        var $topicPopups = $(".MCTopicPopup", context);

        for (var i = 0, length = $topicPopups.length; i < length; i++) {
            var topicPopupEl = $topicPopups[i];
            var topicPopup = new TextEffects.TopicPopupControl(topicPopupEl);
            topicPopup.Init();
        }
    };

    TextEffects.TopicPopupControl.UnLoad = function (context) {
        var $topicPopups = $(".MCTopicPopup", context);

        for (var i = 0, length = $topicPopups.length; i < length; i++)
            TextEffects.UnbindTextEffectControl( $topicPopups[i]);
    };

    TextEffects.TopicPopupControl.prototype.Init = function () {
        this.Close(false);
    };

    TextEffects.TopicPopupControl.prototype.Open = function () {
        this.base.Open.call(this);

        var $containerEl = $("<div></div>");
        $containerEl.addClass("MCTopicPopupContainer needs-pie");

        var href = MadCap.Dom.GetAttribute(this._hotSpotEl, "href");
        var iframeEl = document.createElement("iframe");
        $(iframeEl).addClass("MCTopicPopupBody");
        iframeEl.setAttribute("src", href);
        iframeEl.setAttribute("name", "MCPopup");

        $containerEl.append(iframeEl);

        var mainBody = document.body;
        $containerEl.appendTo(mainBody);

        // check if the popup is set to open at a specific width/height
        var $rootEl = $(this._rootEl);
        var width = $rootEl.attr("data-mc-width");
        var height = $rootEl.attr("data-mc-height");

        if (width != null || height != null) {
            $containerEl.css({
                "top": "50%",
                "left": "50%",
                "width": width,
                "height": height
            });

            // keep it in bounds

            var widthVal = $containerEl.width();
            var heightVal = $containerEl.height();
            var $win = $(window);
            var maxWidth = $win.width() - 100;
            var maxHeight = $win.height() - 100;

            if (widthVal > maxWidth) {
                $containerEl.css({ "width": maxWidth + "px" });
                widthVal = maxWidth;
            }

            if (heightVal > maxHeight) {
                $containerEl.css({ "height": maxHeight + "px" });
                heightVal = maxHeight;
            }

            //

            $containerEl.css({
                "margin-top": (-heightVal / 2) + "px",
                "margin-left": (-widthVal / 2) + "px"
            });
        }

        $(iframeEl).css("height", '100%');

        if ($('html').attr('data-mc-target-type') == "EPUB") {
            var offsetUpBy = ($(this._hotSpotEl).offset().top - $containerEl.offset().top) - $containerEl[0].offsetHeight/2;
            $containerEl.css({
                "margin-top": offsetUpBy + "px",
                "left": $(this._hotSpotEl).offset().left,
                "margin-left": $(this._hotSpotEl).offset().left
            });
        }

        // Animate it
        $containerEl.animate(
        {
            opacity: 1
        }, 200);

        // Add the background tint and animate it

        var bgTintEl = TextEffects.AddBackgroundTint("dark", mainBody);

        $(bgTintEl).animate(
        {
            opacity: 0.5
        }, 200);
    };

    TextEffects.TopicPopupControl.prototype.Close = function () {
        this.base.Close.call(this);

        var $containerEl = $(".MCTopicPopupContainer");
        var $parentContainer = $containerEl.parent();
        $containerEl.remove();

        TextEffects.RemoveBackgroundTint();
        if ($("#topicContent").length > 0)
            $parentContainer.css('overflow', 'auto');
    };

    //

    TextEffects.CreateLinkListTree = function (linkList, parentEl, aEl, prefix, onClick) {

        // Close all other link list popups first
        TextEffects.RemoveLinkListTrees();

        if (!prefix)
            prefix = '';

        var $listContainerEl = $("<ul class='responsive-link-list tree inner'></ul>");
        var target = $(aEl).attr("target");

        for (var i = 0, length = linkList.length; i < length; i++) {
            var currLink = linkList[i];
            var $li = $("<li class='IndexEntry IndexEntryLink tree-node tree-node-leaf'></li>").appendTo($listContainerEl);
            var $div = $("<div class='IndexTerm'></div>").appendTo($li);
            var $span = $("<span class='label'></span>").appendTo($div);
            var $a = $("<a/>").appendTo($span);

            $a.text(currLink.Title);

            var link = currLink.Link;

            $a.attr("href", prefix + link);

            $li.click(onClick);
        }

        $listContainerEl.appendTo(parentEl);
    };

    TextEffects.CreateDummyToolbarDropdown = function (button, dropDownClassName, dummyItemName, documentWithoutTopic) {        
        var links = [];
        var url = new MadCap.Utilities.Url(document.location.href);
        var dummyLink1 = { Title: dummyItemName + '1', Link: url.PlainPath + url.Fragment };
        var dummyLink2 = { Title: dummyItemName + '2', Link: url.PlainPath + url.Fragment };
        links[0] = dummyLink1;
        links[1] = dummyLink2;
        TextEffects.CreateToolbarDropdown(links, button[0], dropDownClassName, documentWithoutTopic);
    }

    TextEffects.CreateToolbarDropdown = function (links, buttonEl, buttonDropdownClass, documentWithoutTopic) {
        var $buttonEl = $(buttonEl);
        var margin = 2;
        var left = $buttonEl.position().left;
        var top = $buttonEl.position().top + $buttonEl.height() + margin;
        var prefix = '';

        TextEffects.CreateLinkListPopup(links, $buttonEl.closest(".popup-container"), top, left, buttonEl, prefix, 'toolbar-button-drop-down ' + buttonDropdownClass, true, false, documentWithoutTopic);
    }

    TextEffects.CreateLinkListPopup = function (linkList, parentEl, top, left, aEl, prefix, linkListClasses, boundX, boundY, documentWithoutTopic) {
        if (typeof linkListClasses === 'undefined')
            linkListClasses = 'link-list-popup';
        if (typeof boundX === 'undefined')
            boundX = true;
        if (typeof boundY === 'undefined')
            boundY = true;

        // Close all other link list popups first
        TextEffects.RemoveLinkListPopups();

        if (!prefix)
            prefix = '';

        var $listContainerEl = $("<div class='" + linkListClasses + " needs-pie'><ul></ul></div>");
        var $listEl = $listContainerEl.children("ul");

        var target = $(aEl).attr("target");

        for (var i = 0, length = linkList.length; i < length; i++) {
            var currLink = linkList[i];
            var hasImage = (typeof (currLink.Image) != "undefined");
            var $li = (hasImage) ? $("<li><img><a></a></li>").appendTo($listEl) : $("<li><a></a></li>").appendTo($listEl);
            var $a = $("a", $li);
            $a.attr("target", target);

            if (target == "_popup")
                $a.click(TextEffects.TopicPopup_Click);

            if (hasImage) {
                var $img = $("img", $li);
                $img.attr("src", currLink.Image);
                $img.attr("alt", currLink.Title)
                $a.text(" " + currLink.Title);
            }
            else {
                $a.text(currLink.Title);
            }

            $a.attr("href", prefix + currLink.Link);

            $li.click(TextEffects.Item_Click);
        }

        $listContainerEl.appendTo(parentEl);

        // keep the popup in bounds
        var $scrollParent = $listContainerEl.closest(".popup-container");

        // When opening help control popups in Chrome and the document isn't scrollable, the :scrollable plugin was returning null so handle that.
        if ($scrollParent.length == 0)
            $scrollParent = $(window);

        // If topic-less, then the popup-container isn't a real toolbar, it's just a bunch of loose buttons.
        // $scrollParent width would be the sum of each button width, which isn't the desired width span of toolbar. Get span width from window.
        if (documentWithoutTopic)
            $scrollParent = $(window);

        var outerWidth = $scrollParent.width();
        var outerHeight = $scrollParent.height();
        var scrollTop = $scrollParent.scrollTop();
        var scrollLeft = $scrollParent.scrollLeft();
        var popupWidth = $listContainerEl[0].offsetWidth;
        var popupHeight = $listContainerEl[0].offsetHeight;
        var offsetTop = 0;
        var offsetLeft = 0;
        /// "outer" width of topicToolbarProxy popup-containers only spans part of the topic, not the full window
        if (typeof ($scrollParent[0].classList) != "undefined" && $scrollParent[0].classList.contains("topicToolbarProxy")) {
            if (typeof ($scrollParent.offset()) != "undefined") {
                offsetTop = $scrollParent.offset().top;
                offsetLeft = $scrollParent.offset().left;
            }
        }            
        if (boundY) {
            top = Math.min(top, scrollTop + offsetTop + outerHeight - popupHeight);
            top = Math.max(top, scrollTop + offsetTop);
        }
        if (boundX) {
            left = Math.min(left, scrollLeft + offsetLeft + outerWidth - popupWidth);
            left = Math.max(left, scrollLeft + offsetLeft);
        }

        // handle keydown case
        if ((top == 0 && left == 0) || MadCap.IsIBooks()) {
            if (boundX)
                left = $(aEl).offset().left + $(aEl).width();
            if (boundY)
                top = $(aEl).offset().top + $(aEl).height();
        }

        if (MadCap.IsIBooks()) {
            $listContainerEl.css("display", "inline-block");
            if (boundX)
                left = left - aEl.offsetWidth;
            if (boundY)
                top = top - ($listContainerEl[0].offsetHeight / 2);
        }

        if (boundX && MadCap.Utilities.IsRTL()) {
            var leftOffsetAndWidth = 0;
            if (typeof ($(aEl).offset()) != "undefined") {
                leftOffsetAndWidth += $(aEl).offset().left;
            }
            if (typeof ($(aEl).width()) != "undefined") {
                leftOffsetAndWidth += $(aEl).width();
            }
            var distance = Math.min($(window).width() - leftOffsetAndWidth, $listContainerEl.width());// max of distance from edge of screen to element's left edge or container width
            left = left - distance;
        }

        $listContainerEl.css("top", top);
        $listContainerEl.css("left", left);
        $listContainerEl.css("zIndex", 1);

        $listContainerEl.hide().fadeIn(200);

        $triggerObject = documentWithoutTopic ? $(aEl) : $([document, aEl]);
        $triggerObject.click(function (e) {
            $listContainerEl.remove();

            $triggerObject.off("click", arguments.callee);
        });

        $triggerObject.keydown(function (e) {
            var e = e || windows.event;

            if (e.keyCode != 27 && e.keyCode != 13)
                return;

            if (!$listContainerEl.is(':focus'))
                return;

            $listContainerEl.remove();

            $triggerObject.off("keydown", arguments.callee);
        });

        // Don't use parent-click to dismiss drop-down if this is a topic-less htm preview stub file.
        // There's no true toolbar in a topic-less stub file, so the parent is the only thing holding
        // on to the drop-down. This click handler would instantly remove the drop-down after adding it.
        if (!documentWithoutTopic) {
            var removeClickHandler = function (e) {
                TextEffects.RemoveLinkListPopups();
                $scrollParent.off("click",  removeClickHandler);
            };

            $scrollParent.click(removeClickHandler);
        }
        
        $listContainerEl.attr("tabindex", 0);
        $listContainerEl.focus();
    };

    TextEffects.Item_Click = function (e) {
        var $a = $('a', this);
        var href = $a.attr('href');
        var frame = $a.attr('target');

        if (href && !MadCap.String.IsNullOrEmpty(href)) {
            if (frame)
                window.open(href, frame);
            else if (document.parentNode != null
                && MadCap.Utilities.HasRuntimeFileType("Topic") &&
                $("html").attr("data-mc-target-type") == "EPUB")//required by most epub reading systems that have their own iframes wrapping content.
                document.parentNode.open(href);
            else
                document.location.href = href;
        }

        MadCap.Utilities.PreventDefault(e);
    };

    TextEffects.RemoveLinkListTrees = function () {
        $(".responsive-link-list").remove();
    }
    TextEffects.RemoveLinkListPopups = function () {
        $(".link-list-popup").remove();
        $(".toolbar-button-drop-down").remove();
    };

    TextEffects.AddBackgroundTint = function (type, parentContainer) {
        if (!parentContainer)
            parentContainer = document.body;

        var $bgTintEl = $("<div id='mc-background-tint'></div>");
        $bgTintEl.addClass(type);
        $bgTintEl.appendTo(parentContainer);

        return $bgTintEl[0];
    };

    TextEffects.RemoveBackgroundTint = function () {
        $("#mc-background-tint").remove();
    };
})();
