#!/usr/bin/env python3
# coding: utf-8
#!/usr/bin/env python -W ignore::DeprecationWarning

# In[33]:


from copy import deepcopy
#from datetime import datetime
from IPython.display import HTML
import json
import pandas as pd
from arcgis.gis import GIS
import arcgis.network as network
import arcgis.geocoding as geocoding
from haversine import haversine

# In[34]:


home = [-123.04555556, 49.26722222]


# In[35]:


def init():
    global gps_points,my_gis,route_service_url,route_service
    gps_points = pd.read_csv('gps_points.csv')
    gps_points[['Date', 'Time']] = gps_points.gmt_timestamp.str.split(' ', expand=True)
    gps_points.drop(['gmt_timestamp'], axis=1)
    #gps_points.add(['Distance'], axis=1)
    
    #user_name = 'arcgis_python'
    #password = 'P@ssword123'
    user_name = 'fr3ncht045t'
    password = 'Sweetstart14'
    my_gis = GIS('https://www.arcgis.com', user_name, password)
    route_service_url = my_gis.properties.helperServices.route.url
    route_service = network.RouteLayer(route_service_url, gis=my_gis)

def remove_points():
    new_results = []
    rows_to_drop = []
    for index,row in gps_points.head(100).iterrows():
        if index == 0:
            result = haversine(home,[gps_points['longitude'][index], gps_points['latitude'][index]])
        elif gps_points['Date'][index] != gps_points['Date'][index-1]:
            result = haversine(home,[gps_points['longitude'][index], gps_points['latitude'][index]])
        elif gps_points['Date'][index] != gps_points['Date'][index+1]:
            result = haversine([gps_points['longitude'][index], gps_points['latitude'][index]],home)
        else:
            result = haversine([gps_points['longitude'][index-1], gps_points['latitude'][index-1]],[gps_points['longitude'][index], gps_points['latitude'][index]])
     
        if result < 2:
            rows_to_drop.append(index)
        else:
            new_results.append(result)
           
    gps_points.drop(rows_to_drop,axis='index',inplace=True)
    gps_points.reset_index(drop=True,inplace=True)

def dist_calc(location1,location2):
    route_layer = network.RouteLayer(route_service_url, gis=my_gis)
    result = route_layer.solve(stops='{},{}; {},{}'.format(location1[0],location1[1],location2[0],location2[1]),
                               return_directions=False, return_routes=True, 
                               output_lines='esriNAOutputLineNone',
                               return_barriers=False, return_polygon_barriers=False,
                               return_polyline_barriers=False)

    #travel_time = result['routes']['features'][0]['attributes']['Total_TravelTime']
    #print("Total travel time is {0:.2f} min".format(travel_time))


    return result['routes']['features'][0]['attributes']['Total_Kilometers']
    #print("Total distance is {0:.2f} km".format(total_distance))


def main():
    init()
    remove_points()
    d=[]
    for index,row in gps_points.head(100).iterrows():
        print("Calculating Point {}\r".format(index),end="")

        if index == 0:
            d.append(dist_calc(home,[gps_points['longitude'][index], gps_points['latitude'][index]]))
        elif gps_points['Date'][index] != gps_points['Date'][index-1]:
            d.append(dist_calc(home,[gps_points['longitude'][index], gps_points['latitude'][index]]))
        elif gps_points['Date'][index] != gps_points['Date'][index+1]:
            d.append(dist_calc([gps_points['longitude'][index], gps_points['latitude'][index]],home))
        else:
            d.append(dist_calc([gps_points['longitude'][index-1], gps_points['latitude'][index-1]],[gps_points['longitude'][index], gps_points['latitude'][index]]))
        #print("Calculating Point {}\b".format(i))
    print(d)

main()



