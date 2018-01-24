from selenium import webdriver
import time
from bs4 import BeautifulSoup
import csv


def login():
    # Login to Fantasy football scout
    browser.get('http://members.fantasyfootballscout.co.uk')
    browser.find_element_by_xpath('//*[@id="cookie-bar"]/div/span/a[2]').click()
    username = browser.find_element_by_id('username')
    password = browser.find_element_by_id('password')
    username.send_keys('#')
    password.send_keys('#')
    browser.find_element_by_xpath('//input[@type="hidden"]').submit()
    time.sleep(1)


def get_table(table_id):
    browser.get('http://members.fantasyfootballscout.co.uk/my-stats-tables/view/%s/' % table_id)
    time.sleep(1)


def html_to_csv(csv_id):
    # Convert the html table to a CSV table
    get_table(csv_id)
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find_all("table", {"id": "DataTables_Table_0"})[0]
    rows = table.find_all('tr')
    csvFile = open('draftkings_1617_%s.csv' % csv_id, 'wt', newline='')
    writer = csv.writer(csvFile)
    try:
        for row in rows:
            csvRow = []
            cells = row.find_all(['td', 'th'])
            for cell in cells[1:]:
                csvRow.append(cell.get_text())
            writer.writerow(csvRow)
    finally:
        csvFile.close()


browser = webdriver.Chrome()
login()
html_to_csv(21501)
html_to_csv(21502)
browser.quit()
