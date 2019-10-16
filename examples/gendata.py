import ehtim as eh
import matplotlib.pyplot as plt
import numpy as np
from os import path, makedirs

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# Note: use the 'dev' branch of ehtim
# Note: run this from inside the directory ehtim to get the proper path to models and arrays

# ============ PARAMS ============ #

# set as true if you want to use a model image, false will load the specified image
modelBool = True
# set as true if you want to create an obs from scratch with SEFDs
# set as False if you want to use the parameters of a previous obs
obsFromScratch = True

sampleimage = '../models/avery_m87_2_eofn.txt'  # path to a sample image. you can load a txt or fits image into ehtim
array = '../arrays/EHT2017_M87.txt'  # path to array file for loading telescope site locations and SEFDs (how noisy they are)
npix = 128  # number of pixels in model image
fov = 200 * eh.RADPERUAS  # field of view in radians in model image

source = 'M87'  # source that you are observing
polrep = 'stokes'  # how data is handled for imaging purposes
mjd = 57853  # day of observation #WARNING: THIS DOESN'T ALIGN WITH THE DATE LOADED IN THE UVFITS, SO IF YOU WANT TO MAKE A SYNTHETIC DATASET FOR A SPECIFIC DAY YOU NEED TO CHANGE THIS
seed = 1  # seed so you get the same realization of noise
# path to the uvfits
# download sample uvfits here: http://datacommons.cyverse.org/browse/iplant/home/shared/commons_repo/curated/EHTC_FirstM87Results_Apr2019/uvfits
obsfilename = '../SR1_' + source + '_2017_101_lo_hops_netcal_StokesI.uvfits'

# ra and dec (location) of each source and how much flux is from the compact component
if source == 'M87':
    ra = 12.513728717168174
    dec = 12.39112323919932
    zbl = 0.8
if source == 'SGRA':
    ra = 17.761122472222223
    dec = -28.992189444444445
    zbl = 2.0
elif source == 'J1924-2914':
    ra = 19.414182210498385
    dec = -29.24170032236311
    zbl = 3.4
rf = 230000000000.0

# where to save results
savefolder = '../results/'
if not path.exists(savefolder):
    makedirs(savefolder)

# ============ LOAD AN IMAGE ============ #

# model image parameters
ring_radius = 22 * eh.RADPERUAS  # the radius of the ring
ring_width = 10 * eh.RADPERUAS  # the width of the ring
nonun_frac = 0.5  # defines how much brighter the brighter location is on the ring
theta_nonun_rad = 270  # defines the angle of the brightest location
fracpol = 0.4  # fractional polarization on model image
corr = 5 * eh.RADPERUAS  # the coherance length of the polarization

# ============ make an image using model parameters ============ #
if modelBool:
    # make an empty image
    simim = eh.image.make_empty(npix, fov, ra, dec, rf=rf, source=source, mjd=mjd)
    # add a non-uniform ring
    simim = simim.add_ring_m1(zbl, nonun_frac, ring_radius, theta_nonun_rad * np.pi / 180., ring_width, x=0, y=0)
    # add random polarization field with a constant fractional polarization
    simim = simim.add_random_pol(fracpol, corr, seed=0)
# ============ load a specified image (can replace load_txt with load_fits) ============ #
else:
    # load a saved image
    simim = eh.image.load_txt(sampleimage)
    simim.mjd = mjd  # replace the mjd of the image
    simim.ra = ra
    simim.dec = dec
    simim.imvec = zbl * simim.imvec / np.sum(simim.imvec)

# display the image
simim.display()  # display the Stokes I image
simim.display(pol='U')  # display the Stokes U image_args
simim.display(plotp=True)  # display the Stokes I image with polarization information

# ============ CREATE AN OBSERVATION ============ #


add_th_noise = True  # False if you *don't* want to add thermal error. If there are no sefds in obs_orig it will use the sigma for each data point
phasecal = False  # True if you don't want to add atmospheric phase error. if False then it adds random phases to simulate atmosphere
ampcal = False  # True if you don't want to add atmospheric amplitude error. if False then add random gain errors
stabilize_scan_phase = True  # if true then add a single phase error for each scan to act similar to adhoc phasing
stabilize_scan_amp = True  # if true then add a single gain error at each scan
jones = True  # apply jones matrix for including noise in the measurements (including leakage)
inv_jones = False  # no not invert the jones matrix
frcal = True  # True if you do not include effects of field rotation
dcal = False  # True if you do not include the effects of leakage
dterm_offset = 0.05  # a random offset of the D terms is given at each site with this standard deviation away from 1

# ============ make an observation from scratch ============ #
if obsFromScratch:
    tint_sec = 10
    tadv_sec = 600
    tstart_hr = 0
    tstop_hr = 24
    bw_hz = 4e9
    eht = eh.array.load_txt(array)

    # these gains are approximated from the EHT 2017 data
    # the standard deviation of the absolute gain of each telescope from a gain of 1
    gain_offset = {'ALMA': 0.15, 'APEX': 0.15, 'SMT': 0.15, 'LMT': 0.6, 'PV': 0.15, 'SMA': 0.15, 'JCMT': 0.15,
                   'SPT': 0.15}
    # the standard deviation of gain differences over the observation at each telescope
    gainp = {'ALMA': 0.05, 'APEX': 0.05, 'SMT': 0.05, 'LMT': 0.5, 'PV': 0.05, 'SMA': 0.05, 'JCMT': 0.05, 'SPT': 0.05}

    obs = simim.observe(eht, tint_sec, tadv_sec, tstart_hr, tstop_hr, bw_hz, add_th_noise=add_th_noise, ampcal=ampcal,
                        phasecal=phasecal,
                        stabilize_scan_phase=stabilize_scan_phase, stabilize_scan_amp=stabilize_scan_amp,
                        gain_offset=gain_offset,
                        gainp=gainp, jones=jones, inv_jones=inv_jones, dcal=dcal, frcal=frcal,
                        dterm_offset=dterm_offset, seed=seed)


# ============ make an observation by taking telescope/sampling params from another observation ============ #
else:
    obs_orig = eh.obsdata.load_uvfits(obsfilename, remove_nan=True)

    # change the image coordinates to align with the obs
    simim.ra = obs_orig.ra
    simim.dec = obs_orig.dec
    simim.rf = obs_orig.rf

    # these gains are approximated from the EHT 2017 data
    # the standard deviation of the absolute gain of each telescope from a gain of 1
    gain_offset = {'AA': 0.15, 'AP': 0.15, 'AZ': 0.15, 'LM': 0.6, 'PV': 0.15, 'SM': 0.15, 'JC': 0.15, 'SP': 0.15,
                   'SR': 0.0}
    # the standard deviation of gain differences over the observation at each telescope
    gainp = {'AA': 0.05, 'AP': 0.05, 'AZ': 0.05, 'LM': 0.5, 'PV': 0.05, 'SM': 0.05, 'JC': 0.05, 'SP': 0.15, 'SR': 0.0}

    obs = simim.observe_same(obs_orig, add_th_noise=add_th_noise, ampcal=ampcal, phasecal=phasecal,
                             stabilize_scan_phase=stabilize_scan_phase, stabilize_scan_amp=stabilize_scan_amp,
                             gain_offset=gain_offset,
                             gainp=gainp, jones=jones, inv_jones=inv_jones, dcal=dcal, frcal=frcal,
                             dterm_offset=dterm_offset, seed=seed)

# ============ DISPLAY AND SAVE ============ #

# These are some simple plots you can check
obs.plotall('u', 'v', conj=True, rangey=[-1e10, 1e10], rangex=[-1e10, 1e10])  # uv coverage
obs.plotall('uvdist', 'amp')  # amplitude with baseline distance'

site1 = obs.tarr[0]['site']
site2 = obs.tarr[1]['site']
site3 = obs.tarr[2]['site']
obs.plot_bl(site1, site2, 'phase', rangey=[-180, 180]).plot()  # visibility phase on a baseline over time
obs.plot_cphase(site1, site2, site3).plot()
plt.show()

obs.save_uvfits(savefolder + 'simobs.uvfits')
simim.save_fits(savefolder + 'simim.fits')
simim.display(label_type='scale', has_title=False, cbar_unit=('$\mu$-Jy', '$\mu$as$^2$'),
              export_pdf=savefolder + 'simim.pdf')
















