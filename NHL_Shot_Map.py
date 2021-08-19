# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 21:50:19 2021

@author: lasin
"""
import streamlit as st
import requests
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
color_map = plt.cm.winter
from matplotlib.patches import RegularPolygon
import math
from PIL import Image

##Parsed through api to retrieve relevent info necessary from endpoints, stored in pickle format
# game_data = []
# year = '2020'
# season_type = '02'
# max_game_ID = 1290
# for i in range (0, max_game_ID):
#     r = requests.get(url='http://statsapi.web.nhl.com/api/v1/game/' + year + season_type + str(i).zfill(4) + '/feed/live')
#     data=r.json()
#     game_data.append(data)

# with open( './'+year+'FullDataset.pkl', 'wb') as f:
#     pickle.dump(game_data, f, pickle.HIGHEST_PROTOCOL)

from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors

#Text and Title
st.title("NHL Player Shot Map")
st.header("Shot map with relative effiencies for each NHL player")
st.subheader("""Data from the 2020-2021 Season""")

#Loading player info for user input
@st.cache
def Player_data(nrows):
    roster_teams=pd.read_csv('C:/Users/lasin/NHLWebApp/nhl-stats.csv', header=[1])
    playerName=roster_teams.iloc[:,0:3]
    return playerName

player_info = Player_data(1000)

#User input
team_input = st.sidebar.selectbox('Select Team: ', player_info['Team'].unique())
team_abb=team_input.title()

filtered_team = player_info[player_info['Team'] == team_input]

player_input = st.sidebar.selectbox('Select Player: ', filtered_team['Player Name'])
full_name=player_input.title()

player_shots = st.sidebar.slider('Select min. number of shots: ', 1,10)

#Figure for plot
fig=plt.figure(figsize = (10,10))
ax = fig.add_subplot(111)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')
fig.patch.set_alpha(0.0)

#clean grid
ax.set_xticklabels(labels = [''], fontsize = 18, alpha = 0.7, minor=False)
ax.set_yticklabels(labels=[''], fontsize = 18, alpha =0.7, minor=False)
ax.set_title(full_name +' Shot Map', fontdict={'family':'Times New Roman', 'style':'normal','weight':'semibold', 'size':24})

#Image from pillow
I = Image.open('C:/Users/lasin/NHLWebApp/Half_rink.png')
ax.imshow(I);width, height = I.size

#Scaling factor and offset to align image and data system
scalingx=width/100-0.7
scalingy=height/100+0.6
x_trans = 33
y_trans = height/2

#scale size of hexbinds with image so a "radius" scaling factor calculated here
S = 3.8*scalingx


#Loading endpoint data from season
@st.cache
def NHL_Data(nrows):
    with open('C:/Users/lasin/2020FullDataset.pkl', 'rb') as f:
        game_data = pickle.load(f)
    return game_data

data_load_state = st.text('Loading data...')
ingame_data = NHL_Data(1000)
data_load_state.text('Data loaded!')

st.text('Data Source: http://statsapi.web.nhl.com/api/v1/game/ID/feed/live')

c = mcolors.ColorConverter().to_rgb
positive_cm = ListedColormap([c('#e1e5e5'), c('#d63b36')])
negative_cm = ListedColormap([c('#e1e5e5'), c('#28aee4')])

#Dictionaries for league data
league_data = {};

league_data['Shot'] = {};
league_data['Shot']['x'] = [];
league_data['Shot']['y'] = [];

league_data['Goal'] = {};
league_data['Goal']['x'] = [];
league_data['Goal']['y'] = [];

#The variables we want to collect
event_types = ['Shot', 'Goal']

#Dictionaries for player data
player_data = {};

player_data['Shot'] = {};
player_data['Shot']['x'] = [];
player_data['Shot']['y'] = [];

player_data['Goal'] = {};
player_data['Goal']['x'] = [];
player_data['Goal']['y'] = [];

#Collecting data for the relevent player
for data in ingame_data:
    if 'liveData' not in data:
        continue
    plays = data['liveData']['plays']['allPlays']
    for play in plays:
        for event in event_types:
            if play ['result']['event'] in [event]:
                   if 'x' in play ['coordinates']:
                       league_data[event]['x'].append(play['coordinates']['x'])
                       league_data[event]['y'].append(play['coordinates']['y'])
    for play in plays:
        if 'players' in play:
            for player in play['players']:
                if player['player']['fullName'] in [full_name] and player['playerType'] in ['Shooter','Scorer']:
                    for event in event_types:
                        if play ['result']['event'] in [event]:
                               if 'x' in play ['coordinates']:
                                   player_data[event]['x'].append(play['coordinates']['x'])
                                   player_data[event]['y'].append(play['coordinates']['y'])

#Assigning them to variables
player_total_shots = len(player_data['Shot']['x']) + len(player_data['Goal']['x'])
player_goal_pct = len(player_data['Goal']['x'])/player_total_shots
league_total_shots = len(league_data['Shot']['x']) + len(league_data['Goal']['x'])
league_goal_pct = len(league_data['Goal']['x'])/league_total_shots
PL_e_spread = player_goal_pct-league_goal_pct


#Figure dimension
xbnds = np.array([-100., 100.0])
ybnds = np.array([-100.,100.0])
extent = [xbnds[0], xbnds[1], ybnds[0], ybnds[1]]

gridsize = 30; mincnt=0

#Concatenate arrays for x and y league data
league_x_all_shots = league_data['Shot']['x'] + league_data['Goal']['x']
league_y_all_shots = league_data['Shot']['y'] + league_data['Goal']['y']

#This is coordinate flipping arrays
league_x_all_shots_normalized = [];
league_y_all_shots_normalized = [];

#List enumerate to use the index for y also
for i, s in enumerate(league_x_all_shots):
    if league_x_all_shots[i] <0:
        league_x_all_shots_normalized.append(-league_x_all_shots[i])
        league_y_all_shots_normalized.append(-league_y_all_shots[i])
    else:
        league_x_all_shots_normalized.append(league_x_all_shots[i])
        league_y_all_shots_normalized.append(league_y_all_shots[i])
        
#Same steps for goals
league_x_goal_normalized = [];
league_y_goal_normalized = [];

for i, s in enumerate(league_data['Goal']['x']):
    if league_data['Goal']['x'][i]<0:
        league_x_goal_normalized.append(-league_data['Goal']['x'][i])
        league_y_goal_normalized.append(-league_data['Goal']['y'][i])
    else:
        league_x_goal_normalized.append(league_data['Goal']['x'][i])
        league_y_goal_normalized.append(league_data['Goal']['y'][i])
        
#Hexbin function to bucket shot data into histogram
league_hex_data = plt.hexbin(league_x_all_shots_normalized, league_y_all_shots_normalized, 
                             gridsize=gridsize, extent = extent, mincnt = mincnt, alpha = 0.0)

#Extract bin coordinates and counts
league_verts = league_hex_data.get_offsets()
league_shot_frequency = league_hex_data.get_array()

#Goal data too
league_goal_hex_data = plt.hexbin(league_x_goal_normalized, league_y_goal_normalized, 
                                  gridsize=gridsize, extent=extent, mincnt=mincnt, alpha=0.0)

#The grid above is the same so we can share bin coordinate set from above
league_goal_frequency = league_goal_hex_data.get_array()

    


##Plotting all league shots+goals
# for i, v in enumerate(league_verts):
#     if league_shot_frequency[i] < 1:
#         continue
#     scaled_league_shot_frequency = league_shot_frequency[i]/max(league_shot_frequency)
#     radius = S*math.sqrt(scaled_league_shot_frequency)
    
#     hex = RegularPolygon((x_trans+v[0]*scalingx, y_trans-v[1]*scalingy), numVertices=6, radius=radius, orientation=np.radians(0), alpha=0.5, edgecolor=None)
#     ax.add_patch(hex)

#Everything the same for players, just replaced league_variables with player_variables
player_x_all_shots = player_data['Shot']['x'] + player_data['Goal']['x']
player_y_all_shots = player_data['Shot']['y'] + player_data['Goal']['y']

player_x_all_shots_normalized = []
player_y_all_shots_normalized = []

for i, s in enumerate(player_x_all_shots):
    if player_x_all_shots[i] <0:
        player_x_all_shots_normalized.append(-player_x_all_shots[i])
        player_y_all_shots_normalized.append(-player_y_all_shots[i])
    else:
        player_x_all_shots_normalized.append(player_x_all_shots[i])
        player_y_all_shots_normalized.append(player_y_all_shots[i])
        
player_x_goal_normalized = [];
player_y_goal_normalized = [];

for i, s in enumerate(player_data['Goal']['x']):
    if player_data['Goal']['x'][i]<0:
        player_x_goal_normalized.append(-player_data['Goal']['x'][i])
        player_y_goal_normalized.append(-player_data['Goal']['y'][i])
    else:
        player_x_goal_normalized.append(player_data['Goal']['x'][i])
        player_y_goal_normalized.append(player_data['Goal']['y'][i])
        

player_hex_data = plt.hexbin(player_x_all_shots_normalized, player_y_all_shots_normalized, 
                             gridsize=gridsize, extent = extent, mincnt = mincnt, alpha = 0.0)
player_verts = player_hex_data.get_offsets()
player_shot_frequency = player_hex_data.get_array()
player_goal_hex_data = plt.hexbin(player_x_goal_normalized, player_y_goal_normalized,
                                  gridsize=gridsize, extent=extent, mincnt=mincnt, alpha=0.0)
player_goal_frequency = player_goal_hex_data.get_array()

##Plotting all player shots+goals
# for i, v in enumerate(player_verts):
#     if player_shot_frequency[i] < 1:
#         continue
#     scaled_player_shot_frequency = player_shot_frequency[i]/max(player_shot_frequency)
#     radius = S*math.sqrt(scaled_player_shot_frequency)
    
#     hex = RegularPolygon((x_trans+v[0]*scalingx, y_trans-v[1]*scalingy), numVertices=6, radius=radius, orientation=np.radians(0), alpha=0.5, edgecolor=None)
#     ax.add_patch(hex)

#Effiency arrays
league_effiency=[]
player_effiency=[]
relative_effiency=[]

#Looping over length of league shots/same as player and looking for shot locations with >2shots during season
for i in range(0,len(league_shot_frequency)):
    if league_shot_frequency[i]<2 or player_shot_frequency[i]<2:
        continue

#Add them to the array
league_effiency.append(league_goal_frequency[i]/league_shot_frequency[i])
player_effiency.append(player_goal_frequency[i]/player_shot_frequency[i])
relative_effiency.append((player_goal_frequency[i]/player_shot_frequency[i])-(league_goal_frequency[i]/league_shot_frequency[i]))

#Max measurements if needed
max_league_effiency = max(league_effiency)
max_player_effiency = max(player_effiency)
max_relative_effiency = max(relative_effiency)
min_relative_effiency = min(relative_effiency)


for i,v in enumerate(player_verts):
    #Player took at least # shots from location
    if player_shot_frequency[i]< player_shots:
        continue
    scaled_player_shot_frequency = player_shot_frequency[i]/max(player_shot_frequency)
    radius = S*math.sqrt(scaled_player_shot_frequency)
    
    #Finds player and relative effiency at this point [i] on the ice
    player_effiency = player_goal_frequency[i]/player_shot_frequency[i]
    league_effiency = league_goal_frequency[i]/league_shot_frequency[i]
    relative_effiency = player_effiency - league_effiency
    
    #Colours for effiencies
    if relative_effiency >0:
        colour = positive_cm(math.pow(relative_effiency, 0.1))
    else:
        colour = negative_cm(math.pow(-relative_effiency,0.1))
    
    #Plot
    hex = RegularPolygon((x_trans+v[0]*scalingx, y_trans-v[1]*scalingy),numVertices=6, radius=radius, orientation=np.radians(0),facecolor=colour, alpha=1, edgecolor=None)
    ax.add_patch(hex)

plt.grid(False)
st.pyplot(fig)