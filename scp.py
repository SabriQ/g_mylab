import paramiko,os,sys,time
def getfilesinpath(file):
    if os.path.isdir(file):
        files = os.listdir(file)
        for f in files:
            if os.path.isdir(f):
                yield getfilesinpath(f)
            else:
                yield os.path.abspath(f)
    else:
        yield os.path.abspath(file)
        


def cluster():
    # img_name示例：07670ff76fc14ab496b0dd411a33ac95-6.webp
    host = "172.16.102.22"  #服务器ip地址
    port = 30722  # 端口号
    username = "sqiu"  # ssh 用户名
    password = "qiushou"  # 密码
 
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)#允许连接不在know_hosts文件中的主机
    ssh.connect(host, port, username, password)#远程访问的服务器信息

    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    sftp = ssh.open_sftp()
    print("sftp has established")

    def upload(localfile, remotefile):
        sftp.put(localfile,remotefile)
        print("%s has uploaded"%localfile)

    return upload

up2cluster = cluster()
remote_rootdir = r"/gpfsdata/home/sqiu/data/wjn_data/miniscope_results/Results_192600"
dirs = [
"20200720_190235_30fps_0605",
"20200719_144303_30fps_0612",
"20200720_181746_30fps_0615",
"20200720_182014_30fps_0623",
"20200720_215126_30fps_0624",
"20200720_215310_30fps_0626",
"20200725_162317_30fps_0630",
"20200725_162559_30fps_0702",
"20200725_171005_30fps_0707",
"20200724_205131_30fps_0709",
"20200724_205728_30fps_0710",
"20200724_205853_30fps_0713",
"20200725_152404_30fps_0714"

]

for dir in dirs:
    localfile = dir+r"/"+"msCam_concat.avi"
    remotefile = remote_rootdir+r"/"+dir+r"/"+"msCam_concat.avi"
    up2cluster(localfile,remotefile)

