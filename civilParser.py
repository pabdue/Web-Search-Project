import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["civilCrawler"]
html_collection = db["civilProfs"]
research_collection = db["civilResearch"]

# Function to parse and persist professor's information
def parse_and_persist_professor_info(html):
    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Extract professor information 
    name = soup.find('h1').text.strip()
    title_dept = soup.find('span', class_='title-dept').text.strip()
    email = soup.find('p', class_='emailicon').find('a')['href'].replace('mailto:', '')
    phone = soup.find('p', class_='phoneicon').text.strip()
    office_location = soup.find('p', class_='locationicon').find('a')['href']
    office_hours = [item.text.strip() for item in soup.find('p', class_='hoursicon').find_all('span')]

    # Extract Research Interests
    research_interests = []

    try:
        accolades_divs = soup.find_all('div', class_='accolades')

        # Initialize variables to store the divs containing research interests
        research_interests_tag = None

        # Iterate through the accolades divs
        for div in accolades_divs:
            h2_tag = div.find('h2')
            if h2_tag and ("Research Interests" in h2_tag.text or "Research Interest" in h2_tag.text):
                research_interests_tag = div
                break  # Exit the loop when the correct div is found

        if research_interests_tag:
                    # Check if the structure is a simple list using <ul> and <li> tags
                    ul_tag = research_interests_tag.find_next('ul')
                    if ul_tag:
                        research_interests = [item.text.strip() for item in ul_tag.find_all('li')]
                    else:
                        # Check if the structure is a simple list using <div> and <p> tags
                        p_tags = research_interests_tag.find_all('p')
                        if p_tags:
                                research_interests = [p.text.strip() for p in p_tags if p.text.strip()]
                        
    except Exception as e:
        print(f"Error extracting research interests: {e}")

    # Insert the professor's information into the research collection
    if name and title_dept and email and phone and office_location and office_hours and research_interests:
        professor_info = {
            "name": name,
            "title_dept": title_dept,
            "email": email,
            "phone": phone,
            "office_location": office_location,
            "office_hours": office_hours,
            "research_interests": research_interests
        }
        research_collection.insert_one(professor_info)
    else:
        print(f"Skipping professor {name} due to missing information.")


# Retrieve HTMLs from MongoDB
htmls_of_professor_pages = html_collection.find()

# Iterate through the HTMLs of professor web pages
for html_doc in htmls_of_professor_pages:
    html = html_doc['html']  # Assuming 'html' is the key for HTML content in the MongoDB document
    parse_and_persist_professor_info(html)

# Print a message when parsing is done
print("Parsing and persisting professor information is done.")

