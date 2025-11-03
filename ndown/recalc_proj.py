#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 15:02:46 2025

@author: mike
"""
import pyproj
import f90nml

import params

###############################################
### Parameters

# fpath = '/home/mike/git/wrf-repos/wrf-testing/namelists/namelist_uc_v02a.wps'

# new_path = '/home/mike/git/wrf-repos/wrf-testing/namelists/namelist_new_d03.wps'

# start_domain = 2

wrf_sphere_radius = 6370000

###############################################
### Convert projection params


def recalc_proj(new_top_domain):

    wps_nml = f90nml.read(params.wps_nml_path)

    geogrid = wps_nml['geogrid']
    
    parent_id = geogrid['parent_id']
    max_domains = len(parent_id)

    # TODO: eventually I'd like to allow multiple sub domains below the ndown domain, but currently only one is allowed
    if new_top_domain == 1 or new_top_domain + 1 >= max_domains:
        raise ValueError('new_top_domain must be > 1 and one less than max_domains')
    
    parent_grid_ratio = geogrid['parent_grid_ratio']
    
    dx = geogrid['dx']
    dy = geogrid['dy']
    
    i_parent_start = geogrid['i_parent_start']
    j_parent_start = geogrid['j_parent_start']
    
    e_we = geogrid['e_we']
    e_sn = geogrid['e_sn']
    
    # define original projection
    map_proj = geogrid['map_proj'].lower()
    lat_0 = geogrid['ref_lat']
    lat_1 = geogrid['truelat1']
    lat_2 = geogrid['truelat2']
    
    if 'stand_lon' in geogrid:
        lon_0 = geogrid['stand_lon']
    else:
        lon_0 = geogrid['ref_lon']
    
    ref_lon = geogrid['ref_lon']
    
    lon_angle = lon_0 - ref_lon
    
    if map_proj == 'lambert':
        pwrf = f"""+proj=lcc +lat_1={lat_1} +lat_2={lat_2} +lat_0={lat_0} +lon_0={lon_0} +x_0=0 +y_0=0 +a={wrf_sphere_radius} +b={wrf_sphere_radius}"""
    elif map_proj == 'mercator':
        pwrf = f"""+proj=merc +lat_ts={lat_1} +lon_0={lon_0} +x_0=0 +y_0=0 +a={wrf_sphere_radius} +b={wrf_sphere_radius}"""
    elif map_proj == 'polar':
        pwrf = f"""+proj=stere +lat_ts={lat_1} +lat_0=90.0 +lon_0={lon_0} +x_0=0 +y_0=0 +a={wrf_sphere_radius} +b={wrf_sphere_radius}"""
    else:
        raise NotImplementedError('WRF proj not implemented yet: '
                                  f'{map_proj}')
    
    proj_crs = pyproj.CRS.from_string(pwrf)
    
    geo_crs = pyproj.CRS(
            proj='latlong',
            R=wrf_sphere_radius
        )
    
    geo_to_proj = pyproj.Transformer.from_crs(geo_crs, proj_crs, always_xy=True)
    proj_to_geo = pyproj.Transformer.from_crs(proj_crs, geo_crs, always_xy=True)
    
    for i in range(1, new_top_domain):
        prev_x_center, prev_y_center = geo_to_proj.transform(ref_lon, lat_0)
    
        prev_dx_center = ((e_we[i-1] - 1) * 0.5) * dx
        prev_dy_center = ((e_sn[i-1] - 1) * 0.5) * dy
    
        i_start = i_parent_start[i] - 1
        j_start = j_parent_start[i] - 1
    
        new_dx_start = i_start * dx
        new_dy_start = j_start * dy
    
        new_dx = dx / parent_grid_ratio[i]
        new_dy = dy / parent_grid_ratio[i]
    
        new_dx_end = new_dx_start + (new_dx * (e_we[i] - 1))
        new_dy_end = new_dy_start + (new_dy * (e_sn[i] - 1))
    
        new_dx_center = (new_dx_end + new_dx_start) * 0.5
        new_dy_center = (new_dy_end + new_dy_start) * 0.5
    
        ddx = new_dx_center - prev_dx_center
        ddy = new_dy_center - prev_dy_center
    
        new_x_center = prev_x_center + ddx
        new_y_center = prev_y_center + ddy
    
        ref_lon, lat_0 = proj_to_geo.transform(new_x_center, new_y_center)
    
    lon_0 = ref_lon + lon_angle
    
    ## Save projection back to namelist.wps
    ref_lat = round(lat_0, 6)
    ref_lon = round(ref_lon, 6)
    stand_lon = round(lon_0, 6)
    
    geogrid['dx'] = int(new_dx)
    geogrid['dy'] = int(new_dy)
    geogrid['ref_lat'] = ref_lat
    geogrid['ref_lon'] = ref_lon
    geogrid['truelat1'] = ref_lat
    geogrid['truelat2'] = ref_lat
    geogrid['stand_lon'] = stand_lon
    
    ## Update other parameters in namelist.wps
    new_top_parent_id = parent_id[new_top_domain - 1]
    geogrid['parent_id'] = [pid - new_top_parent_id if pid > 1 else 1 for pid in range(new_top_domain - 1, max_domains)]
    
    new_parent_grid_ratio = parent_grid_ratio[new_top_domain - 1:]
    new_parent_grid_ratio[0] = 1
    geogrid['parent_grid_ratio'] = new_parent_grid_ratio
    
    new_i_parent_start = i_parent_start[new_top_domain - 1:]
    new_i_parent_start[0] = 1
    geogrid['i_parent_start'] = new_i_parent_start
    
    new_j_parent_start = j_parent_start[new_top_domain - 1:]
    new_j_parent_start[0] = 1
    geogrid['j_parent_start'] = new_j_parent_start
    
    new_max_domain = len(new_j_parent_start)
    
    share = wps_nml['share']
    share['max_dom'] = new_max_domain
    
    # All others
    for grp_name, grp in wps_nml.items():
        for p, v in grp.items():
            if isinstance(v, list):
                if len(v) == max_domains:
                    wps_nml[grp_name][p] = v[new_top_domain - 1:]
    
    with open(params.wps_nml_path, 'w') as nml_file:
       wps_nml.write(nml_file)
    
    ### Update namelist.input for WRF
    wrf_nml = f90nml.read(params.wrf_nml_path)
    
    domains = wrf_nml['domains']
    
    domains['max_dom'] = new_max_domain
    domains['dx'] = int(new_dx)
    domains['dy'] = int(new_dy)
    domains['parent_id'] = geogrid['parent_id']
    domains['parent_grid_ratio'] = geogrid['parent_grid_ratio']
    domains['parent_id'] = geogrid['parent_id']
    domains['i_parent_start'] = geogrid['i_parent_start']
    domains['j_parent_start'] = geogrid['j_parent_start']
    
    new_parent_time_step_ratio = domains['parent_time_step_ratio'][new_top_domain - 1:]
    new_parent_time_step_ratio[0] = 1
    domains['parent_time_step_ratio'] = new_parent_time_step_ratio
    
    domains['grid_id'] = domains['grid_id'][:new_max_domain]
    
    for grp_name, grp in wrf_nml.items():
        for p, v in grp.items():
            if isinstance(v, list):
                if len(v) == max_domains:
                    wrf_nml[grp_name][p] = v[new_top_domain - 1:]
    
    with open(params.wrf_nml_path, 'w') as nml_file:
       wrf_nml.write(nml_file)










# with open(fpath) as f:
#     lines = f.readlines()

# pargs = dict()
# for l in lines:
#     s = l.split('=')
#     if len(s) < 2:
#         continue
#     s0 = s[0].strip().upper()
#     s1 = list(filter(None, s[1].strip().replace('\n', '').split(',')))

#     if s0 == 'PARENT_ID':
#         parent_id = [int(s) for s in s1]
#     if s0 == 'PARENT_GRID_RATIO':
#         parent_ratio = [int(s) for s in s1]
#     if s0 == 'I_PARENT_START':
#         i_parent_start = [int(s) for s in s1]
#     if s0 == 'J_PARENT_START':
#         j_parent_start = [int(s) for s in s1]
#     if s0 == 'E_WE':
#         e_we = [int(s) for s in s1]
#     if s0 == 'E_SN':
#         e_sn = [int(s) for s in s1]
#     if s0 == 'DX':
#         dx = float(s1[0])
#     if s0 == 'DY':
#         dy = float(s1[0])
#     if s0 == 'MAP_PROJ':
#         map_proj = s1[0].replace("'", '').strip().upper()
#     if s0 == 'REF_LAT':
#         pargs['lat_0'] = float(s1[0])
#     if s0 == 'REF_LON':
#         pargs['ref_lon'] = float(s1[0])
#     if s0 == 'TRUELAT1':
#         pargs['lat_1'] = float(s1[0])
#     if s0 == 'TRUELAT2':
#         pargs['lat_2'] = float(s1[0])
#     if s0 == 'STAND_LON':
#         pargs['lon_0'] = float(s1[0])

# # Sometimes files are not complete
# pargs.setdefault('lon_0', pargs['ref_lon'])

# # define projection
# if map_proj == 'LAMBERT':
#     pwrf = '+proj=lcc +lat_1={lat_1} +lat_2={lat_2} ' \
#            '+lat_0={lat_0} +lon_0={lon_0} ' \
#            '+x_0=0 +y_0=0 +a=6370000 +b=6370000'
#     pwrf = pwrf.format(**pargs)
# elif map_proj == 'MERCATOR':
#     pwrf = '+proj=merc +lat_ts={lat_1} +lon_0={lon_0} ' \
#            '+x_0=0 +y_0=0 +a=6370000 +b=6370000'
#     pwrf = pwrf.format(**pargs)
# elif map_proj == 'POLAR':
#     pwrf = '+proj=stere +lat_ts={lat_1} +lat_0=90.0 +lon_0={lon_0} ' \
#            '+x_0=0 +y_0=0 +a=6370000 +b=6370000'
#     pwrf = pwrf.format(**pargs)
# else:
#     raise NotImplementedError('WRF proj not implemented yet: '
#                               '{}'.format(map_proj))
# pwrf = CRS.from_string(pwrf)

# # get easting and northings from dom center (probably unnecessary here)
# transformer = Transformer.from_crs(wgs84, pwrf)

# e, n = transformer.transform(pargs['ref_lon'], pargs['lat_0'])

# # LL corner
# nx, ny = e_we[0]-1, e_sn[0]-1
# x0 = -(nx-1) / 2. * dx + e  # -2 because of staggered grid
# y0 = -(ny-1) / 2. * dy + n







































