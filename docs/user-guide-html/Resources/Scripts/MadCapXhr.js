/// <reference path="MadCapGlobal.js" />
/// <reference path="MadCapUtilities.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */

(function () {
    MadCap.Utilities.Xhr = function (args, LoadFunc, loadContextObj) {
        var mSelf = this;
        this._XmlDoc = null;
        this._XmlHttp = null;
        this._Args = args;
        this._LoadFunc = LoadFunc;
        this._LoadContextObj = loadContextObj;

        this.OnreadystatechangeLocal = function () {
            if (mSelf._XmlDoc.readyState == 4) {
                mSelf._XmlDoc.onreadystatechange = Xhr._Noop;

                var xmlDoc = null;

                if (mSelf._XmlDoc.documentElement != null)
                    xmlDoc = mSelf._XmlDoc;

                if (mSelf._LoadContextObj == null)
                    mSelf._LoadFunc(xmlDoc, mSelf._Args);
                else
                    mSelf._LoadFunc.call(mSelf._LoadContextObj, xmlDoc, mSelf._Args);
            }
        };

        this.OnreadystatechangeRemote = function () {
            if (mSelf._XmlHttp.readyState == 4) {
                mSelf._XmlHttp.onreadystatechange = Xhr._Noop;

                var xmlDoc = null;

                if (mSelf._XmlHttp.responseXML != null && mSelf._XmlHttp.responseXML.documentElement != null)
                    xmlDoc = mSelf._XmlHttp.responseXML;

                if (mSelf._LoadContextObj == null)
                    mSelf._LoadFunc(xmlDoc, mSelf._Args);
                else
                    mSelf._LoadFunc.call(mSelf._LoadContextObj, xmlDoc, mSelf._Args);
            }
        };
    };

    var Xhr = MadCap.Utilities.Xhr;

    // Private functions

    Xhr.prototype._LoadLocal = function (xmlFile, async) {
        if (window.ActiveXObject) {
            this._XmlDoc = Xhr._GetMicrosoftXmlDomObject();
            this._XmlDoc.async = async;

            if (this._LoadFunc)
                this._XmlDoc.onreadystatechange = this.OnreadystatechangeLocal;

            try {
                if (!this._XmlDoc.load(xmlFile))
                    this._XmlDoc = null;
            }
            catch (err) {
                this._XmlDoc = null;
            }
        }
        else if (window.XMLHttpRequest) {
            this._LoadRemote(xmlFile, async); // window.XMLHttpRequest also works on local files
        }

        return this._XmlDoc;
    };

    Xhr.prototype._LoadRemote = function (xmlFile, async) {
        this._XmlHttp = Xhr._GetXhrObject();

        if (this._LoadFunc)
            this._XmlHttp.onreadystatechange = this.OnreadystatechangeRemote;

        try {
            this._XmlHttp.open("GET", xmlFile, async);
            this._XmlHttp.send(null);

            if (!async && (this._XmlHttp.status == 0 || this._XmlHttp.status == 200))
                this._XmlDoc = this._XmlHttp.responseXML;
        }
        catch (err) {
            this._XmlHttp.abort();

            if (this._LoadFunc) {
                if (this._LoadContextObj == null)
                    this._LoadFunc(null, this._Args);
                else
                    this._LoadFunc.call(this._LoadContextObj, null, this._Args);
            }
        }

        return this._XmlDoc;
    };

    // Public functions

    Xhr.prototype.Load = function (xmlFile, async) {
        var xmlDoc = null;
        var protocolType = document.location.protocol;

        if (protocolType == "file:" || protocolType == "mk:" || protocolType == "ms-its:" || protocolType == "app:")
            xmlDoc = this._LoadLocal(xmlFile, async);
        else if (protocolType == "http:" || protocolType == "https:")
            xmlDoc = this._LoadRemote(xmlFile, async);

        return xmlDoc;
    };

    Xhr.LoadXmlString = function (xmlString) {
        var xmlDoc = null;

        if (window.ActiveXObject) {
            xmlDoc = Xhr._GetMicrosoftXmlDomObject();
            xmlDoc.async = false;
            xmlDoc.loadXML(xmlString);
        }
        else if (DOMParser) {
            var parser = new DOMParser();

            xmlDoc = parser.parseFromString(xmlString, "text/xml");
        }

        return xmlDoc;
    };

    Xhr.CreateXmlDocument = function (rootTagName) {
        var rootXml = "<" + rootTagName + " />";
        var xmlDoc = Xhr.LoadXmlString(rootXml);

        return xmlDoc;
    };

    Xhr.GetOuterXml = function (xmlDoc) {
        var xml = null;

        if (window.ActiveXObject) {
            xml = xmlDoc.xml;
        }
        else if (window.XMLSerializer) {
            var serializer = new XMLSerializer();

            xml = serializer.serializeToString(xmlDoc);
        }

        return xml;
    };

    Xhr.ImportNode = function (xmlDoc, xmlNode) {
        if (typeof (xmlDoc.importNode) == "function") {
            return xmlDoc.importNode(xmlNode, true);
        }

        return xmlNode.cloneNode(true);
    }

    Xhr.CallWebService = function (webServiceUrl, async, onCompleteFunc, onCompleteArgs) {
        var xmlParser = new Xhr(onCompleteArgs, onCompleteFunc, null);
        var xmlDoc = xmlParser.Load(webServiceUrl, async);

        return xmlDoc;
    };

    // Static (private)

    Xhr._MicrosoftXmlDomProgIDs = ["Msxml2.DOMDocument.6.0", "Msxml2.DOMDocument", "Microsoft.XMLDOM"];
    Xhr._MicrosoftXmlHttpProgIDs = ["Msxml2.XMLHTTP.6.0", "Msxml2.XMLHTTP", "Microsoft.XMLHTTP"];
    Xhr._MicrosoftXmlDomProgID = null;
    Xhr._MicrosoftXmlHttpProgID = null;
    Xhr._FilePathToXmlStringMap = new MadCap.Utilities.Dictionary();
    Xhr._LoadingFilesPathMap = new MadCap.Utilities.Dictionary();
    Xhr._LoadingFromQueue = false;

    // Static (public)

    Xhr.ForceUseJS = false;

    Xhr.Load = function (xmlPath, async, LoadFunc, args, loadContextObj) {
        function OnScriptLoaded() {
            Xhr._LoadingFilesPathMap.Remove(jsFileUrl.FullPath);

            var xmlString = Xhr._FilePathToXmlStringMap.GetItem(jsFileUrl.Name);

            if (xmlString != null) // occurs if this is reached from the script node's error event (when the file doesn't exist)
            {
                Xhr._FilePathToXmlStringMap.Remove(jsFileUrl.Name);
                xmlDoc = Xhr.LoadXmlString(xmlString);
            }

            // Check if there are any more in the queue. Do this before calling the callback function since the callback function might invoke another call to this same function.
            Xhr._LoadingFilesPathMap.ForEach(function (key, value) {
                var loadingFileUrl = new MadCap.Utilities.Url(key);
                var loadInfo = value;

                if (loadingFileUrl.Name == fileName && loadingFileUrl.FullPath != jsFileUrl.FullPath) {
                    Xhr._LoadingFilesPathMap.Remove(loadingFileUrl.FullPath);
                    Xhr._LoadingFromQueue = true;
                    Xhr.Load(loadingFileUrl.FullPath, loadInfo.async, loadInfo.LoadFunc, loadInfo.args, loadInfo.loadContextObj);

                    return false;
                }

                return true;
            });

            // Call the callback function
            if (loadContextObj == null) {
                LoadFunc(xmlDoc, args);
            }
            else {
                LoadFunc.call(loadContextObj, xmlDoc, args);
            }
        }

        var xmlDoc = null;

        if (Xhr.ForceUseJS || (Boolean(!window.ActiveXObject) && MadCap.String.StartsWith(document.location.protocol, "file")))
        {
            var xmlFileUrl = new MadCap.Utilities.Url(xmlPath);
            var jsFileUrl = xmlFileUrl.ToExtension("js");
            var fileName = jsFileUrl.Name;

            Xhr._LoadingFilesPathMap.Add(jsFileUrl.FullPath, { async: async, LoadFunc: LoadFunc, args: args, loadContextObj: loadContextObj });

            var loadingFileWithSameName = false;

            Xhr._LoadingFilesPathMap.ForEach(function (key, value) {
                var loadingFileUrl = new MadCap.Utilities.Url(key);
                var loadInfo = value;

                if (loadingFileUrl.Name == fileName && loadingFileUrl.FullPath != jsFileUrl.FullPath) {
                    loadingFileWithSameName = true;

                    return false;
                }

                return true;
            });

            if (Xhr._LoadingFromQueue || !loadingFileWithSameName) {
                Xhr._LoadingFromQueue = false;

                //

                MadCap.Utilities.LoadScript(jsFileUrl.FullPath, OnScriptLoaded, OnScriptLoaded);
            }
        }
        else {
            var xmlParser = new Xhr(args, LoadFunc, loadContextObj);
            xmlDoc = xmlParser.Load(xmlPath, async);
        }

        return xmlDoc;
    };

    Xhr._Noop = function () {
    };

    Xhr._GetMicrosoftXmlDomObject = function () {
        var obj = null;

        if (Xhr._MicrosoftXmlDomProgID == null) {
            for (var i = 0; i < Xhr._MicrosoftXmlDomProgIDs.length; i++) {
                var progID = Xhr._MicrosoftXmlDomProgIDs[i];

                try {
                    obj = new ActiveXObject(progID);

                    Xhr._MicrosoftXmlDomProgID = progID;

                    break;
                }
                catch (ex) {
                }
            }
        }
        else {
            obj = new ActiveXObject(Xhr._MicrosoftXmlDomProgID);
        }

        return obj;
    };

    Xhr._GetXhrObject = function () {
        if (window.XMLHttpRequest) {
            return function () {
                return new window.XMLHttpRequest();
            };
        }
        else if (window.ActiveXObject) {
            return function () {
                var xhr = null;

                if (Xhr._MicrosoftXmlHttpProgID == null) {
                    for (var i = 0; i < Xhr._MicrosoftXmlHttpProgIDs.length; i++) {
                        var progID = Xhr._MicrosoftXmlHttpProgIDs[i];

                        try {
                            xhr = new ActiveXObject(progID);

                            Xhr._MicrosoftXmlHttpProgID = progID;

                            break;
                        }
                        catch (ex) {
                        }
                    }
                }
                else {
                    xhr = new ActiveXObject(Xhr._MicrosoftXmlHttpProgID);
                }

                return xhr;
            };
        }
    } ();
})();
