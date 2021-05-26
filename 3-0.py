#!/usr/bin/env python3
# This program looks at whether MLB players have been historically more successful by swinging or taking when up in the count 3-0 based on wOBA

import sys
import numpy as np
import pyexcel as pe
import cv2
import os
import urllib
import re
import json
from bs4 import BeautifulSoup, Comment
import requests



def build_lists(team, start_year, end_year):
    if team == "ALL":
        teamList = [ "ANA","ARI", "ATL", "BAL", "BOS", "CHA", "CLE", "CHN", "COL","CIN","DET","HOU", "KCA","LAN", "MIA","MIL", "MIN", "NYA", "NYN", "PHI","PIT", "WAS",  "OAK","SDN", "SEA", "SLN", "SFN", "TBA", "TEX", "TOR"]
    else:
        teamList = [team]
    

    yearList = [*range(int(start_year), int(end_year))]

    #months during the season
    monthList = ["04", "05","06","07","08","09"]

    dayList = []

    #format days to match BRef url
    for i in range(31):
        day = str(i+1)
        if len(day) == 1:
            day = "0" + day
        dayList.append(day)


    return teamList, yearList, monthList, dayList
    
def main(team, start_year, end_year):

    teamList, yearList, monthList, dayList = build_lists(team, start_year, end_year)
    
    

    numerator_swing = 0
    denom_swing = 0

    numerator_take= 0
    denom_take = 0

    year_vs_wOBA_swinging = {}
    year_vs_wOBA_taking = {}

    for year in yearList:
        for month in monthList:
            for day in dayList:

                for team in teamList:
                    url = "https://www.baseball-reference.com/boxes/" + team + "/" + team + str(year) + month+day+ "0.shtml"
                    
                    try:
                        req = urllib.request.Request(url)
                        response = urllib.request.urlopen(req)
                        page = response.read()

                        parsed = BeautifulSoup(page, 'html.parser')
                        table = parsed.find_all('div', {'id': 'all_play_by_play'})[0]

                    except urllib.error.URLError:
                        continue
                  
                    # BRef has page setup so that placeholder div has comment which terminates scrape
                    # comment holds page info 
                    for element in table(text=lambda text: isinstance(text, Comment)):
                        comment = element.extract()
                        events = str(comment).split('<tr id')

                       
                        for count, event in enumerate(events):
                            if count == 0:
                                continue
                            

                            pitch_seq = ""

                            try:
                                pitch_seq_ind = event.index('pitch_sequence')+16
                            except ValueError:
                                continue
                            
                            # possible characters in play-by-play
                            valid_chars = ['1', '2', '3', '>', '*','+', '.', 'C', 'S', 'F','B', 'X', 'T', 'K','I','H','L', 'M', 'N', 'O', 'P', 'Q', 'R', 'U', 'V', 'Y']
                            while event[pitch_seq_ind] in valid_chars:
                                pitch_seq += event[pitch_seq_ind]
                                pitch_seq_ind +=1

                            #remove pickoff attempts to start AB
                            pitch_seq = pitch_seq.strip("123")


                            #if first 3 pitches are balls
                            if pitch_seq[0:3] == "BBB":
                                

                                #find result of play
                                result_ind = event.index('play_desc')+12
                                
                                #iterate to start of play description string
                                while event[result_ind] != '>':
                                    result_ind +=1
                                play = ""

                                #stop at either end of description (in the case of "Walk"), or Space
                                while event[result_ind+1] != '<' and event[result_ind+1] != ' ':
                                    play += event[result_ind+1]
                                    result_ind +=1
                                

                                play = play.strip(";:")


                                #outcome values for wOBA formula: https://library.fangraphs.com/offense/woba/
                                play_vals = {"Walk": 0.69, "Hit": 0.722, "Single": 0.888, "Double": 1.271, "Ground-Rule": 1.271, "Triple": 1.616, "Home": 2.101}
                                if play in play_vals:
                                    if pitch_seq[3] == "B" or pitch_seq[3] == "C":
                                        numerator_take += play_vals[play]
                                        
                                    elif pitch_seq[3] == "S" or pitch_seq[3] == "F" or pitch_seq[3] == "X" :
                                        numerator_swing += play_vals[play]

                                #skip events of steals or passed balls
                                if len(pitch_seq) == 3:
                                    continue
                                if pitch_seq[3] == "B" or pitch_seq[3] == "C":
                                    denom_take += 1
                                elif pitch_seq[3] == "S" or pitch_seq[3] == "F" or pitch_seq[3] == "X" :
                                    denom_swing += 1




                print(str(month) + "/" + str(day) + "/" + str(year))           
                if denom_swing > 0:
                    print("wOBA swinging: " + str(numerator_swing/denom_swing) + " over " + str(denom_swing) + " PA's")

                if denom_take > 0:
                    print("wOBA taking: " + str(numerator_take/denom_take) + " over " + str(denom_take) + " PA's")
        year_vs_wOBA_swinging[year] = numerator_swing/denom_swing
        year_vs_wOBA_taking[year] = numerator_take/denom_take
    print(year_vs_wOBA_swinging)
    print(year_vs_wOBA_taking)

                            






if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("wrong number of args, python3 3-0.py <team> <start year> <end year>")
        exit
    team = sys.argv[1]
    start_year = sys.argv[2]
    end_year = sys.argv[3]
    
    main(team, start_year, end_year)
