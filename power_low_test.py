from scipy.stats import powerlaw
import matplotlib.pyplot as plt

vals = []
for i in range(10000):
    vals.append(powerlaw.rvs(0.5, 0)*100 + 10)

plt.hist(vals); plt.show()
