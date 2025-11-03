#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 15:28:14 2025

@author: mike
"""
import params


############################################################
### Checks


def check_ndown_params():
    check = False
    
    if 'ndown' in params.file:
        ndown = params.file['ndown']
        if 'new_top_domain' in ndown and 'input' in ndown:
            if ndown['new_top_domain'] > 1 and 'path' in ndown['input']:
                check = True

    return check













































































