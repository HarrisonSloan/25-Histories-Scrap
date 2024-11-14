import requests
from bs4 import BeautifulSoup,SoupStrainer
import xml.etree.ElementTree as ET

# Create root
root = ET.Element("Library")

def scrap_start_end(documentElement,baseURL, startURL, endURL,start=0):
    counter = start
    current_url = startURL
    # Attempt to iterate from the start URL to the end
    while True:
        
        response = requests.get(current_url)

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
        

        if current_url == endURL:
            print("found ending page")
            break
        
        # Proceed to next webpage
        # next link is always contained in the table at the top on the right hand side
        header_table = soup.find('table', class_="header")
        table_data = header_table.find_all('td')
        next_link = table_data[-1].find('a') # -1 to index right most table data element
        if next_link and 'href' in next_link.attrs:
            current_url = baseURL + next_link['href'] # create new url to traverse to
            print(current_url)
            print("found next link")
        else:
            print(counter, " pages scrapped")
            print("No next link found. Exiting.")
            break
    print(counter, " pages scrapped")
    print("found the end")
    # return the counter to pass on to the next call of scrapping to maintain document ID's
    return counter

document = ET.SubElement(root, "document",name="後漢書")

count = scrap_start_end(document,'https://zh.wikisource.org','https://zh.wikisource.org/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B71%E4%B8%8A','https://zh.wikisource.org/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B790')
# missing next link need to call again
scrap_start_end(document,'https://zh.wikisource.org','https://zh.wikisource.org/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B723',"https://zh.wikisource.org/wiki/%E5%BE%8C%E6%BC%A2%E6%9B%B8/%E5%8D%B790",count)

tree = ET.ElementTree(root)
tree.write("scraped_data.xml", encoding="utf-8", xml_declaration=True)