def remove_emoji(string):
    import re
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def updateData():
    import tweepy as tp
    import re
    import string
    import pandas as pd
    from datetime import datetime, timedelta
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
    from sqlalchemy import create_engine
    
    # make your tweet api in twitter developer
    consumer_key = '#'
    consumer_secret = '#'
    access_token = '#'
    access_token_secret = '#'
    
    auth = tp.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tp.API(auth)
        
    keyword = 'vaksin covid'
    newKeyword = keyword + " -filter:retweets"
    ndays=2
    dateRange = datetime.now() - timedelta(days=ndays)
    date_since = dateRange.strftime('%Y-%m-%d')
    date_now = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
    tweets = tp.Cursor(api.search, q=newKeyword, lang="id", since=date_since, until=date_now,tweet_mode="extended").items(1000)
#     tweets = api.search(q=newKeyword, lang='id', until=date_now, since=date_since, tweet_mode='extended')
    items = []
    
    for tweet in tweets:
        item = []
        sn = tweet.user.screen_name
        date = tweet.created_at
        text = tweet.full_text #get full text
        text = text.strip() #remove empty char
        text = text.lower() #to lowercase
        text = re.sub(r"\d+", "", text) #remove number
        text = text.translate(str.maketrans('', '', string.punctuation)) #remove punctuation
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        text = stopword.remove(text)
        text = remove_emoji(text)
        item.append(sn)
        item.append(text)
        item.append(date.strftime('%Y-%m-%d'))
        item.append('-')
        items.append(item)
    
    pd.options.display.max_colwidth = 300
    df = pd.DataFrame(data=items, columns=['user', 'tweet', 'date', 'sentiment'])
    
    engine = create_engine('sqlite:///TugasAkhirDataScience_TweetSentiment.db', echo=False)
    sqlite_connection = engine.connect()
    
    sqlite_table = "tweet_data"
    df.to_sql(sqlite_table, sqlite_connection, if_exists='append', index=False)

def updateSentiment():
    import sqlalchemy as db
    import pandas as pd
    
    engine = db.create_engine('sqlite:///TugasAkhirDataScience_TweetSentiment.db', echo=False)
    sqlite_connection = engine.connect()
    metadata = db.MetaData()
    tweet_data = db.Table('tweet_data', metadata, autoload=True, autoload_with=engine)
    query = db.select([tweet_data])
    ResultProxy = sqlite_connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    
    df = pd.DataFrame(ResultSet)
    df.columns = ResultSet[0].keys()
    df = df.drop_duplicates(subset='tweet', keep='first')
    
    pos_list= open("kata_positif.txt","r")
    pos_kata = pos_list.readlines()
    neg_list= open("kata_negatif.txt","r")
    neg_kata = neg_list.readlines()
    
    s = []
    for index, data in df.iterrows():
        count_p = 0
        count_n = 0
        for kata_pos in pos_kata:
            if kata_pos.strip() in data['tweet']:
                count_p +=1
        for kata_neg in neg_kata:
            if kata_neg.strip() in data['tweet']:
                count_n +=1
        sentiment = count_p - count_n
        s.append(sentiment)
        
    df['sentiment'] = s
    
    sqlite_table = "tweet_sentiment"
    df.to_sql(sqlite_table, sqlite_connection, if_exists='replace', index=False)

def lihatData(since, until):
    import sqlalchemy as db
    import pandas as pd
    
    engine = db.create_engine('sqlite:///TugasAkhirDataScience_TweetSentiment.db', echo=False)
    sqlite_connection = engine.connect()
    metadata = db.MetaData()
    tweet_sentiment = db.Table('tweet_sentiment', metadata, autoload=True, autoload_with=engine)

    ResultProxy = sqlite_connection.execute("SELECT * FROM tweet_sentiment WHERE date BETWEEN :since AND :until", {'since': since, 'until': until})
    ResultSet = ResultProxy.fetchall()
    
    df = pd.DataFrame(ResultSet)
    return df

def visualize(since, until):
    import sqlalchemy as db
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    
    engine = db.create_engine('sqlite:///TugasAkhirDataScience_TweetSentiment.db', echo=False)
    sqlite_connection = engine.connect()
    metadata = db.MetaData()
    tweet_sentiment = db.Table('tweet_sentiment', metadata, autoload=True, autoload_with=engine)

    ResultProxy = sqlite_connection.execute("SELECT * FROM tweet_sentiment WHERE date BETWEEN :since AND :until", {'since': since, 'until': until})
    ResultSet = ResultProxy.fetchall()
    
    df = pd.DataFrame(ResultSet)
    
    labels, counts = np.unique(df[3], return_counts=True)
    fig, ax = plt.subplots(figsize=(12,8))
    ax.bar(labels, counts, align='center')
    ax.set_title('Sentiment terhadap topik tentang vaksin covid')
    print('Nilai rata-rata: ', np.mean(df[3]))
    print('Nilai Median: ', np.median(df[3]))
    print('Standar deviasi: ', np.std(df[3]))
    plt.show()
