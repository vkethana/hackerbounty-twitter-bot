import requests
from bs4 import BeautifulSoup
import json
import tweepy
import os
import sys

# Function to extract bounties
# Source: ChatGPT
# TODO: Make the function less dependent on the exact CSS structure of the
# website
def extract_bounties(url, existing_bounties):
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

def update_bot(request):
  # Load OS environment variables
  secrets = {}
  # Check if environmennt variable CONSUMER_KEY exists
  try:
    secrets['consumer_key'] = os.environ['consumer_key']
    secrets['consumer_secret'] = os.environ['consumer_secret']
    secrets['access_token'] = os.environ['access_token']
    secrets['access_token_secret'] = os.environ['access_token_secret']
    secrets['bearer_token']=os.environ['bearer_token']
  except Exception as E:
    print("Error loading environment variables: ", E)
    print("Please make sure you have set your consumer_key, consumer_secret, access_token, access_token_secret, and bearer_token environment variables.")
    sys.exit()

  client = tweepy.Client(
      consumer_key = secrets['consumer_key'],
      consumer_secret = secrets['consumer_secret'],
      access_token = secrets['access_token'],
      access_token_secret = secrets['access_token_secret'],
      bearer_token=secrets['bearer_token']
  )
  existing_bounties = set()
  if os.path.exists('existing_bounties.json'):
    # Open up existing_bounties.json file and read the contents
    with open('existing_bounties.json', 'r') as f:
      existing_bounties = json.load(f)

  print("Existing bounties: ", existing_bounties)
  existing_bounties = set(existing_bounties)

# URL of the website containing bounties
  url = "https://bountylist.org"  # Replace 'URL_OF_THE_WEBSITE' with the actual URL

# Extract bounties from the URL
  bounties = extract_bounties(url, existing_bounties)

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

          tweet_text = f"Attention all aspiring computer hackers: a new {bounty['reward']} listing has been posted on BountyList!\n\n"
          tweet_text += f"Title: {bounty['title']}\n"
          tweet_text += f"URL: {url+bounty['more_url']}\n"
          tweet_text += f"Time Left: {bounty['status']}"
          # Important formatting quirk: you need an exclamation point because otherwise the link will not appear in the tweet, 
          # because twitter will try to "merge" it into the link preview that appears below the Tweet

          if len(tweet_text) > 240:
            tweet_text = tweet_text[0:240]

          print("New bounty detected. Sending out the following tweet:")
          print(tweet_text)

          try:
            client.create_tweet(text=tweet_text)
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

if __name__ == "__main__":
  update_bot(None) # The "request" parameter is not important
