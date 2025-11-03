#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 15:03:38 2025

@author: mike
"""
import tomllib
import os
import pathlib
import f90nml
import shlex
import subprocess

import pendulum

############################################
### Parameters


#######################################################
### Functions


def create_rclone_config(name, config_path, config_dict):
    """

    """
    type_ = config_dict['type']
    config_list = [f'{k}={v}' for k, v in config_dict.items() if k != 'type']
    config_str = ' '.join(config_list)
    config_path = config_path.joinpath('rclone.config')
    cmd_str = f'rclone config create {name} {type_} {config_str} --config={config_path} --non-interactive'
    cmd_list = shlex.split(cmd_str)
    p = subprocess.run(cmd_list, capture_output=True, text=True, check=True)

    return config_path


def read_last_line(file_path):
    """

    """
    cmd_str = f'tail -1 {file_path}'
    cmd_list = shlex.split(cmd_str)
    p = subprocess.run(cmd_list, capture_output=True, text=True, check=False)

    return p.stdout.strip('\n')


def query_out_files(run_path, output_globs):
    """

    """
    out_files = {}
    for glob in output_globs:
        for file_path in run_path.glob(glob):
            file_name = file_path.name
            out_name, domain, datetime = file_name.split('_', 2)
            if (out_name, domain) in out_files:
                out_files[(out_name, domain)].append(str(file_path))
                out_files[(out_name, domain)].sort()
            else:
                out_files[(out_name, domain)] = [str(file_path)]

    return out_files


def select_files_to_ul(out_files, min_files):
    """

    """
    files = []
    for grp, file_paths in out_files.items():
        n_files = len(file_paths)
        file_paths.sort(reverse=True)
        if n_files > min_files:
            files.extend(file_paths[min_files:n_files])

    return files


def ul_output_files(files, run_path, name, out_path, config_path):
    """

    """
    files_str = '\n'.join([os.path.split(p)[-1] for p in files])
    print(f'-- Uploading files:\n{files_str}')

    cmd_str = f'rclone copy {run_path} {name}:{out_path} --transfers=4 --config={config_path} --files-from-raw -'
    cmd_list = shlex.split(cmd_str)

    start_ul = pendulum.now()
    p = subprocess.run(cmd_list, input=files_str, capture_output=True, text=True, check=False)
    end_ul = pendulum.now()

    diff = end_ul - start_ul

    mins = round(diff.total_minutes(), 1)

    if p.stderr == '':
        for file in files:
            os.remove(file)
        print(f'-- Upload successful in {mins} mins')

















