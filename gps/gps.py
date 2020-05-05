#!/usr/bin/env python3
# coding: utf-8

from copy import deepcopy
from IPython.display import HTML
import json
import pandas as pd
from arcgis.gis import GIS
import arcgis.network as network
import arcgis.geocoding as geocoding
from haversine import haversine
from tqdm import tqdm
from time import sleep
import sys
import logging

logging.basicConfig(filename='gps_log.txt',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

class gps:
    username = 'fr3ncht045t'
    password = 'Sweetstart14'
    home = [-123.04555556, 49.26722222]

    def __init__(self):
        try:
            file = input("File to be processed: ")
            self.gps_points = pd.read_csv(file)
        except:
            sys.exit("Could not open file")

        self.gps_points[['Date', 'Time']] = self.gps_points.gmt_timestamp.str.split(' ', expand=True)
        self.gps_points.drop(['gmt_timestamp','Time'], axis=1)
        self.gps_points["Distance Travelled"] = ""

        try:
            self.my_gis = GIS('https://www.arcgis.com', self.username, self.password)
            self.route_service_url = self.my_gis.properties.helperServices.route.url
            self.route_service = network.RouteLayer(self.route_service_url, gis=self.my_gis)
        except:
            sys.exit("Error accessing ARC-GIS network")

    def dist_calc(self,location1,location2):
        try:
            route_layer = network.RouteLayer(self.route_service_url, gis=self.my_gis)
            result = route_layer.solve(stops='{},{}; {},{}'.format(location1[0],location1[1],location2[0],location2[1]),
                                    return_directions=False, return_routes=True, 
                                    output_lines='esriNAOutputLineNone',
                                    return_barriers=False, return_polygon_barriers=False,
                                    return_polyline_barriers=False)

            return result['routes']['features'][0]['attributes']['Total_Kilometers']
        except:
            return -1

    def remove_points(self,data):
        rows_to_drop = []

        for index,row in tqdm(data.iterrows(),desc="Removing Invalid Points",total=len(self.gps_points.index)):
            #sleep(0.01)
            try:
                if index == 0:
                    result = haversine(self.home,[data['longitude'][index], data['latitude'][index]])
                elif (data['Date'][index] != data['Date'][index-1]) or (index == len(data.index)):
                    result = haversine(self.home,[data['longitude'][index], data['latitude'][index]])
                elif data['Date'][index] != data['Date'][index+1]:
                    result = haversine([data['longitude'][index], data['latitude'][index]],self.home)
                else:
                    result = haversine([data['longitude'][index-1], data['latitude'][index-1]],[data['longitude'][index], data['latitude'][index]])
     
                if result < 2:
                    rows_to_drop.append(index)
            except:
                logging.error("Could not remove point in row: {}".format(row))
                pass
            
        data.drop(rows_to_drop,axis='index',inplace=True)
        data.reset_index(drop=True,inplace=True)
        logging.info('Successful data removal')

    def print_to_file(self,data):
        try:
            new_file = input("Name of new file: ")
            data.to_csv(new_file)
        except:
            logging.critical('File write failure')
            sys.exit('File write failure')

        logging.info('File write success')


