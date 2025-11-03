#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 10:40:23 2025

@author: mike
"""
import os
import pathlib
import shlex
import subprocess
import pendulum
import sentry_sdk
import shutil
import copy

import params

############################################
### Parameters


###########################################
### Functions


def run_ndown(run_uuid, del_old=True):
    """

    """
    # new_top_domain = params.file['ndown']['new_top_domain']

    run_path = params.data_path.joinpath('run')

    ## Prep files
    os.rename(run_path.joinpath('wrfinput_d02'), run_path.joinpath('wrfndi_d02'))

    cmd_str = f'ln -sf {params.data_path}/wrfout_* .'
    p = subprocess.run(cmd_str, shell=True, capture_output=False, text=False, check=False, cwd=run_path)

    cmd_str = f'mpirun -n 4 {params.ndown_exe}'
    cmd_list = shlex.split(cmd_str)
    p = subprocess.run(cmd_list, capture_output=False, text=False, check=False, cwd=params.data_path)

    real_log_path = params.data_path.joinpath('rsl.out.0000')
    with open(real_log_path, 'rt') as f:
        f.seek(0, os.SEEK_END)
        f.seek(f.tell() - 40, os.SEEK_SET)
        results_str = f.read()

    if 'SUCCESS COMPLETE REAL_EM INIT' in results_str:
        if del_old:
            for path in params.data_path.glob('wrfout_*.nc'):
                path.unlink()

            params.run_path.joinpath('wrfndi_d02').unlink()

        for file_path in params.run_path.glob('*_d01'):
            file_path.unlink()

        for file_path in params.run_path.glob('*_d02'):
            file_part = file_path.name.split('_')[0]
            new_file = file_part + '_d01'
            new_file_path = params.run_path.joinpath(new_file)
            os.rename(file_path, new_file_path)

        return True
    else:
        # scope = sentry_sdk.get_current_scope()
        # scope.add_attachment(path=real_log_path)

        remote = copy.deepcopy(params.file['remote']['output'])

        name = 'output'

        if 'path' in remote:
            out_path = pathlib.Path(remote.pop('path'))
        else:
            out_path = None

        print(f'-- Uploading ndown.exe log files for run uuid: {run_uuid}')
        dest_str = f'{name}:{out_path}/logs/{run_uuid}/'
        cmd_str = f'rclone copy {params.data_path} {dest_str} --config={params.config_path} --include "rsl.*" --transfers=8'
        cmd_list = shlex.split(cmd_str)
        p = subprocess.run(cmd_list, capture_output=True, text=True, check=True)

        raise ValueError(f'ndown.exe failed. Look at the logs for details: {results_str}')





