import requests
from bs4 import BeautifulSoup,SoupStrainer
import xml.etree.ElementTree as ET

# Create root
root = ET.Element("Library")

def url_list(baseURL,startURL,endURL):
    urlList = []
    response = requests.get(baseURL)

    if response.status_code==200:
            # Scrap
        soup = BeautifulSoup(response.content, 'lxml')
        main_content = soup.find("div", id="mw-content-text")
        # Get list of URLS from main content of the content page of the respective documentment
        list_urls = main_content.find_all("li")
        found = False
        for l in list_urls:
            link = l.find('a')
            # Find the starting URL
            if link['href'] == startURL:
                found = True
                print("found start")
                urlList.append("https://zh.wikisource.org" + link["href"])
            # Find the end then break out of loop
            elif link['href'] == endURL:
                urlList.append("https://zh.wikisource.org" + link["href"])
                print("broke off")
                break
            # After finding the start keep adding
            elif found:
                urlList.append("https://zh.wikisource.org" + link["href"])
    return urlList


def scrap_start_end(urlList,documentElement):
    counter = 0
    # Attempt to iterate from the start URL to the end
    for url in urlList:
        
        response = requests.get(url)

        if response.status_code==200:
            # Scrap
            soup = BeautifulSoup(response.content, 'lxml')
            # Content is within the main content div with the following ID
            main_context = soup.find("div", id="mw-content-text")
            content = ""
            # Create content to be later added to the XML element
            for item in main_context.find_all("p"):
                content += item.get_text(strip=True) + "\n"
            name_of_volume = soup.find("span", class_="mw-page-title-main").get_text()

            counter+= 1

            # Create XML element for the volume
            name_element = ET.SubElement(documentElement,"volume",id=f"Vol {counter}",name=name_of_volume)
            name_element.text = content.strip()
        else:
            return "Failed to get wepage"
    # return the counter to pass on to the next call of scrapping to maintain document ID's
    return counter

# Create documents
def create_xml(name, eng_name, document_name, baseURL, startURL, endURL):
    document = ET.SubElement(root, "document",name=name,eng_name=eng_name)
    arr = url_list(baseURL, startURL,endURL)
    print(arr)
    scrap_start_end(arr, document)

    tree = ET.ElementTree(root)
    tree.write(document_name, encoding="utf-8", xml_declaration=True)
    

# Best to run invididually incase any responses fail

# 2 Hanshu
#create_xml("漢書","Hansu","2_raw.xml","https://zh.wikisource.org/wiki/%E6%BC%A2%E6%9B%B8","/wiki/%E6%BC%A2%E6%9B%B8/%E5%8D%B7001%E4%B8%8A","/wiki/%E6%BC%A2%E6%9B%B8/%E5%8D%B7100%E4%B8%8B")

# 3 Book of the Later Han Dynasty
#create_xml("後漢書","Book of the Later Han Dynasty", "3_raw.xml", "https://zh.wikisource.org/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8", "/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B71%E4%B8%8A","/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B790")

# 4 Three Kingdoms
#create_xml("三國志", "Three Kingdoms", "4_raw.xml", "https://zh.wikisource.org/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97", "/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E5%8D%B701", "/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E5%8D%B765")

# 5 Jin Shu 
#create_xml("晉書", "Jinshu", "5_raw.xml", "https://zh.wikisource.org/wiki/%E6%99%89%E6%9B%B8", "/wiki/%E6%99%89%E6%9B%B8/%E5%8D%B7001", "/wiki/%E6%99%89%E6%9B%B8/%E5%8D%B7130")

# 6 Songshu
create_xml("宋書", "Songshu", "6_raw.xml","https://zh.wikisource.org/wiki/%E5%AE%8B%E6%9B%B8", "/wiki/%E5%AE%8B%E6%9B%B8/%E5%8D%B71", "/wiki/%E5%AE%8B%E6%9B%B8/%E5%8D%B7100")