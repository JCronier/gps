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
from gps import gps
import logging

logging.basicConfig(filename='gps_log.txt',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.CRITICAL)

def main():
    logging.info('Start of Program')
    gp = gps.gps()
    gp.remove_points(gp.gps_points)

    for index,row in tqdm(gp.gps_points.iterrows(),desc='Calculating Distances',total=len(gp.gps_points.index)):
        try:
            if index == 0:
                gp.gps_points.at[index, "Distance Travelled"] = gp.dist_calc(gp.home,[gp.gps_points['longitude'][index], gp.gps_points['latitude'][index]])
            elif (gp.gps_points['Date'][index] != gp.gps_points['Date'][index-1]) or (index == len(gp.gps_points.index)):
                gp.gps_points.at[index, "Distance Travelled"] = gp.dist_calc(gp.home,[gp.gps_points['longitude'][index], gp.gps_points['latitude'][index]])
            elif gp.gps_points['Date'][index] != gp.gps_points['Date'][index+1]:
                gp.gps_points.at[index, "Distance Travelled"] = gp.dist_calc([gp.gps_points['longitude'][index], gp.gps_points['latitude'][index]],gp.home)
            else:
                gp.gps_points.at[index, "Distance Travelled"] = gp.dist_calc([gp.gps_points['longitude'][index-1], gp.gps_points['latitude'][index-1]],[gp.gps_points['longitude'][index], gp.gps_points['latitude'][index]])

            assert gp.gps_points[index]["Distance Travelled"] != -1
        except AssertionError:
            logging.error("Could not calculate point in row: {}".format(row))
        except Exception as e:
            logging.error(e)

    gp.print_to_file(gp.gps_points.round({'Distance Travelled':2}))

    logging.info('Program termination successful')

main()



