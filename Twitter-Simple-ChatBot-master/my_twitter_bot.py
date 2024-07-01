# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 00:42:20 2020

@author: ninaz
"""
import time
import tweepy

consumer_key = 'Ooe3uTwY2ntkY28E826k2zR9f'
consumer_secret = 'jMtVuWqiIHAQ5GIVucdPxUKKVdlbHaoC8Y2SMz1rzvAp5hl3rc'
access_key = '989553821973209088-ugGiVIybi06fyKjYoZ4eaQV8cRbEEzP'
access_secret = 'mXf96KxqfDIk96fUe29btGq1sCETlxSS7VfHZU3AEr8pl'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth) #will use this to communicate with twitter
mentions = api.mentions_timeline() #returns a list of whole timeline
#print(mentions[0].__dict__.keys) #atribautes of this class and easier to see ex.ID/Text...
#print(mentions[0].text) will print last tweet came to my developer account
#print(mentions[0].id) # returns int
#print(mentions[1].__dict__.keys())

def reply_to_tweets():
    print('retrieving and replying to tweets')
#    for i in mentions:
#        print(i.text +' - ' + str(i.id))
    
    def retrieve_last():
        fread = open('last_seen.txt', 'r')
        last_id = int(fread.read().strip())
        fread.close()
        return last_id
    
    def store_last(l_id):
        fwrite = open('last_seen.txt', 'w')
        fwrite.write(str(l_id))
        fwrite.close()

   
#    print('####################################################')        
    last_id = retrieve_last()
    mentions2 = api.mentions_timeline(last_id)
    for i in reversed(mentions2): # will print the last tweets after "last_seen" or new unprinted tweets 
        l = i.text.lower() #if dont have reversed then it will print duplicates cuz its taking first tweet not last
        if '#helloworld' in l or 'hi' in l:
             print(i.text , '  ' , 'True')
             api.update_status('@' + i.user.screen_name + 'tweet back, this is a text', i.id)
        else:
             print(i.text , '  ' , 'False')
             
        store_last(i.id)
      
    #for i in mentions:
while True:
    reply_to_tweets()
    time.sleep(15)     
