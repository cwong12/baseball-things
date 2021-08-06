#!/usr/bin/python
import pandas as pd
import sys
import os
import math
import numpy as np
import csv
import mysql.connector

RECORD_FILE = "fouls.csv"


def get_status():
    with open(RECORD_FILE, "r", newline="") as input_file:
        reader = csv.reader(input_file)
        leftABTotal = 0
        rightABTotal = 0
        leftFoulTotal = 0
        rightFoulTotal = 0
        print("")
        print("\n\n========Current Logs=======\nDate   ABs(L)  ABs(R)  Fouls(L)  Fouls(R)")
        for (date, leftABs, rightABs, leftFouls, rightFouls) in reader:
            spaceMaker =  "  "
            print(date, spaceMaker, leftABs, spaceMaker,spaceMaker,rightABs, spaceMaker,spaceMaker,leftFouls, spaceMaker,spaceMaker,spaceMaker,rightFouls)
            leftABTotal += int(leftABs)
            rightABTotal += int(rightABs)
            leftFoulTotal += int(leftFouls)
            rightFoulTotal += int(rightFouls)
    print("\n=========Totals==========")
    print("Number of Left-handed at bats: " + str(leftABTotal))
    print("Number of Right-handed at bats: "+ str(rightABTotal))
    print("Number of Left-handed foul balls: "+ str(leftFoulTotal))
    print("Number of Right-handed foul balls: "+ str(rightFoulTotal))
    print("AB Ratio(Right to Left): " +str(rightABTotal/leftABTotal))
    print("Foul Ratio(Right to Left): " +str(rightFoulTotal/leftFoulTotal) + "\n\n")



def calc_prev_dist(start_year, end_year):
    cnx = mysql.connector.connect(user='admin', password='owyupNubDybPyrund4Swobecfesjos',
                              host='brbuild.co6s1tybawgm.us-east-1.rds.amazonaws.com',
                              database='brbuild')
    cursor = cnx.cursor()

    leftTotal = 0
    rightTotal = 0
    for year in range(start_year,end_year+1):
        query = ("select game_id, result_batter, result_batter_hand from pbp where home_team = 'STL' and year_game = %s")

        cursor.execute(query, (year,))

        leftABs = 0
        rightABs = 0 

        count = 0

        for (game_id, batter, batter_hand) in cursor:
            if count == 0:
                prevBatter = "no one"
            if prevBatter == batter:
                # print("non event==========")
                continue

            if batter_hand == "L":
                leftABs += 1
            else:
                rightABs += 1
            prevBatter = batter
            
            count += 1
        print(str(year) + " left ABS: "+ str(leftABs))
        print(str(year) + " right ABS: "+ str(rightABs))
        leftTotal += leftABs
        rightTotal += rightABs
    print("\n=========Totals==========")
    print("Total Left ABs: " + str(leftTotal))
    print("Total Right ABs: " + str(rightTotal))
    print("Ratio: " +str(rightTotal/leftTotal) + "\n\n")

    cnx.close()


def add_fouls(date, leftFouls, rightFouls):

    # with open(RECORD_FILE, "r", newline="") as input_file:


    dateSplit = date.split("/")
    month, day = dateSplit[0], dateSplit[1]
    print(month)
    cnx = mysql.connector.connect(user='admin', password='owyupNubDybPyrund4Swobecfesjos',
                              host='brbuild.co6s1tybawgm.us-east-1.rds.amazonaws.com',
                              database='brbuild')
    cursor = cnx.cursor()

    date_string = "SLN2021" + month + day + "0"
    print(date_string)
    query = ("select game_id, result_batter, result_batter_hand from pbp where game_id = %s")
    cursor.execute(query, (date_string,))

    print(cursor)
    count = 0
    leftABs = 0
    rightABs = 0 
    for (game_id, batter, batter_hand) in cursor:
        if count == 0:
            prevBatter = "no one"
        if prevBatter == batter:
            print("non event==========")
            continue

        if batter_hand == "L":
            leftABs += 1
        else:
            rightABs += 1
        prevBatter = batter
        
        count += 1
    print(leftABs)
    print(rightABs)
    outrow = (date, leftABs, rightABs, leftFouls, rightFouls)

    with open(RECORD_FILE, "a", newline="") as output_file:
        writer = csv.writer(output_file)

        writer.writerow(outrow)
    cnx.close()

if __name__ == '__main__':
    func = sys.argv[1]
    
    if func == "past":
        start_year = int(sys.argv[2])
        if len(sys.argv) == 4:
            end_year = int(sys.argv[3])
            print("\n===Searching at bats from %s to %s===" %(start_year, end_year))
            calc_prev_dist(start_year, end_year)
        elif len(sys.argv) == 3:
            print("\n===Searching at bats from %s===" %(start_year))

            calc_prev_dist(start_year, start_year)

    elif func == "add":
        date = sys.argv[2]
        leftFouls = sys.argv[3]
        rightFouls = sys.argv[4]
        add_fouls(date, leftFouls, rightFouls)
        
    elif func == "status":
        get_status()
    else:
        print("choose one of 'past' 'add' 'status'")
