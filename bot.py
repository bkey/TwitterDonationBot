import tweepy
import threading
import time
import re
from random import randint

#todo: put this somewhere better
consumer_key =  ""
consumer_secret_key = ""
access_token = ""
access_token_secret = ""

class DonationBot(threading.Thread):

    """
        Bot that automates retweets tweets which are supposed to generate a charitable donation 
        so you don't have to
    """

    def __init__(self, consumer_key, consumer_secret_key, access_token, access_token_secret):
        self.api = self.tweepy_api_setup(consumer_key, consumer_secret_key, access_token, access_token_secret)         
        self.output_queue = set()
        self.retweeted_ids = set()
        self.last_id = 0
        threading.Thread.__init__(self)

    def tweepy_api_setup(self, consumer_key, consumer_secret_key, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
        auth.set_access_token(access_token, access_token_secret)

        return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def retweet_from_queue(self):
        if len(self.output_queue) <= 0:
            return
        
        tweet_id = self.output_queue.pop()
        self.retweeted_ids.add(tweet_id)

        try:
            self.api.retweet(tweet_id)
        except tweepy.TweepError as e:
            #most likely this error is caused by retweeting something we have already retweeted
            #todo: need to keep track of all time user retweets 
            print e
            pass

    #cash money or it didn't happen
    def has_monetary_value(self, text):
        res = re.search(r'([\$])(\d+(?:\.\d{2})?)', text)
        if res == None:
            return False
        else:
            return True

    def is_valid_tweet(self, tweet):            
        if (tweet.retweet_count < 10):
            return False
        elif tweet.id in self.retweeted_ids or tweet.retweeted_status.id in self.retweeted_ids:
            return False
        else:
            return self.has_monetary_value(tweet.text)

    def scan_for_tweets(self):
        tweets = [status for status in tweepy.Cursor(self.api.search, q="For every RT donate", since_id=self.last_id, include_rts=False).items(100)]

        for tweet in tweets:
            self.last_twitter_id = tweet.id
            if self.is_valid_tweet(tweet):
                self.output_queue.add(tweet.id)
                            
    def run(self):
        while(1):
            self.scan_for_tweets()
            self.retweet_from_queue()
            time.sleep(60 + randint(0,30))

if __name__ == "__main__":
    t = DonationBot(consumer_key, consumer_secret_key, access_token,access_token_secret)
    t.start()
