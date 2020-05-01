import pandas as pd
import matplotlib.pyplot as plt
import requests
from h3 import h3
import json
from urllib.request import URLError, Request, urlopen
from itertools import combinations
from itertools import permutations
from dateutil import parser
from datetime import datetime, timedelta
import math
import networkx as nx

class Node:
    def __init__(self,idx,data):
        self.id = idx
        self.pickup_location = (data.pickup_latitude,data.pickup_longitude,data.pickup_h3)
        self.dropoff_location = (data.dropoff_latitude,data.dropoff_longitude,data.dropoff_h3)
        self.pickup_time = data.pickup_time
        self.dropoff_time = data.dropoff_time
        self.distance = data.trip_distance
        self.duration = data.duration
        self.delay = data.delay
        self.passenger_count = data.passenger_count


def get_distance_duration(node_a,node_b,trip_type):
    if trip_type==2: 
        e, f, g, h = node_a.pickup_location[0], node_a.pickup_location[1], node_b.pickup_location[0],node_b.pickup_location[1]
    else:
        e, f, g, h = node_a.dropoff_location[0], node_a.dropoff_location[1], node_b.dropoff_location[0],node_b.dropoff_location[1]
    request_str = 'http://localhost:8989/route?point=' + str(e) + '%2C' + str(f) + '&point=' + str(
        g) + '%2C' + str(h) + '&vehicle=car'
    request = Request(request_str)
    res = requests.get(request_str)
    if 'paths' in json.loads(res.text):
        distance = json.loads(res.text)['paths'][0]['distance']
        time = json.loads(res.text)['paths'][0]['time']
        minute, msec = divmod(time, 60000)
        return distance / 1609.344 , minute + (msec / 100000)
    else:
        return float('inf'),float('inf')


def get_all_pairs(node_a,node_b,trip_type):
    if trip_type == 1:
        #Combination LGA--> a -->b
        #if no distance call graphhopper 
        if (node_a.dropoff_location[2],node_b.dropoff_location[2]) not in df_distance.index:
            a_b_distance,a_b_duration = get_distance_duration(node_a,node_b,trip_type)
        else:
            a_b_distance = df_distance.loc[(node_a.dropoff_location[2],node_b.dropoff_location[2])]['distance']
            a_b_duration = df_distance.loc[(node_a.dropoff_location[2],node_b.dropoff_location[2])]['duration']
        
        LGA_a_dist = node_a.distance
        a_b_dist   = a_b_distance
        LGA_a_dur  = node_a.duration
        a_b_dur    = a_b_duration
        
        #Combination LGA--> b -->a
        if (node_b.dropoff_location[2],node_a.dropoff_location[2]) not in df_distance.index:
            b_a_distance,b_a_duration = get_distance_duration(node_a,node_b,trip_type)
        else:
            b_a_distance = df_distance.loc[(node_b.dropoff_location[2],node_a.dropoff_location[2])]['distance']
            b_a_duration = df_distance.loc[(node_b.dropoff_location[2],node_a.dropoff_location[2])]['duration']
            
        LGA_b_dist = node_b.distance
        b_a_dist = b_a_distance
        LGA_b_dur = node_b.duration
        b_a_dur = b_a_duration
        
        path_1_total_dis,path_1_total_dur = LGA_a_dist + a_b_dist,LGA_a_dur + a_b_dur 
        path_1_a_dur,path_1_b_dur = LGA_a_dur,path_1_total_dur
        
        path_2_total_dis,path_2_total_dur = LGA_b_dist+b_a_dist,LGA_b_dur+b_a_dur
        path_2_a_dur,path_2_b_dur         = path_2_total_dur ,LGA_b_dur
               
    else:
        #Combination a--> b --> LGA
        if (node_a.pickup_location[2],node_b.pickup_location[2]) not in df_distance.index:
            a_b_distance,a_b_duration = get_distance_duration(node_a,node_b,trip_type)
        else:
            a_b_distance = df_distance.loc[(node_a.pickup_location[2],node_b.pickup_location[2])]['distance']
            a_b_duration = df_distance.loc[(node_a.pickup_location[2],node_b.pickup_location[2])]['duration']
        
        a_b_dist   = a_b_distance
        b_LGA_dist = node_b.distance 
        a_b_dur    = a_b_duration
        b_LGA_dur  = node_b.duration
        
        #Combination b--> a --> LGA
        if (node_b.pickup_location[2],node_a.pickup_location[2]) not in df_distance.index:
            b_a_distance,b_a_duration = get_distance_duration(node_b,node_a,trip_type)
        else:
            b_a_distance = df_distance.loc[(node_b.pickup_location[2],node_a.pickup_location[2])]['distance']
            b_a_duration = df_distance.loc[(node_b.pickup_location[2],node_a.pickup_location[2])]['duration']
        
        b_a_dist   = b_a_distance
        a_LGA_dist = node_a.distance 
        b_a_dur    = b_a_duration
        a_LGA_dur  = node_a.duration
        
        path_1_total_dis,path_1_total_dur = a_b_dist + b_LGA_dist,a_b_dur + b_LGA_dur 
        path_1_a_dur,path_1_b_dur = path_1_total_dur,b_LGA_dur
        
        path_2_total_dis,path_2_total_dur, = b_a_dist+a_LGA_dist,b_a_dur+a_LGA_dur
        path_2_a_dur,path_2_b_dur         = a_LGA_dur,path_2_total_dur
        
    return ((path_1_total_dis,path_1_total_dur,path_1_a_dur,path_1_b_dur),( path_2_total_dis,path_2_total_dur,path_2_a_dur,path_2_b_dur))


def calculate_edge_weight(node_a,node_b,trip_type):
    path1,path2 = get_all_pairs(node_a,node_b,trip_type)
    minimum_distance = float('inf')
    for path in (path1,path2):
        distance_contraint = (path[0] <= node_a.distance + node_b.distance)
        delay_constraint = (path[2] <= node_a.duration + node_a.delay) & (path[3] <= node_b.duration + node_b.delay)
        #add social constraint too...
        
        
        if distance_contraint and delay_constraint and path[0]< minimum_distance:
            minimum_distance = path[0]
    distance_saved = node_a.distance + node_b.distance - minimum_distance
    return distance_saved


# In[7]:


def get_rsg(G,trip_type):
    for node_a,node_b in list(combinations(G,2)):
        if (node_a.passenger_count+node_b.passenger_count)<=4:
            distance_saved = calculate_edge_weight(node_a,node_b,trip_type)
            if distance_saved!= float('-inf') :
                G.add_edge(node_a,node_b, weight=distance_saved)
    return G


# # Average distance saved per pool as a % of total distance of individual rides

# In[8]:


def Average_distance_saved(merged_trips,Final_Graph):
    with_sharing , without_sharing = [],[]
    for i in range(len(merged_trips)):
        all_nodes =  set()
        total_dis_before_merging = 0
        total_dis_after_merging = 0
        for each_node in Final_Graph[i].nodes:
            total_dis_before_merging += each_node.distance
            all_nodes.add(each_node)
        #remove merged nodes from orginal rga graph
        for u,v in merged_trips[i].edges:
            all_nodes.remove(u)
            all_nodes.remove(v)
            total_dis_after_merging += Final_Graph[i].get_edge_data(u,v)['weight']
        #add unmerged solo trips also
        for solo in all_nodes:
            total_dis_after_merging += solo.distance
        with_sharing.append(total_dis_after_merging)
        without_sharing.append(total_dis_before_merging)
    return sum([(1-x/y) for x, y in zip(with_sharing, without_sharing)]),len(without_sharing)   


# # Average number of trips saved per pool as a % of number of individual trips

def Average_trip_saved(merged_trips,Final_Graph):
    saved_rides = []
    for idx in range(len(merged_trips)):
        num_ind_trips = len(Final_Graph[idx].nodes)
        num_pooled_trips = len(merged_trips[idx].edges)
        saved_rides.append(num_pooled_trips/num_ind_trips)
    return sum(saved_rides),len(saved_rides)



from tqdm import tqdm
df=pd.DataFrame()
df_distance = pd.DataFrame()
import time
def main_algoritm(trip_type,dfs,dfs_distance):
    global df,df_distance
    df = dfs
    df_distance = dfs_distance
    start_execution = time.time()
    Final_Graph = []
    t = 0
    for _,trips in df.groupby(['pool_window']):
        nodes = []
        trips = trips.reset_index()
        for idx, row in trips.iterrows():
            nodes.append(Node(idx,trips.iloc[idx]))
        G = nx.Graph()
        G.add_nodes_from(nodes)
        Final_Graph.append(G)

    #Start of the code
    merged_trips = []
    cn=0
    for individual_graph in tqdm(Final_Graph,total=len(Final_Graph)):
#         s = time.time()
        ride_sharing_graph = get_rsg(individual_graph,trip_type)
        #maximum weighted algorithm
        maximum_weighted_graph = nx.max_weight_matching(ride_sharing_graph, maxcardinality=True)
        g_match = nx.Graph()
        for u,v in maximum_weighted_graph:
            g_match.add_edge(u,v)

        merged_trips.append(g_match)
#         t += time.time()-s
    distance_saved_num,distance_saved_deno = Average_distance_saved(merged_trips,Final_Graph)
    trip_saved_num,trip_saved_deno = Average_trip_saved(merged_trips,Final_Graph)
    del dfs_distance,dfs,df,df_distance
    
    return distance_saved_num,distance_saved_deno,trip_saved_num,trip_saved_deno
   