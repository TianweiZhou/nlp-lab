"""MMAI 5400 Assignment 1 - Web Scraping.

Scrape Costco reviews from SmartCustomer (formerly Sitejabber) and save
them to a CSV file with the columns companyName, datePublished,
ratingValue and reviewBody.

Usage:
    python review_scraper.py
    %run review_scraper.py
"""

import csv
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.smartcustomer.com'
START_URL = BASE_URL + '/reviews/costco.com'
COMPANY_NAME = 'Costco'
OUTPUT_FILE = 'costco_reviews.csv'
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
}
DELAY_SECONDS = 1
MAX_RETRIES = 3
DATE_PATTERN = re.compile(r'^[A-Z][a-z]+ \d{1,2}, \d{4}$')


def get_soup(url):
    """Download a page and return it parsed with BeautifulSoup."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as error:
            print(f'Attempt {attempt} failed for {url}: {error}')
            time.sleep(DELAY_SECONDS * attempt)
    raise RuntimeError(f'Could not download {url}')


def get_total_reviews(soup):
    """Extract the total number of reviews shown on the company page."""
    for item in soup.find_all(name='span', attrs={'class': 'underline'}):
        text = item.get_text(strip=True).replace(',', '')
        text = text.replace('Reviews', '').replace('reviews', '').strip()
        if text.isdigit():
            return int(text)
    return None


def to_iso_date(date_text):
    """Convert a date such as 'February 8, 2025' to '2025-02-08'."""
    return datetime.strptime(date_text, '%B %d, %Y').date().isoformat()


def parse_review(review):
    """Return (datePublished, ratingValue, reviewBody) for one review."""
    rating_tag = review.find(name='div', attrs={'data-rating': True})
    body_tag = review.find(name='p', attrs={'class': 'break-words'})
    date_tag = review.find(
        name='div',
        string=lambda text: text and DATE_PATTERN.match(text.strip()),
    )
    if rating_tag is None or body_tag is None or date_tag is None:
        return None

    date_published = to_iso_date(date_tag.get_text(strip=True))
    rating_value = int(float(rating_tag['data-rating']))
    review_body = ' '.join(body_tag.get_text(separator=' ').split())
    return date_published, rating_value, review_body


def get_next_page(soup):
    """Return the absolute URL of the next review page, or None."""
    next_button = soup.find(
        name='a', attrs={'aria-label': 'Go to next page'}
    )
    if next_button is None or not next_button.get('href'):
        return None
    return BASE_URL + next_button['href']


def scrape_reviews():
    """Scrape every review page and return a list of CSV rows."""
    rows = []
    page = START_URL
    soup = get_soup(page)

    total = get_total_reviews(soup)
    print(f'Total number of reviews for {COMPANY_NAME}: {total}')

    page_number = 1
    while page:
        if page_number > 1:
            time.sleep(DELAY_SECONDS)
            soup = get_soup(page)

        reviews = soup.find_all(
            name='div', attrs={'class': 'review-item'}
        )
        for review in reviews:
            parsed = parse_review(review)
            if parsed is not None:
                rows.append([COMPANY_NAME, *parsed])

        print(f'Page {page_number}: {len(reviews)} reviews '
              f'(collected {len(rows)} so far)')

        next_page = get_next_page(soup)
        if next_page == page:
            break
        page = next_page
        page_number += 1

    return rows


def save_to_csv(rows, file_name):
    """Write the scraped reviews to a CSV file."""
    with open(file_name, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ['companyName', 'datePublished', 'ratingValue', 'reviewBody']
        )
        writer.writerows(rows)


def main():
    """Scrape the reviews and save them to the working directory."""
    rows = scrape_reviews()
    save_to_csv(rows, OUTPUT_FILE)
    print(f'Saved {len(rows)} reviews to {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
