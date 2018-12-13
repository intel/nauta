/// <reference path="jquery.js" />
/// <reference path="MadCapGlobal.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */


(function ()
{
    MadCap.CreateNamespace("Dom");

    var Dom = MadCap.Dom;

    Dom.Dataset = function (el, name)
    {
        // Don't use this for now. In Chrome, the value for a key that doesn't exist in dataset is "" instead of null or undefined which makes it ambiguous whether the value is actually "" or the key is missing.
        // https://bugs.webkit.org/show_bug.cgi?id=68877
        //if (el.dataset)
        //    return el.dataset[name];

        return el.getAttribute("data-" + MadCap.String.ToDashed(name));
    };

    Dom.GetElementsByClassName = function (className, tag, root)
    {
        tag = tag || "*";
        root = root || document;

        var nodes = new Array();
        var elements = root.getElementsByTagName(tag);

        for (var i = 0, length = elements.length; i < length; i++)
        {
            var el = elements[i];

            if ($(el).hasClass(className))
            {
                nodes[nodes.length] = el;
            }
        }

        return nodes;
    };

    Dom.GetElementsByAttribute = function (attName, attValue, tag, root)
    {
        tag = tag || "*";
        root = root || document;

        var nodes = new Array();
        var elements = root.getElementsByTagName(tag);

        for (var i = 0, length = elements.length; i < length; i++)
        {
            var el = elements[i];
            var val = Dom.GetAttribute(el, attName);

            if (val == attValue)
            {
                nodes[nodes.length] = el;
            }
        }

        return nodes;
    };

    Dom.GetChildNodeByTagName = function (root, tagName, index)
    {
        var foundNode = null;
        var numFound = -1;

        for (var currNode = root.firstChild; currNode != null; currNode = currNode.nextSibling)
        {
            if (currNode.nodeName.toLowerCase() == tagName.toLowerCase())
            {
                numFound++;

                if (numFound == index)
                {
                    foundNode = currNode;

                    break;
                }
            }
        }

        return foundNode;
    };

    Dom.GetAncestorNodeByTagName = function (root, tagName, stopEl)
    {
        stopEl = stopEl || document.body;

        var foundNode = null;
        var currNode = root.parentNode;

        while (currNode != null && currNode != stopEl)
        {
            if (currNode.nodeName.toLowerCase() == tagName.toLowerCase())
            {
                foundNode = currNode;
                break;
            }

            currNode = currNode.parentNode;
        }

        return foundNode;
    };

    Dom.GetAttribute = function (el, attName)
    {
        var value = el.getAttribute(attName);

        if (value == null)
        {
            value = el.getAttribute(attName.toLowerCase());

            if (value == null)
            {
                var namespaceIndex = attName.indexOf(":");

                if (namespaceIndex != -1)
                {
                    value = el.getAttribute(attName.substring(namespaceIndex + 1, attName.length));
                }
            }
        }

        return value;
    };

    Dom.GetAttributeInt = function (node, attributeName, defaultValue)
    {
        var intValue = defaultValue;
        var value = Dom.GetAttribute(node, attributeName);

        if (value != null)
            intValue = parseInt(value);

        return intValue;
    };

    Dom.GetAttributeBool = function (node, attributeName, defaultValue)
    {
        var boolValue = defaultValue;
        var value = Dom.GetAttribute(node, attributeName);

        if (value != null)
        {
            boolValue = MadCap.String.ToBool(value, defaultValue);
        }

        return boolValue;
    };

    Dom.GetScrollPosition = function ()
    {
        var x = 0;
        var y = 0;

        if (typeof (window.pageYOffset) != "undefined")
        {
            x = window.pageXOffset;
            y = window.pageYOffset;
        }
        else if (typeof (document.documentElement.scrollTop) != "undefined" && document.documentElement.scrollTop > 0)
        {
            x = document.documentElement.scrollLeft;
            y = document.documentElement.scrollTop;
        }

        return { X: x, Y: y };
    };
})();
