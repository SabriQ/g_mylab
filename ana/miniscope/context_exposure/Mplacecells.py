import pandas as pd
import numpy as np
import scipy.stats
from scipy.ndimage import gaussian_filter1d

def shuffle(df,times=1000):
    for i in range(times):
        new_df = df.sample(frac=1).reset_index(drop=True)
        yield new_df
        
def speed_optimize(speeds,method="gaussian_filter1d",sigma=3,length=12):

    if method == "gaussian_filter1d": # default
        speeds = gaussian_filter1d(speeds,sigma)
        print("speed filter sigma is default to be 3")
    elif method == "slider":
        print("Slider length default to be 12. About 0.4s in 30fps behavioral video")
    elif method == "temporal_bin":
        print("bin_length default to be 12, meaning 12 frames in each temporal_bin")
    else:
        print("This is a warning because method is only available in ['gaussian_filter1d','slider','temporal_bin'].",
              " Here default to return gaussian_filter1d with sigma =3")
        return speed_optimize(X,Y,T,s,method="gaussian_filter1d",sigma=3)
        
    return speeds # in cm/s


def Cal_SIs(df,in_context_placebin_num):
    # p(x) the probability for the mouse being at location x for each trial 
    print("call Cal_SIs")
    p_xs = []
    total_frame = df.shape[0]

    for place_bin in set(in_context_placebin_num):
        p_x = (in_context_placebin_num==place_bin).sum()/total_frame
        p_xs.append(p_x)
        # print("probability in place_bin %s is %s"%(place_bin,p_x))

    # λ(x) the average firing rate for mouse being at location x for each trial
    Afr_xs = df.groupby(in_context_placebin_num).mean()
    # λ
    Afr_all = df[in_context_placebin_num>0].mean()
    # Afr_all = Afr_xs.mean() #20200914矫正
    # si
    SIs = ((((Afr_xs.T)*p_xs).T)*(Afr_xs/Afr_all.values).apply(np.log2)).sum()
    return SIs


def bootstrap_Cal_SIs(df,in_context_placebin_num):
    # p(x) the probability for the mouse being at location x for each trial 
    print("call bootstrap_Cal_SIs")
    p_xs = []
    total_frame = df.shape[0]

    for place_bin in set(in_context_placebin_num):
        p_x = (in_context_placebin_num==place_bin).sum()/total_frame
        p_xs.append(p_x)
        # print("probability in place_bin %s is %s"%(place_bin,p_x))

    #λ(x) the average firing rate for mouse being at location x for each trial
    Afr_xs = df.groupby(in_context_placebin_num).mean()
    # λ
    Afr_all = df[in_context_placebin_num>0].mean()
    # Afr_all = Afr_xs.mean() 20200914矫正
    def shuffle():
        shuffle_Afr_xs = Afr_xs.sample(frac=1).reset_index(drop=True)
        shuffle_SIs = ((((shuffle_Afr_xs.T)*p_xs).T)*(shuffle_Afr_xs/Afr_all.values).apply(np.log2)).sum()
        return shuffle_SIs

    return shuffle 

# def place_cells(idx_accept,corrected_ms_ts,sigraw,aligned_behave2ms,behavelog_info,context=0,min_speed=3,speed_filter_sigma=3,shuffle_time=1000,z_score_cdf=0.95):
#     observe_si = Cal_SIs(idx_accept,corrected_ms_ts,sigraw,aligned_behave2ms,behavelog_info,context,min_speed,speed_filter_sigma)
#     shuffle = bootstrap_Cal_SIs(idx_accept,corrected_ms_ts,sigraw,aligned_behave2ms,behavelog_info,context,min_speed,speed_filter_sigma)    
#     shuffle_SIs = pd.DataFrame(columns=[i+1 for i in range(shuffle_time)])
#     for i in range(shuffle_time):
#         shuffle_SIs[i+1]=shuffle().values
#         if i % 100 == 0:
#             print("shuffle times: %s"%i)
#     shuffle_SIs = shuffle_SIs.T
#     shuffle_SIs.columns=idx_accept
#     threshold = scipy.stats.norm.ppf(z_score_cdf)# 大于百分之95的z_score
#     z_score = (observe_si-shuffle_SIs.mean())/shuffle_SIs.std()
#     return z_score[z_score>threshold].index

def plot():
    pass