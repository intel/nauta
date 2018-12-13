/// <reference path="jquery.js" />
/// <reference path="MadCapDom.js" />

/*!
* Copyright MadCap Software
* http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
*
 * v14.1.6875.33553
*/

/*
MadCap
*/

window.MadCap = {};

MadCap.CreateNamespace = function (name)
{
    var names = name.split(".");
    var o = MadCap;

    for (var j = 0, length = names.length; j < length; j++)
    {
        var name = names[j];

        if (name == "MadCap")
            continue;

        if (typeof (o[name]) != "undefined")
        {
            o = o[name];
            continue;
        }

        o[name] = {};
        o = o[name];
    }

    return o;
};

// Polyfills

// Object.create() polyfill for IE 8 and below from https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Object/create
if (!Object.create)
{
    Object.create = function (o)
    {
        if (arguments.length > 1)
            throw new Error('Object.create implementation only accepts the first parameter.');

        function F() { }
        F.prototype = o;
        return new F();
    };
}

if (typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function () {
        return this.replace(/^\s+|\s+$/g, '');
    };
}

if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (elt /*, from*/) {
        var len = this.length >>> 0;

        var from = Number(arguments[1]) || 0;
        from = (from < 0)
             ? Math.ceil(from)
             : Math.floor(from);
        if (from < 0)
            from += len;

        for (; from < len; from++) {
            if (from in this &&
                this[from] === elt)
                return from;
        }
        return -1;
    };
}

// End Polyfills

MadCap.Extend = function (baseClass, subClass)
{
    subClass.prototype = Object.create(baseClass.prototype);
    subClass.prototype.constructor = subClass;
    subClass.prototype.base = baseClass.prototype;
};

//

MadCap.Exception = function (number, message)
{
    // Public properties

    this.Number = number;
    this.Message = message;
};

MadCap.IsIOS = function ()
{
    return MadCap.String.Contains(navigator.userAgent, "iphone") || MadCap.String.Contains(navigator.userAgent, "ipad");
};

MadCap.IsIBooks = function () {
    return MadCap.HasEpubReadingSystem() && navigator.epubReadingSystem.name == "iBooks";
};

MadCap.HasEpubReadingSystem = function () {
    return "epubReadingSystem" in navigator;
};

MadCap.IsSafari = function () {
    return MadCap.String.Contains(navigator.userAgent, "safari") && !MadCap.String.Contains(navigator.userAgent, "chrome");
};

/*
String helpers
*/

(function ()
{
    var S = MadCap.CreateNamespace("String");

    S.IsNullOrEmpty = function (str)
    {
        if (str == null)
            return true;

        if (str.length == 0)
            return true;

        return false;
    };

    S.StartsWith = function (str1, str2, caseSensitive)
    {
        if (str2 == null)
            return false;

        if (str1.length < str2.length)
            return false;

        var value1 = str1;
        var value2 = str2;

        if (!caseSensitive)
        {
            value1 = value1.toLowerCase();
            value2 = value2.toLowerCase();
        }

        if (value1.substring(0, value2.length) == value2)
        {
            return true;
        }
        else
        {
            return false;
        }
    };

    S.EndsWith = function (str1, str2, caseSensitive)
    {
        if (str2 == null)
            return false;

        if (str1.length < str2.length)
            return false;

        var value1 = str1;
        var value2 = str2;

        if (!caseSensitive)
        {
            value1 = value1.toLowerCase();
            value2 = value2.toLowerCase();
        }

        if (value1.substring(value1.length - value2.length) == value2)
        {
            return true;
        }
        else
        {
            return false;
        }
    };

    S.Contains = function (str1, str2, caseSensitive)
    {
        var value1 = caseSensitive ? str1 : str1.toLowerCase();

        if ($.isArray(str2))
        {
            for (var i = 0, length = str2.length; i < length; i++)
            {
                var value2 = caseSensitive ? str2[i] : str2[i].toLowerCase();

                if (value1.indexOf(value2) != -1)
                    return true;
            }

            return false;
        }

        var value2 = caseSensitive ? str2 : str2.toLowerCase();

        return value1.indexOf(value2) != -1;
    };

    S.Trim = function (str)
    {
        return S.TrimRight(S.TrimLeft(str));
    }

    S.TrimLeft = function (str)
    {
        var i = 0;
        var length = str.length;

        for (i = 0; i < length && str.charAt(i) == " "; i++);

        return str.substring(i, str.length);
    };

    S.TrimRight = function (str)
    {
        var i = 0;

        for (i = str.length - 1; i >= 0 && str.charAt(i) == " "; i--);

        return str.substring(0, i + 1);
    };

    S.ToBool = function (str, defaultValue)
    {
        var boolValue = defaultValue;

        if (str != null)
        {
            var stringValLower = str.toLowerCase();

            if (stringValLower != "true" && stringValLower != "false" && stringValLower != "1" && stringValLower != "0" && stringValLower != "yes" && stringValLower != "no")
            {
                throw new MadCap.Exception(-1, "The string can not be converted to a boolean value.");
            }

            boolValue = stringValLower == "true" || stringValLower == "1" || stringValLower == "yes";
        }

        return boolValue;
    };

    S.ToInt = function (str, defaultValue)
    {
        var intValue = defaultValue;

        if (str != null)
            intValue = parseInt(str);

        return intValue;
    };

    S.ToDashed = function (str)
    {
        return str.replace(/([A-Z])/g, function ($1) { return "-" + $1.toLowerCase(); });
    };

    S.LocaleCompare = function (str1, str2, lang) {
        if (lang) {
            if (typeof Intl !== "undefined" && typeof Intl.Collator !== "undefined") {
                var col = new Intl.Collator(lang);
                if (col)
                    return col.compare(str1, str2);
            }
            if (String.prototype.localeCompare)
                return str1.localeCompare(str2, lang);
        }
        return str1 < str2 ? -1 : str1 > str2 ? 1 : 0;
    };

    S.Compare = function (str1, str2) {
        var length1 = str1.length;
        var length2 = str2.length;

        for (var i = 0; i < length1 && i < length2; i++) {
            var code1 = str1.charCodeAt(i);
            var code2 = str2.charCodeAt(i);

            if (code1 < code2)
                return -1;
            else if (code1 > code2)
                return 1;
        }

        if (length1 < length2)
            return -1;
        else if (length1 > length2)
            return 1;
        else
            return 0;
    };

    S.IsPunctuation = function (str) {
        // Performs the .NET Char.IsPunctuation function
        // See https://msdn.microsoft.com/en-us/library/6w3ahtyy%28v=vs.110%29.aspx for details

        var c = str.charCodeAt(0);

        return (c >= 33 && c <= 35) || // 0021-0023
            (c >= 37 && c <= 42) || // 0025-002A
            (c >= 44 && c <= 47) || // 002C-002F
            (c == 58 || c == 59) || // 003A,003B
            (c == 63 || c == 64) || // 003F,0040
            (c >= 91 && c <= 93) || // 005B-005D
            (c == 95) || // 005F
            (c == 123) || // 007B
            (c == 125) || // 007D
            (c == 161) || // 00A1
            (c == 171) || // 00AB
            (c == 173) || // 00AD
            (c == 183) || // 00B7
            (c == 187) || // 00BB
            (c == 191) || // 00BF
            (c == 894) || // 037E
            (c == 903) || // 0387
            (c >= 1370 && c <= 1375) || // 055A-055F
            (c == 1417 || c == 1418) || // 0589,058A
            (c == 1470) || // 05BE
            (c == 1472) || // 05C0
            (c == 1475) || // 05C3
            (c == 1478) || // 05C6
            (c == 1523 || c == 1524) || // 05F3,05F4
            (c == 1548 || c == 1549) || // 060C,060D
            (c == 1563) || // 061B
            (c == 1566 || c == 1567) || // 061E,061F
            (c >= 1642 && c <= 1645) || // 066A-066D
            (c == 1748) || // 06D4
            (c >= 1792 && c <= 1805) || // 0700-070D
            (c >= 2039 && c <= 2041) || // 07F7-07F9
            (c == 2404 || c == 2405) || // 0964,0965
            (c == 2416) || // 0970
            (c == 3572) || // 0DF4
            (c >= 3663 && c <= 3675) || // 0E4F-0E5B
            (c >= 3844 && c <= 3858) || // 0F04-0F12
            (c >= 3898 && c <= 3901) || // 0F3A-0F3D
            (c == 3973) || // 0F85
            (c == 4048 || c == 4049) || // 0FD0,0FD1
            (c >= 4170 && c <= 4175) || // 104A-104F
            (c == 4347) || // 10FB
            (c >= 4961 && c <= 4968) || // 1361-1368
            (c == 5741 || c == 5742) || // 166D,166E
            (c == 5787 || c == 5788) || // 169B,169C
            (c >= 5867 && c <= 5869) || // 16EB-16ED
            (c == 5941 || c == 5942) || // 1735,1736
            (c >= 6100 && c <= 6102) || // 17D4-17D6
            (c >= 6104 && c <= 6106) || // 17D8-17DA
            (c >= 6144 && c <= 6154) || // 1800-180A
            (c == 6468 || c == 6469) || // 1944,1945
            (c == 6622 || c == 6623) || // 19DE,19DF
            (c == 6686 || c == 6687) || // 1A1E,1A1F
            (c >= 7002 && c <= 7008) || // 1B5A-1B60
            (c >= 8208 && c <= 8231) || // 2010-2027
            (c >= 8240 && c <= 8259) || // 2030-2043
            (c >= 8261 && c <= 8273) || // 2045-2051
            (c >= 8275 && c <= 8286) || // 2053-205E
            (c == 8317 || c == 8318) || // 207D,207E
            (c == 8333 || c == 8334) || // 208D,208E
            (c == 9001 || c == 9002) || // 2329,232A
            (c >= 10088 && c <= 10101) || // 2768-2775
            (c >= 10181 && c <= 10182) || // 27C5-27C6
            (c >= 10214 && c <= 10219) || // 27E6-27EB
            (c >= 10627 && c <= 10648) || // 2983-2998
            (c >= 10712 && c <= 10715) || // 29D8-29DB
            (c == 10748 || c == 10749) || // 29FC,29FD
            (c >= 11513 && c <= 11516) || // 2CF9-2CFC
            (c == 11518 || c == 11519) || // 2CFE,2CFF
            (c >= 11776 && c <= 11799) || // 2E00-2E17
            (c == 11804 || c == 11805) || // 2E1C,2E1D
            (c >= 12289 && c <= 12291) || // 3001-3003
            (c >= 12296 && c <= 12305) || // 3008-3011
            (c >= 12308 && c <= 12319) || // 3014-301F
            (c == 12336) || // 3030
            (c == 12349) || // 303D
            (c == 12448) || // 30A0
            (c == 12539) || // 30FB
            (c >= 43124 && c <= 43127) || // A874-A877
            (c == 64830 || c == 64831) || // FD3E,FD3F
            (c >= 65040 && c <= 65049) || // FE10-FE19
            (c >= 65072 && c <= 65106) || // FE30-FE52
            (c >= 65108 && c <= 65121) || // FE54-FE61
            (c == 65123) || // FE63
            (c == 65128) || // FE68
            (c == 65130 || c == 65131) || // FE6A,FE6B
            (c >= 65281 && c <= 65283) || // FF01-FF03
            (c >= 65285 && c <= 65290) || // FF05-FF0A
            (c >= 65292 && c <= 65295) || // FF0C-FF0F
            (c == 65306 || c == 65307) || // FF1A,FF1B
            (c == 65311 || c == 65312) || // FF1F,FF20
            (c >= 65339 && c <= 65341) || // FF3B-FF3D
            (c == 65343) || // FF3F
            (c == 65371) || // FF5B
            (c == 65373) || // FF5D
            (c >= 65375 && c <= 65381); // FF5F-FF65
    };

    S.Split = function (str, splitOnFunc) {
        var len = str.length;
        var results = [];
        var beginSlice = -1, endSlice = -1;

        for (var i = 0; i <= len; i++) {
            if (i == len || splitOnFunc(str.charAt(i))) {
                if (beginSlice > -1) {
                    results.push(str.slice(beginSlice, endSlice));
                    beginSlice = -1;
                }
            }
            else {
                if (beginSlice == -1)
                    beginSlice = i;
                
                endSlice = i + 1;
            }
        }

        return results;
    };
})();

(function ()
{
    MadCap.CreateNamespace("DEBUG");

    var DEBUG = MadCap.DEBUG;

    DEBUG.Log = {};

    DEBUG.Log.Create = function ()
    {
        var containerEl = document.createElement("div");
        containerEl.setAttribute("id", "DEBUG_Log");

        var headerEl = document.createElement("div");
        $(headerEl).addClass("MCDebugLogHeader");
        headerEl.appendChild(document.createTextNode("Log Console"));
        containerEl.appendChild(headerEl);

        var bodyEl = document.createElement("div");
        $(bodyEl).addClass("MCDebugLogBody");
        containerEl.appendChild(bodyEl);

        var footerEl = document.createElement("div");
        $(footerEl).addClass("MCDebugLogFooter");
        containerEl.appendChild(footerEl);

        document.body.appendChild(containerEl);

        // Set up drag & drop.
        var dd = new MadCap.DragDrop(containerEl, headerEl);
    };

    DEBUG.Log._LoadTime = new Date();

    DEBUG.Log.AddLine = function (message)
    {
        if (parent != window)
        {
            MadCap.Utilities.CrossFrame.PostMessageRequest(parent, "DEBUG-AddLine", [message], null);
            return;
        }

        var logEl = document.getElementById("DEBUG_Log");

        if (logEl == null)
            return;

        // Create the entry time element
        var now = new Date();
        var timeDiff = now - DEBUG.Log._LoadTime;
        var entryTimeEl = document.createElement("p");
        $(entryTimeEl).addClass("MCDebugLogEntryTime");
        entryTimeEl.appendChild(document.createTextNode(timeDiff + "ms" + " " + now.toLocaleTimeString()));

        // Create the entry element
        var entryEl = document.createElement("div");
        $(entryEl).addClass("MCDebugLogEntry");
        entryEl.appendChild(entryTimeEl);
        entryEl.appendChild(document.createTextNode(message));

        var logBodyEl = MadCap.Dom.GetElementsByClassName("MCDebugLogBody", "div", logEl)[0];
        logBodyEl.insertBefore(entryEl, logBodyEl.firstChild);
    };
})();
