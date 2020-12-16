from tkinter import simpledialog as tk_input
from tkinter import messagebox, Frame, Label, Entry, StringVar
import tkinter as tk
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from matplotlib import pyplot as plt
import pandas as pd
import numpy

import time
import sys
import ssl
import os
import csv
import re

class MainDialog(tk_input.Dialog):
    # organize the layout of the input box
    def body(self, master):
        self.winfo_toplevel().title("Sports Analytics (NFL) v1.0")

        Label(master, text="Input Below the NFL Year, Week, & Season\nType For Stat Lookup",
            font=('Roboto', 12, 'bold')).grid(row=0, column=0, columnspan=2, rowspan=2)
        Label(master, text="", font=('Roboto', 12)).grid(row=1)
        Label(master, text="Year  - - - - - - -> ", font=('Roboto', 10)).grid(row=2)
        Label(master, text="Week  - - - - - - ->", font=('Roboto', 10)).grid(row=3)
        Label(master, text="Season Type - > ", font=('Roboto', 10)).grid(row=4)
        Label(master, text="PreSeason: \"1\" | RegSeason: \"2\"", font=('Roboto', 8)).grid(row=5, column=1)

        self.e1 = Entry(master, textvariable=StringVar())
        self.e2 = Entry(master, textvariable=StringVar())
        self.e3 = Entry(master, textvariable=StringVar())

        self.e1.grid(row=2, column=1, sticky='we')
        self.e2.grid(row=3, column=1, sticky='we')
        self.e3.grid(row=4, column=1, sticky='we')
        return self.e1 # initial focus

    # this executes upon hitting 'Okay'
    def validate(self):
        year = str(self.e1.get())
        week = str(self.e2.get())
        seasonType = str(self.e3.get())
        self.result = year, week, seasonType
        if year == '' or week == '' or seasonType == '' or (seasonType != '1' and seasonType != '2'):
            return 0
        else:
            return 1

# Remove html tags from a string
def remove_html_tags(text):

    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# centers a tkinter window
def center(master):

    master.withdraw()
    master.update_idletasks()
    width = master.winfo_width()
    frm_width = master.winfo_rootx() - master.winfo_x()
    win_width = width + 3 * frm_width
    height = master.winfo_height()
    titlebar_height = master.winfo_rooty() - master.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = master.winfo_screenwidth() // 2 - win_width // 2
    y = master.winfo_screenheight() // 2 - win_height // 2
    master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    master.resizable(False, False)
    master.deiconify()

def main():

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    year = ''
    week = ''
    seasonType = ''

    # popup tkinter input box
    ROOT = tk.Tk()
    center(ROOT)
    ROOT.update()
    ROOT.withdraw()
    d = MainDialog(ROOT)

    # get user input
    try:
        year = d.result[0].replace(' ', '')
        week = d.result[1].replace(' ', '')
        seasonType = d.result[2].replace(' ', '')
    except TypeError:
        pass

    # end program upon hitting 'Cancel'
    if year == '' or week == '' or seasonType == '':
        ROOT.destroy()
        raise SystemExit

    # prep pages for scraping
    main_url = f"https://www.espn.com/nfl/scoreboard/_/year/{year}/seasontype/{seasonType}/week/{week}"
    options = webdriver.chrome.options.Options()
    options.headless = False # invisible chrome window
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    drv = webdriver.Chrome(executable_path='./chromedriver', options=options)
    drv.get(main_url)
    time.sleep(1)
    
    # check if games exist
    try:
        nogames = drv.find_element_by_class_name("nogames")
        if nogames.is_displayed():
            messagebox.showerror("Error", "No Games Found!\nCheck your input and try again.")
            drv.quit()
            main()
    except NoSuchElementException:
        pass

    box_score_urls = list()
    for el in drv.find_elements_by_xpath("//a[@name ='&lpos=nfl:scoreboard:boxscore']"):
        box_score_urls.append(el.get_attribute('href'))

    # put data variables here
    away_long = list()
    away_short = list()
    away_passing_yds = list()
    away_rushing_yds = list()
    away_receiving_yds = list()
    away_total_yds = list()
    away_score = list()

    home_long = list()
    home_short = list()
    home_passing_yds = list()
    home_rushing_yds = list()
    home_receiving_yds = list()
    home_total_yds = list()
    home_score = list()

    print()

    for game in box_score_urls:
        drv.get(game)
        time.sleep(1)
        away_long.append(str(drv.find_element_by_xpath("//*[@id=\"gamepackage-passing\"]/div/div[1]/div/div/div/div").text).replace(" Passing", ""))
        away_short.append(drv.find_elements_by_class_name("short-name")[0].text)
        away_passing_yds.append(drv.find_element_by_xpath("//*[@id=\"gamepackage-passing\"]/div/div[1]/div/div/table/tbody/tr[2]/td[3]").text)
        away_rushing_yds.append(drv.find_element_by_css_selector("#gamepackage-rushing > div > div.col.column-one.gamepackage-away-wrap > div > div > table > tbody > tr.highlight > td.yds").text)
        away_receiving_yds.append(drv.find_element_by_css_selector("#gamepackage-receiving > div > div.col.column-one.gamepackage-away-wrap > div > div > table > tbody > tr.highlight > td.yds").text)
        away_total_yds.append(int(away_passing_yds[box_score_urls.index(game)]) + int(away_rushing_yds[box_score_urls.index(game)]) + int(away_receiving_yds[box_score_urls.index(game)]))
        away_score.append(drv.find_element_by_xpath("//div[@class = 'score icon-font-after']").text)

        home_long.append(str(drv.find_element_by_xpath("//*[@id=\"gamepackage-passing\"]/div/div[2]/div/div/div/div").text).replace(" Passing", ""))
        home_short.append(drv.find_elements_by_class_name("short-name")[1].text)
        home_passing_yds.append(drv.find_element_by_css_selector("#gamepackage-passing > div > div.col.column-two.gamepackage-home-wrap > div > div > table > tbody > tr.highlight > td.yds").text)
        home_rushing_yds.append(drv.find_element_by_css_selector("#gamepackage-rushing > div > div.col.column-two.gamepackage-home-wrap > div > div > table > tbody > tr.highlight > td.yds").text)
        home_receiving_yds.append(drv.find_element_by_css_selector("#gamepackage-receiving > div > div.col.column-two.gamepackage-home-wrap > div > div > table > tbody > tr.highlight > td.yds").text)
        home_total_yds.append(int(home_passing_yds[box_score_urls.index(game)]) + int(home_rushing_yds[box_score_urls.index(game)]) + int(home_receiving_yds[box_score_urls.index(game)]))
        home_score.append(drv.find_element_by_xpath("//div[@class = 'score icon-font-before']").text)
        print(f"[ Successfully Scraped ({home_score[box_score_urls.index(game)]}-{away_score[box_score_urls.index(game)]} Home: {home_long[box_score_urls.index(game)]} {home_short[box_score_urls.index(game)]}, Away: {away_long[box_score_urls.index(game)]} {away_short[box_score_urls.index(game)]}) ]")

    drv.quit()

    # write the data variables to CSV file
    file = open(
            'sports_stats.csv',
            'a',
            newline='',
            encoding='utf-8'
        )

    writer = csv.writer(file)

    for game in range(len(box_score_urls)):    
        writer.writerow(
            [
                year,
                seasonType,
                week,
                home_short[game],
                away_short[game],
                home_score[game],
                away_score[game],
                home_passing_yds[game],
                away_passing_yds[game],
                home_rushing_yds[game],
                away_rushing_yds[game],
                home_receiving_yds[game],
                away_receiving_yds[game],
                home_total_yds[game],
                away_total_yds[game],
            ]
        )

    file.close()

    # check for duplicate entries in CSV file and delete them using pandas
    df = pd.read_csv('sports_stats.csv').drop_duplicates(
        subset=
            [
                'Year',
                'PreSeason(1) | RegSeason(2)',
                'Week',
                'Home',
                'Away'
            ],
        keep='last'
    )
    df.to_csv('sports_stats.csv', index=False)

    # plotting stuff

    # restart program
    main()
    
file = open(
    'sports_stats.csv',
    'a',
    newline='',
    encoding='utf-8'
)
writer = csv.writer(file)

# creates the csv file if it doesn't exist
if os.path.getsize('sports_stats.csv') == 0:    
    writer.writerow(
        [
            'Year',
            'PreSeason(1) | RegSeason(2)',
            'Week',
            'Home',
            'Away',
            'Score (Home)',
            'Score (Away)',
            'Passing YDS (Home)',
            'Passing YDS (Away)',
            'Rushing YDS (Home)',
            'Rushing YDS (Away)',
            'Receiving YDS (Home)',
            'Receiving YDS (Away)',
            'Total YDS (Home)',
            'Total YDS (Away)',
        ]
    )
    
file.close()
main()