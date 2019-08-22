"""
This module contains all the code that will gather all the necessary
details that is needed about a facebook user in other to make
our predictions.
"""

# import all necessary libary
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sqlite3
from selenium.common.exceptions import NoSuchElementException
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import csv

class FetchData:

    def __init__(self):
        """
        constructor for the foo class
        """
        #--------- log in details ------------
        # open text file containing login details
        f = open('login_details.txt', 'r')
        login_details = (line for line in f)
        # unpack details
        self.username, self.password = login_details
        # remove end of line character from username
        self.username = self.username[:-1]
        # container to hold list of frnds
        self.frnd_list = list()

        #---------- browser instance ----------------
        # gecko driver path
        gecko = '../../fbCRAWL/code/geckodriver.exe'
        # firefox profile
        ff_prof = webdriver.FirefoxProfile()
        # block images from loading
        ff_prof.set_preference('permissions.default.image', 2)
        # activate incognito mode
        ff_prof.set_preference('browser.privatebrowsing.autostart', True)
        # block all notifications
        ff_prof.set_preference('dom.webnotifications.enabled', False)
        # instantiate the browser
        self.driver = webdriver.Firefox(firefox_profile=ff_prof, executable_path=gecko)


    def go_fb(self):
        # go to facebook
        self.driver.get('http://www.facebook.com/login')
        # check if title contains facebook
        assert ('Facebook') in self.driver.title


    def login(self):
        """log on to facebook"""
        # find the username and password field
        username = self.driver.find_element_by_id('email')
        password = self.driver.find_element_by_id('pass')
        # find the login button
        login_butt = self.driver.find_element_by_css_selector('#loginbutton')
        # wait before filling the form
        time.sleep(8)
        # fill in the username and password
        username.send_keys(self.username)
        time.sleep(9)
        password.send_keys(self.password)
        time.sleep(10)
        # click to login
        login_butt.click()


    def scroll_page(self):
        """scrolls down the page to load fresh content"""
        # Scroll down to bottom
        self.driver.execute_script\
            ("window.scrollTo(0, document.body.scrollHeight);")


    def movie(self):
        """
        find the movie section of the page by id, it scroll
        the page until the film section of the profile page
        is visible; this ensures that the full friend list
        has been loaded
        """
        try:
            self.driver.find_element_by_id\
                ('pagelet_timeline_medley_movies')
            print('movies section now visible')
        except NoSuchElementException:
            # scroll down the page
            self.driver.execute_script\
                ("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(4,6))
            self.movie()


    def get_gender(self):
        """
        return the gender of the user.

        RETURN VALUE:
        1 -- male
        0 -- female
        """
        try:
            # use the places he/she's lived string to get the gender
            self.driver.find_element_by_css_selector\
                ('a[label="Places He\'s Lived"]')
            return(1)
        except NoSuchElementException:
            # try to see if user is a female
            try:
                self.driver.find_element_by_css_selector\
                    ('a[label="Places She\'s Lived"]')
                return(0)
            except NoSuchElementException:
                # return a missing value when sex can't be determined
                return('')


    def get_frnd(self):
        """
        method to get the list of friend
        """
        # locate the logged in user's profile button
        def get_profile():
            """
            locate the logged in user's profile button.
            It performs search recursively till the element
            is found
            """
            try:
                # seaarch for elelment
                profile_but = self.driver.find_element_by_xpath\
                    ('/html/body/div[1]/div[2]/div/div[1]/div/div/div/div[2]/div[1]/div[1]/div/a')
                return(profile_but)
            except NoSuchElementException:
                # wait and re-search recursively
                time.sleep(4)
                get_profile()

        # get the profile button
        profile_but = get_profile()
        # click the button to go to the profile page
        profile_but.click()
        # wait
        time.sleep(5)

        # locate the friend tab element
        friend_tab = self.driver.find_element_by_css_selector\
            ('#fbTimelineHeadline > div:nth-child(2) > ul > li:nth-child(3) > a:nth-child(1)')
        # click the tab
        friend_tab.click()
        time.sleep(random.randint(4,5))
        
        # scroll till movie section is found to ensure all friends
        # has been loaded 
        self.movie()
        # get info from the friend list iteratively
        #  
        # select each friend div using css attribute selector
        frnd_list = self.driver.find_elements_by_css_selector\
            ('div[data-testid="friend_list_item"]')
        # get the link to each user's profile
        self.frnd_list = [(user.find_element_by_css_selector\
            ('a').get_attribute('href')) for user in frnd_list]
        
        # write the links as json
        l = open('fb_users.json', 'w')
        json.dump(self.frnd_list, l)

    def scrape_info(self, user_list):
        """
        gather info about users, takes one argument which must be a list
        containing the link to the users profile
        """
        # info about all user
        data = list()

        for user_link in user_list:
            # visit user's profile with the link
            self.driver.get(user_link)
            # wait
            time.sleep(random.randint(5,7))
            # get the user's name
            name = self.driver.find_element_by_css_selector\
                ('#fb-timeline-cover-name a').text
            # switch to the about tab to get other info
            self.driver.find_element_by_css_selector\
                ('ul[data-referrer="timeline_light_nav_top"] a[data-tab-key="about"]').click()
            # wait
            time.sleep(random.randint(5,7))
            # get the gender
            gender = self.get_gender()
            print(f'{name} - male_status: {gender}')

            # get the gender distribution of user's frnd
            def gender_distr():
                """
                get the total no of friends a user have and
                give the account of the no of male and female
                among these friends.
                """
                # wait
                time.sleep(random.randint(5,7))
                # switch to the friends tab to get other info
                self.driver.find_element_by_css_selector\
                    ('ul[data-referrer="timeline_light_nav_top"] a[data-tab-key="friends"]').click()

                time.sleep(random.randint(4,6))
                #scroll all friends has been loaded
                self.movie()
                
                # select each friend div using css attribute selector
                frnd_list = self.driver.find_elements_by_css_selector\
                    ('div[data-testid="friend_list_item"]')
                # total number pf friends
                total_no_frnds = len(frnd_list)
                no_of_male_frnd = 0
                no_of_female_frnd = 0

                # get the sex of each user
                for user in frnd_list:
                    if self.get_gender() == 1:
                        no_of_male_frnd += 1
                    else:
                        no_of_female_frnd += 1
                return ([total_no_frnds, no_of_male_frnd, no_of_female_frnd])
            # upack the gender distribution details
            total_no_frnds, no_of_male_frnd, no_of_female_frnd = gender_distr()

            # collate the result for each user
            result = [name, gender, total_no_frnds, no_of_male_frnd, no_of_female_frnd]
            # add result to the list of data
            data.append(result)
            print(result)
            time.sleep(random.randint(6,8))
            # write data to csv
            with open('friends_data.csv', 'a') as f:
                writer = csv.writer(f, delimiter=',', lineterminator='\n')
                writer.writerows(data)


    def csv_header(self, header):
        """
        write the header of the csv file to make identification of columns
        easier.

        takes a list of the headers as an argument
        """
        with open('friends_data.csv', 'a') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n')
            # write the headers
            writer.writerow(header)
        f.close()

    def logout(self):
        """sign out of facebook"""
        # click the dropdown menu to reveal the logout button
        dd = self.driver.find_element_by_css_selector('a[id="pageLoginAnchor"]')
        dd.click()
        # wait for the dailog box to show
        time.sleep(5)
        # find the logout button
        css_attr = """data-gt='{"ref":"async_menu","logout_menu_click":"menu_logout"}'"""
        # select the logout
        logout = self.driver.find_element_by_css_selector(f'li[{css_attr}]')
        # click the logout button
        logout.click()
        # rest
        time.sleep(4)
        # close the browser
        self.driver.quit()




if __name__ == "__main__":
    f = FetchData()
    #sleep
    time.sleep(2)
    f.go_fb()
    # sleep for a while
    time.sleep(6)
    f.login()
    # sleep
    #time.sleep(7)
    #f.get_frnd()
    # wait
    time.sleep(10)
    # write the header for the csv file
    f.csv_header(['name', 'gender', 'total_no_frnds', 'no_of_male_frnd', 'no_of_female_frnd'])

    # fetch links from json
    user = open('fb_users.json', 'r')
    links = json.load(user)
    # link of ffirst ten users
    first_ten = links[:6]
    # get users data
    f.scrape_info(first_ten)

    