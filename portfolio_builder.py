import csv
import os
from os.path import isfile
import praw
import pandas as pd
from time import sleep
import re
from collections import Counter
import datetime
import matplotlib.pyplot as plt
import tweepy
from portfolio_builder_constants import *

selected_subreddit = input("Enter subreddit: ")
NAME = input("Enter Twitter User: ")

# Initialising APIs
################################################################################
# Creating the Reddit mention scraper
reddit = praw.Reddit(client_id="ODVkiy6frvzFdw",
                     client_secret="dWbZm7Tm-Cldn-Hk2BbVMDC6va0Ygw",
                     password="Jem20202020<>",
                     user_agent="PortfolioBuilder Project by u/Calm-Water",
                     username="Calm-Water")
################################################################################
# Creating the Twitter mention scraper
# Creating the authentication object
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# Setting your access token and secret
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# Creating the API object while passing in auth information
twitter = tweepy.API(auth)


################################################################################

class SubredditScraper:
    # initialisation
    def __init__(self, sub, sort='new', lim=900, mode='w'):
        self.sub = sub
        self.sort = sort
        self.lim = lim
        self.mode = mode
        print(
            f'SubredditScraper instance created with values '
            f'sub = {sub}, sort = {sort}, lim = {lim}, mode = {mode}')

    # sets the sorting parameters according to the subreddit chosen
    def set_sort(self):
        if self.sort == 'new':
            return self.sort, reddit.subreddit(self.sub).new(limit=self.lim)
        elif self.sort == 'top':
            return self.sort, reddit.subreddit(self.sub).top(limit=self.lim)
        elif self.sort == 'hot':
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)
        else:
            self.sort = 'hot'
            print('Sort method was not recognized, defaulting to hot.')
            return self.sort, reddit.subreddit(self.sub).hot(limit=self.lim)

    # get posts from a specified subreddit
    def get_posts(self):
        """Get unique posts from a specified subreddit."""

        sub_dict = {
            'selftext': [], 'title': [], 'id': [], 'sorted_by': [],
            'num_comments': [], 'score': [], 'ups': [], 'downs': []}
        csv = f'{self.sub}_posts.csv'

        # Attempt to specify a sorting method.
        sort, subreddit = self.set_sort()

        # Set csv_loaded to True if csv exists since you can't
        # evaluate the truth value of a DataFrame.
        df, csv_loaded = (pd.read_csv(csv), 1) if isfile(csv) else ('', 0)

        print(f'csv = {csv}')
        print(f'After set_sort(), sort = {sort} and sub = {self.sub}')
        print(f'csv_loaded = {csv_loaded}')

        print(f'Collecting information from r/{self.sub}.')

        for post in subreddit:

            # Check if post.id is in df and set to True if df is empty.
            # This way new posts are still added to dictionary when df = ''
            unique_id = post.id not in tuple(df.id) if csv_loaded else True

            # Save any unique posts to sub_dict.
            if unique_id:
                sub_dict['selftext'].append(post.selftext)
                sub_dict['title'].append(post.title)
                sub_dict['id'].append(post.id)
                sub_dict['sorted_by'].append(sort)
                sub_dict['num_comments'].append(post.num_comments)
                sub_dict['score'].append(post.score)
                sub_dict['ups'].append(post.ups)
                sub_dict['downs'].append(post.downs)
            sleep(0.1)

            new_df = pd.DataFrame(sub_dict)

            # Add new_df to df if df exists then save it to a csv.
            if 'DataFrame' in str(type(df)) and self.mode == 'w':
                pd.concat([df, new_df], axis=0, sort=0).to_csv(csv, index=False)
                print(
                    f'{len(new_df)} new posts collected and added to {csv}')
            elif self.mode == 'w':
                new_df.to_csv(csv, index=False)
                print(f'{len(new_df)} posts collected and saved to {csv}')
            else:
                print(
                    f'{len(new_df)} posts were collected but they were not '
                    f'added to {csv} because mode was set to "{self.mode}"')


# Twitter API methods
def collect_twitter_sentiment():
    """
    Collects tweet from a user inputted source, storing them in a csv file for processing.
    :return: csv file containing tweet data
    """
    # Open/create a file to append data to
    csvFile = open(NAME+'_posts.csv', 'a')
    # Use csv writer
    csvWriter = csv.writer(csvFile)
    # Calling the user function with current parameters
    results = twitter.user_timeline(id=NAME, count=TWEET_COUNT)
    for tweet in results:
        print(tweet.created_at, tweet.text)
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])
    return csvFile


def get_mentions(reddit_data, twitter_data, reference_data):
    """
    Loops through the saved csv file to find mentions of any stock tickers associated with "stock_tickers.csv"
    and returns frequencies of mentions.
    :return: Count of what stock tickers were mentioned in the input data (raw_data)
    """
    # Join the two files together to create process_data
    raw_data = open(reddit_data, "a")
    twitter_data = open(twitter_data, "r")

    for line in twitter_data:
        raw_data.write(line)

    raw_data.close()
    twitter_data.close()
    os.rename("C:/Users/Jeremy Waters/PycharmProjects/PortfolioBuilder/" + selected_subreddit +".csv",
              "//mentions.csv")

    posts = open(selected_subreddit+".csv", 'r', encoding="utf8").read()
    tickers = open(reference_data, 'r').read()
    expr = r'\$([A-Z]{1,4})'
    mentions = re.findall(expr, posts, re.I)
    cnt = Counter(_ for _ in mentions if _ in tickers)
    print(cnt)
    # find a way of checking if a string/item in posts matches (contains a word in mentions)
    # if so, add to dictionary and +1 to it

    return cnt


def process_mentions(mentions):
    return


def display_mentions(counter):
    counter = {key: val for key, val in counter.items() if val > 2}

    tickers = counter.keys()
    values = counter.values()
    plt.bar(tickers, values)
    plt.show()


if __name__ == '__main__':
    SubredditScraper(
        selected_subreddit,
        lim=997,
        mode='w',
        sort='new').get_posts()
    twitter_file = collect_twitter_sentiment()
    mentions = get_mentions(selected_subreddit + "_posts.csv", twitter_file, "stock_tickers.csv")
    display_mentions(mentions)
