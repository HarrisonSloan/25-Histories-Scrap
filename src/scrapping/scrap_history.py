import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from pathlib import Path

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
            # TODO add a "h2" element in here for the headings
            for item in main_context.find_all(["h2","p"]):
                if item.name == 'h2':  # If it's a header
                    content += item.get_text(strip=True) + "\n"  # Markdown-style header
                elif item.name == 'p':  # If it's a paragraph
                    content += item.get_text(strip=True) + "\n"
            name_of_volume = soup.find("span", class_="mw-page-title-main").get_text()

            counter+= 1

            # Create XML element for the volume
            name_element = ET.SubElement(documentElement,"volume",id=f"{counter}",name=name_of_volume)
            name_element.text = content.strip()
        else:
            return "Failed to get wepage"
    # return the counter to pass on to the next call of scrapping to maintain document ID's
    return counter

# Create documents
def create_xml(name, eng_name, document_name, baseURL, startURL, endURL):
    root = ET.Element("Library")
    document = ET.SubElement(root, "document",name=name,eng_name=eng_name)
    arr = url_list(baseURL, startURL,endURL)
    print(arr)
    scrap_start_end(arr, document)

    # Define the directory and file name
    output_dir = Path(__file__).parent / "../../data/raw/scrapping/raw_scrapped_by_volume"
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

    # Construct the full path
    document_name_and_path = output_dir / document_name

    tree = ET.ElementTree(root)
    tree.write(document_name_and_path, encoding="utf-8", xml_declaration=True)


# Best to run invididually incase any responses fail

# 2 Hanshu
#create_xml("漢書","Book of Han","02_raw_inc_titles.xml","https://zh.wikisource.org/wiki/%E6%BC%A2%E6%9B%B8","/wiki/%E6%BC%A2%E6%9B%B8/%E5%8D%B7001%E4%B8%8A","/wiki/%E6%BC%A2%E6%9B%B8/%E5%8D%B7100%E4%B8%8B")

# # 3 Book of the Later Han Dynasty
#create_xml("後漢書","Book of the Later Han", "03_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8", "/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B71%E4%B8%8A","/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B790")
# include appendix 

# # 4 Three Kingdoms
# create_xml("三國志", "Records of the Three Kingdoms", "04_raw.xml", "https://zh.wikisource.org/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97", "/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E5%8D%B701", "/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E5%8D%B765")
# include appendix
#create_xml("三國志", "Records of the Three Kingdoms", "04_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97", "/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E5%8D%B701", "/wiki/%E4%B8%89%E5%9C%8B%E5%BF%97/%E4%B8%8A%E4%B8%89%E5%9B%BD%E5%BF%97%E8%A8%BB%E8%A1%A8")

# # 5 Jin Shu 
#create_xml("晉書", "Book of Jin", "05_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E6%99%89%E6%9B%B8", "/wiki/%E6%99%89%E6%9B%B8/%E5%8D%B7001", "/wiki/%E6%99%89%E6%9B%B8/%E5%8D%B7130")

# # 6 Songshu
#create_xml("宋書", "Book of Song", "06_raw_inc_titles.xml","https://zh.wikisource.org/wiki/%E5%AE%8B%E6%9B%B8", "/wiki/%E5%AE%8B%E6%9B%B8/%E5%8D%B71", "/wiki/%E5%AE%8B%E6%9B%B8/%E5%8D%B7100")

# # 7 Nan Qi Shu
# create_xml("南齊書", "Book of Southern Qi", "07_raw.xml","https://zh.wikisource.org/wiki/%E5%8D%97%E9%BD%8A%E6%9B%B8", "/wiki/%E5%8D%97%E9%BD%8A%E6%9B%B8/%E5%8D%B71", "/wiki/%E5%8D%97%E9%BD%8A%E6%9B%B8/%E5%8D%B759")
# include appendix 
#create_xml("南齊書", "Book of Southern Qi", "07_raw_inc_titles.xml","https://zh.wikisource.org/wiki/%E5%8D%97%E9%BD%8A%E6%9B%B8", "/wiki/%E5%8D%97%E9%BD%8A%E6%9B%B8/%E5%8D%B71", "/wiki/%E5%8D%97%E9%BD%8A%E6%9B%B8/%E7%99%BE%E8%A1%B2%E6%9C%AC%E8%B7%8B")

# # 8 Liang Shu
# create_xml("梁書", "Book of Liang", "08_raw.xml","https://zh.wikisource.org/wiki/%E6%A2%81%E6%9B%B8", "/wiki/%E6%A2%81%E6%9B%B8/%E5%8D%B701", "/wiki/%E6%A2%81%E6%9B%B8/%E5%8D%B756")
# include appendix 
#create_xml("梁書", "Book of Liang", "08_raw_inc_titles.xml","https://zh.wikisource.org/wiki/%E6%A2%81%E6%9B%B8", "/wiki/%E6%A2%81%E6%9B%B8/%E5%8D%B701", "/wiki/%E6%A2%81%E6%9B%B8%E7%9B%AE%E9%8C%84%E5%BA%8F")

# # 9 Chen Shu 
# create_xml("陳書", "Book of Chen", "09_raw.xml", "https://zh.wikisource.org/wiki/%E9%99%B3%E6%9B%B8", "/wiki/%E9%99%B3%E6%9B%B8/%E5%8D%B71", "/wiki/%E9%99%B3%E6%9B%B8/%E5%8D%B736")
# include appendix
create_xml("陳書", "Book of Chen", "09_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E9%99%B3%E6%9B%B8", "/wiki/%E9%99%B3%E6%9B%B8/%E5%BA%8F", "/wiki/%E9%99%B3%E6%9B%B8/%E5%8D%B736")

# # 10 Wei Shu
# create_xml("魏書", "Book of Wei","10_raw.xml", "https://zh.wikisource.org/wiki/%E9%AD%8F%E6%9B%B8", "/wiki/%E9%AD%8F%E6%9B%B8/%E5%8D%B71", "/wiki/%E9%AD%8F%E6%9B%B8/%E5%8D%B7114")
# include appendix
#create_xml("魏書", "Book of Wei","10_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E9%AD%8F%E6%9B%B8", "/wiki/%E9%AD%8F%E6%9B%B8/%E5%8D%B71", "/wiki/%E8%88%8A%E6%9C%AC%E9%AD%8F%E6%9B%B8%E7%9B%AE%E9%8C%84%E5%8F%99")

# # 11 Book of the Northern Qi
#create_xml("北齊書", "Book of Northern Qi", "11_raw_inc_titles.xml","https://zh.wikisource.org/wiki/%E5%8C%97%E9%BD%8A%E6%9B%B8", "/wiki/%E5%8C%97%E9%BD%8A%E6%9B%B8/%E5%8D%B71", "/wiki/%E5%8C%97%E9%BD%8A%E6%9B%B8/%E5%8D%B750")

# # 12 Zhou Shu
# create_xml("周書", "Book of Zhou", "12_raw.xml", "https://zh.wikisource.org/wiki/%E5%91%A8%E6%9B%B8", "/wiki/%E5%91%A8%E6%9B%B8/%E5%8D%B701", "/wiki/%E5%91%A8%E6%9B%B8/%E5%8D%B750")
# include appendix
#create_xml("周書", "Book of Zhou", "12_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E5%91%A8%E6%9B%B8", "/wiki/%E5%91%A8%E6%9B%B8/%E5%8D%B701", "/wiki/%E5%91%A8%E6%9B%B8%E7%9B%AE%E9%8C%84%E5%BA%8F")

# # 13 Sui Shu
# create_xml("隋書", "Book of Sui", "13_raw.xml", "https://zh.wikisource.org/wiki/%E9%9A%8B%E6%9B%B8", "/wiki/%E9%9A%8B%E6%9B%B8/%E5%8D%B701", "/wiki/%E9%9A%8B%E6%9B%B8/%E5%8D%B785")
# include appendix
#create_xml("隋書", "Book of Sui", "13_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E9%9A%8B%E6%9B%B8", "/wiki/%E9%9A%8B%E6%9B%B8/%E5%8D%B701", "/wiki/%E9%9A%8B%E6%9B%B8/%E5%8E%9F%E8%B7%8B")

# # 14 Southern Histroy 
#create_xml("南史", "History of the Southern Dynasties", "14_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E5%8D%97%E5%8F%B2",  "/wiki/%E5%8D%97%E5%8F%B2/%E5%8D%B701", "/wiki/%E5%8D%97%E5%8F%B2/%E5%8D%B780")

# # 15 Northern History 
#create_xml("北史", "History of the Northern Dynasties", "15_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E5%8C%97%E5%8F%B2", "/wiki/%E5%8C%97%E5%8F%B2/%E5%8D%B7001", "/wiki/%E5%8C%97%E5%8F%B2/%E5%8D%B7100")

# # 16 Old Tang Book 
#create_xml("舊唐書", "Old Book of Tang", "16_raw.xml", "https://zh.wikisource.org/wiki/%E8%88%8A%E5%94%90%E6%9B%B8", "/wiki/%E8%88%8A%E5%94%90%E6%9B%B8/%E5%8D%B71", "/wiki/%E8%88%8A%E5%94%90%E6%9B%B8/%E5%8D%B7200%E4%B8%8B")
# include appendix 
#create_xml("舊唐書", "Old Book of Tang", "16_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E8%88%8A%E5%94%90%E6%9B%B8", "/wiki/%E8%88%8A%E5%94%90%E6%9B%B8/%E5%8D%B71", "/wiki/%E8%88%8A%E5%94%90%E6%9B%B8/%E9%99%84%E9%8C%84")

# # 17 New book of Tang 
# create_xml("新唐書", "New Book of Tang", "17_raw.xml", "https://zh.wikisource.org/wiki/%E6%96%B0%E5%94%90%E6%9B%B8", "/wiki/%E6%96%B0%E5%94%90%E6%9B%B8/%E5%8D%B7001", "/wiki/%E6%96%B0%E5%94%90%E6%9B%B8/%E5%8D%B7225%E4%B8%8B")
# include appendix 
#create_xml("新唐書", "New Book of Tang", "17_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E6%96%B0%E5%94%90%E6%9B%B8", "/wiki/%E6%96%B0%E5%94%90%E6%9B%B8/%E5%8D%B7001", "/wiki/%E6%96%B0%E5%94%90%E6%9B%B8/%E9%99%84%E9%8C%84")

# # 18 History of the Old Five Dynasties 
# create_xml("舊五代史","Old History of the Five Dynasties", "18_raw.xml", "https://zh.wikisource.org/wiki/%E8%88%8A%E4%BA%94%E4%BB%A3%E5%8F%B2",  "/wiki/%E8%88%8A%E4%BA%94%E4%BB%A3%E5%8F%B2/%E5%8D%B71", "/wiki/%E8%88%8A%E4%BA%94%E4%BB%A3%E5%8F%B2/%E5%8D%B7150")
# include appendix 
#create_xml("舊五代史","Old History of the Five Dynasties", "18_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E8%88%8A%E4%BA%94%E4%BB%A3%E5%8F%B2",  "/wiki/%E8%88%8A%E4%BA%94%E4%BB%A3%E5%8F%B2/%E5%8D%B71", "/wiki/%E8%88%8A%E4%BA%94%E4%BB%A3%E5%8F%B2/%E9%99%84%E9%8C%B2")

# # 19 New Five Dynasties History 
# create_xml("新五代史","Historical Records of the Five Dynasties", "19_raw.xml", "https://zh.wikisource.org/wiki/%E6%96%B0%E4%BA%94%E4%BB%A3%E5%8F%B2", "/wiki/%E6%96%B0%E4%BA%94%E4%BB%A3%E5%8F%B2/%E5%8D%B701", "/wiki/%E6%96%B0%E4%BA%94%E4%BB%A3%E5%8F%B2/%E5%8D%B771")
# include appendix (amd volume on Barbarians)
#create_xml("新五代史","Historical Records of the Five Dynasties", "19_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E6%96%B0%E4%BA%94%E4%BB%A3%E5%8F%B2", "/wiki/%E6%96%B0%E4%BA%94%E4%BB%A3%E5%8F%B2/%E5%8D%B701", "/wiki/%E4%BA%94%E4%BB%A3%E5%8F%B2%E8%A8%98%E5%BA%8F")

# # 20 History of Song Dynasty 
# create_xml("宋史", "History of Song", "20_raw.xml", "https://zh.wikisource.org/wiki/%E5%AE%8B%E5%8F%B2","/wiki/%E5%AE%8B%E5%8F%B2/%E5%8D%B7001", "/wiki/%E5%AE%8B%E5%8F%B2/%E5%8D%B7496")
# inlcude appendix 
#create_xml("宋史", "History of Song", "20_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E5%AE%8B%E5%8F%B2","/wiki/%E5%AE%8B%E5%8F%B2/%E5%8D%B7001", "/wiki/%E5%AE%8B%E5%8F%B2/%E9%99%84%E9%8C%B2")

# # 21 Liao History 
# create_xml("遼史", "History of Liao", "21_raw.xml", "https://zh.wikisource.org/wiki/%E9%81%BC%E5%8F%B2", "/wiki/%E9%81%BC%E5%8F%B2/%E5%8D%B71", "/wiki/%E9%81%BC%E5%8F%B2/%E5%8D%B7116")
# include appendix 
#create_xml("遼史", "History of Liao", "21_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E9%81%BC%E5%8F%B2", "/wiki/%E9%81%BC%E5%8F%B2/%E5%8D%B71", "/wiki/%E9%81%BC%E5%8F%B2/%E9%99%84%E9%8C%84")

# # 22 Jinshi 
# create_xml("金史", "History of Jin", "22_raw.xml", "https://zh.wikisource.org/wiki/%E9%87%91%E5%8F%B2", "/wiki/%E9%87%91%E5%8F%B2/%E5%8D%B71", "/wiki/%E9%87%91%E5%8F%B2/%E5%8D%B7135")
# include appendix
#create_xml("金史", "History of Jin", "22_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E9%87%91%E5%8F%B2", "/wiki/%E9%87%91%E5%8F%B2/%E5%8D%B71", "/wiki/%E9%87%91%E5%8F%B2/%E9%99%84%E9%8C%84")

# # 23 Yuan History 
# create_xml("元史", "History of Yuan", "23_raw.xml", "https://zh.wikisource.org/wiki/%E5%85%83%E5%8F%B2", "/wiki/%E5%85%83%E5%8F%B2/%E5%8D%B7001", "/wiki/%E5%85%83%E5%8F%B2/%E5%8D%B7210")
# include appendix
#create_xml("元史", "History of Yuan", "23_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E5%85%83%E5%8F%B2", "/wiki/%E5%85%83%E5%8F%B2/%E5%8D%B7001", "/wiki/%E5%85%83%E5%8F%B2/%E9%80%B2%E5%85%83%E5%8F%B2%E8%A1%A8")

# # 24 History of Ming Dynasty 
# create_xml("明史", "History of Ming", "24_raw.xml", "https://zh.wikisource.org/wiki/%E6%98%8E%E5%8F%B2", "/wiki/%E6%98%8E%E5%8F%B2/%E5%8D%B71", "/wiki/%E6%98%8E%E5%8F%B2/%E5%8D%B7332")
# include appendix
#create_xml("明史", "History of Ming", "24_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E6%98%8E%E5%8F%B2", "/wiki/%E6%98%8E%E5%8F%B2/%E5%8D%B71", "/wiki/%E4%B8%8A%E6%98%8E%E5%8F%B2%E8%A1%A8")

# # 25 Draft History of Qing Dynasty
# create_xml("清史稿", "Draft History of Qing", "25_raw.xml", "https://zh.wikisource.org/wiki/%E6%B8%85%E5%8F%B2%E7%A8%BF", "/wiki/%E6%B8%85%E5%8F%B2%E7%A8%BF/%E5%8D%B71", "/wiki/%E6%B8%85%E5%8F%B2%E7%A8%BF/%E5%8D%B7529")
# include appendix 
#create_xml("清史稿", "Draft History of Qing", "25_raw_inc_titles.xml", "https://zh.wikisource.org/wiki/%E6%B8%85%E5%8F%B2%E7%A8%BF", "/wiki/%E6%B8%85%E5%8F%B2%E7%A8%BF/%E5%8D%B71", "/wiki/%E6%B8%85%E5%8F%B2%E7%A8%BF/%E9%99%84%E9%8C%84")
