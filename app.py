from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import dateparser

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019')
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('table', attrs={'class':'table'}) 
    tr = table.find_all('tr') 

    temp = [] #initiating a tuple

    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
        #get bulan
        TANGGAL = row.find_all('td')[0].text
        TANGGAL = TANGGAL.strip() #for removing the excess whitespace

        #get ASK
        ASK = row.find_all('td')[1].text
        ASK = ASK.strip() #for removing the excess whitespace
    
        #get BID
        BID = row.find_all('td')[2].text
        BID = BID.strip() #for removing the excess whitespace

        temp.append((TANGGAL,ASK,BID)) #append the needed information 
    
    temp = temp[::-1] #remove the header

    df = pd.DataFrame(temp, columns = ('Tanggal','Jual','Beli')) #creating the dataframe
    df[['Jual','Beli']]=df[['Jual','Beli']].replace(",",".",regex=True)
    df['Jual'] = df['Jual'].astype('float64')
    df['Beli'] = df['Beli'].astype('float64')
    df.Tanggal = df.Tanggal.apply(lambda x: dateparser.parse(x))
    df.Tanggal = pd.to_datetime(df.Tanggal)
    df.set_index('Tanggal', inplace=True)
   #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
