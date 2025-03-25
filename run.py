import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

USERNAME = os.getenv('USERNAME')
TOKEN = os.getenv('TOKEN')  # Needs `user:follow` scope

if not USERNAME or not TOKEN:
    raise ValueError("USERNAME and TOKEN environment variables are required")

HEADERS = {'Authorization': f'token {TOKEN}'}

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.headers.update(HEADERS)

def check_rate_limit():
    """Check GitHub API rate limit status."""
    response = session.get('https://api.github.com/rate_limit')
    response.raise_for_status()
    limits = response.json()['resources']['core']
    remaining = limits['remaining']
    reset_time = datetime.fromtimestamp(limits['reset'])
    
    if remaining < 10:
        wait_time = (reset_time - datetime.now()).total_seconds()
        if wait_time > 0:
            logger.warning(f"Rate limit low ({remaining} remaining). Waiting {wait_time:.0f} seconds...")
            time.sleep(wait_time)
    
    return remaining

def get_users(url):
    """Get list of GitHub users from paginated API."""
    users = []
    try:
        while url:
            remaining = check_rate_limit()
            logger.info(f"API calls remaining: {remaining}")
            
            response = session.get(url)
            response.raise_for_status()
            users += [user['login'] for user in response.json()]
            
            # Get next page URL from Link header
            url = response.links.get('next', {}).get('url')
        
        return set(users)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching users from {url}: {str(e)}")
        raise

def main():
    try:
        # Step 1: Get followers
        followers = get_users(f'https://api.github.com/users/{USERNAME}/followers')
        logger.info(f"Followers: {len(followers)}")

        # Step 2: Get following
        following = get_users(f'https://api.github.com/users/{USERNAME}/following')
        logger.info(f"Following: {len(following)}")

        # Step 3: Unfollow those who don't follow you back
        to_unfollow = following - followers
        for user in to_unfollow:
            check_rate_limit()
            resp = session.delete(f'https://api.github.com/user/following/{user}')
            resp.raise_for_status()
            logger.info(f"Unfollowed {user}: {resp.status_code}")

        # Step 4: Follow those who follow you but you're not following yet
        to_follow = followers - following
        for user in to_follow:
            check_rate_limit()
            resp = session.put(f'https://api.github.com/user/following/{user}')
            resp.raise_for_status()
            logger.info(f"Followed {user}: {resp.status_code}")

    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
