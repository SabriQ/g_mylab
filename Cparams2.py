import os
import pickle
import sys
class Animal():
	"""
	Class, create/reload animal info as a dict self._info
		child class: Mouse
		buid-in info, all default:
			"Organization":"ION",
			"LAB":"XuChun"
	Properties：
		animal_id
		info
		keys
	Args:
		animal_id 
		savedir
	methods:
		save: save info dict to animal_id_params.pkl
		save2mat : pass
		save2db : pass
	"""
	def __init__(self,animal_id,savedir=r'C:\Users\admin\Desktop\test'):
		self.__animal_id = str(animal_id)
		self._filepath = os.path.join(savedir,self.__animal_id+'_params.pkl')

		if not os.path.exists(self._filepath):
			self._info={
			"Organization":"ION",
			"Lab":"XuChun"
			}
			print("create %s_params "%self.__animal_id)
		else:
			with open(self._filepath,'rb') as f:
				self._info=pickle.load(f)
			print("Reload %s_params " % self.__animal_id)

	@property
	def animal_id(self):
		return self.__animal_id
	@property	
	def info(self):
		return self._info
	@property
	def keys(self):
		return self._info.keys()

	def __getitem__(self,key):
		return self._info[key]

	def __setitem__(self,key,value):		
		if key in self._info.keys():
			print("updation of property %s is not allowed"%key)
		else:
			self._info[key]=value
			print("add property %s"%key)
	def __delitem__(self,key):
		print("deletion of property is not allowd")
				
	def save(self):		
		with open(self._filepath,'wb') as f:
			pickle.dump(self._info,f)
		print("save %s_Params at %s "% (self.__animal_id,self._filepath))

	def save2mat(self):
		pass
	def save2db(self):
		pass
#%%
class Mouse(Animal):
	"""
	class , create/reload mouse info as a dict self._info
		father class: Animal
		child class: MouseExp
		build-in info, all non-default:
			"mouse_id":mouse_id,
			"species":species,
			"mouse_id":mouse_id,
			"owner":owner,
			"gender":gender,
			"enter_date":enter_date,
			"enter_age":enter_age,
			"experiments":experiments
	properties:
	Args:mouse_id,savedir,species="mouse"
		,owner="qs",gender="m",enter_date="20200000",enter_age="56d",experiments=list()
	method:
		save2db: pass
	"""
	def __init__(self,mouse_id,savedir=r'C:\Users\admin\Desktop\test',species="mouse"
		,owner="qs",gender="m",enter_date="20200000",enter_age="56d",experiments=list()):
		
		super().__init__(mouse_id,savedir) 
		if not os.path.exists(self._filepath):
			print("add mouse properties")
			self._info = {**self._info,**{"mouse_id":mouse_id,
											"species":species,
											"mouse_id":mouse_id,
											"owner":owner,
											"gender":gender,
											"enter_date":enter_date,
											"enter_age":enter_age,
											"experiments":experiments}}
					
	def __setitem__(self,key,value):
		if key in ["Organization","Lab","mouse_id","species","experiments"]:
			print("%s can not be modifed"%key)
		else:
			self._info[key]=value
			if key in self._info.keys():
				print("update property %s"%key)
			else:
				print("add property %s"%key)	
	def save2db(self):
		pass

class MouseExp(Mouse):
	"""
	class. create/reload mouse info as a dict `self._info`. 
		   create dict `self.info[self._dictkey]` to collect all the info in Exp dictkey
		   father class: Mouse
	properties:
	Args:
	Methods:
	"""
	def __init__(self,mouse_id,dictkey
	,savedir=r"C:\Users\admin\Desktop\test"
	,species="mouse"
	,owner="qs"
	,gender="m"
	,enter_date="20200000"
	,enter_age="56d"
	,experiments=[]
	,**kwargs):
		super().__init__(mouse_id,savedir,species,owner,gender,enter_date,enter_age,experiments)
		
		self._dictkey = dictkey
		if not self._dictkey in self._info["experiments"]:
			self._info[self._dictkey]={}
			self.info["experiments"].append(self._dictkey)
			print("add new experiments %s"%self._dictkey)
			
		for key,value in kwargs:		
			if not key in self._info[self._dictkey].keys():
				print("add new param %s in %s"%(key,self._dictkey))
			else:
				print("update param %s in %s"%(key,self._dictkey))

	@property
	def exp_info(self):
		return self._info[self._dictkey]
	def expkeys(self):
		return self._info[self._dictkey].keys()

	def __getitem__(self,key):
		return self._info[self._dictkey][key]
	def __setitem__(self,key,value):
		self._info[self._dictkey][key]=value
		if key in self._info[self._dictkey].keys():
			print("update property %s"%key)
		else:
			print("add new property %s"%key)
	def __delitem__(self,key):
		del self._info[self._dictkey][key]
		if key in self._info[self._dictkey].keys():
			print("del property %s"%key)
		else:
			print("no property %s"%key)

if __name__ == "__main__":
	def fun(cls,dictkey="cd"):		
		def write_expPrams(mouse_id):
			mouse = cls(mouse_id,dictkey=dictkey)
			mouse.save()
		return write_expPrams

	Exp_cd = fun(cls=MouseExp)

	for mouse_id in ["191172","191173","191174"]:
		Exp_cd(mouse_id)
    

	
	# m1 = MouseExpParams(191172,"cfc")
	# print("------0-------")
	# print(m1.info)
	# print("------1-------")
	# m1["experimentor"]="qs"
	# print(m1.exp_info)
	# m1.save()
	# print("------2-------")