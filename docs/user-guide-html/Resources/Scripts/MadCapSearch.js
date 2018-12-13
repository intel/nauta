/// <reference path="../../Scripts/jquery.js" />
/// <reference path="../../Scripts/MadCapGlobal.js" />
/// <reference path="../../Scripts/MadCapUtilities.js" />
/// <reference path="../../Scripts/MadCapDom.js" />
/// <reference path="../../Scripts/MadCapXhr.js" />
/// <reference path="../../Scripts/MadCapFeedback.js" />
/// <reference path="MadCapHelpSystem.js" />
/// <reference path="MadCapParser.js" />

/*!
 * Copyright MadCap Software
 * http://www.madcapsoftware.com/
 * Unlicensed use is strictly prohibited
 *
 * v14.1.6875.33553
 */


(function () {
    MadCap.WebHelp = MadCap.CreateNamespace("WebHelp");

    MadCap.WebHelp.SearchPane = function (helpSystem, container) {
        this._Init = false;
        this._Container = container;
        this._HelpSystem = helpSystem;
        this._FeedbackController = null;
        this._Parser = null;
        this._Filters = null;
        this._Set = null;
        this._FilteredSet = null;
        this._Highlight = "";
        this._DownloadedSynonymXmlDocRootNode = null;
    };

    var SearchPane = MadCap.WebHelp.SearchPane;

    SearchPane.SearchDBs = new Array(); // Fix from being static/global.

    SearchPane.prototype.Init = function (OnCompleteFunc) {
        if (this._Init) {
            if (OnCompleteFunc) {
                OnCompleteFunc.call(this);
            }

            return;
        }

        var mSelf = this;

        if (this._HelpSystem.LiveHelpEnabled) {
            this._FeedbackController = MadCap.WebHelp.LoadFeedbackController(this._HelpSystem.LiveHelpServer);
            this._FeedbackController.Init(function () {
                if (mSelf._FeedbackController.FeedbackActive) {
                    mSelf._FeedbackController.GetSynonymsFile(mSelf._HelpSystem.LiveHelpOutputId, null, function (synonymsXmlDoc, onCompleteArgs) {
                        var xmlDoc = MadCap.Utilities.Xhr.LoadXmlString(synonymsXmlDoc);

                        if (xmlDoc != null)
                            mSelf._DownloadedSynonymXmlDocRootNode = xmlDoc.documentElement;

                        OnGetSynonymsComplete();
                    }, null);
                }
                else {
                    OnGetSynonymsComplete();
                }
            });
        }
        else {
            OnGetSynonymsComplete();
        }

        function OnGetSynonymsComplete() {
            if (!mSelf._HelpSystem.IsWebHelpPlus) {
                mSelf._HelpSystem.GetSearchDBs(OnGetSearchDBsComplete);
            }
            else {
                OnGetSearchDBsComplete(null);
            }
        }

        function OnGetSearchDBsComplete(searchDBs) {
            SearchPane.SearchDBs = searchDBs;

            mSelf._Filters = new Search.Filters(mSelf._HelpSystem);
            mSelf._Filters.Load(function () {
                mSelf._Init = true;

                if (OnCompleteFunc) {
                    OnCompleteFunc.call(mSelf);
                }
            });
        }
    };

    SearchPane.prototype.Search = function (searchQuery, options) {
        if (MadCap.String.IsNullOrEmpty(MadCap.String.Trim(searchQuery))) {
            return;
        }

        this._Container.addClass("loading");

        var deferred = $.Deferred();

        this.Init(function () {
            var results = {};
            var deferredSearches = [];

            if (options.searchContent) {
                var filterName = options.content ? options.content.filterName : null;

                var searchContent = !this._HelpSystem.IsWebHelpPlus ?
                    this.DoSearch(searchQuery, filterName) :
                    this.DoSearchWebHelpPlus(searchQuery, filterName);

                deferredSearches.push(searchContent.then(function (searchResults, includedTerms) {
                    results.content = searchResults;
                    results.contentTotal = searchResults != null ? searchResults.length : 0;
                    results.includedTerms = includedTerms;
                    results.clientPaging = true; // full result set is returned, client responsible for paging
                }));
            }

            if (options.searchGlossary) {
                deferredSearches.push(this._HelpSystem.SearchGlossary(searchQuery).then(function (searchResults) {
                    results.glossary = searchResults;
                }));
            }

            if (options.searchCommunity) {
                if (this._FeedbackController && this._FeedbackController.PulseActive) {
                    var searchCommunity = this._FeedbackController.GetPulseSearchResults(this._HelpSystem.LiveHelpOutputId, searchQuery, options.community.pageSize, options.community.pageIndex);

                    deferredSearches.push(searchCommunity.then(function (searchResults) {
                        results.community = searchResults;
                    }));
                }
            }

            $.when.apply(this, deferredSearches).done($.proxy(function () {
                this._Container.removeClass("loading");

                deferred.resolve(results);
            }, this));
        });

        return deferred.promise();
    };

    SearchPane.prototype.DoSearch = function (searchQuery, filterName) {
        var deferred = $.Deferred();

        this._Parser = new Search.Parser(searchQuery);
        var root = null;

        try {
            root = this._Parser.ParseExpression();
        }
        catch (err) {
            alert("Ensure that the search string is properly formatted.");
            root = null;
        }

        if (!root) {
            return deferred.resolve();
        }

        var searchDB = SearchPane.SearchDBs[0];
        if (this._DownloadedSynonymXmlDocRootNode != null && searchDB.DownloadedSynonymFile == null) {
            searchDB.DownloadedSynonymFile = new Search.SynonymFile(this._DownloadedSynonymXmlDocRootNode, searchDB.Stemmer);
        }

        var mSelf = this;

        root.Evaluate(filterName, function (resultSet) {
            Search.LoadResultData(resultSet).then(function (resultSet, terms) {
                mSelf._Set = resultSet;

                if (mSelf._Set) {
                    mSelf._Set.sort(function (a, b) {
                        return b.Score - a.Score;
                    });
                }

                MadCap.Utilities.ClearRequireCache();

                deferred.resolve(mSelf._Set, terms);
            });
        });

        return deferred.promise();
    };

    SearchPane.prototype.DoSearchWebHelpPlus = function (searchQuery, filterName) {
        var self = this;
        var deferred = $.Deferred();

        function OnGetSearchResultsComplete(xmlDoc, args) {
            var resultSet = [];
            
            if (xmlDoc) {
                var results = xmlDoc.getElementsByTagName("Result");
                var resultsLength = results.length;

                var baseUrl = new MadCap.Utilities.Url(document.location.pathname);

                if (!self._HelpSystem.SearchUrl) {
                    // tripane only
                    if (!MadCap.String.EndsWith(document.location.pathname, "/")) // http://MyServer/MyHTML5/ vs. http://MyServer/MyHTML5/Default.htm
                        baseUrl = baseUrl.ToFolder();
                    baseUrl = baseUrl.CombinePath(self._HelpSystem.ContentFolder);
                }

                for (var i = 0; i < resultsLength; i++) {
                    var resultNode = results[i];
                    var rank = MadCap.Dom.GetAttributeInt(resultNode, "Rank", -1);
                    var title = resultNode.getAttribute("Title");
                    var link = resultNode.getAttribute("Link");
                    var linkUrl = new MadCap.Utilities.Url(link).ToRelative(baseUrl);
                    var abstractText = resultNode.getAttribute("AbstractText");

                    if (MadCap.String.IsNullOrEmpty(title))
                        title = resultNode.getAttribute("Filename");

                    var searchResult = new Search.SearchResult(rank, null, title, linkUrl.FullPath, unescape(abstractText));

                    resultSet.push(searchResult);
                }
            }

            //

            deferred.resolve(resultSet);
        }

        MadCap.Utilities.Xhr.CallWebService(self._HelpSystem.GetPath() + "Service/Service.asmx/GetSearchResults?SearchString=" + encodeURIComponent(searchQuery) + "&FilterName=" + encodeURIComponent(filterName), true, OnGetSearchResultsComplete, null);

        var searchTerms = searchQuery.split(" ");
        var firstStem = true;

        this._Highlight = "?Highlight=";

        for (var i = 0; i < searchTerms.length; i++) {
            if (!firstStem)
                this._Highlight += "||";
            else
                firstStem = false;

            this._Highlight += searchTerms[i];
        }

        return deferred.promise();
    };

    var Search = MadCap.CreateNamespace("WebHelp.Search");

    //
    //    Class SearchDB
    //

    MadCap.WebHelp.Search.SearchDB = function (helpSystem) {
        // Public properties

        this.RelevanceWeight = 0;
        this.TopicChunkMap = null;
        this.UrlChunkMap = null;
        this.StemChunkMap = null;
        this.PhraseChunkMap = null;
        this.HelpSystem = helpSystem;
        this.SearchType = null;
        this.NGramSize = 0;
        this.Stemmer = null;
        this.SynonymFile = null;
        this.DownloadedSynonymFile = null;
        this.LoadChunkCompleteFuncs = new MadCap.Utilities.Dictionary();
    };

    var SearchDB = Search.SearchDB;

    // changed to database object
    SearchDB.prototype.Load = function (dbObj, OnCompleteFunc) {
        var self = this;

        this.LoadStemmer(this.HelpSystem.LanguageName, function () {
            MadCap.Utilities.Xhr.Load(self.HelpSystem.GetPath() + "Data/Synonyms.xml", true, function (xmlDoc) {
                if (xmlDoc != null) {
                    self.SynonymFile = new Search.SynonymFile(xmlDoc.documentElement, self.Stemmer);
                }

                // changed to database object
                self._LoadSearchDB(dbObj, OnCompleteFunc);
            }, null, this);
        });
    };

    SearchDB.prototype.LoadStemmer = function (language, OnCompleteFunc) {
        var supportedLanguages = ["danish", "dutch", "english", "finnish", "french", "german", "hungarian", "italian", 
                                  "norwegian", "portuguese", "romanian", "russian", "spanish"];

        var stemmer = null;

        this.Stemmer = {
            stemWord: function (word) {
                if (word != null)
                    word = word.toLowerCase();
                if (stemmer != null)
                    word = stemmer.stemWord(word);
                return word;
            }
        }

        if (language != null && supportedLanguages.indexOf(language.toLowerCase()) != -1) {
            var scriptFile = "stemmer-" + language.toLowerCase() + ".amd.min.js";
            var scriptFolder = MadCap.Utilities.HasRuntimeFileType("SkinPreview") ?
                    "../WebHelp2/Scripts/Stemmers/" :
                    this.HelpSystem.GetPath() + this.HelpSystem.ScriptsFolderPath;

            require([scriptFolder + scriptFile], function (module) {
                stemmer = new module[language + "Stemmer"];
                OnCompleteFunc();
            });
        }
        else {
            OnCompleteFunc();
        }
    };

    SearchDB.prototype.GetTermPhrases = function (term, isExactMatch, subset) {
        var self = this;
        var stemDic = new MadCap.Utilities.Dictionary();
        var startStem = this.Stemmer.stemWord(term);
        var topicIds = new MadCap.Utilities.Dictionary();

        stemDic.Add(startStem, true);

        if (!isExactMatch) {
            if (this.SynonymFile != null) {
                this.SynonymFile.AddSynonymStems(term, startStem, stemDic);
            }

            if (this.DownloadedSynonymFile != null) {
                this.DownloadedSynonymFile.AddSynonymStems(term, startStem, stemDic);
            }
        }

        var dbTopicMap = Object.create(null);

        var stems = [];

        stemDic.ForEach(function (key, value) {
            if (self.SearchType == "NGram") {
                for (var k = 0; k < key.length - self.NGramSize + 1; k++) {
                    var subText = key.substring(k, k + self.NGramSize);

                    stems.push(subText);
                }
            }
            else {
                stems.push(key);
            }
        });

        var deferredLookups = [];

        $.each(stems, function (index, stem) {
            deferredLookups.push(self.LoadStem(stem).then(function (stemObj) {
                for (var phrase in stemObj) {
                    if (!isExactMatch || phrase == term.toLowerCase()) {
                        var topics = stemObj[phrase];

                        if (subset)
                            topics = subset.Intersect(topics);

                        topicIds.Add(phrase, topics);
                    }
                }
            }));
        });

        var deferred = $.Deferred();

        $.when.apply(this, deferredLookups).done(function () {
            deferred.resolve(term, topicIds);
        });

        return deferred.promise();
    }

    SearchDB.prototype.LookupPhrase = function (text, isExactMatch, filterName) {
        var self = this;
        var deferred = $.Deferred();
        var terms = Search.SplitPhrase(text);
        var resultSet = null;
        var deferredLookups = [];
        var termPhraseMap = new MadCap.Utilities.Dictionary();
        
        if (text)
            text = text.trim();

        if (!text || MadCap.Utilities.StopWords.indexOf(text) > -1) {
            deferred.resolve(self, null);
            return deferred.promise();
        }

        var subset;
        if (filterName) {
            subset = []; // initialize as empty set
            var filterMap = this.HelpSystem.GetMasterHelpsystem().GetSearchFilters();

            if (filterMap) {
                var filterTopics = filterMap[filterName];

                if (filterTopics) {
                    var concepts = filterTopics.c;
                    var conceptArr = concepts.split(';');

                    var conceptTopics = this.HelpSystem.GetConcepts();
                    for (var i = 0; i < conceptArr.length; i++) {
                        var concept = conceptArr[i];
                        subset = subset.Union(conceptTopics[concept]);
                    }
                }
            }
        }

        // gets list of topic ids for each term's phrases
        for (var i = 0; i < terms.length; i++) {
            var term = terms[i];

            deferredLookups.push(this.GetTermPhrases(term, isExactMatch, subset).then(function (term, topicIds) {
                termPhraseMap.Add(term, topicIds);
            }));
        }

        $.when.apply(self, deferredLookups).done(function () {
            var intersection;

            // unions the topic ids of all the phrases per term
            termPhraseMap.ForEach(function (term, phrases) {
                var union = [];
                phrases.ForEach(function (phrase, topicIds) {
                    union = union.Union(topicIds);
                });

                // (1st intersection) calculates the intersection of topic ids of the previous term(s) and current term
                if (!intersection)
                    intersection = union;
                else
                    intersection = intersection.Intersect(union);
            });

            var termWordMap = Object.create(null);
            var deferredLookups = [];

            termPhraseMap.ForEach(function (term, phrases) {
                termWordMap[term] = Object.create(null);

                // (2nd intersection) gets individual topics from the word , from the list of intersected topics
                phrases.ForEach(function (phrase, topicIds) {
                    var phraseTopicIds = topicIds.Intersect(intersection);

                    // do deferred here and load phrases/calculate scores
                    // loop through topic ids
                    $.each(phraseTopicIds, function (index, topicId) {
                        deferredLookups.push(self.LoadPhrase(phrase, topicId).then(function (topicId, phraseObj) {
                            var topicPhraseObj = termWordMap[term][topicId];
                            if (phraseObj) {
                                if (!topicPhraseObj)
                                    termWordMap[term][topicId] = phraseObj;
                                else {
                                    topicPhraseObj.r = MadCap.Utilities.CombineRelevancy(topicPhraseObj.r, phraseObj.r);
                                    $.extend(true, topicPhraseObj.w, phraseObj.w);
                                }
                            }
                        }));
                    });
                });
            });

            // for terms in this search database
            var topicRelevancyMap = Object.create(null);
            var topicDataMap = Object.create(null);
            $.when.apply(this, deferredLookups).done(function () {
                $.each(intersection, function (i, topicId) {
                    var topicRelevancy = 0;

                    if (!isExactMatch) {
                        topicRelevancy = termWordMap[terms[0]][topicId].r;
                    }
                    else {
                        var wordMap = termWordMap[terms[0]][topicId].w;
                        for (var word in wordMap) {
                            var phraseRelevancy = wordMap[word];

                            for (var termIndex = 1; termIndex < terms.length; termIndex++) {
                                var wordIndex = parseInt(word);
                                var nextTerm = terms[termIndex];
                                var nextWordMap = termWordMap[nextTerm][topicId].w;

                                var nextWordRel = nextWordMap[wordIndex + termIndex];
                                if (nextWordRel) {
                                    phraseRelevancy = Math.max(phraseRelevancy, nextWordRel);
                                }
                                else {
                                    phraseRelevancy = 0;
                                    break;
                                }
                            }

                            topicRelevancy = MadCap.Utilities.CombineRelevancy(topicRelevancy, phraseRelevancy);
                        }
                    }

                    if (topicRelevancy > 0)
                        topicDataMap[topicId] = { r: topicRelevancy };
                });

                deferred.resolve(self, topicDataMap);
            });
        });

        return deferred.promise();
    }

    SearchDB.prototype.LoadTopics = function (topicDataMap) {
        var deferredTopicLookups = [];
        var data = topicDataMap.data;

        for (var topicId in data) {
            deferredTopicLookups.push(this.LoadTopic(topicId).then(function (topicId, topicData) {
                $.extend(data[topicId], topicData);
            }));
        }

        topicDataMap.count = deferredTopicLookups.length;

        var deferred = $.Deferred();

        $.when.apply(this, deferredTopicLookups).done(function () {
            deferred.resolve(topicDataMap);
        });

        return deferred.promise();
    }

    // Private functions

    // changed to database object
    SearchDB.prototype._LoadSearchDB = function (dbObj, OnCompleteFunc) {
        this.TopicChunkMap = dbObj["t"];
        this.UrlChunkMap = dbObj["u"];
        this.StemChunkMap = dbObj["s"];
        this.PhraseChunkMap = dbObj["p"];
        this.RelevanceWeight = dbObj["r"];
        this.SearchType = dbObj["st"];
        this.NGramSize = dbObj["n"];

        if (OnCompleteFunc)
            OnCompleteFunc();
    };

    SearchDB.prototype.LookupPhraseChunkId = function (phrase, topicId) {
        var mapLength = this.PhraseChunkMap.length;
        for (var i = 0; i < mapLength; i++) {
            var lookupString = this.PhraseChunkMap[i][0];
            var compareIndex = MadCap.String.Compare(phrase, lookupString);

            if (compareIndex == 0) {
                if (topicId < this.PhraseChunkMap[i][1])
                    return i - 1;
                else if (topicId == this.PhraseChunkMap[i][1])
                    return i;
            }
            else if (compareIndex == -1) {
                return i - 1;
            }
        }

        return mapLength - 1;
    }

    SearchDB.prototype.LoadTopic = function (topicId) {
        var deferred = $.Deferred();

        var chunkId = MadCap.Utilities.GetChunkId(this.TopicChunkMap, topicId, function (a, b) {
            if (a < b)
                return -1;
            else if (a == b)
                return 0;
            else
                return 1;
        });

        if (chunkId == -1)
            deferred.resolve();
        else {
            MadCap.Utilities.Require([this.HelpSystem.GetPath() + "Data/SearchTopic_Chunk" + chunkId + ".js"], function (data) {
                deferred.resolve(topicId, data[topicId]);
            });
        }

        return deferred.promise();
    }

    SearchDB.prototype.LoadUrl = function (url) {
        var deferred = $.Deferred();

        var chunkId = MadCap.Utilities.GetChunkId(this.UrlChunkMap, url, function (a, b) {
            return MadCap.String.Compare(a, b);
        });

        if (chunkId == -1)
            deferred.resolve();
        else {
            MadCap.Utilities.Require([this.HelpSystem.GetPath() + "Data/SearchUrl_Chunk" + chunkId + ".js"], function (data) {
                deferred.resolve(url, data[url]);
            });
        }

        return deferred.promise();
    }

    SearchDB.prototype.LoadTopicByUrl = function (url) {
        var self = this;

        return this.LoadUrl(url).then(function (url, topicID) {
            return self.LoadTopic(topicID);
        });
    }

    SearchDB.prototype.LoadStem = function (stem) {
        var self = this;
        var deferred = $.Deferred();

        var chunkIds = MadCap.Utilities.GetChunkIds(this.StemChunkMap, stem, function (a, b) {
            return MadCap.String.Compare(a, b);
        });

        if (chunkIds.length === 0)
            deferred.resolve();
        else {
            var deferreds = [];
            var result = Object.create(null);

            $.each(chunkIds, function(index, chunkId) {
                deferreds.push(self.LoadStemChunk(chunkId).then(function(data) {
                    $.extend(result, data[stem]);
                }));
            });

            $.when.apply(this, deferreds).done(function() {
                deferred.resolve(result);
            }, this);
        }

        return deferred.promise();
    }

    SearchDB.prototype.LoadStemChunk = function (chunkId) {
        var deferred = $.Deferred();

        MadCap.Utilities.Require([this.HelpSystem.GetPath() + "Data/SearchStem_Chunk" + chunkId + ".js"], function (data) {
            deferred.resolve(data);
        });

        return deferred.promise();
    }

    SearchDB.prototype.LoadPhrase = function (phrase, topicId) {
        var deferred = $.Deferred();

        var chunkId = this.LookupPhraseChunkId(phrase, topicId);
        MadCap.Utilities.Require([this.HelpSystem.GetPath() + "Data/SearchPhrase_Chunk" + chunkId + ".js"], function (data) {
            var phraseObj;
            if (data[phrase])
                phraseObj = data[phrase][topicId];

            deferred.resolve(topicId, phraseObj);
        });

        return deferred.promise();
    }

    //
    //    End class SearchDB
    //

    //
    //    Class SearchQuery
    //

    Search.SearchQuery = function (query, filter, pageIndex) {
        // Private 
        function AppendParams(query, params) {
            var isTripane = MadCap.Utilities.HasRuntimeFileType("TriPane");
            var hasParam = false;
            for (var i = 0; i < params.length; i++) {
                var name = params[i][0];
                var val = params[i][1];

                if (!MadCap.String.IsNullOrEmpty(val)) {
                    query += (!hasParam && isTripane ? "?" : "&") + name + "=" + val;
                    hasParam = true;
                }
            }

            return query;
        }

        // Public 
        this.Query = query;
        this.Filter = filter;
        this.PageIndex = pageIndex;

        this.ToString = function () {
            return AppendParams(this.Query, [[Search.SearchQuery._filter, this.Filter], [Search.SearchQuery._pageIndex, this.PageIndex]]);
        };
    };

    Search.SearchQuery._query = "q";
    Search.SearchQuery._filter = "f";
    Search.SearchQuery._pageIndex = "p";

    Search.SearchQuery.Parse = function (queryString) {
        var queryUrl = new MadCap.Utilities.Url(queryString);

        var searchQuery = queryUrl.PlainPath;
        if (MadCap.String.IsNullOrEmpty(searchQuery))
            searchQuery = queryUrl.QueryMap.GetItem(Search.SearchQuery._query);

        if (!MadCap.String.IsNullOrEmpty(searchQuery))
            searchQuery = decodeURIComponent(searchQuery);

        var searchFilter = queryUrl.QueryMap.GetItem(Search.SearchQuery._filter);
        if (searchFilter)
            searchFilter = decodeURIComponent(searchFilter);

        var pageIndex = queryUrl.QueryMap.GetItem(Search.SearchQuery._pageIndex);
        if (pageIndex != null)
            pageIndex = parseInt(pageIndex);

        return new Search.SearchQuery(searchQuery, searchFilter, pageIndex);
    }

    //
    //    End class SearchQuery
    //

    //
    //    Class SearchResult
    //

    Search.SearchResult = function (score, rank, title, link, abstractText, highlighted) {
        // Public properties
        this.Score = score;
        this.Rank = rank;
        this.Title = title;
        this.Link = link;
        this.AbstractText = abstractText;
        this.Highlighted = highlighted;
    };

    //
    //    End class SearchResult
    //

    //
    //    Class Filters
    //

    Search.Filters = function (helpSystem) {
        // Private member variables

        var _HelpSystem = helpSystem;

        // Public member functions

        this.Load = function (OnCompleteFunc) {
            _HelpSystem.LoadSearchFilters().then(function () {
                _HelpSystem.LoadAllConcepts(function () {
                    OnCompleteFunc();
                });
            }, null, null);
        };
    };

    //
    //    End class Filters
    //

    //
    //    Class SynonymFile
    //

    Search.SynonymFile = function (rootNode, stemmer) {
        // Public properties

        this.Stemmer = stemmer;
        this.WordToStem = new MadCap.Utilities.Dictionary(true);
        this.Directionals = new MadCap.Utilities.Dictionary(true);
        this.DirectionalStems = new MadCap.Utilities.Dictionary(true);
        this.Groups = new MadCap.Utilities.Dictionary(true);
        this.GroupStems = new MadCap.Utilities.Dictionary(true);
        this.GroupStemSources = new MadCap.Utilities.Dictionary(true);

        this.LoadSynonymFile(rootNode);
    };

    var SynonymFile = Search.SynonymFile;

    SynonymFile.prototype.LoadSynonymFile = function (rootNode) {
        var groups = MadCap.Dom.GetChildNodeByTagName(rootNode, "Groups", 0);
        var syns = MadCap.Dom.GetChildNodeByTagName(rootNode, "Directional", 0);

        if (syns != null) {
            var childNodesLength = syns.childNodes.length;

            for (var i = 0; i < childNodesLength; i++) {
                var child = syns.childNodes[i];

                if (child.nodeName == "DirectionalSynonym") {
                    var from = MadCap.Dom.GetAttribute(child, "From");
                    var to = MadCap.Dom.GetAttribute(child, "To");
                    var stem = MadCap.Dom.GetAttributeBool(child, "Stem", false);
                    var fromStem = MadCap.Dom.GetAttribute(child, "FromStem");
                    var toStem = MadCap.Dom.GetAttribute(child, "ToStem");

                    if (stem) {
                        if (fromStem == null) {
                            fromStem = this.Stemmer.stemWord(from);
                        }
                    }

                    if (toStem == null) {
                        toStem = this.Stemmer.stemWord(to);
                    }

                    if (from != null && to != null) {
                        if (stem) {
                            this.DirectionalStems.Add(fromStem, toStem);

                            this.WordToStem.Add(from, fromStem);
                            this.WordToStem.Add(to, toStem);
                        }
                        else {
                            this.Directionals.Add(from, toStem);

                            this.WordToStem.Add(to, toStem);
                        }
                    }
                }
            }
        }

        if (groups != null) {
            var childNodesLength = groups.childNodes.length;

            for (var i = 0; i < childNodesLength; i++) {
                var child = groups.childNodes[i];

                if (child.nodeName == "SynonymGroup") {
                    var words = new Array();
                    var stemmedWords = new Array();
                    var stem = MadCap.Dom.GetAttributeBool(child, "Stem", false);

                    var synGroupChildNodesLength = child.childNodes.length;

                    for (var j = 0; j < synGroupChildNodesLength; j++) {
                        var wordNode = child.childNodes[j];

                        if (wordNode.nodeType != 1) {
                            continue;
                        }

                        words.push(wordNode.firstChild.nodeValue);
                    }

                    for (var j = 0; j < synGroupChildNodesLength; j++) {
                        var wordNode = child.childNodes[j];

                        if (wordNode.nodeType != 1) {
                            continue;
                        }

                        var stemmed = MadCap.Dom.GetAttribute(wordNode, "Stem");

                        if (stemmed == null) {
                            stemmed = this.Stemmer.stemWord(wordNode.firstChild.nodeValue);
                        }

                        this.WordToStem.Add(wordNode.firstChild.nodeValue, stemmed);

                        stemmedWords.push(stemmed);
                    }


                    //

                    var wordsLength = words.length;

                    for (var j = 0; j < wordsLength; j++) {
                        var word = words[j];
                        var stemmedWord = stemmedWords[j];

                        for (var k = 0; k < wordsLength; k++) {
                            var word1 = words[k];

                            if (stem) {
                                var group = this.GroupStemSources.GetItem(word);

                                if (group == null) {
                                    group = new MadCap.Utilities.Dictionary();
                                    this.GroupStemSources.Add(word, group);
                                }

                                group.Add(word1, stemmedWord);
                            }
                            else {
                                var group = this.GroupStemSources.GetItem(word);

                                if (group == null) {
                                    group = new MadCap.Utilities.Dictionary();
                                    this.Groups.Add(word, group);
                                }

                                group.Add(word1, stemmedWord);
                            }
                        }
                    }

                    //

                    var stemmedWordsLength = stemmedWords.length;

                    for (var j = 0; j < stemmedWordsLength; j++) {
                        var stemmedWord = stemmedWords[j];

                        for (var k = 0; k < stemmedWordsLength; k++) {
                            var stemmedWord1 = stemmedWords[k];
                            var group = this.GroupStems.GetItem(stemmedWord);

                            if (group == null) {
                                group = new MadCap.Utilities.Dictionary();
                                this.GroupStems.Add(stemmedWord, group);
                            }

                            group.Add(stemmedWord1, stemmedWord);
                        }
                    }
                }
            }
        }
    };

    SynonymFile.prototype.AddSynonymStems = function (term, termStem, stems) {
        var synonym = this.Directionals.GetItem(term);

        if (synonym != null) {
            stems.AddUnique(synonym);
        }

        //

        synonym = this.DirectionalStems.GetItem(termStem);

        if (synonym != null) {
            stems.AddUnique(synonym);
        }

        var group = this.Groups.GetItem(term);

        if (group != null) {
            group.ForEach(function (key, value) {
                stems.AddUnique(key);

                return true;
            });
        }

        //

        group = this.GroupStems.GetItem(termStem);

        if (group != null) {
            group.ForEach(function (key, value) {
                stems.AddUnique(key);

                return true;
            });
        }
    };

    //
    //    End class SynonymFile
    //
})();
