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
    var Search = MadCap.CreateNamespace("WebHelp.Search");

    //
    //    Class Tokenizer
    //

    Search.Tokenizer = function () {
        // Private variables

        var mOriginalString = "";
        var mPos = -1;
        var mTokens = new Array();

        // Public functions

        this.Tokenize = function (str) {
            var token = null;

            mOriginalString = str;
            mPos = -1;

            for (var i = 0; token = ReadNextToken() ; i++) {
                mTokens[i] = token;
            }

            return mTokens;
        }

        // Private functions

        function Peek() {
            return mOriginalString.charAt(mPos + 1);
        }

        function Read() {
            mPos++;
        }

        function ReadString() {
            var str = "";

            for (; ;) {
                var c = Peek();

                if (!c) break;

                if (c == "\"") {
                    Read();
                    break;
                }
                else {
                    Read();
                    str += c;
                }
            }

            return (str == "") ? null : str;
        }

        function ReadNextToken() {
            var c = Peek();
            var token = null;
            var tokenText = "";

            if (!c) {
                token = null;
            }
            else if (Search.IsWhiteSpace(c)) {
                for (c = Peek(); Search.IsWhiteSpace(c); c = Peek()) {
                    Read();
                    tokenText += c;
                }

                token = new Search.Token(tokenText, Search.Token.WhiteSpace);
            }
            else if (c == "(") {
                Read();
                token = new Search.Token(c, Search.Token.LeftParen);
            }
            else if (c == ")") {
                Read();
                token = new Search.Token(c, Search.Token.RightParen);
            }
            else if (c == "^" || c == "!") {
                Read();
                token = new Search.Token(c, Search.Token.Not);
            }
            else if (c == "+" || c == "&") {
                Read();
                token = new Search.Token(c, Search.Token.And);
            }
            else if (c == "|") {
                Read();
                token = new Search.Token(c, Search.Token.Or);
            }
            else if (c == "\"") {
                Read();

                var str = ReadString();

                token = new Search.Token(str, (str == null) ? Search.Token.Error : Search.Token.Phrase);
            }
            else if (Search.IsTermSeparator(c)) {
                Read();
                token = new Search.Token(c, Search.Token.TermSeparator);
            }
            else {
                for (c = Peek() ; Search.IsNameChar(c); c = Peek()) {
                    Read();
                    tokenText += c;
                }

                if (tokenText == "and" || tokenText == "AND") {
                    token = new Search.Token(tokenText, Search.Token.And);
                }
                else if (tokenText == "or" || tokenText == "OR") {
                    token = new Search.Token(tokenText, Search.Token.Or);
                }
                else if (tokenText == "not" || tokenText == "NOT") {
                    token = new Search.Token(tokenText, Search.Token.Not);
                }
                else {
                    var tokenType = Search.Token.Word;

                    if (MadCap.WebHelp.SearchPane.SearchDBs[0].SearchType == "NGram") {
                        tokenType = Search.Token.Phrase;
                    }

                    token = new Search.Token(tokenText, tokenType);
                }
            }

            return token;
        }
    };

    //
    //    End class Tokenizer
    //

    //
    //    Class Token
    //

    Search.Token = function (tokenText, type) {
        // Private member variables

        var mTokenText = tokenText;
        var mType = type;

        // Public member functions

        this.GetTokenText = function () {
            return mTokenText;
        };

        this.GetType = function () {
            return mType;
        };
    };

    var Token = Search.Token;

    // Static properties

    Token.Eof = 0;
    Token.Error = 1;
    Token.WhiteSpace = 2;
    Token.Phrase = 3;
    Token.Word = 4;
    Token.RightParen = 5;
    Token.LeftParen = 6;
    Token.Not = 7;
    Token.And = 8;
    Token.Or = 9;
    Token.ImplicitAnd = 10;
    Token.TermSeparator = 11;

    //
    //    End class Token
    //

    //
    //    Class Parser
    //

    Search.Parser = function (str) {
        // Private member variables

        var mSelf = this;
        var mSearchString = str;
        var mCurrentToken = -1;
        var mTokenizer = new Search.Tokenizer();
        var mSearchTokens = mTokenizer.Tokenize(mSearchString);

        // Public member functions
        this.ParseExpression = function () {
            var node = ParseUnary();

            SkipWhiteSpace();

            if (Peek() == Search.Token.Eof) {
                return node;
            }
            else if (Peek() == Search.Token.And || Peek() == Search.Token.Or || Peek() == Search.Token.Not) {
                EatToken();

                var binNode = new Search.Node(mSearchTokens[mCurrentToken],
                                       node,
                                       this.ParseExpression());

                return binNode;
            }
            else if (Peek() == Search.Token.Word || Peek() == Search.Token.Phrase || Peek() == Search.Token.Not || Peek() == Search.Token.LeftParen) {
                var binNode = new Search.Node(new Search.Token(node.GetToken().GetTokenText() + " " + mSearchTokens[mCurrentToken + 1].GetTokenText(), Search.Token.ImplicitAnd),
                                       node,
                                       this.ParseExpression());

                return binNode;
            }
            else if (Peek() == Search.Token.RightParen) {
                return node;
            }

            throw gInvalidTokenLabel;
        };

        // Private member functions

        function EatToken() {
            mCurrentToken++;
        }

        function ParseUnary() {
            SkipWhiteSpace();

            if (Peek() == Search.Token.Word) {
                EatToken();

                return new Search.Node(mSearchTokens[mCurrentToken], null, null);
            }
            else if (Peek() == Search.Token.Phrase) {
                EatToken();

                return new Search.Node(mSearchTokens[mCurrentToken], null, null);
            }
            else if (Peek() == Search.Token.LeftParen) {
                EatToken();

                var token = mSearchTokens[mCurrentToken];
                var node = new Search.Node(token, mSelf.ParseExpression(), null);

                if (Peek() != Search.Token.RightParen) {
                    throw "Missing right paren ')'.";
                }

                EatToken();

                return node;
            }

            throw gInvalidTokenLabel;
        }

        function Peek() {
            if (mSearchTokens[mCurrentToken + 1] == null) {
                return Search.Token.Eof;
            }
            else {
                return mSearchTokens[mCurrentToken + 1].GetType();
            }
        }

        function SkipWhiteSpace() {
            for (; Peek() == Search.Token.WhiteSpace || Peek() == Search.Token.TermSeparator;) {
                EatToken();
            }
        }
    };

    //
    //    End class Parser
    //

    //
    //    Class Node
    //

    Search.Node = function (token, op1, op2) {
        // Private member variables

        var mToken = token;
        var mOperand1 = op1;
        var mOperand2 = op2;

        // Public member functions
        this.Evaluate = function (filterName, OnCompleteFunc) {
            var self = this;
            var tokenType = mToken.GetType();

            if (tokenType == Search.Token.Word || tokenType == Search.Token.Phrase) {
                this.EvaluatePhrase(filterName).then(OnCompleteFunc);
            }
            else if (tokenType == Search.Token.And ||
                  tokenType == Search.Token.ImplicitAnd ||
                  tokenType == Search.Token.Or ||
                  tokenType == Search.Token.Not) {
                mOperand1.Evaluate(filterName, function (leftResults) {
                    mOperand2.Evaluate(filterName, function (rightResults) {
                        if (mToken.GetType() == Search.Token.And || mToken.GetType() == Search.Token.ImplicitAnd) {
                            OnCompleteFunc(Search.IntersectResults(leftResults, rightResults));
                        }
                        else if (mToken.GetType() == Search.Token.Or) {
                            OnCompleteFunc(Search.UnionResults(leftResults, rightResults));
                        }
                        else if (mToken.GetType() == Search.Token.Not) {
                            OnCompleteFunc(Search.SubtractResults(leftResults, rightResults));
                        }
                    });
                });
            }
            else if (tokenType == Search.Token.LeftParen) {
                if (mOperand1)
                    mOperand1.Evaluate(filterName, OnCompleteFunc);
                else
                    OnCompleteFunc(null);
            }
            else
                OnCompleteFunc(null);
        };

        this.EvaluatePhrase = function (filterName) {
            //if (!_HelpSystem.IsWebHelpPlus) {

            //}
            //else {
            //    title = result.Title;
            //    abstractText = result.AbstractText;
            //    var resultUrl = new MadCap.Utilities.Url(result.Link);
            //    var baseUrl = new MadCap.Utilities.Url(document.location.pathname);

            //    if (!MadCap.String.EndsWith(document.location.pathname, "/")) // http://MyServer/MyHTML5/ vs. http://MyServer/MyHTML5/Default.htm
            //        baseUrl = baseUrl.ToFolder();

            //    baseUrl = baseUrl.CombinePath(_HelpSystem.ContentFolder);
            //    linkUrl = resultUrl.ToRelative(baseUrl);
            //}

            var self = this;
            var deferred = $.Deferred();
            var tokenText = mToken.GetTokenText();
            var isExactMatch = mToken.GetType() == Search.Token.Phrase;

            // lookup phrase in each helpsystem
            var deferredLookups = [];
            var dbResults = Object.create(null);
            dbResults.results = Object.create(null);
            dbResults.terms = [];
            dbResults.ignore = MadCap.Utilities.StopWords.indexOf(tokenText) > -1;

            if (!dbResults.ignore) {
                dbResults.terms.push(tokenText);

                for (var j = 0; j < MadCap.WebHelp.SearchPane.SearchDBs.length; j++) {
                    var searchDB = MadCap.WebHelp.SearchPane.SearchDBs[j];

                    deferredLookups.push(searchDB.LookupPhrase(tokenText, isExactMatch, filterName).then(function (searchDB, topicDataMap) {
                        if (topicDataMap) {
                            dbIndex = MadCap.WebHelp.SearchPane.SearchDBs.indexOf(searchDB);
                            dbResults.results[dbIndex] = { data: topicDataMap };
                        }
                    }));
                }
            }

            $.when.apply(this, deferredLookups).done(function () {
                deferred.resolve(dbResults);
            });

            return deferred.promise();
        };

        this.GetToken = function () {
            return mToken;
        };
    };

    //
    //    End class Node
    //

    Search.LoadResultData = function (resultSet) {
        var deferredLookups = [];
        var totalTopics = 0;
        var dbResultsMap = resultSet.results;

        for (var dbIndex in dbResultsMap) {
            var searchDB = MadCap.WebHelp.SearchPane.SearchDBs[dbIndex];
            var topicDataMap = dbResultsMap[dbIndex];

            deferredLookups.push(searchDB.LoadTopics(topicDataMap).then(function (topicDataMap) {
                totalTopics += topicDataMap.count;
            }));
        }

        var relevanceWeight = MadCap.WebHelp.SearchPane.SearchDBs[0].RelevanceWeight;

        var deferred = $.Deferred();
        var searchResults = [];

        $.when.apply(this, deferredLookups).done(function () {
            for (var dbIndex in dbResultsMap) {
                var searchDB = MadCap.WebHelp.SearchPane.SearchDBs[dbIndex];
                var topicDataMap = dbResultsMap[dbIndex];

                for (var topicId in topicDataMap.data) {
                    var topicData = topicDataMap.data[topicId];
                    var link = searchDB.HelpSystem.GetTopicPath(topicData.u).FullPath;
                    var importance = topicData.i * topicDataMap.count / totalTopics;
                    var score = MadCap.Utilities.CalculateScore(topicData.r, importance, relevanceWeight);

                    searchResults.push(new Search.SearchResult(score, null, topicData.t, link, topicData.a));
                }
            }

            deferred.resolve(searchResults, resultSet.terms);
        });

        return deferred.promise();
    };

    Search.IsNameChar = function (c) {
        if (!c) { return false; }
        else if (c == "\"") { return false; }
        else if (c == "+") { return false; }
        else if (c == "^") { return false; }
        else if (c == "|") { return false; }
        else if (c == "&") { return false; }
        else if (Search.IsWhiteSpace(c)) { return false; }
        else if (Search.IsTermSeparator(c)) { return false; }
        else { return true; }
    };

    Search.IsWhiteSpace = function (c) {
        if (!c) {
            return false;
        }
        else if (c == " ") {
            return true;
        }
        else if (c.charCodeAt(0) == 12288) {
            return true;
        }
        else {
            return false;
        }
    };

    Search.IsTermSeparator = function (c) {
        return (MadCap.String.IsPunctuation(c) && c != '\'' && c != '_')
            || c == '>' || c == '<' || c == '=';
    };

    Search.SplitPhrase = function (text) {
        var terms = null;
        var searchDB = MadCap.WebHelp.SearchPane.SearchDBs[0];

        if (searchDB.SearchType == "NGram") {
            terms = new Array(Math.max(0, text.length - (searchDB.NGramSize + 1)));

            for (var i = 0; i < text.length - searchDB.NGramSize + 1; i++) {
                terms[i] = text.substring(i, i + searchDB.NGramSize);
            }
        }
        else {
            terms = MadCap.String.Split(text, function (c) {
                return Search.IsWhiteSpace(c) || Search.IsTermSeparator(c);
            });
        }

        return terms;
    };

    Search.FilterResults = function (resultSet1, resultSet2, onFilterData, onFilterTerms) {
        if ((resultSet1.ignore && resultSet2.ignore) || resultSet2.ignore)
            return resultSet1;
        else if (resultSet1.ignore)
            return resultSet2;

        var resultSet = Object.create(null);
        resultSet.results = Object.create(null);
        var result = resultSet.results;

        for (var dbIndex in resultSet1.results) {
            result[dbIndex] = Object.create(null);
            result[dbIndex].data = Object.create(null);

            var data1 = resultSet1.results[dbIndex].data;
            var data2 = resultSet2.results[dbIndex];
            if (data2)
                data2 = data2.data;

            onFilterData(data1, data2, result[dbIndex].data);
        }

        resultSet.terms = onFilterTerms(resultSet1.terms, resultSet2.terms);

        return resultSet;
    };

    Search.UnionResults = function (resultSet1, resultSet2) {
        return Search.FilterResults(resultSet1, resultSet2, function (data1, data2, result) {
            for (var topicId in data1) {
                result[topicId] = data1[topicId];
            }

            if (data2) {
                for (var topicId in data2) {
                    var topicData1 = data1[topicId];
                    var topicData2 = data2[topicId];

                    if (topicData1)
                        result[topicId] = { r: MadCap.Utilities.CombineRelevancy(topicData1.r, topicData2.r) };
                    else
                        result[topicId] = topicData2;
                }
            }
        }, function (terms1, terms2) {
            return terms1.Union(terms2);
        });
    };

    Search.IntersectResults = function (resultSet1, resultSet2) {        
        return Search.FilterResults(resultSet1, resultSet2, function (data1, data2, result) {
            if (data2) {
                for (var topicId in data1) {
                    var topicData2 = data2[topicId];
                    if (topicData2)
                        result[topicId] = { r: MadCap.Utilities.CombineRelevancy(data1[topicId].r, topicData2.r) };
                }
            }
        }, function (terms1, terms2) {
            return terms1.Union(terms2);
        });
    };

    Search.SubtractResults = function (resultSet1, resultSet2) {
        if (resultSet1.ignore || resultSet2.ignore)
            return resultSet1;

        return Search.FilterResults(resultSet1, resultSet2, function (data1, data2, result) {
            if (data2) {
                for (var topicId in data1) {
                    var topicData2 = data2[topicId];
                    if (!topicData2)
                        result[topicId] = data1[topicId];
                }
            }
        }, function (terms1, terms2) {
            return terms1;
        });
    };
})();
