from mylab.process.miniscope.context_exposure.Cminiresult import MiniResult as MR
from Mfunctions import *
from Mplots import *
from mylab.process.miniscope.Mfunctions import *
class MiniCDResult(MR):
    def __init__(self,Result_dir):
        super().__init__(Result_dir)
        self.exp_name = "context_discrimination"


    def add_info2aligned_behave2ms(ms_session,scale=0.2339021309714166,placebin_number=10):
    #     scale = 0.2339021309714166 #cm/pixel 40cm的台子，202016，202017.202019适用
        update = 0
        with open(ms_session,'rb') as f:
            result = pickle.load(f)
            
        if "aligned_behave2ms" in result.keys():
            #1 添加 "in_context" in behave_track
            mask = result["in_context_mask"]
            if not "in_context" in result["aligned_behave2ms"].columns:
                in_context=[]
                for x,y in zip(result["aligned_behave2ms"]["Body_x"],result["aligned_behave2ms"]["Body_y"]):
                    if 255 in mask[int(y),int(x)]:
                        in_context.append(0)
                    else:
                        in_context.append(1)
                result["aligned_behave2ms"]["in_context"]=in_context
                print("'in_context' has added")
                update = 1
            else:
                print("'in_context' has been there")

            #2 添加“Body_speed" "Body_speed_angle"
            if not "Body_speed" in result["aligned_behave2ms"].columns:
                Body_speed,Body_speed_angle = Video.speed(X=result["aligned_behave2ms"]["Body_x"],Y=result["aligned_behave2ms"]["Body_y"],T=result["aligned_behave2ms"]["be_ts"],s=scale)
                result["aligned_behave2ms"]["Body_speed"]=list(Body_speed)
                result["aligned_behave2ms"]["Body_speed_angle"]=list(Body_speed_angle)
                update = 1
            else:
                print("'Body_speed'and'Body_speed_angle' has been there")
            
            #3 添加 “in_context_place_bin"
            if not "in_context_placebin_num" in result["aligned_behave2ms"].columns:
                Cx_min = np.min(result["in_context_coords"][:,0])
                Cx_max = np.max(result["in_context_coords"][:,0])
    
                palcebinwidth=(Cx_max-Cx_min)/placebin_number
                placebins = [] #从1开始 0留给所有‘其他区域’
                for n in range(placebin_number):
                    placebins.append([Cx_min+n*palcebinwidth,Cx_min+(n+1)*palcebinwidth])
                in_context_placebin_num = []
                print(placebins)
                for in_context,x in zip(result["aligned_behave2ms"]['in_context'],result["aligned_behave2ms"]['Body_x']):
                    x = int(x)
                    if not in_context:
                        in_context_placebin_num.append(0)
                    else:   
                        for i in range(placebin_number):
                            if i == 0 :
                                if x<placebins[i][1]:
                                    in_context_placebin_num.append(i+1)
                                else:
                                    pass
                            elif not i == placebin_number-1:
                                if x>=placebins[i][0] and x<placebins[i][1]:
                                    in_context_placebin_num.append(i+1)
                                else:             
                                    pass
                            else:
                                if x>=placebins[i][0]:
                                    in_context_placebin_num.append(i+1)
                                else:
                                    pass
                        
                print(len(in_context_placebin_num),result["aligned_behave2ms"].shape)
                result["aligned_behave2ms"]["in_context_placebin_num"] = in_context_placebin_num
                update = 1
            else:
                print("'in_context_placebin_num' has been there")
            
        else:
            print("you haven't align behave to ms or it's homecage session")

        if update:
            with open(ms_session,'wb') as f:
                pickle.dump(result,f)
            print("aligned_behave2ms is updated and saved %s" %ms_session)
# add_info2aligned_behave2ms(ms_sessions)