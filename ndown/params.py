#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 15:03:38 2025

@author: mike
"""
import tomllib
import os
import pathlib

############################################
### Read params file

base_path = pathlib.Path(os.path.realpath(os.path.dirname(__file__)))

with open(base_path.joinpath("parameters.toml"), "rb") as f:
    file = tomllib.load(f)

if 'data_path' in file:
    data_path = pathlib.Path(file['data_path'])
else:
    data_path = pathlib.Path('/data')

##############################################
### Assign executables

if 'wrf_path' in file['executables']:
    wrf_path = pathlib.Path(file['executables']['wrf_path'])
else:
    wrf_path = pathlib.Path('/WRF')

wrf_exe = wrf_path.joinpath('main/wrf.exe')
real_exe = wrf_path.joinpath('main/real.exe')
ndown_exe = wrf_path.joinpath('main/ndown.exe')

if 'wps_path' in file['executables']:
    wps_path = pathlib.Path(file['executables']['wps_path'])
else:
    wps_path = pathlib.Path('/WPS')

geogrid_exe = wps_path.joinpath('geogrid.exe')
metgrid_exe = wps_path.joinpath('metgrid.exe')


###########################################
### WPS

wps_nml_path = data_path.joinpath('namelist.wps')

wps_date_format = '%Y-%m-%d_%H:%M:%S'

geogrid_array_fields = ('parent_id', 'parent_grid_ratio', 'i_parent_start', 'j_parent_start', 'e_we', 'e_sn', 'geog_data_res')

domain_array_fields = ('parent_id', 'parent_grid_ratio', 'i_parent_start', 'j_parent_start', 'e_we', 'e_sn', 'geog_data_res', 'e_vert', 'parent_time_step_ratio')

########################################
### WRF

wrf_nml_path = data_path.joinpath('namelist.input')

history_outname = "wrfout_d<domain>_<date>.nc"
summ_outname = "wrfxtrm_d<domain>_<date>.nc"
zlevel_outname = 'wrfzlevels_d<domain>_<date>.nc'

###########################################
### Others

config_path = data_path.joinpath('rclone.config')



