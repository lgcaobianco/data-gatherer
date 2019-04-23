import urllib
from searchtweets import ResultStream, gen_rule_payload, load_credentials
from searchtweets import collect_results
import json

searchTerm = "#BBMAsTopSocial"
encoded = urllib.parse.quote(searchTerm)
premium_search_args = load_credentials("~/.twitter_keys.yaml",
                                       yaml_key="search_tweets_30_day_dev",
                                       env_overwrite=False)
# testing with a sandbox account
rule = gen_rule_payload(searchTerm, results_per_call=100)
print(rule)
tweets = collect_results(rule,
                         max_results=200,
                         result_stream_args=premium_search_args)
[print(tweet.all_text, end='\n\n') for tweet in tweets[0:len(tweets)]]
with open('tweets.json', "w") as fp:
    for tweet in tweets:
        json.dump(tweet, fp)
        fp.write("\n")
