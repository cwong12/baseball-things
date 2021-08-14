#!/usr/bin/python
import pandas as pd
import sys
import os
import math
import numpy as np
import csv
import mysql.connector
import datetime

# teamList = [ "ANA","ARI", "ATL", "BAL", "BOS", "CHA", "CLE", "CHN", "COL","CIN","DET","HOU", "KCA","LAN", "MIA","MIL", "MIN", "NYA", "NYN", "PHI","PIT",  "OAK","SDN", "SEA", "STL", "SFN", "TBA", "TEX", "TOR", "WSN"]
# teamList= []
RECORD_FILE = "mlbAbb.csv"

cnx = mysql.connector.connect(user='admin', password='owyupNubDybPyrund4Swobecfesjos',
                              host='brbuild.co6s1tybawgm.us-east-1.rds.amazonaws.com',
                              database='brbuild')
cursor = cnx.cursor()
def read_abbrev_csv():
    with open(RECORD_FILE, "r", newline="") as input_file:
        reader = csv.reader(input_file)

        teamList = []
        for abb in reader:
            print(abb)
            teamList.append(abb)
    return teamList

def find_oldest_hist():

    teamList = read_abbrev_csv()
    


    print("old")

    
    team = "STL"
    # year = 2021
    print(len(teamList))
    query = ("select *, avg(inn.Age) from (SELECT majors_pitching.player_ID AS player_ID, majors_pitching.year_ID, majors_pitching.team_ID, majors_pitching.stint_ID, birth_year, majors_pitching.year_ID-birth_year as Age, GS FROM majors_pitching INNER JOIN bio     USING (player_ID) INNER JOIN players USING (player_ID) WHERE majors_pitching.year_ID=%s AND majors_pitching.team_ID= %s AND GS > 0 GROUP BY majors_pitching.player_ID ORDER BY Age desc LIMIT 5) as inn")
    team_to_age_dict = {}
    for teamTrip in teamList:
        team = teamTrip[0]
        minYear = int(teamTrip[1])
        maxYear = int(teamTrip[2])
        print(teamTrip)
        for year in range(minYear, maxYear+1):
            cursor.execute(query, (year,team))
            for row in cursor:
                if row[0] == None or row[-1] == None:
                    continue
                avAge = float(row[-1])
                keyVal = row[2] + str(row[1])
                print(keyVal + ": " + str(avAge))
                if (avAge > 36.5):
                    team_to_age_dict[keyVal] = avAge
    
    print(team_to_age_dict)
    sort_teams = sorted(team_to_age_dict.items(), key=lambda x: x[1], reverse=True)
    with open("oldest_teams.csv", "w", newline="") as output_file:
        writer = csv.writer(output_file)
        

        for i in sort_teams:
            print(i[0], i[1])
            writer.writerow((i[0], i[1]))



def find_top_8_pitchers():
    print("top 8")
    
    with open("oldest_teams.csv", "r", newline="") as input_file:
        reader = csv.reader(input_file)
        query = """SELECT majors_pitching.player_ID AS player_ID, majors_pitching.year_ID, majors_pitching.team_ID, birth_year, majors_pitching.year_ID-birth_year as Age, GS
  FROM majors_pitching
       INNER JOIN bio     USING (player_ID)
       INNER JOIN players USING (player_ID)
 WHERE majors_pitching.year_ID=%s AND majors_pitching.team_ID=%s AND GS > 0
 GROUP BY majors_pitching.player_ID ORDER BY Age desc LIMIT 7"""
        with open("oldest_teams_with_pitchers.csv", "w", newline="") as output_file:
            writer = csv.writer(output_file)

            for row in reader:
                
                teamYear = row[0]
                team = teamYear[:-4]
                year = teamYear[-4:]
                cursor.execute(query, (year,team))

                outRow = [year, team]
                for row in cursor:
                    print(row)
                    if row[0] == None or row[-1] == None:
                        continue
                    outRow.append(row[0])
                writer.writerow(outRow)

                print((team,year))



def get_game_dates_for_top_8():
    print("\n\n\n\ndaters============================================")
    with open("oldest_teams_with_pitchers.csv", "r", newline="") as input_file:
        reader = csv.reader(input_file)
        ranker = 1
        for row in reader:

            team = row[1]
            year = row[0]
            pitcher1 = row[2]
            pitcher2 = row[3]
            pitcher3 = row[4]
            pitcher4 = row[5]
            pitcher5 = row[6]
            pitcher6 = row[7]
            pitcher7 = row[8]

            query = """
            SELECT date_game, majors_pitching.player_ID AS player_ID, majors_pitching.year_ID, majors_pitching.team_ID, majors_pitching.stint_ID, birth_year, majors_pitching.year_ID-birth_year as Age, GS, bio.name_common
    FROM majors_pitching
        INNER JOIN bio     USING (player_ID)
        INNER JOIN players USING (player_ID)
        JOIN gamelogs ON 
        (
        (majors_pitching.player_ID = gamelogs.pitcher_home_id OR majors_pitching.player_ID = gamelogs.pitcher_visitor_id)
        AND majors_pitching.year_ID=gamelogs.year_game 
        AND (gamelogs.home_team = majors_pitching.team_ID OR gamelogs.visitor_team = majors_pitching.team_ID )
        )
    WHERE majors_pitching.year_ID=%s AND majors_pitching.team_ID=%s AND GS > 0 
    AND (majors_pitching.player_ID = %s OR majors_pitching.player_ID = %s OR majors_pitching.player_ID = %s 
    OR majors_pitching.player_ID = %s OR majors_pitching.player_ID = %s OR majors_pitching.player_ID = %s)
    ORDER BY date_game asc;
            
            """
            cursor.execute(query, (year, team, pitcher1, pitcher2 ,pitcher3 ,pitcher4, pitcher5, pitcher6))

            df = pd.DataFrame(cursor.fetchall())
            # print(df)

            # print(df[0:5])
            # print(len(df))
            for i in range(len(df)-4):
                curWindow = df[i:i+5]


                earliest_game_date = curWindow[0][i]
                last_game_date = curWindow[0][i+4]

                diff = (last_game_date-earliest_game_date).days
                if diff <= 5:
                    # print("\n\nNEW WINDOW")
                    names = curWindow[1]
                    # print(names)
                    if pitcher1 in names.unique() and pitcher2 in names.unique() and pitcher3 in names.unique() and pitcher4 in names.unique() and (pitcher5 in names.unique() or pitcher6 in names.unique() ):

                        print("\n\n==========MATCH " + str(ranker) + "   ===========")
                        print(curWindow)
                        ranker += 1
                        break
            # prev_game_date = datetime.date(2019, 4, 13)
            # for row in cursor:
            #     print(row)
            #     game_date = row[0]
            #     diff = game_date-prev_game_date
            #     print(diff.days)
            #     prev_game_date = game_date

if __name__ == '__main__':
    # find_oldest_hist()
    # find_top_8_pitchers()
    get_game_dates_for_top_8()

