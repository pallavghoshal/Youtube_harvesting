#importing the necessary libraries
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import pymongo
from googleapiclient.discovery import build
# from PIL import Image
# SETTING PAGE CONFIGURATIONS
# icon = Image.open("Youtube_logo.png")
st.set_page_config(page_title= "Youtube Data Harvesting and Warehousing | By Pallav",
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={'About': """# This app is created by *Pallav!*"""})
# CREATING OPTION MENU
with st.sidebar:
    selected = option_menu(None, ["Home","Extract and Transform","View"], 
                           icons=["house-door-fill","tools","card-text"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px", 
                                                "--hover-color": "#C80101"},
                                   "icon": {"font-size": "30px"},
                                   "container" : {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#C80101"}})
# Bridging a connection with MongoDB Atlas and Creating a new database(youtube_data)
client = pymongo.MongoClient("mongodb+srv://ytharvesting:2v7lalqTcm9C4o3S@cluster0.goezfsa.mongodb.net/")
db = client['youtube_data']
# CONNECTING WITH MYSQL DATABASE
conn = mysql.connector.connect(host='localhost', user='root', password='2v7lalqTcm9C4o3S', database='youtube_data')
cursor = conn.cursor()
# BUILDING CONNECTION WITH YOUTUBE API
api_key = "AIzaSyDosX4iLh2c6kP-erK3DYc3znOO1GwZfL0"
youtube = build('youtube','v3',developerKey=api_key)
# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = []
    response = youtube.channels().list(part = 'snippet,contentDetails,statistics',
                                     id= channel_id).execute()
    for i in range(len(response['items'])):
        data = dict(        
                            channel_id = response['items'][0]['id'],
                            channel_name = response   ['items'][i]['snippet']['title'],
                            channel_type = '',
                            channel_views = response['items'][i]['statistics']['viewCount'],
                            channel_description = response['items'][i]['snippet']['description'],
                            channel_status = '',
                            Video_count = response['items'][0]['statistics']['videoCount']
                    )
        ch_data.append(data)
    return ch_data
# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids
# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids,channel_id):
    video_stats = []
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails, statistics').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=','.join(v_ids[i:i+50])).execute()
        for video in response['items']:
                video_details = dict(   Video_id = video['id'],
                                        Playlist_id = playlist_id,
                                        Video_Title = video['snippet']['title'],
                                        Video_Description = video['snippet']['description'],
                                        Published_date = video['snippet']['publishedAt'],
                                        View_count = int(video['statistics']['viewCount']),
                                        Like_count = int(video['statistics'].get('likeCount', 0)),
                                        Dislike_count = 0,
                                        Favorite_count = int(video['statistics']['favoriteCount']),
                                        Comment_count = int(video['statistics'].get('commentCount', 0)),
                                        Duration = video['contentDetails']['duration'],
                                        Thumbnail = video['snippet']['thumbnails']['default']['url'],
                                        Caption_status = video['contentDetails']['caption']
                               )
            
        video_stats.append(video_details)
    return video_stats

#FUNCTION TO GET PLAYLIST DETAILS
def get_playlist_details(channel_id):
                playlists = []
                request = youtube.playlists().list(
            part="snippet",
            channelId=channel_id,)
                response = request.execute()

# Extract the playlist data.
                for playlist in response["items"]:
                        playlist_data = {
                            "playlistid": playlist["id"],
                            "channel_id": playlist["snippet"]["channelId"],
                            "playlist_name": playlist["snippet"]["title"]
                            }
                        playlists.append(playlist_data)
                return playlists


# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                    videoId=v_id,
                                                    maxResults=100,
                                                    textFormat="plainText",
                                                    pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = dict(Comment_id = cmt['id'],
                            Video_id = cmt['snippet']['videoId'],
                            Comment_text = cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author = cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_published_date = cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            )
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    except:
        pass
    return comment_data
# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():   
    ch_name = []
    for i in db.channel_details.find(): #database -> collections named channel details
        keys = i.keys()
        if 'channel_name' in keys: #channel_name : "Nat GEO", "NDTV", "TLC"
            ch_name.append(i['channel_name'])
    return ch_name
# HOME PAGE
if selected == "Home":
    # Title Image
    
    col1,col2 = st.columns(2,gap= 'medium')
    col1.markdown("## :blue[Domain] : Social Media")
    col1.markdown("## :blue[Technologies used] : Python,MongoDB, Youtube Data API, MySql, Streamlit")
    col1.markdown("## :blue[Overview] : Retrieving the Youtube channels data from the Google API, storing it in a MongoDB as data lake, migrating and transforming data into a SQL database,then querying the data and displaying it in the Streamlit app.")
    col2.markdown("#   ")
    col2.markdown("#   ")
    col2.markdown("#   ")
    # col2.image("youtubeMain.png")
    
    
# EXTRACT and TRANSFORM PAGE
if selected == "Extract and Transform":
    tab1,tab2 = st.tabs(["$\huge EXTRACT $", "$\huge TRANSFORM $"])
    
    # EXTRACT TAB
    with tab1:
        st.markdown("#    ")
        st.write("### Enter YouTube Channel_ID below :") #"", 0 , False
        ch_id = st.text_input("Hint : Goto channel's home page > Right click > View page source > Find channel_id")
        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["channel_name"]}"] channel')
            st.table(ch_details)
        if st.button("Upload to MongoDB"):
            with st.spinner('Please Wait for it...'):
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids, ch_id)
                play_details = get_playlist_details(ch_id)
                
                def comments():
                    com_d = []
                    for i in v_ids:
                        com_d+= get_comments_details(i)
                    return com_d
                comm_details = comments()
                collections1 = db.channel_details
                collections1.insert_many(ch_details)
                collections2 = db.video_details
                collections2.insert_many(vid_details)
                collections3 = db.comments_details
                collections3.insert_many(comm_details)
                collections4 = db.playlist_details
                collections4.insert_many(play_details)
                st.success("Upload to MongoDB successful !!")
      
    # TRANSFORM TAB
    with tab2:     
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")
        
        ch_names = channel_names()
        user_inp = st.selectbox("Select channel", options= ch_names)
        
        def insert_channels():
                collections = db['channel_details']
                query = """INSERT INTO yt_channel VALUES(%s,%s,%s,%s,%s,%s,%s)"""
                for i in collections.find({"channel_name" : user_inp},{'_id':0}):
                        cursor.execute(query,tuple(i.values()))
                        conn.commit()

        def insert_into_videos():
            collectionss = db['video_details']
            query1 = """INSERT INTO yt_video VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for i in collectionss.find():
                    cursor.execute(query1,tuple(i.values()))
                    conn.commit()
        def insert_into_comments():
            collections1 = db.video_details
            collections2 = db.comments_details
            query2 = """INSERT INTO yt_comment VALUES(%s,%s,%s,%s,%s)"""
            for vid in collections1.find():
                for i in collections2.find({'Video_id': vid['Video_id']},{'_id' : 0}):
                        t=tuple(i.values())
                        cursor.execute(query2,t)
                        conn.commit()
          def insert_into_playlist():
             col = db['playlist_details']
             coll = db['channel_details']
             query = """INSERT INTO yt_playlist VALUES(%s,%s,%s)"""
             for i in coll.find({"channel_name" : user_inp},{'_id':0}):
                  for j in col.find({'Channel_id': i['channel_id']},{'_id' : 0}):
                       cursor.execute(query,tuple(i.values()))
                       conn.commit()

        if st.button("Submit"):
            cursor.execute("SELECT channel_name FROM yt_channel")
                    # Fetch the results.
            results = cursor.fetchall()
            res = False
                    # Print the results
            for row in results:
                     if row[0] == user_inp:
                          res = True
            if res:
                st.error("Channel already inserted")
            else:
                insert_channels()
                insert_into_videos()
                insert_into_comments()
                insert_
                st.success("Sucesfully inserted")
                st.balloons()
                
# VIEW PAGE
if selected == "View":
    
    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Questions',
    ['Click the question that you would like to query',
    '1. What are the names of all the videos and their corresponding channels?',
    '2. Which channels have the most number of videos, and how many videos do they have?',
    '3. What are the top 10 most viewed videos and their respective channels?',
    '4. How many comments were made on each video, and what are their corresponding video names?',
    '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
    '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
    '7. What is the total number of views for each channel, and what are their corresponding channel names?',
    '8. What are the names of all the channels that have published videos in the year 2022?',
    '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
    '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])
    
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        cursor.execute("""SELECT video_name AS name, channel_name AS Channel_Name FROM yt_video ORDER BY channel_name""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
        
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        cursor.execute("""SELECT channel_name 
        AS Channel_Name, video_count AS Total_Videos
                            FROM yt_channel
                            ORDER BY total_videos DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        #st.bar_chart(df,x= cursor.column_names[0],y= cursor.column_names[1])
        fig = px.bar(df,
                     x=cursor.column_names[0],
                     y=cursor.column_names[1],
                     orientation='v',
                     color=cursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        cursor.execute("""SELECT channel_name AS Channel_Name, video_name AS Video_Title, view_count AS Views 
                            FROM yt_video
                            ORDER BY view_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x=cursor.column_names[2],
                     y=cursor.column_names[1],
                     orientation='h',
                     color=cursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        cursor.execute("""SELECT a.video_id AS Video_id, a.video_name AS Video_Title, b.comment_count
                            FROM yt_video AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM yt_comment GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
          
    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        cursor.execute("""SELECT channel_name AS Channel_Name,video_name AS Title,like_count AS Likes_Count 
                            FROM videos
                            ORDER BY like_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        fig = px.bar(df,
                     x=cursor.column_names[2],
                     y=cursor.column_names[1],
                     orientation='h',
                     color=cursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        cursor.execute("""SELECT video_name AS Title, like_count AS Likes_Count
                            FROM yt_video
                            ORDER BY like_count DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
         
    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        cursor.execute("""SELECT channel_name AS Channel_Name, view_count AS Views
                            FROM yt_channel
                            ORDER BY view_count DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
        st.write("### :green[Channels vs Views :]")
        fig = px.bar(df,
                     x=cursor.column_names[0],
                     y=cursor.column_names[1],
                     orientation='v',
                     color=cursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        cursor.execute("""SELECT channel_name AS Channel_Name
                            FROM yt_video
                            WHERE published_date LIKE '2022%'
                            GROUP BY channel_name
                            ORDER BY channel_name""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        cursor.execute("""SELECT channel_name AS Channel_Name,
                            AVG(duration)/60 AS "Average_Video_Duration (mins)"
                            FROM yt_video
                            GROUP BY channel_name
                            ORDER BY AVG(duration)/60 DESC""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        cursor.execute("""SELECT channel_name, 
                        SUM(duration_sec) / COUNT(*) AS average_duration
                        FROM (
                            SELECT channel_name, 
                            CASE
                                WHEN duration REGEXP '^PT[0-9]+H[0-9]+M[0-9]+S$' THEN 
                                TIME_TO_SEC(CONCAT(
                                SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'H', 1), 'T', -1), ':',
                            SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'M', 1), 'H', -1), ':',
                            SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'M', -1)
                            ))
                                WHEN duration REGEXP '^PT[0-9]+M[0-9]+S$' THEN 
                                TIME_TO_SEC(CONCAT(
                                '0:', SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'M', 1), 'T', -1), ':',
                                SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'M', -1)
                            ))
                                WHEN duration REGEXP '^PT[0-9]+S$' THEN 
                                TIME_TO_SEC(CONCAT('0:0:', SUBSTRING_INDEX(SUBSTRING_INDEX(duration, 'S', 1), 'T', -1)))
                                END AS duration_sec
                        FROM yt_video
                        ) AS subquery
                        GROUP BY channel_name""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names
                          )
        st.write(df)
        st.write("### :green[Avg video duration for channels :]")
        fig = px.bar(df,
                     x=cursor.column_names[0],
                     y=cursor.column_names[1],
                     orientation='v',
                     color=cursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        st.write("### :green[Average video duration for channels :]")



    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        cursor.execute("""SELECT channel_name AS Channel_Name,video_id AS Video_ID,comment_count AS Comments
                            FROM yt_video
                            ORDER BY comment_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(cursor.fetchall(),columns=cursor.column_names)
        st.write(df)
        st.write("### :green[Videos with most comments :]")
        fig = px.bar(df,
                     x=cursor.column_names[1],
                     y=cursor.column_names[2],
                     orientation='v',
                     color=cursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
