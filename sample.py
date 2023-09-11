from googleapiclient.discovery import build
import streamlit as st
import pymongo
import mysql.connector

api_key = 'AIzaSyCmvBt6TF03_gAK0savUONhkkssNzlvLPc'
youtube = build("youtube", "v3", developerKey=api_key)
client = pymongo.MongoClient("mongodb+srv://ytharvesting:2v7lalqTcm9C4o3S@cluster0.goezfsa.mongodb.net/")
db = client['youtube_data']
conn = mysql.connector.connect(host='localhost',port = 3306, user='root', password='2v7lalqTcm9C4o3S', database='youtube_data')
cursor = conn.cursor()
st.write("### Enter YouTube Channel_ID below :")
channel_id = st.text_input("Enter here")

response = youtube.channels().list(
      part='snippet,contentDetails,statistics',
      id=channel_id).execute()

def get_channel_details(channel_id):
    ch_data = []
        
    if 'items' in response:
        for i in range(len(list(response['items']))):   
                data = {
                        'channel_id': response['items'][0]['id'],
                        'channel_name': response['items'][0]['snippet']['title'],
                        'channel_type': "",
                        'channel_views': response['items'][0]['statistics']['viewCount'],
                        'channel_description': response['items'][0]['snippet']['description'],
                        'channel_status': ""
                        }
                ch_data.append(data)
        return ch_data


if channel_id and st.button("Extract Data"):
            ch_details = get_channel_details(channel_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["channel_name"]}"] channel')
            st.table(ch_details)
            # ch_details = get_channel_details(channel_id)

if st.button("Upload to MongoDB"):
                with st.spinner('Please Wait for it...'):
                    ch_details = get_channel_details(channel_id)
                    collections1 = db.channel_details
                    collections1.insert_many(ch_details)
                    st.success("Upload to MongoDB successful !!")

def channel_names():
    ch_name = []
    for i in db.channel_details.find():
        keys = i.keys()
        if 'channel_name' in keys:
            ch_name.append(i['channel_name'])
    return ch_name

st.markdown("#   ")
st.markdown("### Select a channel to begin Transformation to SQL")
        
ch_names = channel_names()
user_inp = st.selectbox("Select channel",options= ch_names)
        
def insert_channels():
                collections = db.channel_details
                query = """INSERT INTO yt_channel VALUES(%s,%s,%s,%s,%s,%s)"""
                
                for i in collections.find({"Channel_name" : user_inp},{'_id':0}):
                    # cursor.execute(query,)
                    try:
                        cursor.execute(query, tuple(i.values()))
                        conn.commit()
                        st.success("Successfully inserted")
                        st.balloons()
                    except mysql.connector.Error as err:
                        st.error(f"MySQL Error: {err}")

if st.button("Insert into MYSQL"):
       try:
              insert_channels()
              st.success("Successfully inserted")
              st.balloons()
       except:
              st.error("Channel details already transformed!!")