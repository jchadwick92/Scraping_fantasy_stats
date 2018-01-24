import csv
import pandas as pd
import numpy as np
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import sqlite3
from urllib.request import urlopen
import DK_player_ID_dict


def to_float(a):
    # Converts Fraction odds to a decimal
    if a == 'evens':
        a = 2.0
    elif a == 'EVS':
        a = 2.0
    else:
        a = a.split('/')
        a = (float(a[0]) / float(a[1]))
    return a


def get_html(url):
    Client = urlopen(url)
    page_html = Client.read()
    Client.close()
    page_soup = BeautifulSoup(page_html, 'html.parser')
    return page_soup


def clean_sheet_odds():
    # Scrapes Clean sheets and returns a dictionary in the form of {Team: odds}
    team_abbv = {'West Ham ': 'WHU', 'Tottenham ': 'TOT', 'Burnley ': 'BUR', 'Huddersfield ': 'HUD', 'Everton ': 'EVE', 'Bournemouth ': 'BOU', 'Man City ': 'MCI',
                'Crystal Palace ': 'CRY', 'Southampton ': 'SOU', 'Man Utd ': 'MU', 'Stoke ': 'STK', 'Chelsea ': 'CHE', 'Swansea ': 'SWA', 'Watford ': 'WAT',
                'Leicester ': 'LEI', 'Liverpool ': 'LIV', 'Brighton ': 'BHA', 'Newcastle ': 'NEW', 'Arsenal ': 'ARS', 'West Brom ': 'WBA'}

    team_dict = {}
    soup = get_html('http://www.paddypower.com/football/football-matches/premier-league?ev_oc_grp_ids=9551')
    for i in team_abbv.keys():
        team = soup.find(text=i)
        odds = to_float(team.parent.parent.find('span', {'class': 'odds-value'}).text)
        team = team_abbv[team]
        team_dict[team] = odds
    return team_dict


def match_odds():
    # Scrapes the match odds and returns a dictionary in the form of {Team: odds}
    team_abbv = {'West Ham': 'WHU', 'Tottenham': 'TOT', 'Burnley': 'BUR', 'Huddersfield': 'HUD', 'Everton': 'EVE', 'Bournemouth': 'BOU', 'Man City': 'MCI',
                'Crystal Palace': 'CRY', 'Southampton': 'SOU', 'Man Utd': 'MU', 'Stoke': 'STK', 'Chelsea': 'CHE', 'Swansea': 'SWA', 'Watford': 'WAT',
                'Leicester': 'LEI', 'Liverpool': 'LIV', 'Brighton': 'BHA', 'Newcastle': 'NEW', 'Arsenal': 'ARS', 'West Brom': 'WBA'}

    match_dict = {}
    soup = get_html('https://www.oddschecker.com/football/english/premier-league')
    matches = soup.find_all('tr', {'class':'match-on'})

    for match in matches[:10]:
        teams = match.find_all('span', {'class': 'fixtures-bet-name'})
        odds = match.find_all('span', {'class': 'odds'})
        match_dict[team_abbv[teams[0].text.strip()]] = to_float(odds[0].text.strip('( ) '))
        match_dict[team_abbv[teams[2].text.strip()]] = to_float(odds[2].text.strip('( ) '))

    return match_dict


def read_1617_stats():
    stats_1617_A = pd.read_csv('draftkings_1617_21501.csv', encoding='latin-1')
    stats_1617_B = pd.read_csv('draftkings_1617_21502.csv', encoding='latin-1')
    stats_1617 = pd.merge(stats_1617_A, stats_1617_B, on='Name')

    stats_1617['Total'] = ((stats_1617['Goals']*10) + (stats_1617['Assists']*6) + (stats_1617['Shots']*1) + (stats_1617['Shots On Target']*1)
                           + (stats_1617['Crosses']*0.75) + (stats_1617['Fouls Won']*1) + (stats_1617['Tackles Won - Possession']*1) + (stats_1617['Interceptions']*0.5)
                           - (stats_1617['Fouls Conceded']*0.5) - (stats_1617['Premier League Yellow Cards']*1.5) - (stats_1617['Penalties Missed']*5))

    stats_1617['Floor_total'] = ((stats_1617['Shots']*1) + (stats_1617['Shots On Target']*1) + (stats_1617['Crosses']*0.75) + (stats_1617['Fouls Won']*1) +
                           (stats_1617['Tackles Won - Possession']*1) + (stats_1617['Interceptions']*0.5) - (stats_1617['Fouls Conceded']*0.5) -
                           (stats_1617['Premier League Yellow Cards']*1.5) - (stats_1617['Penalties Missed']*5))

    stats_1617['Pts/1617_game'] = np.where(stats_1617['Time Played'] > 100, stats_1617['Total'] / (stats_1617['Starts'] + stats_1617['Subbed On']*0.5), 0)
    stats_1617['Pts/1617_90'] = np.where(stats_1617['Time Played'] > 100, (stats_1617['Total'] / stats_1617['Time Played'])*90, 0)

    stats_1617['Floor_game'] = np.where(stats_1617['Time Played'] > 100, stats_1617['Floor_total'] / (stats_1617['Starts'] + stats_1617['Subbed On']*0.5), 0)
    stats_1617['Floor_90'] = np.where(stats_1617['Time Played'] > 100, (stats_1617['Floor_total'] / stats_1617['Time Played'])*90, 0)
    stats_1617['Floor_1617'] = stats_1617[['Floor_game', 'Floor_90']].mean(axis=1)
    stats_1617.replace(0, np.NaN, inplace=True)

    return stats_1617


def read_1718_stats():
    stats_1718_A = pd.read_csv('draftkings_1718_21501.csv', encoding='latin-1')
    stats_1718_B = pd.read_csv('draftkings_1718_21502.csv', encoding='latin-1')
    stats_1718 = pd.merge(stats_1718_A, stats_1718_B, on='Name')
    stats_1718.loc[stats_1718['Name'] == 'Kane', 'Name'] = 'Kane (Harry)'
    stats_1718.loc[stats_1718['Name'] == 'Jones', 'Name'] = 'Jones (Phil)'
    stats_1718.loc[stats_1718['Name'] == 'Keane', 'Name'] = 'Keane (Michael))'
    stats_1718.loc[stats_1718['Name'] == 'Olsson', 'Name'] = 'Olsson (Martin)'
    stats_1718.loc[stats_1718['Name'] == 'Davis', 'Name'] = 'Davis (Steven)'
    stats_1718.loc[stats_1718['Name'] == 'Dawson', 'Name'] = 'Dawson (Craig)'
    stats_1718.loc[stats_1718['Name'] == 'Fulton', 'Name'] = 'Fulton (Jay)'
    stats_1718.loc[stats_1718['Name'] == 'Maguire', 'Name'] = 'Maguire (Harry)'
    stats_1718.loc[stats_1718['Name'] == 'Austin (Charlie)', 'Name'] = 'Austin'
    stats_1718.loc[stats_1718['Name'] == 'Sterling (Raheem)', 'Name'] = 'Sterling'

    stats_1718['Total'] = ((stats_1718['Goals']*10) + (stats_1718['Assists']*6) + (stats_1718['Shots']*1) + (stats_1718['Shots On Target']*1)
                           + (stats_1718['Crosses']*0.75) + (stats_1718['Fouls Won']*1) + (stats_1718['Tackles Won - Possession']*1) + (stats_1718['Interceptions']*0.5)
                           - (stats_1718['Fouls Conceded']*0.5) - (stats_1718['Premier League Yellow Cards']*1.5) - (stats_1718['Penalties Missed']*5))
    stats_1718['Floor_total'] = ((stats_1718['Shots']*1) + (stats_1718['Shots On Target']*1) + (stats_1718['Crosses']*0.75) + (stats_1718['Fouls Won']*1) +
                                 (stats_1718['Tackles Won - Possession']*1) + (stats_1718['Interceptions']*0.5) - (stats_1718['Fouls Conceded']*0.5) -
                                 (stats_1718['Premier League Yellow Cards']*1.5) - (stats_1718['Penalties Missed']*5))

    stats_1718['Pts/1718_game'] = np.where(stats_1718['Time Played'] > 100, stats_1718['Total'] / (stats_1718['Starts'] + stats_1718['Subbed On']*0.5), 0)
    stats_1718['Pts/1718_90'] = np.where(stats_1718['Time Played'] > 100, (stats_1718['Total'] / stats_1718['Time Played'])*90, 0)

    stats_1718['Floor_game'] = np.where(stats_1718['Time Played'] > 100, stats_1718['Floor_total'] / (stats_1718['Starts'] + stats_1718['Subbed On']*0.5), 0)
    stats_1718['Floor_90'] = np.where(stats_1718['Time Played'] > 100, (stats_1718['Floor_total'] / stats_1718['Time Played'])*90, 0)
    stats_1718['Floor_1718'] = stats_1718[['Floor_game', 'Floor_90']].mean(axis=1)
    stats_1718.replace(0, np.NaN, inplace=True)

    return stats_1718


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
    csvFile = open('draftkings_1718_%s.csv' % csv_id, 'wt', newline='')
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


def read_DKSalaries():
    DK_salaries = pd.read_csv('DKSalaries.csv', encoding='latin-1')
    DK_salaries['Id'] = DK_salaries['Name'].map(DK_player_ID_dict.DK_player_dict)
    #DK_salaries['Id'] = DK_salaries['Id'].astype(int)
    DK_salaries = DK_salaries.rename(columns={'Name':'DK_Name'})

    DK_salaries['Clean sheet'] = DK_salaries['teamAbbrev']
    DK_salaries['Clean sheet'] = DK_salaries['Clean sheet'].map(clean_sheet_odds())
    DK_salaries['Clean sheet'] = round((1.18 ** (-(DK_salaries['Clean sheet'] ** 2))) * 3, 2)

    return DK_salaries


def read_1617_IDs():
    # Read stats from 2016/2017 season and return pandas dataframe
    all_stats_1617 = pd.read_excel('C:\\Users\\samuel-ortega\\Documents\\Joe\\Yahoo_1617.xlsx', sheetname='Sheet1', encoding='latin-1')
    all_stats_1617['Id'].replace('soccer.p.', '', regex=True, inplace=True)
    all_stats_1617 = all_stats_1617[all_stats_1617['Id'].notnull()]
    all_stats_1617['Id'] = all_stats_1617['Id'].astype(float)
    return all_stats_1617[['Name', 'Id']]


def combine_tables():
    df1 = read_DKSalaries()
    df2 = read_1617_stats()[['Name', 'Pts/1617_game', 'Pts/1617_90', 'Floor_1617']]
    df3 = read_1718_stats()[['Name', 'Pts/1718_game', 'Pts/1718_90', 'Floor_1718']]
    df4 = read_1617_IDs()
    df = pd.merge(df2,df3,on='Name', how='outer')
    df = pd.merge(df,df4,on='Name', how='inner')
    df = pd.merge(df1,df,on='Id', how='left')
    
    df.set_index('Id', inplace=True)
    df['Clean sheet'] = np.where(df['Position'] == 'D', df['Clean sheet'], 0)
    df['Projection'] = (df[['Pts/1617_game', 'Pts/1617_90', 'Pts/1718_game', 'Pts/1718_90']].mean(axis=1)) + df['Clean sheet']
    df['Floor'] = df[['Floor_1617', 'Floor_1718']].mean(axis=1)
    df['Pts/1718_90'] = df['Pts/1718_90'] + df['Clean sheet']
    df['Value'] = (df['Pts/1718_90'] / df['Salary']) * 1000 
    
    print(df[['DK_Name', 'Salary', 'Pts/1718_90', 'Projection', 'Floor', 'Value']].sort_values('Value', ascending=False).to_string())


browser = webdriver.Chrome()
login()
html_to_csv(21501)
html_to_csv(21502)
browser.quit()

combine_tables()

