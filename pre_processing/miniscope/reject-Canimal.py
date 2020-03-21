import os
import pickle
import datetime

class Params():
	"""
	To construct class which could create two-layer dict.
	The 1st layer:
		1 specis
		2 lab
		3 organization
		4 animal_id
		5 filepath
		6 2nd layer dict
	The 2nd layer:
		{exp:params}
	properties:
		all_info: show the dict from the 1st layer
		info: show the dict from the 2nd layer
		animal_id: show animal id
		keys: show all the keys of the 2nd layer
	Args:
		animal_id: string. e.g. "191120"
		exp: string. the key of the 2nd dict in 1st layer. e.g. "basic_info"
		params: dict. the value of the 2nd dict the 1st layer. e.g.
				{"owner":"qs"
				,"gender":"M"
				,"enter_date":"20200000"
				,"enter_age":"8w"
				,"gene_type":"C57"
				,"experiments":list()}
		savedir: string. the directory of where to save this two-layer dict named as anima_id_params.pkl. e.g. "191120_params.pkl"
		species: string. e.g. "mouse"
		lab: string. e.g. "XuChun"
		organization: string. e.g. "ION"
	methods:
		save. save this two layer dict at self.filepath
	"""
	def __init__(self,animal_id,exp,params
		,savedir=r'C:\Users\admin\Desktop\test'
		,species="mouse"
		,lab="XuChun"
		,organization="ION"):

		if not isinstance(animal_id,str):
			self._animal_id = str(animal_id)
		else:
			self._animal_id=animal_id
		if not isinstance(exp,str):
			self.exp = str(exp)
		else:
			self.exp = exp

		self._filepath = os.path.join(savedir,self._animal_id+'_params.pkl')
		if not os.path.exists(self._filepath):	
			self._all_info = {"species": species
			,"lab":lab
			,"organization":organization
			,"animal_id":self._animal_id
			,"filepath":self._filepath}
			self._all_info[self.exp]=params
		else:
			with open(self._filepath,'rb') as f:
				self._all_info=pickle.load(f)
			print("Reload %s" % self._animal_id)

			if not self.exp in self._all_info.keys():
				self._all_info[self.exp] = {} 

	@property
	def all_info(self):
		return self._all_info
	@property	
	def info(self):
		return self._all_info[self.exp]
	@property
	def animal_id(self):
		return self._animal_id
	@property
	def keys(self):
		return list(self._all_info[self.exp].keys())
	

	def __getitem__(self,key):
		return self._all_info[self.exp][key]
	def __setitem__(self,key,value):
		self._all_info[self.exp][key]=value	
	def __delitem__(self,key):
		del self._all_info[self.exp][key]
		print("delete %s"% key)
	def save(self):			
		with open(self._filepath,'wb') as f:
			pickle.dump(self._all_info,f)
		print("save Params of  %s"% self._animal_id)
	def save_to_mat(self):
		pass

class Mouse():
	"""
	A class that could record and reload the basic_info of each mouse, {"basic_info":{*}}
	This class is the father of other classes of experiments, 
		that means it will always show basic_info when you call class.info

	properties:
		all_info: show the dict from the 1st layer
		info: show the dict "basic_info"
		mouse_id: show mouse_id
		keys: show all the keys of dict "basic_info"
		experiments:show all the experiments in basic_info["experiments"]
	Args:
		mouse_id
		params_info. dict. the value of basic_info. e.g.
			{"owner":"qs"
			,"gender":"M"
			,"enter_date":"20200000"
			,"enter_age":"8w"
			,"gene_type":"C57"
			,"experiments":list()}
	methods:
		add_exp. add `value` in list, basic_info["experiments"]
		rename_exp. rename old_name with new_name in basic_info["experiments"]
		save. params are saved.
	"""
	def __init__(self,mouse_id,params_info= {"owner":"qs"
		,"gender":"M"
		,"enter_date":"20200000"
		,"enter_age":"8w"
		,"gene_type":"C57"
		,"experiments":list()}
		):

		if not isinstance(mouse_id,str):
			self._mouse_id = str(mouse_id)
		else:
			self._mouse_id=mouse_id
		
		self._param=Params(self._mouse_id,exp="basic_info",params=params_info)		

	@property
	def info(self):
		return self._param.info
	@property
	def all_info(self):
		return self._param.all_info	
	@property
	def mouse_id(self):
		return self._mouse_id
	@property
	def keys(self):
		return self._param.keys
	@property
	def expriments(self):
		return self._param["experiments"]

	def __getitem__(self,key):
		return self._param[key]
	def __setitem__(self,key,value):
		self._param[key]=value
	def __delitem__(self,key):
		del self._param[key]
	def add_exp(self,value):
		if not value in self._param["experiments"]:
			self._param["experiments"].append(value)
			print("Add experiments %s"% value)
		else:
			print("you have done this %s. "% value)
	def rename_exp(self,old_name, new_name):
		if not old_name in self._param["experiments"]:
			print("you haven't done %s" % old_name)
		else:
			if new_name in self._param["experiments"]:
				print("you have donw this %s"% new_name)
			else:
				self._param["experiments"] = [new_name if i == old_name else i for i in self._param["experiments"]]
				print("replace %s with %s "%(old_name,new_name))
	def save(self):
		return self._param.save()



	

# 定义__slots__属性，它是用来申明实例属性名字的列表，减小内存开销
if __name__ == "__main__":

	#%%
	# p1=Params(191172,exp="basic_info",params = {"owner":"qs"
	# 	,"gender":"M"
	# 	,"enter_date":"20200000"
	# 	,"enter_age":"8w"
	# 	,"gene_type":"C57"
	# 	,"experiments":list()}
	# )
	# print(p1.info)
	# print(p1.all_info)
	# print(p1["experiments"])
	# p1.save()
	# %%
	m1 = Mouse(191172)
	m1["test"] = "test"
	print(m1.info)
	# m1.add_exp("contextual fear conditioning")
	# m1.rename_exp("contextual fear conditioning","CFC")
	# print(m1.info)
	# m1.save()
	# print("------")
	# m2 = Mouse(191172)
	# print(m2.info)


