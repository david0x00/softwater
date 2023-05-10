import matplotlib.pyplot as plt

lr0x = -1.90252717903648
lr0y = 33.10513550700130

lr2x = -2.1510445532061700
lr2y = 32.74235678374990

lr4x = -2.185281242153150
lr4y = 32.093517307211200
	
rl0x = -4.6934385044474300
rl0y = 31.91702401002720

	
rl2x = -3.2191930828353500
rl2y = 31.629221212922200

rl4x = -3.4217668564228300
rl4y = 32.148207002087400

plt.plot(lr0x, lr0y, marker="o", label="LR-0")
plt.plot(lr2x, lr2y, marker="o", label="LR-0.5")
plt.plot(lr4x, lr4y, marker="o", label="LR-0.25")
plt.plot(rl0x, rl0y, marker="o", label="RL-0")
plt.plot(rl2x, rl2y, marker="o", label="RL-0.5")
plt.plot(rl4x, rl4y, marker="o", label="RL-0.25")
plt.xlim((-5,-1.5))
plt.ylim((31,34.5))
plt.legend()
plt.show()