import requests
from bs4 import BeautifulSoup
from tweepy_test import send_tweet
import json
import sys

# Open up bounties.json file and read the contents
with open('bounties.json', 'r') as f:
  existing_bounties = json.load(f)

print("Existing bounties: ", existing_bounties)
existing_bounties = set(existing_bounties)

# Function to extract bounties
def extract_bounties(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all elements containing bounty information
        bounty_elements = soup.find_all(class_='rounded-lg border border-gray-200 bg-white p-3')
        
        # List to store extracted bounties
        bounties = []
        
        # Extract information for each bounty
        for bounty in bounty_elements:
            title = bounty.find(class_='text-base font-semibold text-gray-800').get_text()
            if (title in existing_bounties):
                print("Bounty already exists: ", title)
                continue

            description = bounty.find(class_='flex flex-col md:flex-row md:items-center md:justify-between').find_all('div')[1].get_text()
            status = bounty.find(class_='whitespace-nowrap text-sm text-gray-500 md:block').get_text()
            reward = bounty.find_all(class_='whitespace-nowrap text-sm text-gray-500 md:block')[1].get_text()
            
            # Find the "More" button and get its URL
            more_button = bounty.find('a', class_='whitespace-nowrap rounded bg-blue-500 px-2 py-1 text-sm font-semibold text-white hover:bg-blue-600')
            if more_button:
                more_url = more_button['href']
            else:
                more_url = None
           
            # Append the extracted bounty to the list
            bounties.append({
                'title': title,
                'description': description,
                'status': status,
                'reward': reward,
                'more_url': more_url
            })
        
        return bounties
    else:
        print("Failed to retrieve the webpage.")
        return None

# URL of the website containing bounties
url = "https://bountylist.org/"  # Replace 'URL_OF_THE_WEBSITE' with the actual URL

# Extract bounties from the URL
bounties = extract_bounties(url)

# Print the extracted bounties
if bounties:
    for bounty in bounties:
        print("Title:", bounty['title'])
        print("Description:", bounty['description'])
        print("Status:", bounty['status'])
        print("Reward:", bounty['reward'])
        print("URL:", url+bounty['more_url'])
        print("-" * 50)

    # Save list of bounty names into a json file
    # Dump JUST the title attributes
    with open('bounties.json', 'w') as f:
      for i in bounties:
        existing_bounties.add(i['title'])
      json.dump(list(existing_bounties), f)
else:
    print("No new bounties found.")
