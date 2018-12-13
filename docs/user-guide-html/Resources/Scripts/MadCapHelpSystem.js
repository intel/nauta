/// <reference path="../../Scripts/jquery.js" />
/// <reference path="../../Scripts/require.js" />
/// <reference path="../../Scripts/MadCapGlobal.js" />
/// <reference path="../../Scripts/MadCapUtilities.js" />
/// <reference path="../../Scripts/MadCapDom.js" />
/// <reference path="../../Scripts/MadCapXhr.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */

MadCap.WebHelp = MadCap.CreateNamespace("WebHelp");

//
//    Class HelpSystem
//

MadCap.WebHelp.HelpSystem = function (parentSubsystem, parentPath, xmlFile, tocPath, browseSequencePath) {
    // Private member variables

    var mSelf = this;
    var mParentSubsystem = parentSubsystem;
    var mPath = new MadCap.Utilities.Url(xmlFile).ToFolder().ToFolder().FullPath;
    var mAbsolutePath = null;
    var mSubsystems = new Array();
    var mTocPath = tocPath;
    var mBrowseSequencePath = browseSequencePath;
    var mFilterMap = null;
    var mFilterUrls = [];
    var mIndexLinkMap = new MadCap.Utilities.Dictionary();
    var mConceptMap = null;
    var mViewedConceptMap = new MadCap.Utilities.Dictionary();
    var mExists = false;
    var mAliasFile = new MadCap.WebHelp.AliasFile(mPath + "Data/Alias.xml", this);
    var mTocFile = new MadCap.WebHelp.TocFile(this, MadCap.WebHelp.TocFile.TocType.Toc);
    var mIndexXmlDoc = null;
    var mBrowseSequenceFile = new MadCap.WebHelp.TocFile(this, MadCap.WebHelp.TocFile.TocType.BrowseSequence);
    var mSkinMap = new MadCap.Utilities.Dictionary();

    // Public properties

    this.TargetType = null;
    this.DefaultStartTopic = null;
    this.InPreviewMode = null;
    this.LiveHelpOutputId = null;
    this.LiveHelpServer = null;
    this.LiveHelpEnabled = false;
    this.IsWebHelpPlus = false;
    this.ContentFolder = null;
    this.UseCustomTopicFileExtension = false;
    this.CustomTopicFileExtension = null;
    this.IsMultilingual = false;
    this.GlossaryUrl = null;
    this.SearchFilterSetUrl = null;
    this.SyncTOC = null;
    this.IndexPartialWordSearch = true;
    this.GlossaryPartialWordSearch = true;
    this.DefaultSkin = null;
    this.IsAutoMerged = false;
    this.LanguageUrl = null;
    this.BreakpointsUrl = null;
    this.PreventExternalUrls = false;
    this.IsResponsive = false;
    this.SearchUrl = null;
    this.PulsePage = null;
    this.ScriptsFolderPath = null;
    this.LanguageCode = null;
    this.LanguageName = null;
    this.IncludeCSHRuntime = null;

    // Constructor

    (function () {
    })();

    // Public functions

    this.Load = function (OnCompleteFunc) {
        MadCap.Utilities.Xhr.Load(xmlFile, true, function (xmlDoc) {
            var loaded = 0;

            function OnLoadSubHelpSystemComplete() {
                loaded++;

                if (loaded == mSubsystems.length)
                    OnCompleteFunc();
            }

            function LoadSubsystems(OnLoadSubHelpSystemComplete, OnCompleteFunc) {
                if (mSubsystems.length > 0) {
                    for (var i = 0; i < mSubsystems.length; i++) {
                        mSubsystems[i].Load(OnLoadSubHelpSystemComplete);
                    }
                }
                else {
                    OnCompleteFunc();
                }
            }

            mExists = xmlDoc != null;

            if (!mExists) {
                OnCompleteFunc();
                return;
            }
   
            this.LanguageCode = xmlDoc.documentElement.getAttribute("xml:lang");
            this.LanguageName = xmlDoc.documentElement.getAttribute("LanguageName");
            this.TargetType = xmlDoc.documentElement.getAttribute("TargetType");
            this.DefaultStartTopic = xmlDoc.documentElement.getAttribute("DefaultUrl");
            this.InPreviewMode = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "InPreviewMode", false);
            this.LiveHelpOutputId = xmlDoc.documentElement.getAttribute("LiveHelpOutputId");
            this.LiveHelpServer = xmlDoc.documentElement.getAttribute("LiveHelpServer");
            this.LiveHelpEnabled = this.LiveHelpOutputId != null;
            this.MoveContentToRoot = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "MoveOutputContentToRoot", false);
            this.ReplaceReservedCharacters = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "ReplaceReservedCharacters", false);
            this.MakeFileLowerCase = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "MakeFileLowerCase", false);
            this.PreventExternalUrls = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "PreventExternalUrls", false);
            this.IsResponsive = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "EnableResponsiveOutput", false);
            this.IncludeGlossarySearchResults = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "IncludeGlossarySearchResults", true);
            this.ResultsPerPage = MadCap.Dom.GetAttributeInt(xmlDoc.documentElement, "ResultsPerPage", 20);
            this.SearchEngine = MadCap.Dom.GetAttribute(xmlDoc.documentElement, "SearchEngine");
            this.IncludeCSHRuntime = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "IncludeCSHRuntime", true);
            this.DebugMode = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "DebugMode", false);

            if (this.SearchEngine == "Elasticsearch") {
                var elements = xmlDoc.documentElement.getElementsByTagName("Elasticsearch");
                this.Elasticsearch = elements.item(0);
            }

            var serverEnabled = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "ServerEnabled", false);
            this.IsWebHelpPlus = (this.TargetType == "WebHelpPlus" || serverEnabled) && MadCap.String.StartsWith(document.location.protocol, "http", false);

            var contentFolder = "";

            if (!this.MoveContentToRoot)
                contentFolder = "Content/";

            if (this.MakeFileLowerCase)
                contentFolder = contentFolder.toLowerCase();

            this.ContentFolder = contentFolder;
            this.UseCustomTopicFileExtension = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "UseCustomTopicFileExtension", false);
            this.CustomTopicFileExtension = MadCap.Dom.GetAttribute(xmlDoc.documentElement, "CustomTopicFileExtension");
            this.IsMultilingual = MadCap.Dom.GetAttributeBool(xmlDoc.documentElement, "Multilingual", false);

            this.GlossaryUrl = GetDataFileUrl(xmlDoc, "Glossary");
            this.TocUrl = GetDataFileUrl(xmlDoc, "Toc");
            this.SearchUrl = GetDataFileUrl(xmlDoc, "SearchUrl");
            this.PulsePage = GetDataFileUrl(xmlDoc, "PulsePage");
            this.BrowseSequencesUrl = GetDataFileUrl(xmlDoc, "BrowseSequence");
            this.IndexUrl = GetDataFileUrl(xmlDoc, "Index");
            this.SearchFilterSetUrl = GetDataFileUrl(xmlDoc, "SearchFilterSet");
            this.LanguageUrl = mPath + "Data/Language.js";
            this.BreakpointsUrl = mPath + "Data/Breakpoints.js";
            this.ScriptsFolderPath = xmlDoc.documentElement.getAttribute("PathToScriptsFolder");
            this.HasBrowseSequences = xmlDoc.documentElement.getAttribute("BrowseSequence") != null;
            this.HasToc = xmlDoc.documentElement.getAttribute("Toc") != null;
            this.TopNavTocPath = xmlDoc.documentElement.getAttribute("TopNavTocPath") == 'true';

            //

            CacheSkins.call(this, xmlDoc);
            this.DefaultSkin = this.GetSkin($(xmlDoc.documentElement).attr("SkinID"));

            this.SyncTOC = this.DefaultSkin != null && MadCap.String.ToBool(this.DefaultSkin.AutoSyncTOC, false);
            this.IndexPartialWordSearch = this.DefaultSkin == null || MadCap.String.ToBool(this.DefaultSkin.IndexPartialWordSearch, true);
            this.GlossaryPartialWordSearch = this.DefaultSkin == null || MadCap.String.ToBool(this.DefaultSkin.GlossaryPartialWordSearch, true);
            this.DisplayCommunitySearchResults = this.DefaultSkin == null || MadCap.String.ToBool(this.DefaultSkin.DisplayCommunitySearchResults, true);

            this.CommunitySearchResultsCount = 3;
            if (this.DefaultSkin != null) {
                this.CommunitySearchResultsCount = MadCap.String.ToInt(this.DefaultSkin.CommunitySearchResultsCount, 3);
            }
            //

            var subsystemsNodes = xmlDoc.getElementsByTagName("Subsystems");

            if (subsystemsNodes.length > 0 && subsystemsNodes[0].getElementsByTagName("Url").length > 0) {
                var urlNodes = xmlDoc.getElementsByTagName("Subsystems")[0].getElementsByTagName("Url");

                for (var i = 0; i < urlNodes.length; i++) {
                    var urlNode = urlNodes[i];
                    if (!urlNode)
                        continue;

                    var url = urlNode.getAttribute("Source");
                    var subPath = url.substring(0, url.lastIndexOf("/") + 1);
                    var tocPath = urlNode.getAttribute("TocPath");
                    var browseSequencePath = urlNode.getAttribute("BrowseSequencePath");

                    var subHelpSystem = new MadCap.WebHelp.HelpSystem(this, mPath + subPath, mPath + subPath + "Data/HelpSystem.xml", tocPath, browseSequencePath);
                    mSubsystems.push(subHelpSystem);
                }
            }

            
            this.LoadBreakpoints(function () {
                mSelf.LoadLanguage(function () {
                    if (!mSelf.IsAutoMerged && mSelf.IsWebHelpPlus) {
                        MadCap.Utilities.Xhr.CallWebService(mSelf.GetPath() + "Service/Service.asmx/GetSubsystems", true, function (xmlDoc, args) {
                            if (xmlDoc) {
                                $.each(xmlDoc.documentElement.childNodes, function (i, node) {
                                    if (node.nodeName == "Subsystems") {
                                        $.each(node.childNodes, function (i, node) {
                                            if (node.nodeName == "Url") {
                                                var url = node.getAttribute("Source");
                                                var subPath = url.substring(0, url.lastIndexOf("/") + 1);
                                                if (subPath) {
                                                    var subHelpSystem = new MadCap.WebHelp.HelpSystem(mSelf, mPath + subPath, mPath + subPath + "Data/HelpSystem.xml", null, null);
                                                    subHelpSystem.IsAutoMerged = true;
                                                    mSubsystems.push(subHelpSystem);
                                                }
                                            }
                                        });
                                    }
                                });
                            }

                            LoadSubsystems(OnLoadSubHelpSystemComplete, OnCompleteFunc);
                        });
                    }
                    else {
                        LoadSubsystems(OnLoadSubHelpSystemComplete, OnCompleteFunc);
                    }
                })
            });
        }, null, this);
    };

    this.GetExists = function () {
        return mExists;
    };

    this.GetMasterHelpsystem = function () {
        var master = this;

        for (var curr = master.GetParentSubsystem(); curr != null; curr = curr.GetParentSubsystem()) {
            master = curr;
        }

        return master;
    };

    this.GetParentSubsystem = function () {
        return mParentSubsystem;
    };

    this.GetPath = function () {
        return mPath;
    };

    this.GetCurrentTopicPath = function () {
        return MadCap.Utilities.Url.GetDocumentUrl().ToRelative(MadCap.Utilities.Url.GetAbsolutePath(mPath)).FullPath;
    };

    this.GetAbsolutePath = function () {
        if (mAbsolutePath == null) {
            var url = new MadCap.Utilities.Url(mPath);
            mAbsolutePath = url.IsAbsolute ? url.FullPath : new MadCap.Utilities.Url(document.location.href).Path;
        }

        return mAbsolutePath;
    };

    this.GetContentPath = function () {
        return mPath + this.ContentFolder;
    };

    this.GetSkin = function (skinID) {
        return mSkinMap.GetItem(skinID);
    };

    this.GetSkinByName = function (name) {
        var skins = this.GetSkins();
        for (var i = 0; i < skins.length; i++){
            var skin = skins[i];
            if (skin.Name == name) {
                return skin;
            }
        };

        return null;
    };

    this.GetCurrentSkin = function () {
        var url = MadCap.Utilities.Url.GetDocumentUrl();
        var skinName = url.QueryMap.GetItem("skinName") || url.HashMap.GetItem("skinName");
        if (skinName) {
            var skin = this.GetSkin(skinName);
            if (!skin)
                skin = this.GetSkinByName(skinName);
            return skin;
        }

        var cshid = url.QueryMap.GetItem('cshid');
        if (cshid) {
            var idInfo = mAliasFile.LookupID(cshid);
            if (idInfo.Skin) {
                var skin = this.GetSkin(idInfo.Skin);
                if (!skin)
                    skin = this.GetSkinByName(idInfo.Skin);
                return skin;
            }
        }

        return this.DefaultSkin;
    };

    this.GetTocPath = function (tocType) {
        return tocType == "toc" ? mTocPath : mBrowseSequencePath;
    };

    this.GetFullTocPath = function (tocType, href) {
        var subsystem = this.GetHelpSystem(href);

        if (subsystem == null)
            return null;

        var fullTocPath = new Object();

        fullTocPath.tocPath = this.GetTocPath(tocType);
        subsystem.ComputeTocPath(tocType, fullTocPath);

        return fullTocPath.tocPath;
    };

    this.GetTopicPath = function (linkUrl) {
        var path = this.GetPath();
        var isSubProject = !this.IsRoot;
        var masterHelpSystem = this.GetMasterHelpsystem();

        if (isSubProject && !masterHelpsystem.MoveContentToRoot) // add "../" to search results from child projects
            path = "../" + path;

        var docUrl = (new MadCap.Utilities.Url(document.location.href)).ToPath();
        var absUrl = docUrl.CombinePath(path + "Data/").CombinePath(linkUrl);
        var relUrl = absUrl.ToRelative(docUrl);

        // TriPane expects links relative to Content folder
        if (MadCap.Utilities.HasRuntimeFileType("TriPane") && !isSubProject && !masterHelpSystem.MoveContentToRoot) {
            relUrl = relUrl.ToRelative(masterHelpSystem.ContentFolder);
        }
        
        return relUrl;
    }

    this.GetPatchedPath = function (linkUrl) {
        if (this.ReplaceReservedCharacters)
            linkUrl = MadCap.Utilities.Url.ReplaceReservedCharacters(linkUrl, '_');
        if (this.MakeFileLowerCase)
            linkUrl = linkUrl.toLowerCase();
        if (this.UseCustomTopicFileExtension)
            linkUrl = new MadCap.Utilities.Url(linkUrl).ToExtension(this.CustomTopicFileExtension).FullPath;

        return linkUrl;
    }

    this.GetAbsoluteTopicPath = function (linkUrl) {
        var href = new MadCap.Utilities.Url(linkUrl);
        var currentUrl = (new MadCap.Utilities.Url(document.location.href)).ToPlainPath();

        return currentUrl.CombinePath(this.GetTopicPath('../' + href.FullPath).FullPath);
    }

    this.ComputeTocPath = function (tocType, tocPath) {
        if (mParentSubsystem) {
            var hsTocPath = this.GetTocPath(tocType);

            if (!MadCap.String.IsNullOrEmpty(hsTocPath)) {
                tocPath.tocPath = tocPath.tocPath ? hsTocPath + "|" + tocPath.tocPath : hsTocPath;
            }

            mParentSubsystem.ComputeTocPath(tocType, tocPath);
        }
    };

    this.GetHelpSystem = function (path) {
        var helpSystem = null;

        for (var i = 0; i < mSubsystems.length; i++) {
            helpSystem = mSubsystems[i].GetHelpSystem(path);

            if (helpSystem != null) {
                return helpSystem;
            }
        }

        if (MadCap.String.StartsWith(path, mPath, false)) {
            return this;
        }

        return null;
    };

    this.GetSubsystem = function (id) {
        return mSubsystems[id];
    };

    this.GetMergedAliasIDs = function (OnCompleteFunc) {
        mAliasFile.Load(function () {
            function OnGetIDs(ids) {
                for (var i = 0, length2 = ids.length; i < length2; i++) {
                    mergedIDs[mergedIDs.length] = ids[i];
                }

                completed++;

                if (completed == length + 1) {
                    OnCompleteFunc(mergedIDs);
                }
            }

            var mergedIDs = new Array();
            var length = mSubsystems.length;
            var completed = 0;
            var ids = mAliasFile.GetIDs();

            OnGetIDs(ids);

            for (var i = 0; i < length; i++) {
                mSubsystems[i].GetMergedAliasIDs(OnGetIDs);
            }
        });
    };

    this.GetMergedAliasNames = function (OnCompleteFunc) {
        mAliasFile.Load(function () {
            function OnGetNames(names) {
                for (var i = 0, length2 = names.length; i < length2; i++) {
                    mergedNames[mergedNames.length] = names[i];
                }

                completed++;

                if (completed == length + 1) {
                    OnCompleteFunc(mergedNames);
                }
            }

            var mergedNames = new Array();
            var length = mSubsystems.length;
            var completed = 0;
            var names = mAliasFile.GetNames();

            OnGetNames(names);

            for (var i = 0, length = mSubsystems.length; i < length; i++) {
                mSubsystems[i].GetMergedAliasNames(OnGetNames);
            }
        });
    };

    this.LookupCSHID = function (id, OnCompleteFunc) {
        mAliasFile.Load(function () {
            function OnLookupCSHID(idInfo) {
                if (found)
                    return;

                completed++;

                if (idInfo.Found) {
                    found = true;

                    OnCompleteFunc(idInfo);

                    return;
                }

                if (completed == length) {
                    OnCompleteFunc(cshIDInfo);
                }
            }

            var cshIDInfo = mAliasFile.LookupID(id);

            if (cshIDInfo.Found) {
                cshIDInfo.Topic = mSelf.GetPath() + cshIDInfo.Topic;

                OnCompleteFunc(cshIDInfo);

                return;
            }

            if (mSubsystems.length == 0) {
                OnCompleteFunc(cshIDInfo);
                return;
            }

            var found = false;
            var completed = 0;

            for (var i = 0, length = mSubsystems.length; i < length; i++) {
                mSubsystems[i].LookupCSHID(id, OnLookupCSHID);
            }
        });
    };

    this.GetTocFile = function () {
        return mTocFile;
    };

    this.GetBrowseSequenceFile = function () {
        return mBrowseSequenceFile;
    };

    this.IsMerged = function () {
        return (mSubsystems.length > 0);
    };

    this.IsRoot = function () {
        return mParentSubsystem == null;
    };

    this.IsTabletLayout = function (width) {
        if (this.IsResponsive && this.Breakpoints) {
            var tabletBreakpoint = this.Breakpoints.mediums['Tablet'];
            var prop = this.Breakpoints.prop;

            if (prop == "max-width") {
                if (!width)
                    width = window.innerWidth;

                return width <= tabletBreakpoint;
            }
            else {
                return window.matchMedia('(' + prop + ': ' + tabletBreakpoint + 'px)').matches;
            }
        }

        return false;
    };

    this.LoadLanguage = function (onCompleteFunc, loadContextObj) {
        var self = this;

        require([this.LanguageUrl], function (language) {
            self.Language = language;

            onCompleteFunc.call(loadContextObj, language);
        });
    };

    this.LoadBreakpoints = function (onCompleteFunc, loadContextObj) {
        if (this.IsResponsive && this.IsRoot()) {
            var self = this;

            require([this.BreakpointsUrl], function (breakpoints) {
                self.Breakpoints = breakpoints;

                onCompleteFunc.call(loadContextObj, breakpoints);
            });
        }
        else {
            onCompleteFunc.call(loadContextObj, null);
        }
    };

    this.LoadConcepts = function () {
        var deferred = $.Deferred();

        require([mPath + "Data/Concepts.js"], function (concepts) {
            mConceptMap = concepts;
            deferred.resolve(mConceptMap);
        });

        return deferred.promise();
    };

    this.LoadAllConcepts = function (OnCompleteFunc) {
        function OnLoadConceptsComplete() {
            completed++;

            if (completed == length + 1)
                OnCompleteFunc();
        }

        var completed = 0;
        var length = mSubsystems.length;

        this.LoadConcepts().then(OnLoadConceptsComplete);

        for (var i = 0; i < length; i++) {
            var subsystem = mSubsystems[i];

            if (!subsystem.GetExists()) {
                OnLoadConceptsComplete();
                continue;
            }

            subsystem.LoadAllConcepts(OnLoadConceptsComplete);
        }
    };

    this.GetConceptsLinks = function (conceptTerms){
        var deferred = $.Deferred();
        var links = [];

        if (this.IsWebHelpPlus) {
            function OnGetTopicsForConceptsComplete(xmlDoc, args) {
                var nodes = xmlDoc.documentElement.getElementsByTagName("Url");
                var nodeLength = nodes.length;

                for (var i = 0; i < nodeLength; i++) {
                    var node = nodes[i];
                    var title = node.getAttribute("Title");
                    var url = node.getAttribute("Source");

                    url = mPath + ((url.charAt(0) == "/") ? url.substring(1, url.length) : url);

                    links[links.length] = { Title: title, Link: url };
                }

                deferred.resolve(links);
            }

            MadCap.Utilities.Xhr.CallWebService(mPath + "Service/Service.asmx/GetTopicsForConcepts?Concepts=" + conceptTerms, true, OnGetTopicsForConceptsComplete);
        }
        else {
            function UnionLinks(links2) {
                links = links.Union(links2);
            }

            conceptTerms = conceptTerms.replace("\\;", "%%%%%");

            if (conceptTerms == "")
                deferred.resolve(links);
            else {
                var concepts = conceptTerms.split(";");

                var deferreds = [];

                deferreds.push(this.GetConceptsLinksLocal(concepts).then(UnionLinks));

                for (var i = 0; i < mSubsystems.length; i++) {
                    var subsystem = mSubsystems[i];

                    if (subsystem.GetExists())
                        deferreds.push(subsystem.GetConceptsLinks(conceptTerms).then(UnionLinks));
                }

                $.when.apply(this, deferreds).done(function () {
                    deferred.resolve(links);
                });
            }
        }

        return deferred.promise();
    };

    this.GetConceptsLinksLocal = function (concepts) {
        var links = [];
        var deferreds = [];

        for (var i = 0; i < concepts.length; i++) {
            var concept = concepts[i];

            concept = concept.replace("%%%%%", ";");
            //concept = concept.toLowerCase();

            deferreds.push(this.GetConceptLinks(concept).then(function(currLinks) {
                links = links.concat(currLinks);
            }));
        }

        var deferred = $.Deferred();

        $.when.apply(this, deferreds).done(function () {
            deferred.resolve(links);
        });

        return deferred.promise();
    };

    this.LoadTopicChunk = function (chunkId) {
        var deferred = $.Deferred();

        MadCap.Utilities.Require([mPath + "Data/SearchTopic_Chunk" + chunkId + ".js"], function (data) {
            deferred.resolve(data);
        });

        return deferred.promise();
    }

    this.GetSearchChunkIds = function (topicIds) {
        var deferred = $.Deferred();

        MadCap.Utilities.Require([mPath + "Data/Search.js"], function (data) {
            var topicChunkMap = data.t;

            var searchChunks = [];
            // find search chunks to load
            for (var i = 0; i < topicIds.length; i++)
                searchChunks.push(MadCap.Utilities.GetChunkId(topicChunkMap, topicIds[i], function (a, b) {
                    if (a < b)
                        return -1;
                    else if (a === b)
                        return 0;
                    else
                        return 1;
                }));

            deferred.resolve(searchChunks);
        });

        return deferred.promise();
    }

    this.GetConceptLinks = function (concept) {
        var deferred = $.Deferred();
        var self = this;

        this.LoadConcepts().done(function () {
            var links = [];
            var topicIds = mConceptMap[concept];

            if (!topicIds)
                deferred.resolve(links);
            else {
                self.GetSearchChunkIds(topicIds).then(function (chunkIds) {
                    var deferreds = [];

                    // load search chunks
                    for (var i = 0; i < chunkIds.length; i++) {
                        var chunkId = chunkIds[i];
                        deferreds.push(self.LoadTopicChunk(chunkId).then(function (data) {
                            for (var i = 0; i < topicIds.length; i++) {
                                var topic = data[topicIds[i]];
                                if (topic) {
                                    topic.Url = self.GetTopicPath(topic.u);
                                    links.push(topic);
                                }
                            }
                        }));
                    }

                    $.when.apply(this, deferreds).done(function () {
                        deferred.resolve(links);
                    });
                });
            }
        });

        return deferred.promise();
    };

    this.LoadToc = MadCap.Utilities.Memoize(function (tocArray) {
        var deferred = $.Deferred();
        var type = tocArray[0];
        var url = tocArray[1];

        this.GetToc(type, url, function (toc) {
            deferred.resolve(toc);
        });

        return deferred.promise();
    });

    this.GetToc = function (type, tocUrl, OnCompleteFunc) {
        var self = this;
        var url = this[type + "Url"];
        if (tocUrl) {
            url = GetComputedDataFileUrl(tocUrl);
        }

        require([url], function (toc) {
            if (typeof toc == 'undefined' || (self[type] && toc.chunks)) {
                OnCompleteFunc(toc);
                return;
            }

            self[type] = toc;

            toc.type = type;
            toc.helpSystem = self;

            // Create chunks array
            toc.chunks = [];
            toc.entries = [];
            toc.nodes = {};
            var dataPath = new MadCap.Utilities.Url(url).ToFolder();

            for (var c = 0; c < toc.numchunks; c++) {
                toc.chunks[c] = {
                    path: dataPath.AddFile(toc.prefix + c + '.js').FullPath,
                    loaded: false
                };
            }

            // Traverse toc nodes and set relationships, store nodes to merge
            var node = toc.tree;
            var merge = {};
            toc.automerge = toc.tree;

            while (node != null) {
                node.toc = toc;
                node.childrenLoaded = false;

                toc.nodes[node.i] = node;

                if (typeof node.m !== 'undefined') {
                    merge[node.m] = node;
                }

                if (typeof node.a !== 'undefined') {
                    toc.automerge = node;
                }

                if (typeof node.n !== 'undefined') {
                    for (var i = 0; i < node.n.length; i++) {
                        node.n[i].parent = node; // parent
                        if (i < node.n.length - 1)
                            node.n[i].next = node.n[i + 1]; // next sibling
                        if (i > 0)
                            node.n[i].previous = node.n[i - 1]; // previous sibling
                    }
                }

                node = GetNextNode(node);
            }

            // If we have no subsystems, return
            var mergeSystems = [];
            var hasAutoMergeSystems = false;

            for (var i = 0; i < mSubsystems.length; i++) {
                var subsystem = mSubsystems[i];

                if (subsystem.GetExists()) {
                    if (!subsystem.IsAutoMerged)
                        subsystem.MergeNode = merge[i];
                    else
                        hasAutoMergeSystems = true;

                    if (subsystem.IsAutoMerged || typeof subsystem.MergeNode !== 'undefined')
                        mergeSystems.push(subsystem);
                }
                else {
                    RemoveNode(merge[i]);
                }
            }

            if (!hasAutoMergeSystems && toc.automerge.a == 'replace')
                RemoveNode(toc.automerge);

            if (mergeSystems.length == 0) {
                OnCompleteFunc(toc);
                return;
            }

            // Merge tocs
            MadCap.Utilities.AsyncForeach(mergeSystems, function (system, callback) {
                MergeTocs(toc, system, callback);
            }, function () {
                OnCompleteFunc(toc);
            });
        });
    };

    function RemoveNode(node) {
        var parent = node.parent;
        var previous = node.previous;
        var next = node.next;

        if (previous) {
            previous.next = next;
            node.previous = null;
        }
        if (next) {
            next.previous = previous;
            node.next = null;
        }
        if (parent) {
            var i = node.parent.n.indexOf(node);
            parent.n.splice(i, 1);
            node.parent = null;
        }
    }

    function GetNextNode(node) {
        var next = null;

        if (typeof node.n != 'undefined') {
            next = node.n[0]; // first child
        }
        else if (typeof node.next != 'undefined') {
            next = node.next;
        }
        else {
            next = node;

            while (typeof next.parent != 'undefined') {
                if (typeof next.parent.next != 'undefined') {
                    next = next.parent.next;
                    break;
                }
                else {
                    next = next.parent;
                }
            }

            if (typeof next.parent == 'undefined') { // reached root
                next = null;
            }
        }

        return next;
    }

    function GetPreviousNode(node) {
        var previous = null;

        if (typeof node.previous != 'undefined') {
            previous = node.previous;

            while (typeof previous.n !== 'undefined' && previous.n.length > 0) {
                previous = previous.n[previous.n.length - 1];
            }
        }
        else if (typeof node.parent != 'undefined') {
            previous = node.parent;
        }

        return previous;
    }

    function GetTocPath(node, encode) {
        var tocPath = "";
        var linkNodeIndex = -1;
        var childNode = null;

        if (node.n && node.n.length > 0) {
            tocPath = node.toc.entries[node.i].title;
                if (encode)
                    tocPath = encodeURIComponent(tocPath);

            linkNodeIndex = 0;
        }
        else {
            linkNodeIndex = node.parent.n.indexOf(node) + 1;
        }

        if (tocPath.length > 0)
            tocPath += "|";

        tocPath += ("_____" + linkNodeIndex);

        for (var currNode = node.parent; currNode && typeof currNode.i !== 'undefined'; currNode = currNode.parent) {
            if (tocPath == null)
                tocPath = "";

            if (tocPath.length > 0)
                tocPath = "|" + tocPath;

            var entry = currNode.toc.entries[currNode.i];
            if (entry) {
                var tocTitle = entry.title;
                if (encode)
                    tocTitle = encodeURIComponent(tocTitle);
                tocPath = tocTitle + tocPath;
            }
        }

        return tocPath;
    }

    function MergeTocs(toc1, subsystem, OnCompleteFunc) {
        subsystem.GetToc(toc1.type, null, function (toc2) {
            if (typeof toc2 == 'undefined') {
                OnCompleteFunc();
                return;
            }

            var node = subsystem.IsAutoMerged ? toc1.automerge : subsystem.MergeNode;
            var newNode = toc2.tree;

            if (newNode.n !== undefined && node !== undefined) {
                var replace = node.r == 1 || (subsystem.IsAutoMerged && node.a == 'replace');
                var insertBefore = replace || (subsystem.IsAutoMerged && (node.a == 'before-head' || node.a == 'after-head'));
                var insertSibling = replace || (subsystem.IsAutoMerged && (node.a == 'before-head' || node.a == 'after-tail'));
                var parent = insertSibling ? node.parent : node;

                if (typeof parent.n == 'undefined') {
                    parent.n = [];
                }

                var childIndex = insertSibling ? parent.n.indexOf(node) + (insertBefore ? 0 : 1)
                                               : insertBefore ? 0 : parent.n.length;
                var length = newNode.n.length;

                for (var i = 0; i < length; i++) {
                    newNode.n[i].parent = parent;
                    parent.n.splice(childIndex + i, 0, newNode.n[i]);
                }

                if (replace) {
                    parent.n.splice(childIndex + length, 1);
                }

                if (childIndex > 0) {
                    parent.n[childIndex].previous = parent.n[childIndex - 1];
                    parent.n[childIndex - 1].next = parent.n[childIndex];
                }

                var lastChildIndex = childIndex + length - (replace ? 1 : 0) - 1;
                if (lastChildIndex >= 0 && lastChildIndex + 1 < parent.n.length) {
                    parent.n[lastChildIndex].next = parent.n[lastChildIndex + 1];
                    parent.n[lastChildIndex + 1].previous = parent.n[lastChildIndex];
                }

                if (subsystem.IsAutoMerged) {
                    toc1.automerge = parent.n[childIndex + length - 1];
                    toc1.automerge.a = 'after-tail';
                }
            }

            OnCompleteFunc();
        });
    }

    this.LoadTocChunk = function (toc, chunkIndex) {
        var deferred = $.Deferred();
        require([toc.chunks[chunkIndex].path], function (chunk) {
            // load entries from chunk if not loaded already
            if (!toc.chunks[chunkIndex].loaded) {
                for (var link in chunk) {
                    for (var i = 0; i < chunk[link].i.length; i++) {
                        toc.entries[chunk[link].i[i]] = {
                            link: link,
                            title: chunk[link].t[i],
                            bookmark: chunk[link].b[i]
                        };
                    }
                }

                toc.chunks[chunkIndex].loaded = true;
            }

            return deferred.resolve(chunk);
        });

        return deferred.promise();
    }

    this.GetTocEntryHref = function (entry, tocType, useHash, appendTocPath) {
        var href = null;
        var toc = entry.toc;
        var e = toc.entries[entry.i];

        if (e) {
            var link = e.link + e.bookmark;

            if (typeof entry.m == 'undefined' && link != '___') { // '___' is a placeholder for no href
                var url = null;
                var linkUrl = new MadCap.Utilities.Url(link);
                var helpSystem = toc.helpSystem;
                var helpSystemPath = helpSystem.GetPath();
                var root = helpSystem.GetMasterHelpsystem().GetContentPath();
                var hasFrame = typeof entry.f != 'undefined';

                if (!linkUrl.IsAbsolute) {
                    if (!MadCap.String.IsNullOrEmpty(helpSystemPath)) {
                        linkUrl = new MadCap.Utilities.Url(helpSystemPath).CombinePath(link);

                        url = linkUrl.ToRelative(root);
                    }
                    else {
                        linkUrl = linkUrl.ToRelative("/" + root);
                        url = linkUrl;
                    }
                }
                else {
                    url = linkUrl;
                }

                if (hasFrame || !useHash) {
                    if (url.IsAbsolute)
                        href = url.FullPath;
                    else
                        href = root + url.FullPath;
                }
                else if (MadCap.Utilities.HasRuntimeFileType("TriPane")) {
                    href = "#" + url.FullPath;
                } else {
                    href = linkUrl.FullPath;
                }
            }
        }

        if (href != null && tocType && appendTocPath) {
            var isEmbeddedTopic = window.name == "topic" && !MadCap.Utilities.HasRuntimeFileType("Default");
            var tocPath = GetTocPath(entry, true);
            if (MadCap.Utilities.HasRuntimeFileType("TriPane")) {
                href += encodeURIComponent('?' + tocType + 'Path=' + tocPath);
            } else {
                var hrefUrl = new MadCap.Utilities.Url(href);
                if (isEmbeddedTopic) {
                    href = hrefUrl.PlainPath + encodeURIComponent('?' + tocType + 'Path=' + tocPath) + hrefUrl.Fragment;
                } else {
                    href = hrefUrl.PlainPath + '?' + (tocType + 'Path=' + tocPath) + hrefUrl.Fragment;
                }
            }
        }

        return href;
    }

    this.GetTocData = function (href) {
        var tocType = null, tocPath = null, bsPath = null;
        var isTriPane = MadCap.Utilities.HasRuntimeFileType("TriPane");

        if (isTriPane && !MadCap.String.IsNullOrEmpty(href.Fragment) && href.Fragment.length > 1 || !isTriPane) {

            var queryMapUrl = (isTriPane && !(href.QueryMap.GetItem('TocPath') || href.QueryMap.GetItem('BrowseSequencesPath')) && !MadCap.String.IsNullOrEmpty(href.Fragment)) ? new MadCap.Utilities.Url(href.Fragment) : href;
            tocPath = queryMapUrl.QueryMap.GetItem('TocPath');


            if (tocPath != null) {
                tocType = 'Toc';
            }
            else {
                bsPath = queryMapUrl.QueryMap.GetItem('BrowseSequencesPath');

                if (bsPath != null) {
                    tocType = 'BrowseSequences';
                }
            }

            if (href.HashMap.GetItem('cshid') == null) {
                var iq1 = href.Query.indexOf('?');
                var iq2 = href.Query.lastIndexOf('?');
                var query = '';
                if (iq1 != iq2) {
                    query = href.Query.substr(iq1, iq2);
                }
                if (isTriPane)
                    href = new MadCap.Utilities.Url(href.Fragment.substr(1));
                if (!MadCap.String.IsNullOrEmpty(query)) {
                    href.Query = query;
                }
            }
        }
        else {
            href = new MadCap.Utilities.Url(this.DefaultStartTopic).ToRelative(this.GetContentPath());
        }

        return { TocType: tocType, TocPath: tocPath, BrowseSequencesPath: bsPath, Href: href };
    }

    this.FindTocNode = function (title, href, onCompleteFunc, tocUrl) {
        mSelf.FindNode("Toc", title, href, onCompleteFunc, tocUrl);
    }

    this.FindBrowseSequenceNode = function (title, href, onCompleteFunc) {
        mSelf.FindNode("BrowseSequences", title, href, onCompleteFunc);
    }

    this.FindNode = function (tocType, tocPath, href, onCompleteFunc, tocUrl) {
        mSelf.FindNodeInToc(tocType, tocPath, href, onCompleteFunc, tocUrl, true);
    }

    this.FindNodeInToc = function (tocType, tocPath, href, onCompleteFunc, tocUrl, loadSubsystems) {
        mSelf.LoadToc([tocType, tocUrl]).then(function (toc) {
            var root = new MadCap.Utilities.Url(mSelf.GetMasterHelpsystem().GetContentPath());
            var url = href;
            var chunkIndex = 0;
            var foundNode;

            if (!href.IsAbsolute) {
                var url = !MadCap.String.IsNullOrEmpty(root.FullPath) ? root.CombinePath(href) : href;
                url = url.ToRelative(mSelf.GetPath());

                url = new MadCap.Utilities.Url('/' + url.FullPath);
            }

            // find chunk
            for (var i = 1; i < toc.chunkstart.length; i++) {
                if (toc.chunkstart[i] <= decodeURIComponent(url.PlainPath))
                    chunkIndex++;
            }

            mSelf.LoadTocChunk(toc, chunkIndex).then(function (chunk) {
                var entry = chunk[decodeURIComponent(url.PlainPath)];

                if (typeof entry !== 'undefined') {
                    var ids = [];

                    if (!foundNode)
                        foundNode = toc.nodes[entry.i[0]];

                    if (tocPath) {
                        for (var i = 0; i < entry.i.length; i++) {
                            if (GetTocPath(toc.nodes[entry.i[i]], false) == tocPath) {
                                ids.push(entry.i[i]);
                            }
                        }
                    }
                    else {
                        for (var i = 0; i < entry.i.length; i++) {
                            if (entry.b[i].toLowerCase() == decodeURIComponent(url.Fragment).toLowerCase()) {
                                ids.push(entry.i[i]);
                            }
                        }
                    }

                    if (ids.length) {
                        onCompleteFunc(toc.nodes[ids.pop()]);
                        return;
                    }
                }

                if (mSubsystems.length > 0 && loadSubsystems) {
                    MadCap.Utilities.AsyncForeach(mSubsystems,
                        function (subSystem, callback) {
                            subSystem.FindNode(tocType, tocPath, href, function (node) {
                                if (typeof node !== 'undefined') {
                                    onCompleteFunc(node);
                                    return;
                                }
                                callback();
                            });
                        },
                        function () {
                            onCompleteFunc(foundNode);
                        }
                    );
                }
                else {
                    onCompleteFunc(foundNode);
                }
            });
        });
    }

    this.NodeDepth = function (node) {
        var depth = 1;
        while (node.parent && node.c !== undefined) {
            depth++;
            node = node.parent;
        }

        return depth;
    }

    this.LoadGlossary = function (onCompleteFunc, loadContextObj) {
        if (typeof this.Glossary != 'undefined') {
            onCompleteFunc.call(loadContextObj, this.Glossary);
            return;
        }

        var self = this;

        this.GetGlossary(function (glossary) {
            // build term map
            if (glossary && glossary.terms) {
                glossary.termMap = Object.create(null);

                for (var i = 0; i < glossary.terms.length; i++) {
                    var term = glossary.terms[i];
                    glossary.termMap[term.t.toLowerCase()] = term;
                }
            }

            self.Glossary = glossary;

            onCompleteFunc.call(loadContextObj, glossary);
        });
    }

    this.GetGlossary = function (OnCompleteFunc) {
        var self = this;

        require([this.GlossaryUrl], function (glossary) {
            function OnMergeGlossariesComplete() {
                completed++;

                if (completed == length) {
                    OnCompleteFunc(glossary);
                }
            }

            if (typeof glossary == 'undefined') {
                OnCompleteFunc(glossary);
                return;
            }

            var completed = 0;
            var length = 0;

            // Create chunks array
            glossary.chunks = [];
            var dataPath = new MadCap.Utilities.Url(mSelf.GlossaryUrl).ToFolder();
            for (var c = 0; c < glossary.numchunks; c++) {
                glossary.chunks.push({
                    helpSystem: self,
                    path: dataPath.AddFile(glossary.prefix + c + '.js').FullPath
                });
            }

            // Calculate "length" first
            for (var i = 0; i < mSubsystems.length; i++) {
                var subsystem = mSubsystems[i];

                if (!subsystem.GetExists()) { continue; }

                length++;
            }

            if (length == 0) {
                OnCompleteFunc(glossary);
                return;
            }

            for (var i = 0; i < mSubsystems.length; i++) {
                var subsystem = mSubsystems[i];

                if (!subsystem.GetExists()) {
                    continue;
                }

                MergeGlossaries(glossary, subsystem, OnMergeGlossariesComplete);
            }
        });
    };

    this.SearchGlossary = function (searchQuery) {
        var deferred = $.Deferred();
        var self = this;

        this.LoadGlossary(function (glossary) {
            var foundTerm = false;

            if (glossary && glossary.termMap) {
                var term = glossary.termMap[searchQuery.toLowerCase()];
                foundTerm = typeof term != 'undefined';
                if (foundTerm) {
                    var chunk = glossary.chunks[term.c];
                    require([chunk.path], function (data) {
                        var entry = {
                            term: term.t,
                            definition: data[term.t].d,
                            link: data[term.t].l
                        };

                        if (entry.link) {
                            var helpSystem = chunk.helpSystem;
                            var link = (new MadCap.Utilities.Url("../")).CombinePath(entry.link).FullPath;
                            entry.link = helpSystem.GetTopicPath(link).FullPath;

                            helpSystem.SearchDB.LoadTopicByUrl(link).done(function (topicID, topic) {
                                if (topic)
                                    entry.abstractText = topic.a;

                                deferred.resolve(entry);
                            });
                        }
                        else {
                            deferred.resolve(entry);
                        }
                    });
                }
            }

            if (!foundTerm)
                deferred.resolve();
        }, this);

        return deferred.promise();
    };

    this.LoadIndex = function (onCompleteFunc, loadContextObj) {
        if (typeof this.Index !== 'undefined') {
            onCompleteFunc.call(loadContextObj, this.Index);
            return;
        }

        var self = this;

        this.GetIndex(function (index) {
            self.Index = index;

            onCompleteFunc.call(loadContextObj, index);
        });
    }

    this.GetIndex = function (OnCompleteFunc) {
        var self = this;

        require([this.IndexUrl], function (index) {
            function OnMergeIndexesComplete() {
                completed++;

                if (completed == length) {
                    OnCompleteFunc(index);
                }
            }

            if (typeof index == 'undefined') {
                OnCompleteFunc(index);
                return;
            }

            var completed = 0;
            var length = 0;

            // Create chunks array
            index.chunks = [];
            var dataPath = new MadCap.Utilities.Url(mSelf.IndexUrl).ToFolder();
            for (var c = 0; c < index.numchunks; c++) {
                index.chunks.push({
                    helpSystem: self,
                    path: dataPath.AddFile(index.prefix + c + '.js').FullPath
                });
            }

            // Calculate "length" first
            for (var i = 0; i < mSubsystems.length; i++) {
                var subsystem = mSubsystems[i];

                if (!subsystem.GetExists()) { continue; }

                length++;
            }

            if (length == 0) {
                OnCompleteFunc(index);
                return;
            }

            for (var i = 0; i < mSubsystems.length; i++) {
                var subsystem = mSubsystems[i];

                if (!subsystem.GetExists()) {
                    continue;
                }

                MergeIndexes(index, subsystem, OnMergeIndexesComplete);
            }
        });
    };

    this.LoadRootIndexEntry = function (rootEntry, onCompleteFunc) {
        if (rootEntry.loaded) {
            if (onCompleteFunc)
                onCompleteFunc(rootEntry);
            return;
        }

        this.LoadIndex(function (index) {
            var chunks = typeof rootEntry.c == 'number' ? [rootEntry.c] : rootEntry.c;

            MadCap.Utilities.AsyncForeach(chunks, function (c, callback) {
                var chunk = index.chunks[c];

                // Load chunk
                require([chunk.path], function (data) {
                    var entry = data[rootEntry.t];

                    mSelf.SetIndexEntryHelpSystem(entry, chunk.helpSystem);
                    mSelf.MergeIndexEntries(rootEntry, entry);

                    callback();
                });
            },
            function () {
                mSelf.LoadIndexEntry(rootEntry);

                if (onCompleteFunc)
                    onCompleteFunc(rootEntry);
            });
        });
    }

    this.SetIndexEntryHelpSystem = function (entry, helpSystem) {
        if (entry.l) {
            $.each(entry.l, function (index, link) {
                link.helpSystem = helpSystem;
            });
        }

        if (entry.e) {
            $.each(entry.e, function (term, entry) {
                mSelf.SetIndexEntryHelpSystem(entry, helpSystem);
            });
        }
    }

    this.LoadIndexEntry = function (entry) {
        // Load link (if exists)
        if (entry.l) {
            var linkList = [];

            $.each(entry.l, function (i, indexLink) {
                var link = { Title: indexLink.t, Link: indexLink.helpSystem.GetTopicPath(".." + indexLink.u).FullPath };

                linkList[linkList.length] = link;
            });

            entry.linkList = mSelf.SortLinkList(linkList);
        }

        if (entry.e) {
            $.each(entry.e, function (term, entry) {
                mSelf.LoadIndexEntry(entry);
            });
        }

        entry.loaded = true;
    }

    this.MergeIndexEntries = function (entry1, entry2) {
        // merge links
        if (entry2.l) {
            if (typeof entry1.l == 'undefined') {
                entry1.l = entry2.l;
            }
            else {
                entry1.l = entry1.l.concat(entry2.l);
            }
        }

        // merge see also
        if (entry2.r) {
            if (typeof entry1.r == 'undefined') {
                entry1.r = entry2.r;
            }
            else if (entry1.r == 'SeeAlso' || entry2.r == 'SeeAlso') {
                entry1.r = 'SeeAlso';
            }

            if (typeof entry1.f == 'undefined') {
                entry1.f = entry2.f;
            }
            else {
                var seeAlso1 = entry1.f.split(';');
                var seeAlso2 = entry2.f.split(';');
                $.each(seeAlso2, function (i, seeAlso) {
                    if ($.inArray(seeAlso1, seeAlso)) {
                        seeAlso1.push(seeAlso);
                    }
                });
                seeAlso1.sort(function (term1, term2) {
                    var t1 = term1.toLowerCase();
                    var t2 = term2.toLowerCase();

                    return t1 < t2 ? -1 : t1 > t2 ? 1 : 0;
                });
                entry1.f = seeAlso1.join('; ');
            }
        }

        // merge subentries
        if (entry2.e) {
            if (typeof entry1.e == 'undefined') {
                entry1.e = {};
            }

            $.each(entry2.e, function (term, e) {
                if (typeof entry1.e[term] !== 'undefined') {
                    mSelf.MergeIndexEntries(entry1.e[term], e);
                }
                else {
                    entry1.e[term] = e;
                }
            });
        }
    }

    this.FindIndexEntry = function (terms, onCompleteFunc) {
        mSelf.LoadIndex(function (index) {
            if (!index.entries) {
                index.entries = {};
                $.each(index.terms, function (i, entry) {
                    index.entries[entry.t] = entry;
                });
            }

            var termList = terms.split(':');
            var termCount = termList.length;
            var rootEntry = index.entries[termList[0]];

            if (rootEntry) {
                mSelf.LoadRootIndexEntry(rootEntry, function (rootEntry) {
                    var entry = rootEntry;

                    for (var i = 1; i < termCount; i++) {
                        entry = entry.e[termList[i]];
                        if (!entry)
                            break;
                    }

                    if (onCompleteFunc)
                        onCompleteFunc(rootEntry, entry);
                });
            }
            else {
                if (onCompleteFunc)
                    onCompleteFunc();
            }
        });
    }

    this.SortLinkList = function (links) {
        links.sort(function (link1, link2) {
            var title1 = link1.Title.toLowerCase();
            var title2 = link2.Title.toLowerCase();

            return title1 < title2 ? -1 : title1 > title2 ? 1 : 0;
        });

        return links;
    }

    this.GetSearchDBs = function (OnCompleteFunc) {
        var searchDBs = new Array();
        var self = this;
        require([mPath + "Data/Search.js"], function(obj) {
            function OnGetSearchDBsComplete(searchDBs2) {
                if (searchDBs2 != null) {
                    for (var i = 0; i < searchDBs2.length; i++) {
                        searchDBs[searchDBs.length] = searchDBs2[i];
                    }
                }

                completed++;

                if (completed == length) {
                    OnCompleteFunc(searchDBs);
                }
            }

            var completed = 0;
            var length = mSubsystems.length;

            var searchDB = new MadCap.WebHelp.Search.SearchDB(self);
            self.SearchDB = searchDB;
            searchDBs[searchDBs.length] = searchDB;
            searchDB.Load(obj, function () {
                var preMerged = obj["pm"]; // TODO: add premerged variable in json file
                if (preMerged || length == 0) {
                    OnCompleteFunc(searchDBs);
                }
                else {
                    for (var i = 0; i < length; i++) {
                        var subsystem = mSubsystems[i];

                        if (!subsystem.GetExists()) {
                            OnGetSearchDBsComplete(null);
                            continue;
                        }

                        subsystem.GetSearchDBs(OnGetSearchDBsComplete);
                    }
                }
            });
        });
    };

    this.GetConcepts = function () {
        return mConceptMap;
    };

    this.GetSearchFilters = function () {
        return mFilterMap.map;
    };

    this.ParseSearchFilterDoc = function (xmlDoc) {
        filterMap = Object.create(null);

        if (xmlDoc != null) {
            var filters = xmlDoc.getElementsByTagName("SearchFilter");

            for (var i = 0; i < filters.length; i++) {
                var filter = filters[i];
                var name = filter.getAttribute("Name");
                var order = filter.getAttribute("Order");
                var concepts = filter.getAttribute("Concepts");

                if (!concepts)
                    continue;

                filterMap[name] = {
                    c: concepts,
                    o: order,
                    group: 0
                };
            }
        }

        return filterMap;
    };

    this.LoadSearchFiltersLocal = function () {
        var deferred = $.Deferred();

        require([this.SearchFilterSetUrl], function (filterMap) {
            var filters = null;
            if (filterMap)
                filters = { map: filterMap, count: 1 };

            deferred.resolve(filters);
        });

        return deferred.promise();
    };

    this.LoadSearchFilters = function () {
        var deferred = $.Deferred();

        if (!this.IsWebHelpPlus) {
            function MergeSearchFilters(filters) {
                if (filters) {
                    if (!mergedFilters) {
                        mergedFilters = filters;

                        // initialize group (filter set id)
                        for (var filterName in filters.map)
                            filters.map[filterName].group = 0;
                    }
                    else {
                        for (var filterName in filters.map) {
                            if (!mergedFilters.map[filterName]) {
                                mergedFilters.map[filterName] = filters.map[filterName];
                                mergedFilters.map[filterName].group += mergedFilters.count;
                            }
                            else // filter exists, so merge
                            {
                                var filter1 = mergedFilters.map[filterName];
                                var filter2 = filters.map[filterName];

                                // merge concepts
                                var concepts1 = filter1.c.split(';');
                                var concepts2 = filter2.c.split(';');
                                filter1.c = concepts1.Union(concepts2).join(';');

                                // merge comment
                                if (MadCap.String.IsNullOrEmpty(filter1.cm))
                                    filter1.cm = filter2.cm;
                            }
                        }
                        mergedFilters.count += filters.count;
                    }
                }
            }

            var mergedFilters;
            var deferreds = [];

            deferreds.push(this.LoadSearchFiltersLocal().then(MergeSearchFilters));

            for (var i = 0; i < mSubsystems.length; i++) {
                var subsystem = mSubsystems[i];

                if (subsystem.GetExists())
                    deferreds.push(subsystem.LoadSearchFilters().then(MergeSearchFilters));
            }

            $.when.apply(this, deferreds).done(function () {
                mFilterMap = mergedFilters;

                deferred.resolve(mergedFilters);
            });
        }
        else {
            var mSelf = this;

            MadCap.Utilities.Xhr.CallWebService(mPath + "Service/Service.asmx/GetSearchFilters", true, function (xmlDoc, args) {
                var filterMap = mSelf.ParseSearchFilterDoc(xmlDoc);

                deferred.resolve({ map: filterMap });
            });
        }

        return deferred.promise();
    };

    this.AdvanceTopic = function (tocType, moveType, tocPath, appendTocPath, href, CallBackFunc) {
        var file = null;

        mSelf.FindNode(tocType, tocPath, href, function (node) {
            if (node) {
                function AdvanceNode(node, moveType) {
                    node = moveType == 'next' ? GetNextNode(node) : GetPreviousNode(node);

                    if (node && typeof node.i !== 'undefined') {
                        mSelf.LoadTocChunk(node.toc, node.c).then(function (chunk) {
                            var entry = node.toc.entries[node.i];
                            var link = mSelf.GetTocEntryHref(node, tocType, true, appendTocPath);

                            if (link) {
                                if (MadCap.String.StartsWith(link, '#')) {
                                    link = link.substring(1);
                                }

                                CallBackFunc(link);
                            }
                            else {
                                AdvanceNode(node, moveType);
                            }
                        });
                    }
                }

                AdvanceNode(node, moveType);
            }
        });
    };

    this.SetBrowseSequencePath = function (bsPath, href) {
        var $currentTopicIndex = $(".current-topic-index-button");

        if (bsPath != null) {
            this.FindBrowseSequenceNode(bsPath, href, function (node) {
                if (node && node.parent) {
                    $currentTopicIndex.removeClass("disabled");

                    $(".sequence-index").text(node.parent.n.indexOf(node) + 1);
                    $(".sequence-total").text(node.parent.n.length);
                }
                else {
                    $currentTopicIndex.addClass("disabled");
                }
            });
        }
        else {
            $currentTopicIndex.addClass("disabled");
        }
    }

    this.GetSkins = function()
    {
       var skins = [];
       mSkinMap.ForEach( function( key, value )
       {
           skins.push(value);
       });

       return skins;
    }

    // Private member functions

    function GetDataFileUrl(xmlDoc, att) {
        var url = xmlDoc.documentElement.getAttribute(att);
        return GetComputedDataFileUrl(url);
    }

    function GetComputedDataFileUrl(url) {
        if (url == null) {
            return null;
        }

        var root = new MadCap.Utilities.Url(mPath);

        if (!root.IsAbsolute) {
            return mPath + url;
        }

        return root.AddFile(url).ToRelative(document.location.href).FullPath;
    }

    function CacheSkins(xmlDoc) {
        var skinNodes = $("CatapultSkin", xmlDoc.documentElement);

        for (var i = 0, length = skinNodes.length; i < length; i++) {
            var skinNode = skinNodes[i];
            var $skinNode = $(skinNode);
            var skinID = $skinNode.attr("SkinID");
            var skinData = {};

            for (var j = 0, length2 = skinNode.attributes.length; j < length2; j++) {
                var att = skinNode.attributes[j];
                skinData[att.name] = att.value;
            }

            var children = $skinNode.children();

            for (var j = 0, length2 = children.length; j < length2; j++) {
                var childNode = children[j];
                var name = childNode.nodeName;
                var nodeData = {};
                skinData[name] = nodeData;

                for (var k = 0, length3 = childNode.attributes.length; k < length3; k++) {
                    var att = childNode.attributes[k];
                    nodeData[att.name] = att.value;
                }
            }

            mSkinMap.Add(skinID, skinData);
        }
    }

    function ConvertGlossaryPageEntryToAbsolute(glossaryPageEntry, path) {
        if (glossaryPageEntry.nodeName.toLowerCase() == "madcap:glossarychunkref") {
            var $glossaryPageEntry = $(glossaryPageEntry);
            var href = $glossaryPageEntry.attr("src");

            if (!MadCap.String.IsNullOrEmpty(href)) {
                var url = new MadCap.Utilities.Url(path).CombinePath("../../Data/").CombinePath(href);

                var encodedPath = MadCap.Utilities.EncodeHtml("../" + url.FullPath);
                $glossaryPageEntry.attr("src", encodedPath);
            }
        }
        else {
            var entryNode = glossaryPageEntry.getElementsByTagName("a")[0];
            var href = $(entryNode).attr("href");

            if (!MadCap.String.IsNullOrEmpty(href)) {
                var url = new MadCap.Utilities.Url(path).CombinePath("../../Content/").CombinePath(href);

                var encodedPath = MadCap.Utilities.EncodeHtml("../" + url.FullPath);
                $(entryNode).attr("href", encodedPath);
            }
        }
    }

    function ConvertIndexLinksToAbsolute(indexEntry) {
        for (var i = 0; i < indexEntry.childNodes.length; i++) {
            var currNode = indexEntry.childNodes[i];

            if (currNode.nodeName == "Entries") {
                for (var j = 0; j < currNode.childNodes.length; j++)
                    ConvertIndexLinksToAbsolute(currNode.childNodes[j]);
            }
            else if (currNode.nodeName == "Links") {
                for (var j = 0; j < currNode.childNodes.length; j++) {
                    if (currNode.childNodes[j].nodeType == 1) {
                        var link = MadCap.Dom.GetAttribute(currNode.childNodes[j], "Link");

                        link = mPath + ((link.charAt(0) == "/") ? link.substring(1, link.length) : link);
                        currNode.childNodes[j].setAttribute("Link", link);
                    }
                }
            }
        }
    }

    function MergeConceptLinks(links1, links2) {
        if (!links2)
            return;

        for (var i = 0; i < links2.length; i++)
            links1[links1.length] = links2[i];
    }

    function MergeGlossaries(glossary1, subsystem, OnCompleteFunc) {
        subsystem.GetGlossary(function (glossary2) {
            if (typeof glossary2 == 'undefined') {
                OnCompleteFunc();
                return;
            }

            // Append chunk paths
            glossary1.chunks = glossary1.chunks.concat(glossary2.chunks);

            // Merge terms
            for (var i = 0, j = 0; i < glossary1.terms.length && j < glossary2.terms.length; ) {
                var entry1 = glossary1.terms[i];
                var entry2 = glossary2.terms[j];

                var term1 = entry1.t;
                var term2 = entry2.t;

                if (term1.toLowerCase() == term2.toLowerCase()) {
                    i++;
                    j++;
                }
                else if (term1.toLowerCase() > term2.toLowerCase()) {
                    entry2.c += glossary1.numchunks;
                    glossary1.terms.splice(i, 0, entry2);

                    j++;
                }
                else {
                    i++;
                }
            }

            // Append remaining nodes.
            for (; j < glossary2.terms.length; j++) {
                var entry = glossary2.terms[j];
                entry.c += glossary1.numchunks;
                glossary1.terms.push(entry);
            }

            glossary1.numchunks = glossary1.chunks.length;

            OnCompleteFunc();
        });
    }

    function MergeIndexes(index1, subsystem, OnCompleteFunc) {
        subsystem.GetIndex(function (index2) {
            if (typeof index2 == 'undefined') {
                OnCompleteFunc();
                return;
            }

            // Append chunk paths
            index1.chunks = index1.chunks.concat(index2.chunks);

            // Merge terms
            for (var i = 0, j = 0; i < index1.terms.length && j < index2.terms.length; ) {
                var entry1 = index1.terms[i];
                var entry2 = index2.terms[j];

                var term1 = entry1.s || entry1.t; // sort as or term
                var term2 = entry2.s || entry2.t;

                if (term1 == term2 && entry1.t == entry2.t) {
                    if (typeof entry1.c == 'number') {
                        entry1.c = [entry1.c];
                    }

                    var chunks = entry2.c;
                    if (typeof entry2.c == 'number') {
                        chunks = [entry2.c];
                    }

                    $.each(chunks, function (index, chunk) {
                        entry1.c.push(chunk + index1.numchunks);
                    });

                    entry1.$ = (entry1.$ === 1 && entry2.$ === 1) ? 1 : 0;

                    i++;
                    j++;
                }
                else if (term1.toLowerCase() > term2.toLowerCase() ||
                    (term1.toLowerCase() == term2.toLowerCase() && entry1.t.toLowerCase() > entry2.t.toLowerCase())) {
                    entry2.c += index1.numchunks;
                    index1.terms.splice(i, 0, entry2);

                    j++;
                }
                else {
                    i++;
                }
            }

            // Append remaining nodes.
            for (; j < index2.terms.length; j++) {
                var entry = index2.terms[j];
                entry.c += index1.numchunks;
                index1.terms.push(entry);
            }

            index1.numchunks = index1.chunks.length;

            OnCompleteFunc();
        });
    }
};

(function ()
{
    MadCap.WebHelp.HelpSystem.LoadHelpSystem = MadCap.Utilities.Memoize(function(path) {
        var deferred = $.Deferred();

        var helpSystem = new MadCap.WebHelp.HelpSystem(null, null, path, null, null);
        helpSystem.Load(function () {
            deferred.resolve(helpSystem);
        });

        return deferred.promise();
    });
})();

//
//    End class HelpSystem
//

//
//    Class TocFile
//

MadCap.WebHelp.TocFile = function (helpSystem, tocType)
{
    // Private member variables

    var mSelf = this;
    var mHelpSystem = helpSystem;
    var mTocType = tocType;
    var mInitialized = false;
    var mRootNode = null;
    var mInitOnCompleteFuncs = new Array();
    var mTocPath = null;
    var mTocHref = null;
    var mOwnerHelpSystems = new Array();

    // Public properties

    // Constructor

    (function ()
    {
    })();

    // Public member functions

    this.Init = function (OnCompleteFunc)
    {
        if (mInitialized)
        {
            if (OnCompleteFunc != null)
                OnCompleteFunc();

            return;
        }

        //

        if (OnCompleteFunc != null)
            mInitOnCompleteFuncs.push(OnCompleteFunc);

        //

        var fileName = null;

        if (tocType == MadCap.WebHelp.TocFile.TocType.Toc)
            fileName = "Toc.xml";
        else if (tocType == MadCap.WebHelp.TocFile.TocType.BrowseSequence)
            fileName = "BrowseSequences.xml";

        this.LoadToc(mHelpSystem.GetPath() + "Data/" + fileName, OnLoadTocComplete);

        function OnLoadTocComplete(xmlDoc)
        {
            mInitialized = true;

            mRootNode = xmlDoc.documentElement;

            InitOnComplete();
        }
    };

    this.LoadToc = function (xmlFile, OnCompleteFunc)
    {
        if (mTocType == MadCap.WebHelp.TocFile.TocType.Toc && mHelpSystem.IsWebHelpPlus)
        {
            MadCap.Utilities.Xhr.CallWebService(mHelpSystem.GetPath() + "Service/Service.asmx/GetToc", true, OnTocXmlLoaded, null);
        }
        else if (mTocType == MadCap.WebHelp.TocFile.TocType.BrowseSequence && mHelpSystem.IsWebHelpPlus)
        {
            MadCap.Utilities.Xhr.CallWebService(mHelpSystem.GetPath() + "Service/Service.asmx/GetBrowseSequences", true, OnTocXmlLoaded, null);
        }
        else
        {
            var xmlPath = (xmlFile.indexOf("/") == -1) ? mHelpSystem.GetPath() + "Data/" + xmlFile : xmlFile;

            MadCap.Utilities.Xhr.Load(xmlPath, false, OnTocXmlLoaded, null, null);
        }

        function OnTocXmlLoaded(xmlDoc, args)
        {
            if (!xmlDoc || !xmlDoc.documentElement)
            {
                if (OnCompleteFunc != null)
                    OnCompleteFunc(xmlDoc);

                return;
            }

            //

            if (OnCompleteFunc != null)
                OnCompleteFunc(xmlDoc);
        }
    };

    this.LoadChunk = function (parentNode, xmlFile, OnCompleteFunc)
    {
        var xmlPath = (xmlFile.indexOf("/") == -1) ? mHelpSystem.GetPath() + "Data/" + xmlFile : xmlFile;

        MadCap.Utilities.Xhr.Load(xmlFile, true, OnTocXmlLoaded, null, null);

        function OnTocXmlLoaded(xmlDoc, args)
        {
            if (!xmlDoc || !xmlDoc.documentElement)
            {
                if (OnCompleteFunc != null)
                    OnCompleteFunc(parentNode);

                return;
            }

            parentNode.removeAttribute("Chunk");

            var rootNode = xmlDoc.documentElement;

            for (var i = 0, length = rootNode.childNodes.length; i < length; i++)
            {
                var childNode = rootNode.childNodes[i];

                if (childNode.nodeType != 1) { continue; }

                var importedNode = null;

                if (typeof (xmlDoc.importNode) == "function")
                    importedNode = xmlDoc.importNode(childNode, true);
                else
                    importedNode = childNode.cloneNode(true);

                parentNode.appendChild(importedNode);
            }

            //

            if (OnCompleteFunc != null)
                OnCompleteFunc(parentNode);
        }
    }

    this.LoadMerge = function (parentNode, OnCompleteFunc)
    {
        var mergeHint = MadCap.Dom.GetAttributeInt(parentNode, "MergeHint", -1);

        if (mergeHint == -1)
        {
            OnCompleteFunc(parentNode, false, null, null);

            return;
        }

        parentNode.removeAttribute("MergeHint");

        var ownerHelpSystem = GetOwnerHelpSystem(parentNode);
        var subsystem = ownerHelpSystem.GetSubsystem(mergeHint);
        var replace = MadCap.Dom.GetAttributeBool(parentNode, "ReplaceMergeNode", false);

        if (!replace)
            parentNode.setAttribute("ownerHelpSystemIndex", mOwnerHelpSystems.length);

        mOwnerHelpSystems[mOwnerHelpSystems.length] = subsystem;

        var xmlPath = subsystem.GetPath() + "Data/" + (mTocType == MadCap.WebHelp.TocFile.TocType.Toc ? "Toc.xml" : "BrowseSequences.xml");
        var xmlDoc = MadCap.Utilities.Xhr.Load(xmlPath, true, OnTocXmlLoaded);

        function OnTocXmlLoaded(xmlDoc, args)
        {
            if (!xmlDoc || !xmlDoc.documentElement)
            {
                if (OnCompleteFunc != null)
                    OnCompleteFunc(parentNode, false, null, null);

                return;
            }

            var rootNode = xmlDoc.documentElement;
            var currNode = null;
            var isFirst = true;
            var firstNode = null;
            var lastNode = null;
            var parentXmlDoc = parentNode.ownerDocument;

            for (var i = 0, length = rootNode.childNodes.length; i < length; i++)
            {
                var childNode = rootNode.childNodes[i];

                if (childNode.nodeType != 1) { continue; }

                var importedNode = null;

                if (typeof (parentXmlDoc.importNode) == "function")
                    importedNode = parentXmlDoc.importNode(childNode, true);
                else
                    importedNode = childNode.cloneNode(true);

                if (replace)
                {
                    importedNode.setAttribute("ownerHelpSystemIndex", mOwnerHelpSystems.length - 1);

                    if (isFirst)
                    {
                        isFirst = false;

                        parentNode.parentNode.replaceChild(importedNode, parentNode);

                        firstNode = importedNode;
                        lastNode = firstNode;
                    }
                    else
                    {
                        currNode.parentNode.insertBefore(importedNode, currNode.nextSibling);

                        lastNode = importedNode;
                    }

                    currNode = importedNode
                }
                else
                {
                    parentNode.appendChild(importedNode);
                }
            }

            //

            if (OnCompleteFunc != null)
                OnCompleteFunc(parentNode, replace, firstNode, lastNode);
        }
    }

    this.AdvanceTopic = function (moveType, tocPath, href, CallBackFunc)
    {
        this.GetTocNode(tocPath, href, OnComplete);

        function OnComplete(tocNode)
        {
            if (tocNode == null)
            {
                CallBackFunc(null);
                return;
            }

            var moveNode = null;

            GetMoveTocTopicNode(moveType, tocNode, OnGetMoveTocNodeComplete);

            function OnGetMoveTocNodeComplete(moveNode)
            {
                var href = null;

                if (moveNode != null)
                {
                    href = MadCap.Dom.GetAttribute(moveNode, "Link");

                    //if (FMCIsHtmlHelp())
                    //    href = href.substring("/Content/".length);
                    //else
                    href = href.substring("/".length);

                    var hrefUrl = new MadCap.Utilities.Url(href);

                    // CHMs don't support query strings in links
                    //if (!FMCIsHtmlHelp())
                    {
                        var prefix = null;

                        if (mTocType == MadCap.WebHelp.TocFile.TocType.Toc)
                            prefix = "TocPath";
                        else if (mTocType == MadCap.WebHelp.TocFile.TocType.BrowseSequence)
                            prefix = "BrowseSequencePath";

                        var tocPath = GetTocPath(moveNode, false);
                        var newHrefUrl = hrefUrl.ToQuery(prefix + "=" + encodeURIComponent(tocPath));

                        href = newHrefUrl.FullPath;
                    }

                    var subsystem = GetOwnerHelpSystem(moveNode);

                    href = subsystem.GetPath() + href;

                    CallBackFunc(href);
                }
                else
                {
                    CallBackFunc(href);
                }
            }
        }
    };

    this.GetRootNode = function (onCompleteFunc)
    {
        this.Init(OnInit);

        function OnInit()
        {
            onCompleteFunc(mRootNode);
        }
    };

    this.GetTocNode = function (tocPath, href, onCompleteFunc)
    {
        this.Init(OnInit);

        function OnInit()
        {
            mTocPath = tocPath;
            mTocHref = href;

            //

            var steps = (tocPath == "") ? new Array(0) : tocPath.split("|");
            var linkNodeIndex = -1;

            if (steps.length > 0)
            {
                var lastStep = steps[steps.length - 1];

                if (MadCap.String.StartsWith(lastStep, "_____"))
                {
                    linkNodeIndex = parseInt(lastStep.substring("_____".length));
                    steps.splice(steps.length - 1, 1);
                }
            }

            var tocNode = mRootNode;

            for (var i = 0, length = steps.length; i < length; i++)
            {
                if (CheckChunk(tocNode))
                    return;

                if (CheckMerge(tocNode))
                    return;

                //

                tocNode = FindBook(tocNode, decodeURIComponent(steps[i]));
            }

            if (tocNode == null)
            {
                onCompleteFunc(null);

                return;
            }

            if (CheckChunk(tocNode))
            {
                return;
            }

            if (CheckMerge(tocNode))
            {
                return;
            }

            if (linkNodeIndex >= 0)
            {
                if (linkNodeIndex == 0)
                    foundNode = tocNode;
                else
                    foundNode = $(tocNode).children("TocEntry")[linkNodeIndex - 1];
            }
            else
            {
                var ownerHelpSystem = GetOwnerHelpSystem(tocNode);
                var relHref = href.ToRelative(new MadCap.Utilities.Url(ownerHelpSystem.GetPath()));
                var foundNode = FindLink(tocNode, relHref.FullPath.toLowerCase(), true);

                if (!foundNode)
                    foundNode = FindLink(tocNode, relHref.PlainPath.toLowerCase(), false);
            }

            //

            mTocPath = null;
            mTocHref = null;

            //

            onCompleteFunc(foundNode);
        }

        function CheckChunk(tocNode)
        {
            var chunk = MadCap.Dom.GetAttribute(tocNode, "Chunk");

            if (chunk != null)
            {
                mSelf.LoadChunk(tocNode, chunk,
					function (tocNode)
					{
					    mSelf.GetTocNode(mTocPath, mTocHref, onCompleteFunc)
					}
				);

                return true;
            }

            return false;
        }

        function CheckMerge(tocNode)
        {
            var mergeHint = $(tocNode).attr("MergeHint") || -1;

            if (mergeHint >= 0)
            {
                mSelf.LoadMerge(tocNode,
					function (tocNode)
					{
					    mSelf.GetTocNode(mTocPath, mTocHref, onCompleteFunc)
					}
				);

                return true;
            }

            return false;
        }
    };

    this.GetEntrySequenceIndex = function (tocPath, href, onCompleteFunc)
    {
        this.GetTocNode(tocPath, href, OnCompleteGetTocNode);

        function OnCompleteGetTocNode(tocNode)
        {
            var sequenceIndex = -1;

            if (tocNode != null)
                sequenceIndex = ComputeEntrySequenceIndex(tocNode);

            onCompleteFunc(sequenceIndex);
        }
    };

    this.GetIndexTotalForEntry = function (tocPath, href, onCompleteFunc)
    {
        this.GetTocNode(tocPath, href, OnCompleteGetTocNode);

        function OnCompleteGetTocNode(tocNode)
        {
            var total = -1;

            if (tocNode != null)
            {
                var currNode = tocNode;

                while (currNode.parentNode != mRootNode)
                {
                    currNode = currNode.parentNode;
                }

                total = MadCap.Dom.GetAttributeInt(currNode, "DescendantCount", -1);
            }

            onCompleteFunc(total);
        }
    };

    // Private member functions

    function InitOnComplete()
    {
        for (var i = 0, length = mInitOnCompleteFuncs.length; i < length; i++)
        {
            mInitOnCompleteFuncs[i]();
        }
    }

    function FindBook(tocNode, step)
    {
        var foundNode = null;

        for (var i = 0; i < tocNode.childNodes.length; i++)
        {
            if (tocNode.childNodes[i].nodeName == "TocEntry" && MadCap.Dom.GetAttribute(tocNode.childNodes[i], "Title") == step)
            {
                foundNode = tocNode.childNodes[i];

                break;
            }
        }

        return foundNode;
    }

    function FindLink(node, bodyHref, exactMatch)
    {
        var foundNode = null;
        var bookHref = MadCap.Dom.GetAttribute(node, "Link");

        if (bookHref != null)
        {
            //            if (FMCIsHtmlHelp())
            //                bookHref = bookHref.substring("/Content/".length);
            //            else
            bookHref = bookHref.substring("/".length);

            bookHref = bookHref.replace(/%20/g, " ");
            bookHref = bookHref.toLowerCase();
        }

        if (bookHref == bodyHref)
        {
            foundNode = node;
        }
        else
        {
            for (var k = 0; k < node.childNodes.length; k++)
            {
                var currNode = node.childNodes[k];

                if (currNode.nodeType != 1) { continue; }

                var currTopicHref = MadCap.Dom.GetAttribute(currNode, "Link");

                if (currTopicHref == null)
                    continue;

                //                if (FMCIsHtmlHelp())
                //                    currTopicHref = currTopicHref.substring("/Content/".length);
                //                else
                currTopicHref = currTopicHref.substring("/".length);

                currTopicHref = currTopicHref.replace(/%20/g, " ");
                currTopicHref = currTopicHref.toLowerCase();

                if (!exactMatch)
                {
                    var hashPos = currTopicHref.indexOf("#");

                    if (hashPos != -1)
                        currTopicHref = currTopicHref.substring(0, hashPos);

                    var searchPos = currTopicHref.indexOf("?");

                    if (searchPos != -1)
                        currTopicHref = currTopicHref.substring(0, searchPos);
                }

                if (currTopicHref == bodyHref)
                {
                    foundNode = currNode;

                    break;
                }
            }
        }

        return foundNode;
    }

    function GetMoveTocTopicNode(moveType, tocNode, onCompleteFunc)
    {
        if (moveType == "previous")
            GetPreviousNode(tocNode);
        else if (moveType == "next")
            GetNextNode(tocNode);

        function OnCompleteGetNode(moveNode)
        {
            var moveTopicNode = null;

            if (moveNode != null)
            {
                var link = MadCap.Dom.GetAttribute(moveNode, "Link");

                if (link == null)
                {
                    GetMoveTocTopicNode(moveType, moveNode, onCompleteFunc);

                    return;
                }

                var linkUrl = new MadCap.Utilities.Url(link);
                var ext = linkUrl.Extension.toLowerCase();
                var masterHS = mHelpSystem.GetMasterHelpsystem();

                if (masterHS.UseCustomTopicFileExtension)
                {
                    if (ext != masterHS.CustomTopicFileExtension)
                    {
                        GetMoveTocTopicNode(moveType, moveNode, onCompleteFunc);
                        return;
                    }
                }
                else if (ext != "htm" && ext != "html")
                {
                    GetMoveTocTopicNode(moveType, moveNode, onCompleteFunc);
                    return;
                }

                moveTopicNode = moveNode;
            }

            onCompleteFunc(moveTopicNode);
        }

        function GetPreviousNode(tocNode)
        {
            function OnLoadChunk(tNode)
            {
                var childTocNode = GetDeepestChild(tNode, "TocEntry");

                if (childTocNode == null)
                {
                    previousNode = tNode;
                }
                else
                {
                    previousNode = childTocNode;

                    if (CheckChunk(childTocNode, OnLoadChunk))
                    {
                        return;
                    }

                    if (CheckMerge(childTocNode, OnLoadMerge))
                        return;
                }

                OnCompleteGetNode(previousNode);
            }

            function OnLoadMerge(tNode, replaced, firstNode, lastNode)
            {
                if (replaced)
                    OnLoadChunk(lastNode);
                else
                    OnLoadChunk(tNode);
            }

            var previousNode = null;

            for (var currNode = tocNode.previousSibling; currNode != null; currNode = currNode.previousSibling)
            {
                if (currNode.nodeName == "TocEntry")
                {
                    previousNode = currNode;
                    break;
                }
            }

            if (previousNode != null)
            {
                if (CheckChunk(previousNode, OnLoadChunk))
                    return;

                if (CheckMerge(previousNode, OnLoadMerge))
                    return;

                OnLoadChunk(previousNode);

                return;
            }
            else
            {
                if (tocNode.parentNode.nodeType == 1)
                    previousNode = tocNode.parentNode;
            }

            OnCompleteGetNode(previousNode);
        }

        function GetNextNode(tocNode)
        {
            function OnLoadChunk(tNode)
            {
                var nextNode = $(tNode).children("TocEntry")[0];

                for (var currNode = tNode; currNode != null && nextNode == null; currNode = currNode.parentNode)
                {
                    nextNode = $(currNode).next("TocEntry")[0];
                }

                OnCompleteGetNode(nextNode);
            }

            function OnLoadMerge(tNode, replaced, firstNode, lastNode)
            {
                if (replaced)
                {
                    OnCompleteGetNode(firstNode);

                    return;
                }

                OnLoadChunk(tNode);
            }

            var nextNode = null;

            if (CheckChunk(tocNode, OnLoadChunk))
                return;

            if (CheckMerge(tocNode, OnLoadMerge))
                return;

            OnLoadChunk(tocNode);
        }

        function CheckChunk(tocNode, OnCompleteFunc)
        {
            var chunk = MadCap.Dom.GetAttribute(tocNode, "Chunk");

            if (chunk != null)
            {
                mSelf.LoadChunk(tocNode, chunk, OnCompleteFunc);

                return true;
            }

            return false;
        }

        function CheckMerge(tocNode, OnCompleteFunc)
        {
            var mergeHint = $(tocNode).attr("MergeHint") || -1;

            if (mergeHint >= 0)
            {
                mSelf.LoadMerge(tocNode, OnCompleteFunc);

                return true;
            }

            return false;
        }
    }

    function GetDeepestChild(tocNode, nodeName)
    {
        var node = $(tocNode).children(nodeName + ":last")[0];

        if (node != null)
        {
            var nodeChild = GetDeepestChild(node, nodeName);

            if (nodeChild != null)
                return nodeChild;

            return node;
        }

        return null;
    }

    function GetOwnerHelpSystem(tocNode)
    {
        var ownerHelpSystem = null;
        var currNode = tocNode;

        while (true)
        {
            if (currNode == currNode.ownerDocument.documentElement)
            {
                ownerHelpSystem = mHelpSystem;

                break;
            }

            var ownerHelpSystemIndex = MadCap.Dom.GetAttributeInt(currNode, "ownerHelpSystemIndex", -1);

            if (ownerHelpSystemIndex >= 0)
            {
                ownerHelpSystem = mOwnerHelpSystems[ownerHelpSystemIndex];

                break;
            }

            currNode = currNode.parentNode;
        }

        return ownerHelpSystem;
    }

    function GetTocPath(tocNode)
    {
        var tocPath = "";
        var linkNodeIndex = -1;
        var childNode = $(tocNode).children("TocEntry")[0];

        if (childNode != null)
        {
            tocPath = encodeURIComponent(MadCap.Dom.GetAttribute(tocNode, "Title"));

            linkNodeIndex = 0;
        }
        else
        {
            linkNodeIndex = $(tocNode).index() + 1;
        }

        if (tocPath.length > 0)
            tocPath += "|";

        tocPath += ("_____" + linkNodeIndex);

        for (var currNode = tocNode.parentNode; currNode != null && currNode.parentNode.nodeType == 1; currNode = currNode.parentNode)
        {
            if (tocPath == null)
                tocPath = "";

            if (tocPath.length > 0)
                tocPath = "|" + tocPath;

            tocPath = encodeURIComponent(MadCap.Dom.GetAttribute(currNode, "Title")) + tocPath;
        }

        return tocPath;
    }

    function ComputeEntrySequenceIndex(tocNode)
    {
        if (tocNode.parentNode == tocNode.ownerDocument.documentElement)
            return 0;

        var sequenceIndex = 0;

        var link = MadCap.Dom.GetAttribute(tocNode, "Link");

        if (link != null)
            sequenceIndex++;

        for (var currNode = tocNode.previousSibling; currNode != null; currNode = currNode.previousSibling)
        {
            if (currNode.nodeType != 1) { continue; }

            var descendantCount = MadCap.Dom.GetAttributeInt(currNode, "DescendantCount", 0);

            sequenceIndex += descendantCount;

            var link = MadCap.Dom.GetAttribute(currNode, "Link");

            if (link != null)
            {
                var linkUrl = new MadCap.Utilities.Url(link);
                var ext = linkUrl.Extension.toLowerCase();

                if (ext == "htm" || ext == "html")
                    sequenceIndex++;
            }
        }

        return sequenceIndex + ComputeEntrySequenceIndex(tocNode.parentNode);
    }
};

// Enumerations

MadCap.WebHelp.TocFile.TocType =
{
    "Toc": 0,
    "BrowseSequence": 1
};

//
//    End class TocFile
//

//
//    Class AliasFile
//
MadCap.WebHelp.AliasFile = function (xmlFile, helpSystem, OnLoadFunc)
{
    // Private member variables

    var mRootNode = null;
    var mHelpSystem = helpSystem;
    var mNameMap = null;
    var mIDMap = null;

    // Public properties

    // Constructor

    (function ()
    {
    })();

    // Public member functions

    this.Load = function (OnCompleteFunc)
    {
        MadCap.Utilities.Xhr.Load(xmlFile, true, function OnLoad(xmlDoc)
        {
            if (xmlDoc)
                mRootNode = xmlDoc.documentElement;

            OnCompleteFunc();
        });
    };

    this.GetIDs = function ()
    {
        var ids = new Array();

        AssureInitializedMap();

        mIDMap.ForEach(function (key, value)
        {
            ids[ids.length] = key;

            return true;
        });

        return ids;
    };

    this.GetNames = function ()
    {
        var names = new Array();

        AssureInitializedMap();

        mNameMap.ForEach(function (key, value)
        {
            names[names.length] = key;

            return true;
        });

        return names;
    };

    this.LookupID = function (id)
    {
        var found = false;
        var topic = null;
        var skin = null;

        if (id)
        {
            if (typeof (id) == "string" && id.indexOf(".") != -1)
            {
                var pipePos = id.indexOf("|");

                if (pipePos != -1)
                {
                    topic = id.substring(0, pipePos);
                    skin = id.substring(pipePos + 1);
                }
                else
                {
                    topic = id;
                }

                found = true;
            }
            else
            {
                var mapInfo = GetFromMap(id);

                if (mapInfo != null)
                {
                    found = true;
                    topic = mapInfo.Topic;
                    skin = mapInfo.Skin;
                }
            }
        }
        else
        {
            found = true;
        }

        if (topic)
            topic = mHelpSystem.ContentFolder + topic;

        return { Found: found, Topic: topic, Skin: skin };
    };

    // Private member functions

    function GetFromMap(id)
    {
        var mapInfo = null;

        AssureInitializedMap();

        if (mNameMap != null)
        {
            if (typeof (id) == "string")
            {
                mapInfo = mNameMap.GetItem(id);

                if (mapInfo == null)
                    mapInfo = mIDMap.GetItem(id);
            }
            else if (typeof (id) == "number")
            {
                mapInfo = mIDMap.GetItem(id.toString());
            }
        }

        return mapInfo;
    }

    function AssureInitializedMap()
    {
        if (mNameMap == null)
        {
            if (mRootNode)
            {
                mNameMap = new MadCap.Utilities.Dictionary(true);
                mIDMap = new MadCap.Utilities.Dictionary();

                var maps = mRootNode.getElementsByTagName("Map");

                for (var i = 0; i < maps.length; i++)
                {
                    var topic = maps[i].getAttribute("Link");
                    var skin = maps[i].getAttribute("Skin");
                    var currMapInfo = { Topic: topic, Skin: skin };

                    var name = maps[i].getAttribute("Name");

                    if (name != null)
                        mNameMap.Add(name, currMapInfo);

                    var resolvedId = maps[i].getAttribute("ResolvedId");

                    if (resolvedId != null)
                        mIDMap.Add(resolvedId, currMapInfo);
                }
            }
        }
    }
};

//
//    End class AliasFile
//

//
//    Class IndexEntry
//

MadCap.WebHelp.IndexEntry = function (indexEntry, level)
{
    // Public properties

    var indexLinks = MadCap.Dom.GetChildNodeByTagName(indexEntry, "Links", 0).childNodes;
    var numNodes = indexLinks.length;
    var nodeCount = 0;

    this.Term = MadCap.Dom.GetAttribute(indexEntry, "Term");
    this.IndexLinks = new Array();
    this.Level = level;
    this.GeneratedReferenceType = MadCap.Dom.GetAttribute(indexEntry, "GeneratedReferenceType");

    for (var i = 0; i < numNodes; i++)
    {
        var indexLink = indexLinks[i];

        if (indexLink.nodeType != 1) { continue; }

        this.IndexLinks[nodeCount] = new MadCap.WebHelp.IndexLink(indexLink);

        nodeCount++;
    }
};

//
//    End class IndexEntry
//

//
//    Class IndexLink
//

MadCap.WebHelp.IndexLink = function (indexLink)
{
    this.Title = MadCap.Dom.GetAttribute(indexLink, "Title");
    this.Link = MadCap.Dom.GetAttribute(indexLink, "Link");
};

//
//    End class IndexLink
//
