from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import titles
from titles import search_download,snowflake_connnect
app = Flask(__name__)
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    print("hello")
    return render_template("index.html")

@app.route('/data',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
           channel_link=request.form['content']
           search_download(channel_link,20)
           channel_title="".join(i for i in channel_link.split("/")[4] if i.isalnum())
           select_query=''' select * from {0}'''.format(channel_title)
           query_result=snowflake_connnect(select_query,'select')
        except:
            print("Exceptio occured while collectiong data")
        else:
            return render_template('results.html',query_results=query_result)
    else:
        return render_template('index.html')


if __name__ == "__main__":
	app.run(debug=True)
