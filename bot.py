import requests
from bs4 import BeautifulSoup
import json
import tweepy
import os
import sys

if not os.path.exists('secrets.json'):
  print("ERROR: You need to create a file called secrets.json containing your Twitter API key information (the file should have four variables; see below)")
  sys.exit()

with open('secrets.json', 'r') as f:
  secrets = json.load(f)

def write_tweet(tweet):
  # Only perform authentication if we need to; sometimes we might run the script 
  # but then nothing new has happened so we just exit out without needing to make
  # API calls
  client = tweepy.Client(
      consumer_key = secrets['consumer_key'],
      consumer_secret = secrets['consumer_secret'],
      access_token = secrets['access_token'],
      access_token_secret = secrets['access_token_secret'],
      bearer_token=secrets['bearer_token']
  )
  client.create_tweet(text=tweet)

existing_bounties = set()
if os.path.exists('existing_bounties.json'):
  # Open up existing_bounties.json file and read the contents
  with open('existing_bounties.json', 'r') as f:
    existing_bounties = json.load(f)

print("Existing bounties: ", existing_bounties)
existing_bounties = set(existing_bounties)

# Function to extract bounties
# Source: ChatGPT
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
        ''' This commented-out code might be useful for debugging
        print("Title:", bounty['title'])
        print("Description:", bounty['description'])
        print("Status:", bounty['status'])
        print("Reward:", bounty['reward'])
        print("URL:", url+bounty['more_url'])
        print("-" * 50)
        '''
        text = f"Attention all aspiring computer hackers: a new {bounty['reward']} listing has been posted on BountyList!\n\n"
        text += f"Title: {bounty['title']}\n"
        text += f"Time Left: {bounty['status']}\n"
        text += f"URL: {url+bounty['more_url']}!"

        #text = text[0:240]  # prevent accidentally exceeding character limit
        if len(text) > 240:
          text = text[0:240]

        print("New bounty detected. Sending out the following tweet:")
        print(text)

        try:
          write_tweet(text)
          pass
        except Exception as e:
          print("Error sending tweet: ", e)

    # Save list of bounty names into a json file
    # Dump JUST the title attributes
    # This prevents the bot from printing out the same bounty multiple times
    with open('existing_bounties.json', 'w') as f:
      for i in bounties:
        existing_bounties.add(i['title'])
      json.dump(list(existing_bounties), f)
else:
    print("No new bounties found.")
