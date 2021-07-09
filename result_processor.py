import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import ticker as mtick
from random import normalvariate as nrd

f = open('results/sig4').read().split("\n")[:-1]
res_sig = list(map(int, f))
dv = 0
hrs = sig4 = [int(nrd(120, dv)) for _ in range(12 * 5)] + \
             [120, 130, 140, 145, 150] + [int(nrd(150, dv)) for _ in range(12)] + [150, 140, 135, 130, 125, 120,
                                                                                   120] + \
             [int(nrd(125, dv)) for _ in range(12 * 3)] + \
             [int(nrd(120, dv)) for _ in range(12 * 1)] + [int(nrd(125, dv)) for _ in range(12 * 2)] + \
             [130, 130, 130, 140, 142, 143] + [int(nrd(145, dv)) for _ in range(12)] + [140, 135, 130, 120, 110,
                                                                                        115] + \
             [int(nrd(125, dv)) for _ in range(12 * 1)] + [int(nrd(120, dv)) for _ in range(12 * 2)] + \
             [int(nrd(115, dv)) for _ in range(12 * 2)]

print("real BaseLine %f" % (sum(hrs) / len(hrs)))

diff = list(map(lambda p, q: p - q, hrs, res_sig))
# plt.plot(diff)
# plt.show()
print("diff mean: %f variance: %f" % (np.mean(diff), np.var(diff)))

diff = np.abs(np.array(diff))
# print("<=0: %d" % len(diff[diff <= 0]))
# print("<=3: %d" % len(diff[diff <= 3]))
# print("<=5: %d" % len(diff[diff <= 5]))
# print("<=10: %d" % len(diff[diff <= 10]))

x_labels = []
buckets = [0] * 11
for i in range(11):
    v = len(diff[diff >= i]) if i == 10 else len(diff[diff == i])
    buckets[i] = v / len(diff) * 100
    x_labels.append(str(i))
x_labels[-1] = '>' + x_labels[-2]

fig, ax = plt.subplots(figsize=(8, 6))
# fig = plt.figure(2)
# ax = fig.add_subplot(1, 1, 1, figsize=(12, 4.5))

ax.bar(x_labels, np.cumsum(buckets))


def format(a: plt.Axes):
    fmt = '%.0f%%'
    yticks = mtick.FormatStrFormatter(fmt)
    a.yaxis.set_major_formatter(yticks)
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    a.set_xlabel("difference of the acutal value and the measured value (BPM)")
    a.set_ylabel("percentage of samples with this difference")


format(ax)

plt.savefig("plot.png", dpi=500)
