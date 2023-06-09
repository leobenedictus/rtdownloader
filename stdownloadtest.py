import streamlit as st
import pandas as pd


import requests
import os
import json
import time



# # This is my bearer token from my Twitter dev account

bearer_token = st.secrets["bearer_token"]


# This formats it into something that I don't quite understand, but which seems to make Twitter's API happy. (What is the "r" in the function doing?)
def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RetweetedByPython"
    return r


# WARNING

st.header("Retweet downloader")

# tweet url needs to have the id number at the end (you can see this url by clicking on the date of the tweet)
url = st.text_input("", "plain tweet url")

st.write("Remember: some quote-tweets may be disagreements. Please check before using. The app needs a plain tweet id, something like 'twitter.com/FullFact/status/1639942774223953920' without the ? and anything that follows at the end.")

# Sets sleep time, fast = 0, slow = 15
sleep_time = 0

slow_mode = st.checkbox('Tick to go slow if the tweet has more than about 7,000 retweets in total', help="Twitter's API won't allow itself to be swamped, so if we try to go too fast and demand too much, it's designed to break")

if slow_mode:
    st.write('Set to slow mode. The more retweets there are, the longer this will take. Check back every few minutes. 10,000 retweets can take half an hour or more.')
    sleep_time = 15

# Waits for an input with a tweet 
while "twitter.com" not in url:
     continue

# This is the bit that does the work

tweet_id = url.split("status")[1][1:] 

st.write("Collecting retweets...")

token=0

payload1 = {'user.fields': 'verified,public_metrics,description,location,entities', 'tweet.fields': 'author_id,created_at,geo,context_annotations,non_public_metrics,organic_metrics', "max_results":"100"} 

response = requests.request("GET", f"https://api.twitter.com/2/tweets/{tweet_id}/retweeted_by", 
                            auth=bearer_oauth, params=payload1)
print(response)
# print(response.json())
result_count = response.json()["meta"]["result_count"]
# print(result_count)
st.write(result_count)
if result_count == 0:
    print("done!")
    data = response.json()["data"]
else:
    data = response.json()["data"]
    token = response.json()["meta"]["next_token"]
    print(token)

while result_count != 0:
        payload2 = {"pagination_token":token, 'user.fields': 'verified,public_metrics,description,location,entities', 'tweet.fields': 'author_id,created_at,geo,context_annotations,non_public_metrics,organic_metrics', "max_results":"100"}
        # remove the next line if there are fewer than 7,000ish retweets and you want it to speed up
        time.sleep(sleep_time)
        response = requests.request("GET", f"https://api.twitter.com/2/tweets/{tweet_id}/retweeted_by", 
                                auth=bearer_oauth, params=payload2)
        print(response)
        result_count = response.json()["meta"]["result_count"]
        # print(result_count)
        st.write(result_count)
        if result_count == 0:
            print("done!")
        else:
            data_list = response.json()["data"]
            token = response.json()["meta"]["next_token"]
            for t in data_list:
                data.append(t)
    



    # And now for Quote Tweets we have to do a separate request

# tweet url needs to have the id number at the end (you can see this url by clicking on the date of the tweet)
# url = "https://twitter.com/profnfenton/status/1558140271694585858"
# tweet_id = url.split("status")[1][1:] 


st.write("Now collecting quote tweets...")

token=0

payload1 = {"expansions": "author_id", 'user.fields': 'verified,public_metrics,description,location,entities', 'tweet.fields': 'id,text,author_id,created_at,geo', "max_results":"100"} 

response = requests.request("GET", f"https://api.twitter.com/2/tweets/{tweet_id}/quote_tweets", 
                            auth=bearer_oauth, params=payload1)
print(response)
# print(response.json())
result_count = response.json()["meta"]["result_count"]
# print(result_count)
st.write(result_count)
if "next_token" not in response.json()["meta"]:
    print("done!")
    q_data = response.json()["data"]
    q_users = response.json()["includes"]["users"]
else:
    q_data = response.json()["data"]
    q_users = response.json()["includes"]["users"]
    token = response.json()["meta"]["next_token"]
    print(token)

while "next_token" in response.json()["meta"]:
        payload2 = {"pagination_token":token, "expansions": "author_id", 'user.fields': 'verified,public_metrics,description,location,entities', 'tweet.fields': 'id,text,author_id,created_at,geo', "max_results":"100"}
        # remove the next line if there are fewer than 7,000ish retweets and you want it to speed up
        time.sleep(sleep_time)
        response = requests.request("GET", f"https://api.twitter.com/2/tweets/{tweet_id}/quote_tweets", 
                                auth=bearer_oauth, params=payload2)
        print(response)
        result_count = response.json()["meta"]["result_count"]
        # print(result_count)
        st.write(result_count)
        if "next_token" in response.json()["meta"]:
            data_list = response.json()["data"]
            includes_list = response.json()["includes"]["users"]
            token = response.json()["meta"]["next_token"]
            for t in data_list:
                q_data.append(t)
            for i in includes_list:
                q_users.append(i)         
        else:
            print("done!")
    

q_tweeters = [[q["name"], q["username"], q["verified"], q["public_metrics"]["followers_count"], q["description"]] for q in q_users]
q_df = pd.DataFrame(q_tweeters)
q_df.rename(columns={0: "name", 1:"username", 2:"verified", 3:"followers", 4:"description"}, inplace=True)
q_df.sort_values(by=["followers"], inplace=True, ascending=False)


retweeters = [[d["name"], d["username"], d["verified"], d["public_metrics"]["followers_count"], d["description"]] for d in data]

q_re_tweeters = q_tweeters + retweeters

df = pd.DataFrame(q_re_tweeters)
df.rename(columns={0: "name", 1:"username", 2:"verified", 3:"followers", 4:"description"}, inplace=True)
df.sort_values(by=["followers"], inplace=True, ascending=False)


# df = pd.read_csv("q_re_tweets1635577217789878278.csv")

st.write("Just wait a moment. Your data is coming.")

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name=f"q_re_tweets{tweet_id}.csv",
    mime='text/csv',
)

st.write("Fun fact: The long number in the file name is the tweet id. If you paste it after twitter.com/anyone/status/ it'll take you back to the original tweet!")

st.balloons()

# st.balloons()

# if st.download_button(...):
#    st.write('Thanks for downloading!')