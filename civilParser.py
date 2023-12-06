import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["civilCrawler"]
html_collection = db["civilProfs"]
research_collection = db["civilResearch"]

# Function to parse and persist professor's information
def parse_and_persist_professor_info(html,url):
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Extract professor information 
    name = soup.find('h1').text.strip()
    title_dept = soup.find('span', class_='title-dept').text.strip()
    email = soup.find('p', class_='emailicon').find('a')['href'].replace('mailto:', '')
    phone = soup.find('p', class_='phoneicon').text.strip()
    office_location = soup.find('p', class_='locationicon').find('a')['href']
    office_hours = [item.text.strip() for item in soup.find('p', class_='hoursicon').find_all('span')]

    # Create an array to store the area of search for each blurb
    area_of_search = []

    # Iterate through blurb divs and categorize based on headers
    blurb_divs = soup.find_all('div', class_='blurb')
    for blurb in blurb_divs:
        header = blurb.find('h2').text.strip()  # Extract the header text and strip whitespace
        content = blurb.get_text().strip()  # Get the content of the blurb and strip leading/trailing whitespace
        
        # Store the content in the list with the header as the key
        area_of_search.append({header: content})


    # Extract Research Interests
    research_interests = []

    # Iterate through accolades divs and categorize based on headers
    accolades_divs = soup.find_all('div', class_='accolades')
    for accolades in accolades_divs:
        header = accolades.find('h2').text.strip()  # Extract the header text and strip whitespace
        content = accolades.get_text().strip()  # Get the content of the accolades and strip leading/trailing whitespace
        
        # Store the content in the list with the header as the key
        research_interests.append({header: content})

    # Insert the professor's information into the research collection
    if name and title_dept and email and phone and office_location and office_hours and research_interests and area_of_search :
        professor_info = {
            "name": name,
            "url": url,
            "title_dept": title_dept,
            "email": email,
            "phone": phone,
            "office_location": office_location,
            "office_hours": office_hours,
            "research_interests": research_interests,
            "area_of_search": area_of_search,

        }
        research_collection.insert_one(professor_info)
    else:
        print(f"Skipping professor {name} due to missing information.")
    


# Retrieve HTMLs from MongoDB
htmls_of_professor_pages = html_collection.find()

# Iterate through the HTMLs of professor web pages
for html_doc in htmls_of_professor_pages:
    html = html_doc['html']  # Assuming 'html' is the key for HTML content in the MongoDB document
    url  = html_doc['url'] 
    parse_and_persist_professor_info(html,url)

# Print a message when parsing is done
print("Parsing and persisting professor information is done.")

