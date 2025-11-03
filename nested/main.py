#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 15:09:38 2025

@author: mike
"""
import uuid

import pendulum
import sentry_sdk

from download_nml_domain import dl_nml_domain
from set_params import check_set_params
from download_era5 import dl_era5
from run_era5_to_int import run_era5_to_int
from run_metgrid import run_metgrid
from run_real import run_real
from monitor_wrf import monitor_wrf
from upload_namelists import upload_namelists

import params

run_uuid = uuid.uuid4().hex[-13:]

########################################
## Sentry
sentry = params.file['sentry']

if sentry['dsn'] != '':
    sentry_sdk.init(
        dsn=sentry['dsn'],
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )

if sentry['tags']:
    sentry_sdk.set_tags(sentry['tags'])

sentry_sdk.set_tags({'run_uuid': run_uuid})

########################################
### Run sequence

start_time = pendulum.now()

print(f'--  run uuid: {run_uuid}')

print(f"-- start time: {start_time.format('YYYY-MM-DD HH:mm:ss')}")

print('-- Downloading namelists...')
dl_check = dl_nml_domain()

start_date, end_date, hour_interval, outputs = check_set_params()

print('-- Uploading updated namelists')
ul_nml_check = upload_namelists(run_uuid)

print(f'start date: {start_date}, end date: {end_date}, input hour interval: {hour_interval}')

print('-- Downloading ERA5 data...')
era5_check = dl_era5(start_date, end_date)

print('-- Processing ERA5 to WPS Int...')
run_era5_to_int(start_date, end_date, hour_interval)

print('-- Running metgrid.exe...')
run_metgrid()

print('-- Running real.exe...')
run_real(run_uuid)

print('-- Running WRF...')
monitor_wrf(outputs, end_date, run_uuid)

end_time = pendulum.now()

print(f"-- end time: {end_time.format('YYYY-MM-DD HH:mm:ss')}")

diff = end_time - start_time

mins = round(diff.total_minutes())

print(f"-- Total run minutes: {mins}")



























