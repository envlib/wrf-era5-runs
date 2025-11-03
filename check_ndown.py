#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 15:28:14 2025

@author: mike
"""
import copy

import params


############################################################
### Checks


def check_ndown_params(domains):
    ndown_check = False
    domains_init = copy.deepcopy(domains)

    if 'ndown' in params.file:
        ndown = params.file['ndown']

        if 'input' in ndown:
            if 'path' in ndown['input']:
                ndown_input_bool = True

        if ndown_input_bool:
            if domains:
                if len(domains) > 1 or domains[0] == 1:
                    raise ValueError("If ndown inputs are passed, then domains should be a list with a single domain integer that isn't domain 1.")
                ndown_check = True
                domains_init = [domains[0] - 1, domains[0]]
            else:
                raise ValueError("If ndown inputs are passed, then domains should be a list with a single domain integer that isn't domain 1.")

    return ndown_check, domains_init













































































