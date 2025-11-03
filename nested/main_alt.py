#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 15:09:38 2025

@author: mike
"""
import uuid

from download_nml_domain import dl_nml_domain
from set_params import check_set_params
from download_era5 import dl_era5
from run_era5_to_int import run_era5_to_int
from run_metgrid import run_metgrid
from run_real import run_real
from monitor_wrf import monitor_wrf

import params

import sentry_sdk

run_uuid = uuid.uuid4().hex[-13:]

########################################
## Sentry
# sentry = params.file['sentry']

# if sentry['dsn'] != '':
#     sentry_sdk.init(
#         dsn=sentry['dsn'],
#         # Add data like request headers and IP for users,
#         # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
#         send_default_pii=True,
#     )

# if sentry['tags']:
#     sentry_sdk.set_tags(sentry['tags'])


########################################
### Run sequence

print('-- Downloading namelists...')
dl_check = dl_nml_domain()

start_date, end_date, hour_interval, outputs = check_set_params()

print(f'start date: {start_date}, end date: {end_date}, input hour interval: {hour_interval}')

print('-- Downloading ERA5 data...')
era5_check = dl_era5(start_date, end_date)

print('-- Processing ERA5 to WPS Int...')
run_era5_to_int(start_date, end_date, hour_interval, False)

print('-- Running metgrid.exe...')
run_metgrid(False)

# print('-- Running real.exe...')
run_real(run_uuid, False)

# print('-- Running WRF...')
# monitor_wrf()



































