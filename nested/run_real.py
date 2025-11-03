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


def run_real(run_uuid, del_old=True):
    """

    """
    cmd_str = f'mpirun -n 4 {params.real_exe}'
    cmd_list = shlex.split(cmd_str)
    p = subprocess.run(cmd_list, capture_output=False, text=False, check=False, cwd=params.data_path)

    real_log_path = params.data_path.joinpath('rsl.out.0000')
    with open(real_log_path, 'rt') as f:
        f.seek(0, os.SEEK_END)
        f.seek(f.tell() - 40, os.SEEK_SET)
        results_str = f.read()

    if 'SUCCESS COMPLETE REAL_EM INIT' in results_str:
        if del_old:
            for path in params.data_path.glob('met_em.*.nc'):
                path.unlink()

        run_path = params.data_path.joinpath('run')
        if run_path.exists():
            shutil.rmtree(run_path)

        run_path.mkdir()
        wrf_run_path = params.wrf_path.joinpath('run')
        cmd_str = f'ln -sf {wrf_run_path}/* .'
        # cmd_list = shlex.split(cmd_str)
        p = subprocess.run(cmd_str, shell=True, capture_output=False, text=False, check=False, cwd=run_path)
        for path in params.data_path.glob('wrf*'):
            file_name = path.name
            path.rename(run_path.joinpath(file_name))

        cmd_str = f'ln -sf {params.wrf_nml_path} .'
        p = subprocess.run(cmd_str, shell=True, capture_output=False, text=False, check=False, cwd=run_path)

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

        print(f'-- Uploading WRF/real.exe log files for run uuid: {run_uuid}')
        dest_str = f'{name}:{out_path}/logs/{run_uuid}/'
        cmd_str = f'rclone copy {params.data_path} {dest_str} --config={params.config_path} --include "rsl.*" --transfers=8'
        cmd_list = shlex.split(cmd_str)
        p = subprocess.run(cmd_list, capture_output=True, text=True, check=True)

        raise ValueError(f'real.exe failed. Look at the logs for details: {results_str}')





