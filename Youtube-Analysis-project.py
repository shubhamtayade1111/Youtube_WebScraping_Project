#!/usr/bin/env python
# coding: utf-8

# # Loading Libraries and packages

# In[1]:


from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns


# # Creating youtube API key and extracting data from a few channel URL

# In[2]:


api_key = 'AIzaSyCFURJptGCj0i4NyoJWdEhTYG0-QF3oyuY'

channel_ids = ['UCYJyrEdlwxUu7UwtFS6jA_Q' , #unveiled
                'UCvhsiQGy_zcNCiSbeXEjhLg' , #rsa animate
                'UCLXo7UDZvByw2ixzpQCufnA' , #vox
                 'UCphTF9wHwhCt-BzIq-s4V-g' , #what if
                'UCkQO3QsgTpNTsOw6ujimT5Q' , #be amazed
              ]

youtube = build('youtube', 'v3', developerKey=api_key)


# ## Function to get channel statistics

# In[3]:


def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(channel_ids))
    response = request.execute() 
    
    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscribers = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)
    
    return all_data


# In[4]:


channel_statistics = get_channel_stats(youtube, channel_ids)


# In[5]:


channel_data = pd.DataFrame(channel_statistics)


# In[6]:


channel_data


# # Checking the data type of each column

# In[7]:


channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
channel_data.dtypes


# # Who has the highest number of subcribers ?

# In[9]:


sns.set(rc={'figure.figsize':(10,8)})
ax = sns.barplot(x='Channel_name', y='Subscribers', data=channel_data)


# # Who's got the most views ?

# In[18]:


ax = sns.barplot(x='Channel_name', y='Views', data=channel_data)


# # Who uploaded the highest number of videos?

# In[12]:


ax = sns.barplot(x='Channel_name', y='Total_videos', data=channel_data)


# ## Function to get video ids

# In[13]:


channel_data


# # Analyzing a channel in Detail : What If

# In[138]:


playlist_id = channel_data.loc[channel_data['Channel_name']=='What If', 'playlist_id'].iloc[0]


# In[139]:


def get_video_ids(youtube, playlist_id):
    
    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()
    
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
        
    return video_ids


# In[140]:


video_ids = get_video_ids(youtube, playlist_id)


# In[141]:


video_ids


# ## Function to get video details for channel What If

# In[142]:


def get_video_details(youtube, video_ids):
    all_video_stats = []
    
    for i in range(0,len(video_ids),50):
        
        request = youtube.videos().list(
             part = 'snippet,statistics',
              id = ','.join(video_ids[i:i+50]))
    response = request.execute()
    
    for video in response['items']:
        video_stats = dict(Title = video['snippet']['title'],
                           Published_date = video['snippet']['publishedAt'],
                           Views = video['statistics']['viewCount'],
                           Likes = video['statistics']['likeCount'],
                           Comments = video['statistics']['commentCount'],
                           )
        all_video_stats.append(video_stats)
        
    return all_video_stats


# In[143]:


video_details = get_video_details(youtube, video_ids)


# In[144]:


video_data = pd.DataFrame(video_details)


# In[145]:


video_data


# In[146]:


video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data


# ## Top 10 Videos of What If

# In[147]:


top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)


# In[148]:


top10_videos


# In[149]:


ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)


# In[150]:


video_data


# ## Videos released per month by What If

# In[151]:


video_data['Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')


# In[152]:


video_data


# In[153]:


videos_per_month = video_data.groupby('Month', as_index=False).size()


# In[154]:


videos_per_month


# In[155]:


sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


# In[156]:


videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories=sort_order, ordered=True)


# In[157]:


videos_per_month = videos_per_month.sort_index()


# In[158]:


ax2 = sns.barplot(x='Month', y='size', data=videos_per_month)


# In[160]:


video_data.to_csv('Video_Details(What If).csv')


# In[ ]:




