import json
import random
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from bs4 import BeautifulSoup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=["*"],
    max_age=36000
)

# Define user agents
user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]

@app.post('/search')
async def search_coursera(request: Request):
    body = await request.json()
    url_prompt = body.get('search')
    
    if not url_prompt:
        return {"error": "No search query provided"}
    
    url_prompt = url_prompt.strip().lower().replace(' ', '+')
    url = f'https://www.coursera.org/search?query={url_prompt}&q=search&language=English'
    
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        time.sleep(3)  # Be respectful to the server
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ching = soup.find_all('h3', class_='cds-CommonCard-title css-6ecy9b')
        chong = soup.find_all('p', class_="cds-ProductCard-partnerNames css-vac8rf")
        rating = soup.find_all('p', class_="css-2xargn")
        links = soup.find_all('a', class_='cds-119 cds-113 cds-115 cds-CommonCard-titleLink css-si869u cds-142')
        
        courses_list = []
        for course_title, partner_name, rating_name, link in zip(ching, chong, rating, links):
            courses_list.append({
                'Course Title': course_title.text.strip(),
                'Partner': partner_name.text.strip(),
                'Rating': rating_name.text.strip(),
                'Link': 'https://www.coursera.org' + link.get('href')
            })
        
        return courses_list
    
    except requests.RequestException as e:
        return {"error": f"Failed to fetch data: {str(e)}"}


