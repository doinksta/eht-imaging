import ehtim as eh
import matplotlib.pyplot as plt
import numpy as np
from os import path, makedirs

import glob

# Note: use the 'dev' branch of ehtim
# Note: run this from inside the directory ehtim to get the proper path to models and arrays

# where to save results
savefolder = '../results/'
if not path.exists(savefolder):
    makedirs(savefolder)

# ============ LOAD IN INDIVIDUAL IMAGES AND STRING THEM INTO A MOVIE ============ #

# Grab all the png files within specified folder
frame_names = glob.glob("../aaaa/*")

nframes = len(frame_names)
frame_duration = 0.2
mjd = 3

frames = []

for i, frame_name in zip(range(nframes), frame_names):
    im = eh.image.load_fits(frame_name) # <= put in the name of the image file indexed in some way by i
    im.time = i * frame_duration
    im.mjd  = mjd
    frames.append(im)

# nframes = ?
# frame_duration = ?
# mjd = ?
#
# frames = []
# for i in range(nframes):
#     im = eh.image.load_fits(<name of image file>) # <= put in the name of the image file indexed in some way by i
#     im.time = i * frame_duration
#     im.mjd  = mjd
#     frames.append(im)

movie = eh.movie.merge_im_list(frames)
movie.reset_interp(interp='linear', bounds_error=False)
movie.save_hdf5('./movie.hdf5')

# # ============ LOAD A MOVIE ============ #
#
# filepath = ?
# movie = eh.movie.load_hdf5(filepath)
# movie.reset_interp(interp='linear', bounds_error=False)
#
# # ============ CREATE AN OBSERVATION ============ #
#
# obsFromScratch = True
#
# array = '../arrays/EHT2017_M87.txt' # path to array file for loading telescope site locations and SEFDs (how noisy they are)
# add_th_noise = True # False if you *don't* want to add thermal error. If there are no sefds in obs_orig it will use the sigma for each data point
# phasecal = False # True if you don't want to add atmospheric phase error. if False then it adds random phases to simulate atmosphere
# ampcal = False # True if you don't want to add atmospheric amplitude error. if False then add random gain errors
# stabilize_scan_phase = True # if true then add a single phase error for each scan to act similar to adhoc phasing
# stabilize_scan_amp = True # if true then add a single gain error at each scan
# jones = True # apply jones matrix for including noise in the measurements (including leakage)
# inv_jones = False # no not invert the jones matrix
# frcal = True # True if you do not include effects of field rotation
# dcal = False # True if you do not include the effects of leakage
# dterm_offset = 0.05 # a random offset of the D terms is given at each site with this standard deviation away from 1
#
#
# # ============ make an observation from scratch ============ #
# if obsFromScratch:
#     tint_sec = 10
#     tadv_sec = 600
#     tstart_hr = 0 # note you will have to make sure the times line up with the movie file's times, otherwise it will just take data from the first or last frame
#     tstop_hr = 24
#     bw_hz = 4e9
#     eht = eh.array.load_txt(array)
#
#     # these gains are approximated from the EHT 2017 data
#     # the standard deviation of the absolute gain of each telescope from a gain of 1
#     gain_offset = {'ALMA':0.15, 'APEX':0.15, 'SMT':0.15, 'LMT':0.6, 'PV':0.15, 'SMA':0.15, 'JCMT':0.15, 'SPT':0.15}
#     # the standard deviation of gain differences over the observation at each telescope
#     gainp = {'ALMA':0.05, 'APEX':0.05, 'SMT':0.05, 'LMT':0.5, 'PV':0.05, 'SMA':0.05, 'JCMT':0.05, 'SPT':0.05}
#
#
#     # note there seems to be some issues with the leakage simulation for observations generated from movies.
#     #you don't need to worry about this now but just wanted to let you know why I removed some of the arguments. I am looking into it.
#     obs = movie.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz, add_th_noise=add_th_noise, ampcal=ampcal, phasecal=phasecal,
#         stabilize_scan_phase=stabilize_scan_phase, stabilize_scan_amp=stabilize_scan_amp, gain_offset=gain_offset,
#         gainp=gainp)
#
#
# # ============ make an observation by taking telescope/sampling params from another observation ============ #
# else:
#     obs_orig = eh.obsdata.load_uvfits(obsfilename, remove_nan=True)
#
#     # change the image coordinates to align with the obs
#     simim.ra = obs_orig.ra
#     simim.dec = obs_orig.dec
#     simim.rf = obs_orig.rf
#
#     # these gains are approximated from the EHT 2017 data
#     # the standard deviation of the absolute gain of each telescope from a gain of 1
#     gain_offset = {'AA':0.15, 'AP':0.15, 'AZ':0.15, 'LM':0.6, 'PV':0.15, 'SM':0.15, 'JC':0.15, 'SP':0.15, 'SR':0.0}
#     # the standard deviation of gain differences over the observation at each telescope
#     gainp = {'AA':0.05, 'AP':0.05, 'AZ':0.05, 'LM':0.5, 'PV':0.05, 'SM':0.05, 'JC':0.05, 'SP':0.15, 'SR':0.0}
#
#     obs = movie.observe_same(obs_orig, add_th_noise=add_th_noise, ampcal=ampcal, phasecal=phasecal,
#         stabilize_scan_phase=stabilize_scan_phase, stabilize_scan_amp=stabilize_scan_amp, gain_offset=gain_offset,
#         gainp=gainp)
#
#
#
# # ============ DISPLAY AND SAVE ============ #
#
# # These are some simple plots you can check
# obs.plotall('u','v', conj=True, rangey=[-1e10, 1e10], rangex=[-1e10, 1e10]) # uv coverage
# obs.plotall('uvdist','amp') # amplitude with baseline distance'
#
# site1 = obs.tarr[0]['site']
# site2 = obs.tarr[1]['site']
# site3 = obs.tarr[2]['site']
# obs.plot_bl(site1, site2,'phase', rangey=[-180, 180]) # visibility phase on a baseline over time
# obs.plot_cphase(site1, site2, site3)
#
#
# obs.save_uvfits(savefolder + 'simobs.uvfits')
# simim.save_fits(savefolder + 'simim.fits')
# simim.display(label_type='scale', has_title=False, cbar_unit=('$\mu$-Jy', '$\mu$as$^2$'), export_pdf=savefolder + 'simim.pdf')
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
