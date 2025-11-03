#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 17:21:47 2025

@author: mike
"""
import pathlib
import f90nml
from datetime import datetime, timedelta

import params


################################################
### function



def check_set_params():

    ##############################################
    ### Assign and check executables

    if not params.wrf_path.exists():
        raise ValueError(f'wrf path does not exist: {params.wrf_path}')

    if not params.wrf_exe.exists():
        raise ValueError(f'wrf.exe does not exist: {params.wrf_exe}')

    if not params.real_exe.exists():
        raise ValueError(f'real.exe does not exist: {params.real_exe}')

    if not params.wps_path.exists():
        raise ValueError(f'wps path does not exist: {params.wps_path}')

    if not params.geogrid_exe.exists():
        raise ValueError(f'geogrid.exe does not exist: {params.geogrid_exe}')

    if not params.metgrid_exe.exists():
        raise ValueError(f'metgrid.exe does not exist: {params.metgrid_exe}')


    ##############################################
    ### Namelist checks

    wps_nml = f90nml.read(params.wps_nml_path)
    wrf_nml = f90nml.read(params.wrf_nml_path)

    n_domains = wps_nml['share']['max_dom']


    #########################################
    ### Assign values in namelists

    data_path = params.data_path
    # if not data_path.exists():
    #     raise ValueError(f'data_path does not exist: {data_path}')

    # geog_data_path = pathlib.Path(params.file['input_data']['geog_data_path'])
    # if not geog_data_path.exists():
    #     raise ValueError(f'geog_data_path does not exist: {geog_data_path}')

    ## Paths
    wps_nml['share']['opt_output_from_geogrid_path'] = str(data_path)
    wps_nml['metgrid']['opt_output_from_metgrid_path'] = str(data_path)
    # wps_nml['geogrid']['geog_data_path'] = str(geog_data_path)
    wps_nml['geogrid']['opt_geogrid_tbl_path'] = str(params.geogrid_exe.parent.joinpath('geogrid'))
    wps_nml['metgrid']['opt_metgrid_tbl_path'] = str(params.metgrid_exe.parent.joinpath('metgrid'))

    ## Time control
    start_date = datetime.fromisoformat(params.file['time_control']['start_date'])
    end_date = datetime.fromisoformat(params.file['time_control']['end_date'])

    if start_date > end_date:
        raise ValueError(f'start_date ({start_date}) is greater than end_date ({end_date}).')

    # date_diff = end_date - start_date

    history_begin = wrf_nml['time_control']['history_begin'][0]

    # if date_diff.total_seconds()/60 < history_begin:
    #     raise ValueError('The date difference must be greater than the history_begin value.')

    start_date = start_date - timedelta(minutes=history_begin)

    wps_nml['share']['start_date'] = [start_date.strftime(params.wps_date_format)] * n_domains
    wps_nml['share']['end_date'] = [end_date.strftime(params.wps_date_format)] * n_domains

    wrf_nml['time_control']['start_year'] = [start_date.year] * n_domains
    wrf_nml['time_control']['start_month'] = [start_date.month] * n_domains
    wrf_nml['time_control']['start_day'] = [start_date.day] * n_domains
    wrf_nml['time_control']['start_hour'] = [start_date.hour] * n_domains
    wrf_nml['time_control']['end_year'] = [end_date.year] * n_domains
    wrf_nml['time_control']['end_month'] = [end_date.month] * n_domains
    wrf_nml['time_control']['end_day'] = [end_date.day] * n_domains
    wrf_nml['time_control']['end_hour'] = [end_date.hour] * n_domains

    outputs = ['wrfout']
    if wrf_nml['time_control']['output_diagnostics'] == 1:
        outputs.append('summ')
    if wrf_nml['diags']['z_lev_diags'] == 1:
        outputs.append('zlevel')

    #############################################
    ### Write namelists

    with open(params.wps_nml_path, 'w') as nml_file:
       wps_nml.write(nml_file)

    with open(params.wrf_nml_path, 'w') as nml_file:
       wrf_nml.write(nml_file)

    return start_date, end_date, int(wrf_nml['time_control']['interval_seconds']/(60*60)), outputs




















































