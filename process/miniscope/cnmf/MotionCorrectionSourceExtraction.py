#!/usr/bin/env python
import logging
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use("Agg")
import numpy as np

try:
    if __IPYTHON__:
        # this is used for debugging purposes only. allows to reload classes when changed
        get_ipython().magic('load_ext autoreload')
        get_ipython().magic('autoreload 2')
except NameError:
    pass

import caiman as cm
from caiman.source_extraction import cnmf
from caiman.utils.utils import download_demo
from caiman.utils.visualization import inspect_correlation_pnr
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import params as params
import glob,os,sys
#%%
# Set up the logger; change this if you like.
# You can log to a file using the filename parameter, or make the output more or less
# verbose by setting level to logging.DEBUG, logging.INFO, logging.WARNING, or logging.ERROR

logging.basicConfig(format=
                    "%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s]"\
                    "[%(process)d] %(message)s",
                    level=logging.WARNING)

def Motioncorrection_Sourceextraction(fnames=['data_endscope.tif'],motion_correction = True,source_extraction = True,n_processes=None):
	"""for motioncorrection and sourceextraction
	fnames is a list of of video , the length of which is 1
	motion_correction = True
	source_extraction = True 
	n_process = None # how many cores are used for parallel computing, default to be None
	problem
	if running in ipython, accident termination will not stop the parallel server. it needs to restart ipython.
	"""
	try:
		cm.stop_server()
	except:
		pass
#%%
	c, dview, n_processes = cm.cluster.setup_cluster(backend='local', n_processes=n_processes, single_thread=False)

	mc_dict={'fnames': fnames,
		'fr': 10, # movie frame rate
		'decay_time': 0.4, # length of a typical transient in seconds
		'pw_rigid': False,
		'max_shifts': (25,25), # maximum allowed rigid shift
		'gSig_filt': (3, 3), #size of filter, in general gSig (see below), change this one if algorithm does not work
		'strides': (96, 96), # start a new patch for pw-rigid motion correction every x pixels
		'overlaps': (32, 32), # overlap between pathes (size of patch strides+overlaps)
		'max_deviation_rigid': 5,# maximum deviation allowed for patch with respect to rigid shifts
		'border_nan': 'copy'}
	opts = params.CNMFParams(params_dict=mc_dict)
# %% MOTION CORRECTION
# The pw_rigit flag set above, determines where to use rigid or pw-rigid
# motion correction 

	if motion_correction:
		mc = MotionCorrect(fnames, dview=dview, **opts.get_group('motion'))
		mc.motion_correct(save_movie=True)

		if mc_dict['pw_rigid']:
			fname_mc = mc.fname_tot_els
			bord_px	= np.ceil(np.maximum(np.max(np.abs(mc.x_shifts_els)),np.max(np.abs(mc.y_shifts_els)))).astype(np.int)
		else:
			fname_mc = mc.fname_tot_rig
			bord_px = np.ceil(np.max(np.abs(mc.shifts_rig))).astype(np.int)
			plt.subplot(1, 2, 1); plt.imshow(mc.total_template_rig)  # % plot template
			plt.subplot(1, 2, 2); plt.plot(mc.shifts_rig)  # % plot rigid shifts
			plt.legend(['x shifts', 'y shifts'])
			plt.xlabel('frames')
			plt.ylabel('pixels')

		bord_px = 0 if mc_dict['border_nan'] is 'copy' else bord_px
		fname_new = cm.save_memmap(fname_mc, base_name='memmap_', order='C',border_to_0=bord_px)

		cm.load(fname_mc).save(os.path.join(os.path.dirname(fnames[0]),'ms_mc.avi'))
		print('Motion correction has been done!')
		print('ms_mc.avi is saved!')
	else: # if no motion_correction just memory map the file
		try:
			fname_new = glob.glob(os.path.join(os.path.dirname(fnames[0]),'memmap_*.mmap'))[0]
		except:
			print("Motion Correction has not been done!")
			sys.exit()
		bord_px = 0
		print(">>>>>>>>>>>>>>>>>>")
		print(fname_new)
		print("<<<<<<<<<<<<<<<<<<")
		print("skip Motion correction, go to Source Extraction!")

#fname_new = cm.save_memmap(fnames, base_name='memmap_',order='C', border_to_0=0, dview=dview)
# save ms_mc.avi to the samve directory of fnames[0]	
#%% setup some parameters for source extraction
	if source_extraction:
# load memory mappable file
		Yr, dims, T = cm.load_memmap(fname_new)
		images = Yr.T.reshape((T,) + dims, order='F')

#%% parameters for source extraction and deconvolution (CNMF-E algorithm)
		opts.change_params(params_dict={'dims':dims,
			'method_init':'corr_pnr', # use this for 1 photon
			'K':None, # upper bound on number of components per patch, in general None for 1p data

			'gSig':(3,3), # gaussian width of a 2D gaussian kernel, which approximates a neuron
			'gSiz':(13,13), # average diameter of a neuron,in general 4*gSig+1
			'stride': 20,# amount of overlap between the patches in pixels (keep it at least large as gSiz, i.e 4 times the neuron size gSig)
			'tsub':1,# downsampling factor in time for initialization, increase if you have memory problems
			'ssub':1,# downsampling factor in space for initialization, increase if you have memory problems
			'rf': 48, # half-size of the patches in pixels. e.g., if rf=40, patches are 80x80       


			'merge_thr':.7, # merging threshold, max correlation allowed
			'p':1, # order of the autoregressive system
			'only_init': True,    # set it to True to run CNMF-E
			'nb': 0,# number of background components (rank) if positive,
			#                 else exact ring model with following settings
			#                         gnb= 0: Return background as b and W
			#                         gnb=-1: Return full rank background B
			#                         gnb<-1: Don't return background
			'nb_patch': 0,# number of background components (rank) per patch if gnb>0,
			#                   else it is set automatically
			'method_deconvolution': 'oasis',       # could use 'cvxpy' alternatively
			'low_rank_background': None,# None leaves background of each patch intact,
			#                     True performs global low-rank approximation if gnb>0
			'update_background_components': True,  # sometimes setting to False improve the results
			'min_corr': .8,# min peak value from correlation image
			'min_pnr': 10, # min peak to noise ratio from PNR image
			'normalize_init': False,               # just leave as is
			'center_psf': True,                    # leave as is for 1 photon
			'ssub_B': 2, # additional downsampling factor in space for background
			'ring_size_factor': 1.4, # radius of ring is gSiz*ring_size_factor
			'del_duplicates': True,  # whether to remove duplicates from initialization
			'border_pix': bord_px}) # number of pixels to not consider in the borders


		cn_filter, pnr = cm.summary_images.correlation_pnr(images[::1], gSig=3, swap_dim=False)
		# inspect_correlation_pnr(cn_filter, pnr)
		# print(min_corr)
		# print(min_pnr)

#%% RUN CNMF ON PATCHES
		cnm = cnmf.CNMF(n_processes=n_processes, dview=dview, Ain=None, params=opts)
		cnm.fit(images)

# discard low quality components
		cnm.params.set('quality',{'min_SNR':2.5,# adaptive way to set threshold on the transien size
			'rval_thr':0.85,# threshold on space consistency 
			#(if lower more components will be accepted, potentially with worst quality)
			'use_cnn':False})
		cnm.estimates.evaluate_components(images, cnm.params, dview=dview)
		print(' ***** ')
		print('Number of total components: ', len(cnm.estimates.C))
		print('Number of accepted components: ', len(cnm.estimates.idx_components))


#%%	    #detrend
		cnm.estimates.detrend_df_f()
		cnm.estimates.deconvolve(cnm.params,dview=dview,dff_flag=True)                      
#%% save result as result.hdf5
		cnm.save(os.path.join(os.path.dirname(fnames[0]),'result.hdf5'))

#%% plot the result for a glimp 
#How many neurons to plot 
		neuronsToPlot = 30        
		      
		DeconvTraces = cnm.estimates.S
		RawTraces = cnm.estimates.C
		SFP = cnm.estimates.A     
		SFP_dims = list(dims)     
		SFP_dims.append(SFP.shape[1])
		print('Spatial foootprints dimensions (height x width x neurons): ' + str(SFP_dims))
		numNeurons = SFP_dims[2]  
		idx_accepted=cnm.estimates.idx_components
		idx_deleted=cnm.estimates.idx_components_bad
		dff=cnm.estimates.F_dff[idx_accepted,:]
		S_dff=cnm.estimates.S_dff[idx_accepted,:]
		SFP = np.reshape(SFP.toarray(), SFP_dims, order='F')

		maxRawTraces = np.amax(RawTraces)
		plt.figure(figsize=(30,15))
		plt.subplot(341); 
		if motion_correction:        
			plt.subplot(345); plt.plot(mc.shifts_rig); plt.title('Motion corrected shifts')
		plt.subplot(3,4,9);       
		plt.subplot(3,4,2); plt.imshow(cn_filter); plt.colorbar(); plt.title('Correlation projection')
		plt.subplot(3,4,6); plt.imshow(pnr); plt.colorbar(); plt.title('PNR')
		plt.subplot(3,4,10); plt.imshow(np.amax(SFP,axis=2)); plt.colorbar(); plt.title('Spatial footprints')
		      
		plt.subplot(2,2,2); plt.figure; plt.title(f'Example traces (first {neuronsToPlot} cells)')
		plot_gain = 10 # To change the value gain of traces
		if numNeurons >= neuronsToPlot:
			for i in range(neuronsToPlot):
				if i == 0:        
					plt.plot(RawTraces[i,:],'k')
				else:             
					trace = RawTraces[i,:] + maxRawTraces*i/plot_gain
					plt.plot(trace,'k')
		else:                     
			for i in range(numNeurons):
				if i == 0:        
					plt.plot(RawTraces[i,:],'k')
				else:             
					trace = RawTraces[i,:] + maxRawTraces*i/plot_gain
					plt.plot(trace,'k')
		plt.subplot(2,2,4); plt.figure; plt.title(f'Deconvolved traces (first {neuronsToPlot} cells)')
		plot_gain = 20 # To change the value gain of traces
		if numNeurons >= neuronsToPlot:
			for i in range(neuronsToPlot):
				if i == 0:       
					plt.plot(DeconvTraces[i,:],'k')
				else:            
					trace = DeconvTraces[i,:] + maxRawTraces*i/plot_gain
					plt.plot(trace,'k')
		else:                    
			for i in range(numNeurons):
				if i == 0:       
					plt.plot(DeconvTraces[i,:],'k')
				else:            
					trace = DeconvTraces[i,:] + maxRawTraces*i/plot_gain
					plt.plot(trace,'k')
		# Save summary figure
		plt.savefig(os.path.dirname(fnames[0]) + '/' + 'summary_figure.pdf', edgecolor='w', format='pdf', transparent=True)	
		print("Source Extraction is done.")

	cm.stop_server(dview=dview)

if __name__ == "__main__":
	Motioncorrection_Sourceextraction(fnames=[r'/home/qiushou/Documents/QS_data/miniscope/miniscope_result/Results_191082/20191022_164420_test/msCam_concat.avi'],
		n_processes=8,motion_correction=False,source_extraction=True)