from bs4 import BeautifulSoup
import csv
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

baseURL = 'https://www.tripadvisor.co.uk'
PATHtoDRIVER = '/home/john/Documents/TripadvisorWebScraper/chromedriver_linux64'

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def readCSV():
    with open(os.path.join(__location__, 'input.csv'), newline='') as csvfile:
        allPlaces = list(csv.reader(csvfile))
        return allPlaces

def walker():
    values = readCSV()
    browser = webdriver.Chrome(os.path.join(__location__, 'chromedriver_linux64/chromedriver'))
    browser.implicitly_wait(30)
    
    #road to first page
    for x in values:
        browser.get('https://www.tripadvisor.co.uk/')
        mainPage, spaPage, theaterPage, nightlifePage = 'none'
        try:
            searchBar = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Where to?']")))
            searchBar.send_keys(x)
            searchBar.send_keys(Keys.ENTER)
            time.sleep(5)
            searchResult = browser.find_elements_by_xpath('//*[@id="BODY_BLOCK_JQUERY_REFLOW"]/div[2]/div/div[2]/div/div/div/div/div[1]/div/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div/div/div/div')[0]
            searchResult.click()
            browser.switch_to.window(browser.window_handles[1])
            thingsToDo = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"[title^='Things to Do']")))
            thingsToDo.click()
            time.sleep(5)
            attractions = browser.find_element_by_xpath('//*[@id="lithium-root"]/main/div[4]/div/div[1]/a[5]')
            attractions.click()
            time.sleep(5)
            mainPage = (browser.current_url)

            #road to second page
            searchBar = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH,'//*[@id="component_6"]/div/div[2]/header/div/nav/div[1]/div/div/form/input[1]')))
            searchBar.send_keys('Spas & Wellness Centres ',x)
            searchBar.send_keys(Keys.ENTER)
            time.sleep(5)
            spaPage = (browser.current_url)

            #road to third page
            button = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH,'//*[@id="component_9"]/div/div/div/div/ul/li[6]/div/div/a')))
            button.click()
            time.sleep(5)
            theaterPage = (browser.current_url)

            #road to fourth page
            searchBar = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH,'//*[@id="component_6"]/div/div[2]/header/div/nav/div[1]/div/div/form/input[1]')))
            searchBar.send_keys(x,' nightlife')
            searchBar.send_keys(Keys.ENTER)
            time.sleep(5)
            nightlifePage = (browser.current_url)
        except:
            pass
        
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        getInfo(x, mainPage, spaPage, theaterPage, nightlifePage)

def getInfo(place, mainPage, spaPage, theaterPage, nightlifePage):
    things = ['Sights and landmarks', 'Museums', 'Nature & parks', 'Casinos & gambling', 'Spas and Wellness', 'Theatres', 'Concerts', 'Nightlife']
    numberOfThings = ['N/A']*8

    try:
        #first page
        source = requests.get(mainPage).text
        soup = BeautifulSoup(source,'lxml')
            
        for numbers in soup.find_all('div', class_='aHmccbzd'):
            if numbers.span.span.text == 'Sights & Landmarks':
                result = numbers.span
                numberOfThings[0] = result.find_next_sibling('span').text
            if numbers.span.span.text == 'Museums':
                result = numbers.span
                numberOfThings[1] = result.find_next_sibling('span').text
            if numbers.span.span.text == 'Nature & Parks':
                result = numbers.span
                numberOfThings[2] = result.find_next_sibling('span').text
            if numbers.span.span.text == 'Casinos & Gambling':
                result = numbers.span
                numberOfThings[3] = result.find_next_sibling('span').text
        
        #spa and welness
        source = requests.get(spaPage).text
        soup = BeautifulSoup(source,'lxml')
            
        for numbers in soup.find_all('span', class_='_3g57cNXm')[:1]:
            numberOfThings[4] = numbers.text
        
        #theatres
        sources = requests.get(theaterPage).text
        soup = BeautifulSoup(sources,'lxml')
        
        for numbers in soup.find_all('div', class_='aHmccbzd'):
            if numbers.span.span.text == 'Theatres':
                result = numbers.span
                numberOfThings[5] = result.find_next_sibling('span').text
            if numbers.span.span.text == 'Concerts':
                result = numbers.span
                numberOfThings[6] = result.find_next_sibling('span').text
        
        #nightlife
        source = requests.get(nightlifePage).text
        soup = BeautifulSoup(source,'lxml')
            
        for numbers in soup.find_all('span', class_='_3g57cNXm')[:1]:
            numberOfThings[7] = numbers.text
    except:
        pass

    print(place)
    print(things)
    print(numberOfThings)
    
    printCSV(place,things,numberOfThings)

def printCSV(place,things,numberOfThings):
    fileOpened = open(os.path.join(__location__, "output.csv"), "a")
    outfile = csv.writer(fileOpened)
    outfile.writerow(place)
    outfile.writerow(things)
    outfile.writerow(numberOfThings)
    fileOpened.close()

if __name__ == '__main__':
    walker()


