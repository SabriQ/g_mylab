import matplotlib.pyplot as plt
import time
plt.ion()
fig, ax = plt.subplots()
y1 = []
# for i in range(50):
i=10
y1.append(i)  # 每迭代一次，将i放入y1中画出来
plt.cla()   # 清除键
ax.bar(y1, label='test', height=y1, width=0.3)
ax.legend()
ax.figure.canvas.draw()
# fig.canvas.draw_artist()
print("----%s---"%fig.__sizeof__())
plt.ioff()
plt.show()		
	# plt.pause(2)
# plt.show()


