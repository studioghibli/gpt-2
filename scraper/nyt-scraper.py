# web scraper that exports data on news articles about COVID-19, Black Lives Matter, and the U.S. election

from bs4 import BeautifulSoup
import csv
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import sys
import time


def wait_for(condition_function):
  start_time = time.time()
  while time.time() < start_time + 10:
    if condition_function():
      return True
    else:
      time.sleep(0.1)
  raise Exception('timeout waiting for {}'.format(condition_function.__name__))


class wait_for_page_load(object):
    '''
    waits for change to happen before proceeding to next action
    '''
    def __init__(self, browser):
        self.browser = browser


    def __enter__(self):
        self.old_links = self.browser.find_elements_by_css_selector('li[data-testid=search-bodega-result]')


    def page_has_loaded(self):
        '''
        returns True when:
            (1) there is no "Show More" button
            (2) after the "Show More" button has been clicked
        returns False otherwise
        '''
        if self.browser.find_elements_by_css_selector('button[data-testid=search-show-more-button]') == []:
            return True
        new_links = self.browser.find_elements_by_css_selector('li[data-testid=search-bodega-result]')
        return new_links != self.old_links


    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


def add_data(data, search_url):
    driver = webdriver.Chrome()
    driver.get(search_url)

    # ensures all links are visible on page
    while_bool = True
    while while_bool:
        with wait_for_page_load(driver):
            try:
                driver.find_element_by_css_selector('button[data-testid=search-show-more-button]').click()
            except (NoSuchElementException, StaleElementReferenceException):
                while_bool = False

    # find all links for articles
    search_results = driver.find_element_by_css_selector('ol[data-testid=search-results]')
    articles = search_results.find_elements_by_css_selector('li[data-testid=search-bodega-result]')
    article_links = []
    for article in articles:
        link = article.find_element_by_tag_name('a')
        article_links.append(link.get_attribute('href'))

    driver.close()

    for article_url in article_links:
        article_page = requests.get(article_url)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')

        try:
            # retrieve article body text
            results = article_soup.find('section', {'name':'articleBody'})
            article_elems = results.find_all('p')
            article_text = ''
            for article_elem in article_elems:
                article_text += '\n\n' + article_elem.text
            article_text = article_text[2:]

            # retrieve article title
            article_title = article_soup.find('h1', {'data-test-id':'headline'}).text

            # add information to data
            data.append([article_title, article_text])

        except AttributeError:
            # skip if unable to retrieve necessary information from article
            print("unable to retrieve article information: " + article_url)


def format_model_training(data_lst, data_type):
    acc = ''
    for i in range(len(data_lst)):
        acc += data_lst[i][data_type]
        if i < len(data_lst) - 1:
            acc += '\n\n<|endoftext|>\n\n'
    return acc


fields = ['name', 'text']
covid_data = []
covid_start_date = '20200322'
covid_end_date = '20200404'

print('extracting articles on COVID-19')
covid_url = 'https://www.nytimes.com/search?dropmab=false&endDate=' + covid_end_date + \
    '&query=COVID-19&sections=U.S.%7Cnyt%3A%2F%2Fsection%2Fa34d3d6c-c77f-5931-b951-241b4e28681c&sort=best&startDate=' + covid_start_date + \
    '&types=article'
add_data(covid_data, covid_url)

blm_data = []
blm_start_date = '20200531'
blm_end_date = '20200627'

print('extracting articles on Black Lives Matter')
blm_url = 'https://www.nytimes.com/search?dropmab=false&endDate=' + blm_end_date + \
    '&query=black%20lives%20matter&sections=U.S.%7Cnyt%3A%2F%2Fsection%2Fa34d3d6c-c77f-5931-b951-241b4e28681c&sort=best&startDate=' + blm_start_date + \
    '&types=article'
add_data(blm_data, blm_url)

election_data = []
election_start_date = '20201101'
election_end_date = '20201114'

print('extracting articles on election')
election_url = 'https://www.nytimes.com/search?dropmab=false&endDate=' + election_end_date + \
    '&query=2020%20Election&sections=U.S.%7Cnyt%3A%2F%2Fsection%2Fa34d3d6c-c77f-5931-b951-241b4e28681c&sort=best&startDate=' + election_start_date + \
    '&types=article'
add_data(election_data, election_url)

# export COVID-19 data
print('exporting COVID-19 data to csv')
with open('nyt-covid.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(fields)
    write.writerows(covid_data)

print('exporting COVID-19 headlines to txt')
with open('covid-headlines.txt', 'w') as f:
    f.write(format_model_training(covid_data, 0))

print('exporting COVID-19 articles to txt')
with open('covid-articles.txt', 'w') as f:
    f.write(format_model_training(covid_data, 1))

# export Black Lives Matter data
print('exporting Black Lives Matter data to csv')
with open('nyt-blm.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(fields)
    write.writerows(blm_data)

print('exporting Black Lives Matter headlines to txt')
with open('blm-headlines.txt', 'w') as f:
    f.write(format_model_training(blm_data, 0))

print('exporting Black Lives Matter articles to txt')
with open('blm-articles.txt', 'w') as f:
    f.write(format_model_training(blm_data, 1))

# export election data
print('exporting election data to csv')
with open('nyt-election.csv', 'w') as f:
    write = csv.writer(f)
    write.writerow(fields)
    write.writerows(election_data)

print('exporting election headlines to txt')
with open('election-headlines.txt', 'w') as f:
    f.write(format_model_training(election_data, 0))

print('exporting election articles to txt')
with open('election-articles.txt', 'w') as f:
    f.write(format_model_training(election_data, 1))