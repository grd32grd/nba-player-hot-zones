#Imports
import tkinter as tk
from tkinter import ttk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from matplotlib.patches import Circle, Rectangle, Arc, Polygon

from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playercareerstats


#Dataframe sizing.
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


#Function that fetches the list of all active NBA players' names.
def get_player_names():
    active_players = [player for player in players.get_players() if player['is_active']]
    return [player['full_name'] for player in active_players]

#Function that takes in basic player info, calculates individual and league average stats, and returns a player's hot and cold zones.
def player_shotzonedetail(player_name, season_id, season_type):

    #States basic info about player (name, id, retired or active)
    player_dict = [player for player in players.get_players() if player['full_name'] == player_name][0]

    #Dataframe that illustrates player's career stats.
    career = playercareerstats.PlayerCareerStats(player_id=player_dict['id'])
    career_dataframe = career.get_data_frames()[0]

    team_id = career_dataframe[career_dataframe['SEASON_ID'] == season_id]['TEAM_ID']

    shot_chart_list = shotchartdetail.ShotChartDetail(team_id = int(team_id), player_id = int(player_dict['id']), season_type_all_star = season_type, season_nullable = season_id, context_measure_simple = "FGA").get_data_frames()

    #Dataframe of a a player's every shot attempt in a season.                                      
    player_stats = np.array(shot_chart_list[0])

    #Dataframe of the league average percentage per shot zone.
    league_stats = np.array(shot_chart_list[1])

    #Array of dictionaries representing the the 14 shot zones recognized by nba.com/stats [ID, side of court, distance from hoop]
    shot_zones_dict = [
        {'id': 1, 'side': '(C)', 'distance': '24+'},
        {'id': 2, 'side': '(LC)', 'distance': '24+'},
        {'id': 3, 'side': '(RC)', 'distance': '24+'},
        {'id': 9, 'side': '(L)', 'distance': '24+'},
        {'id': 10, 'side': '(C)', 'distance': '8-16'},
        {'id': 11, 'side': '(C)', 'distance': '16-24'},
        {'id': 12, 'side': '(LC)', 'distance': '16-24'},
        {'id': 13, 'side': '(L)', 'distance': '16-24'},
        {'id': 14, 'side': '(L)', 'distance': '8-16'},
        {'id': 15, 'side': '(RC)', 'distance': '16-24'},
        {'id': 16, 'side': '(R)', 'distance': '16-24'},
        {'id': 17, 'side': '(R)', 'distance': '8-16'},
        {'id': 18, 'side': '(C)', 'distance': 'Less'},
        {'id': 19, 'side': '(R)', 'distance': '24+'}
    ]

    #Empty dictionary that'll store info on if each zone is a hot or cold one for the player.
    zone_colors = []
    #Empty dictionary that'll store the difference between the player and the league average efficiency for each zone.
    zone_difference = []

    #Goes through every shot attempt, find if it's a make or a miss, and determines which shot zone it falls under.
    for shot_zone in shot_zones_dict:
        made = 0
        miss = 0
        for shot in range(len(player_stats)):
            if (player_stats[shot][20] == 1) and (shot_zone['side'] in player_stats[shot][14]) and (shot_zone['distance'] in player_stats[shot][15]):
                made += 1
            elif (player_stats[shot][20] == 0) and (shot_zone['side'] in player_stats[shot][14]) and (shot_zone['distance'] in player_stats[shot][15]):
                miss += 1
            
       #Scenario in which player has attempt zero shots from a specific zone.    
        try:
            avg = ( made / (made + miss) )
        except ZeroDivisionError: 
            avg = 0
        
       #Compares player efficiency with league average efficiency and determines whether each zone is a hot or cold one for the player and by how much.
        if avg > (league_stats[shot_zone['id']][6]):
            zone_colors.append("red")
            difference = (avg - league_stats[shot_zone['id']][6]) * 10
            if difference > 1:
                difference = 1
            elif difference < 0.1:
                difference = 0.1
            zone_difference.append(difference)
        
        elif avg < (league_stats[shot_zone['id']][6]):
            zone_colors.append("blue")
            difference = (league_stats[shot_zone['id']][6] - avg) * 10
            if difference > 1:
                difference = 1
            elif difference < 0.1:
                difference = 0.1
            zone_difference.append(difference)
        
        else:
            zone_colors.append("gray")
            zone_difference.append(1)
    
    #Returns a player's hot & cold zones.
    return zone_colors, zone_difference

#Function that draws court and plots a player's hot and cold zones.
def draw_court(graphic, color, lw, outer_lines, zone_colors, zone_diff, xlim=(-250, 250), ylim=(422.5, -47.5),flip_court=False):
    if graphic is None:
        graphic = plt.gca()
    
    #Sets up the limits for the matplotlib graphic.
    if not flip_court:
        graphic.set_xlim(xlim)
        graphic.set_ylim(ylim)
    else:
        graphic.set_xlim(xlim[::-1])
        graphic.set_ylim(ylim[::-1])

    #Sets up the labels for the matplotlib graphic.
    graphic.tick_params(labelbottom="off", labelleft="off")

    #Court Elements
    hoop = Circle((0,0), radius=7.5, linewidth=lw, color=color, fill=False)
    backboard = Rectangle((-30, -12.5), 60, 0, linewidth=lw, color=color)
    paint_outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
    paint_inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
    top_ft = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
    bottom_ft = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
    corner_three_left = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
    corner_three_right = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
    mid_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
    mid_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)

    #Zone Elements
    one =  Polygon      ([[80,225],[-80,225],[-122.5,422.5],[122.5,422.5]],
                        fill=True, color=zone_colors[0],alpha=zone_diff[0])
    two = Polygon       ([[-250,92.5],[-250,422.5],[-122.5,422.5],[-80,225],[-220,92.5]], 
                        fill=True, color=zone_colors[1],alpha=zone_diff[1])
    three = Polygon     ([[250,92.5],[250,422.5],[122.5,422.5],[80,225],[220,92.5]], 
                        fill=True, color=zone_colors[2],alpha=zone_diff[2])
    nine = Polygon      ([[-250,-47.5],[-250,92.5],[-220,92.5],[-220,-47.5]], 
                        fill=True, color=zone_colors[3],alpha=zone_diff[3])
    ten = Polygon       ([[-82.5,145],[82.5,145],[45,70],[-45,70]], 
                        fill=True, color=zone_colors[4],alpha=zone_diff[4])
    eleven = Polygon    ([[-85,225],[85,225],[80,145],[-80,145]], 
                        fill=True, color=zone_colors[5],alpha=zone_diff[5])
    twelve = Polygon    ([[-85,225],[-210,100],[-150,58],[-80,145]], 
                        fill=True, color=zone_colors[6],alpha=zone_diff[6])
    thirteen = Polygon  ([[-220,-47.5],[-150,-47.5],[-150,60],[-210,100],[-220,92.5]], 
                        fill=True, color=zone_colors[7],alpha=zone_diff[7]) 
    fourteen = Polygon  ([[-150,60],[-82.5,145],[-45,70],[-80,20],[-80,-47.5],[-150,-47.5]], 
                        fill=True, color=zone_colors[8],alpha=zone_diff[8])
    fifteen = Polygon   ([[85,225],[210,100],[150,58],[80,145]],
                        fill=True, color=zone_colors[9],alpha=zone_diff[9])
    sixteen = Polygon   ([[220,-47.5],[150,-47.5],[150,60],[210,100],[220,92.5]], 
                        fill=True, color=zone_colors[10],alpha=zone_diff[10])
    seventeen = Polygon ([[150,60],[82.5,145],[45,70],[80,20],[80,-47.5],[150,-47.5]], 
                        fill=True, color=zone_colors[11],alpha=zone_diff[11])
    eighteen = Circle   ((0, 0), 80, color=zone_colors[12], alpha=zone_diff[12])
    nineteen = Polygon  ([[250,-47.5],[250,92.5],[220,92.5],[220,-47.5]], 
                        fill=True, color=zone_colors[13],alpha=zone_diff[13])

    #All elements to be plotted on the graphic.
    final_court = [ one, two, three, nine, ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, seventeen, eighteen, nineteen,
                    hoop, backboard, paint_outer_box, paint_inner_box, top_ft, bottom_ft, restricted, corner_three_left, corner_three_right, three_arc, mid_outer_arc, mid_inner_arc]

    if outer_lines:
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
        final_court.append(outer_lines)

    #Plots elements on the graphic.
    for element in final_court:
        graphic.add_patch(element)
    
    return graphic

#Function that takes in user input and generates the corresponding graphic.
def generate_graphic():
    player_name = player_name_combobox.get()
    season_id = season_id_entry.get()
    season_type = season_type_combobox.get()

    #Obtains our statistical data.
    zone_colors, zone_difference = player_shotzonedetail(player_name, season_id, season_type)

    #Draws our court.
    draw_court(None, 'black', 2, False, zone_colors, zone_difference)
    plt.title(f"{player_name} Hot Zones {season_id} {season_type}")
    plt.show()


#Main window
root = tk.Tk()
root.title("Player Hot Zones")

#Player info inputs
player_name_label = ttk.Label(root, text="Select Player:")
player_name_label.grid(row=0, column=0, padx=5, pady=5)
player_name_combobox = ttk.Combobox(root, values=get_player_names())
player_name_combobox.grid(row=0, column=1, padx=5, pady=5)
player_name_combobox.current(0)

season_id_label = ttk.Label(root, text="Season ID:")
season_id_label.grid(row=1, column=0, padx=5, pady=5)
season_id_entry = ttk.Entry(root)
season_id_entry.grid(row=1, column=1, padx=5, pady=5)

season_type_label = ttk.Label(root, text="Season Type:")
season_type_label.grid(row=2, column=0, padx=5, pady=5)
season_type_combobox = ttk.Combobox(root, values=["Regular Season", "Playoffs"])
season_type_combobox.grid(row=2, column=1, padx=5, pady=5)
season_type_combobox.current(0)

generate_button = ttk.Button(root, text="Generate Plot", command=generate_graphic)
generate_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

#Running the GUI
root.mainloop()