import urllib
from searchtweets import ResultStream, gen_rule_payload, load_credentials
from searchtweets import collect_results
import json
from emoji import UNICODE_EMOJI
import string
from collections import Counter
import pandas as pd
from textblob import TextBlob
from enum import Enum


class LanguageEnum(Enum):
    ENGLISH = "en"
    PORTUGUESE = "pt"
    SPANISH = "es"


def searchTweetsAndWriteToFile(search_term, file_name, lang):
    if(not isinstance(lang, LanguageEnum)):
        raise TypeError("lang must be LanguageEnum instance")

    if(not len(search_term > 0)):
        return ""
    premium_search_args = load_credentials("~/.twitter_keys.yaml",
                                           yaml_key="search_tweets_30_day_dev",
                                           env_overwrite=False)
    # testing with a sandbox account
    rule = gen_rule_payload(search_term + " lang:" +
                            lang.value, results_per_call=100)
    print(rule)
    tweets = collect_results(rule,
                             max_results=200,
                             result_stream_args=premium_search_args)
    with open(file_name, "w") as fp:
        for tweet in tweets:
            json.dump(tweet, fp)
            fp.write("\n")
    fp.close()


def readTweetsJsonFromFile(file_name):
    tweetList = list()
    with open(file_name, "r") as file:
        for line in file:
            tweetList.append(json.loads(line))
    return tweetList


def changeTextFromTweetsToLower(tweetList):
    for tweet in tweetList:
        tweet['text'] = tweet['text'].lower()


def countWords(tweetList):
    tweetList2 = list(tweetList)
    uniqueWords = list()
    occurrence = list()
    for tweet in tweetList2:
        text = tweet.get("text").split()
        for word in text:
            if word not in uniqueWords:
                uniqueWords.append(word)
                occurrence.append(1)
            else:
                occurrence[uniqueWords.index(word)] += 1

    return pd.DataFrame({'Unique Words': uniqueWords, 'Occurrences': occurrence})


def get_sentiments(tweetList):
    sentiments = list()
    subjectivity = list()
    textList = list()
    for tweet in tweetList:
        if(tweet.get("user").get("lang") == "en"):
            text = tweet.get("text")
            textList.append(text)
            analysis = TextBlob(text)
            sentiments.append(analysis.sentiment.polarity)
            subjectivity.append(analysis.sentiment.subjectivity)
    return pd.DataFrame(
        {'Tweet text': textList, 'Sentiment': sentiments, 'Subjectivity': subjectivity})


# read from file so i dont have to query again
tweetList = readTweetsJsonFromFile('tweets.json')
# switch everything to lowercase
changeTextFromTweetsToLower(tweetList)
# count the words and reorder from most used
df = countWords(tweetList).sort_values(by=['Occurrences'], ascending=False)
sentiments = get_sentiments(tweetList)
print(sentiments.head())
print(df.head(10))
