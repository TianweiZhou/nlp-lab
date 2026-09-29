# nlp-lab

Natural Language Processing (MMAI 5400) coursework.

## Assignment 1 – Web Scraping

`review_scraper.py` scrapes Costco reviews from
[SmartCustomer](https://www.smartcustomer.com/reviews/costco.com)
(formerly Sitejabber) with `requests` and `BeautifulSoup`, and saves them to
`costco_reviews.csv` with the columns `companyName`, `datePublished`,
`ratingValue` and `reviewBody`.

```bash
pip install requests beautifulsoup4
python review_scraper.py
```
