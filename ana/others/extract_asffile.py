import os,shutil,sys
if sys.argv:
    prefix = sys.argv[1]
else:
    prefix = r'C:\Users\Sabri\Desktop\14.Wang Guang-ling cases\20190328-0404_#1945017-1945027'
path = glob.glob(os.path.join(prefix,'*\*.asf'),recursive=True)
os.mkdir(os.path.join(prefix,'asf'))
for i in path:
    source = os.path.join(prefix,i)
    dst = os.path.join(prefix,"asf")
    shutil.copy(source,dst) x,"asf")
     hutil.copy(source,dst)
