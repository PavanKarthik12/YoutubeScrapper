import os
import time
import requests
from selenium import webdriver
import snowflake.connector
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as bs
videos_title={}
videos_links={}
videos_likes={}
videos_comments_count={}
commetators_comments={}
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
def snowflake_connnect(query,type=None):
    print("Data")
    conn = snowflake.connector.connect(
                    user='karthik777',
                    password='Pavan@123',
                    account='px65781.ap-southeast-1',
                    database='YOUTUBE_DB',
                    warehouse='YOUTUBE',
                    schema='PUBLIC',
                    )
    cur=conn.cursor()
    cur.execute('USE ROLE ACCOUNTADMIN')
    cur.execute(query)
    if type=='select':
        return cur.fetchall()
    cur.close()
    conn.commit()
    return "task done"
def fetch_image_titles(search_term,max_links_to_fetch,wd,sleep_between_interactions):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)
    wd.get(search_term)
    image_count = 0
    results_start = 0
    counter=0
    while image_count < max_links_to_fetch:
        print("Again")
        scroll_to_end(wd)
        thumbnail_results = wd.find_elements("css selector","ytd-grid-video-renderer.ytd-grid-renderer")
        number_results = len(thumbnail_results)
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        for each_thumb in thumbnail_results[results_start:number_results]:
            for each_title in each_thumb.find_elements("css selector","a.ytd-grid-video-renderer"):
                print(each_title.get_attribute('title'),image_count)
                if each_title.get_attribute('title') and image_count not in videos_title: 
                    videos_title[image_count]=each_title.get_attribute('title')
            for each_link in each_thumb.find_elements("css selector","a.ytd-thumbnail"):
                print(each_link.get_attribute('href'))
                if each_link.get_attribute('href') and image_count not in videos_links:
                    videos_links[image_count]=each_link.get_attribute('href')
                    with webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options) as wd1:
                        wd1.get(each_link.get_attribute('href'))
                        time.sleep(sleep_between_interactions)
                        for each_like in wd1.find_elements('css selector','yt-formatted-string.style-text'):
                            print(each_like.get_attribute('aria-label'))
                            if each_like.get_attribute('aria-label') and image_count not in videos_likes:
                                videos_likes[image_count]=each_like.get_attribute('aria-label')
                        counter_comment=0
                        for each_comments_count in wd1.find_elements('css selector','span.yt-formatted-string'):
                                if each_comments_count.text.isdigit():
                                    videos_comments_count[image_count]=each_comments_count.text
                                    print(each_comments_count.text)
                        for each_like in wd1.find_elements('css selector','yt-formatted-string.style-text'):
                            print(each_like.get_attribute('aria-label'))
                            if each_like.get_attribute('aria-label') and image_count not in videos_likes:
                                videos_likes[image_count]=each_like.get_attribute('aria-label')
                        each_video_comments=set()
                        time.sleep(sleep_between_interactions)
            image_count = len(videos_title)
            if len(videos_links)  >= max_links_to_fetch:
                print(f"Found: {len(videos_links)} title links, done!")
                break
        else:
            print("Found:", len(videos_links), "title links, looking for more ...")
            load_more_button = wd.find_elements("css selector", ".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")
        results_start = len(thumbnail_results)

def search_download(search_term,number_images,target_path='./images'):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))
    channel_name="".join(i for i in search_term.split("/")[4] if i.isalnum())
    drop_query='''DROP TABLE if exists {0} ;'''.format(channel_name)
    snowflake_connnect(drop_query)
    create_query="""create table {0} if not exists (s_no VARCHAR(250), title VARCHAR(250)  NULL,link VARCHAR(250)  NULL,likes VARCHAR(250)  NULL,comments VARCHAR(250) NULL);""".format(channel_name)
    print(snowflake_connnect(create_query))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    with webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options) as wd:
        res = fetch_image_titles(search_term, number_images, wd=wd, sleep_between_interactions=2)
    print(videos_links,videos_title,videos_likes,videos_comments_count,commetators_comments)
    return "Data is excuted"
