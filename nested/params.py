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


##############################################
### Assign executables

if 'wrf_path' in file['executables']:
    wrf_path = pathlib.Path(file['executables']['wrf_path'])
else:
    wrf_path = pathlib.Path('/WRF')

wrf_exe = wrf_path.joinpath('main/wrf.exe')

real_exe = wrf_path.joinpath('main/real.exe')

if 'wps_path' in file['executables']:
    wps_path = pathlib.Path(file['executables']['wps_path'])
else:
    wps_path = pathlib.Path('/WPS')

geogrid_exe = wps_path.joinpath('geogrid.exe')

metgrid_exe = wps_path.joinpath('metgrid.exe')


###########################################
### Others

if 'data_path' in file:
    data_path = pathlib.Path(file['data_path'])
else:
    data_path = pathlib.Path('/data')

wps_nml_path = data_path.joinpath('namelist.wps')
wrf_nml_path = data_path.joinpath('namelist.input')

config_path = data_path.joinpath('rclone.config')

wps_date_format = '%Y-%m-%d_%H:%M:%S'















