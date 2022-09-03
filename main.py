import requests
from glob import glob
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import sleep

HEADERS = ({
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
})


def serach_products(interval_count=3, interval_hours=6):
    prod_tracker = pd.read_csv('trackers/TRACKER_PRODUCTS.csv', sep=',')
    prod_tracker_URLS = prod_tracker.url
    tracker_log = pd.DataFrame()
    now = datetime.now().strftime('%Y-%m-%d %Hh%Mm')
    interval = 0

    while interval < interval_count:

        for x, url in enumerate(prod_tracker_URLS):
            page = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(page.content, features="lxml")

            # product title
            title = soup.find(id='productTitle').get_text().strip()
            print(title)

            # Check for the price, and try and except to prevent the script from crashing if product is out of stock.
            try:
                price = float(soup.find(
                    "span", class_="a-offscreen").get_text().replace('$', '').replace(',', '').strip())
            except:
                price = ''
            print(price)

            try:
                review_score = soup.find(
                    "span", class_="a-icon-alt").get_text()
                review_count = int(soup.select('#acrCustomerReviewText')[
                    0].get_text().split(' ')[0].replace(".", ""))
            except:
                # Sometimes review scores are in different positions.
                try:
                    review_score = float(soup.select(
                        'i[class*="a-icon a-icon-star a-star-"]')[1].get_text().split(' ')[0].replace(",", "."))
                    review_count = int(soup.select('#acrCustomerReviewText')[
                                       0].get_text().split(' ')[0].replace(".", ""))
                except:
                    review_score = ''
                    review_count = ''

            print(review_score)
            print(review_count)

            # checking if there is "Out of stock"
            try:
                soup.select(
                    '#availability .a-size-medium a-color-success')[0].get_text().strip()
                stock = 'Out of Stock'
            except:
                # checking if there is "Out of stock" on a second possible position
                try:
                    soup.select(
                        '#availability .a-size-medium a-color-success')[0].get_text().strip()
                    stock = 'Out of Stock'
                except:
                    # if there is any error in the previous try statements, it means the product is available
                    stock = 'Available'
            print(stock)

            log = pd.DataFrame({'date': now.replace('h', ':').replace('m', ''),
                                # this code comes from the TRACKER_PRODUCTS file
                                'code': prod_tracker.code[x],
                                'url': url,
                                'title': title,
                                # this price comes from the TRACKER_PRODUCTS file
                                'buy_below': prod_tracker.buy_below[x],
                                'price': price,
                                'stock': stock,
                                'review_score': review_score,
                                'review_count': review_count}, index=[x])

            tracker_log = tracker_log.append(log)
            print('appended ' + prod_tracker.code[x] + '\n' + title + '\n\n')
            sleep(5)

        interval += 1  # counter update
        sleep(interval_hours*1*1)
        print('end of interval ' + str(interval))
    # path to file in the folder
    last_search = glob('C:/Users/Blue/idk/search_history/*.xlsx')[-1]
    search_hist = pd.read_excel(last_search)
    final_df = search_hist.append(tracker_log, sort=False)

    final_df.to_excel(
        'search_history/SEARCH_HISTORY_{}.xlsx'.format(now), index=False)
    print('end of search')


serach_products()
