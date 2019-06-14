'''
Scrapes case documents from MA EFSB case

Created on Apr 18, 2019

@author: bschineller
'''

# Import libraries
import sys
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import datetime
from random import randint

OFFLINE = 1
DOWNLOAD = 0

def main():

    # echo command line arguments
    print("command line args=", sys.argv)    
    
    case_id = sys.argv[1]
    text = ''

    time_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    print(time_str)


    if not OFFLINE: 
           
        # Set the URL you want to webscrape from
        url = ('https://eeaonline.eea.state.ma.us/DPU/Fileroom//dockets/get/'
              '?number=' + case_id + '&edit=false')
 
    
        # Connect to the URL
        response = requests.get(url)
        text = response.text
        

    else:
        file = open(case_id+'.html','r')
        text = file.read()
        file.close()
    


    
    # Parse HTML and save to BeautifulSoup object¶
    soup = BeautifulSoup(text, "html.parser")
    # Write to file
    with open(case_id+time_str+".html", "w") as file:
        file.write(str(soup.prettify()))

    
    # Grab case header info
    case_number = soup.find_all("input",attrs={"name": "Number"})[0]["value"]
    print("number=", case_number)
    
    case_type = soup.find_all("input",attrs={"name": "CaseType"})[0]["value"]
    print("case_type=", case_type)
    
    industry = soup.find_all("input",attrs={"name": "Industry"})[0]["value"]
    print("industry=", industry)

    petitioner = soup.find_all("input",attrs={"name": "Petitioner"})[0]["value"]
    print("petitioner=", petitioner)

    case_caption = soup.find_all("textarea",attrs={"name": "CaseCaption"})[0].contents
    print("case_caption=", case_caption)

    hearing_officer = soup.find_all("input",attrs={"name": "HearingOfficer.DisplayName"})[0]["value"]
    print("hearing_officer=", hearing_officer)

    date_filed = soup.find_all("input",attrs={"name": "DateFiled"})[0]["value"]
    print("date_filed=", date_filed)

    date_closed = soup.find_all("input",attrs={"name": "DateClosed"})[0]["value"]
    print("date_closed=", date_closed)


    rows = soup.find_all("div", class_="divGridRow")
    for r in rows:
        print("-" * 40)
        
        filing_id = r['id']
        filing_created = r.find_next("span",class_="created").find_next('strong').string.replace('\n','').strip()
        filing_filer = r.find_next("span",class_="filer").string
        filing_type = r.find_next("span",class_="filingtype").string
        filing_description = r.find_next("div",class_="description").string
        
        
        
        print("id=", filing_id)
        print("created=", filing_created)
        print("filer=", filing_filer)
        print("filingtype=", filing_type)
        print("description=", filing_description)
        
        curr_id = r['id']
        ftag = r.find_next("div", id="files_"+curr_id)
        for f in ftag.find_all('a'):
            filename = f.string.strip()
            download_url = f['href']
            print("filename=", filename)
            print("url=", download_url)
            
            dpart = datetime.datetime.strptime(filing_created, "%m/%d/%Y").date().strftime("%Y%m%d")
            filer_part = (filing_filer.upper().replace(' ','').replace('\r','')
                            .replace('\n', '').replace('/','')
                         )
            local_filename = './'+case_number+'/'+ dpart + '-' + filer_part + '-' + filing_id + '-' + filename

            # temporary hack to get the older ones 
            if DOWNLOAD and dpart <= '20170614':            

                with open(local_filename, 'wb') as fn:
                    resp = requests.get(download_url, verify=False)
                    fn.write(resp.content)                
                
                time.sleep(1) #pause the code for a sec

if __name__ == '__main__':
    main()