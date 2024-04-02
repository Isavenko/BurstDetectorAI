from sklearn.neighbors import KernelDensity
import matplotlib.pyplot as plt
import numpy as np
with open('AIBurst.npy', 'rb') as f:
    a = np.load(f).reshape(-1,1)
    kde = KernelDensity(kernel='gaussian', bandwidth=0.025).fit(a)
    linspace = np.linspace(0, 1, num=1000)[:, np.newaxis]
    log_dens1 = np.exp(kde.score_samples(linspace))
    # print(np.exp(log_dens))
    plt.plot(linspace,log_dens1)
    with open('AIDud.npy', 'rb') as f:
        a = np.load(f).reshape(-1,1)
        kde = KernelDensity(kernel='gaussian', bandwidth=0.025).fit(a)
        linspace = np.linspace(0, 1, num=1000)[:, np.newaxis]
        log_dens2 = np.exp(kde.score_samples(linspace))
        # print(np.exp(log_dens))
        plt.plot(linspace,log_dens2)
        plt.show()
        plt.plot(linspace,log_dens1/(log_dens2+log_dens1))
        plt.ylim([0,1.1])
        plt.show()
        for i in range(len(linspace)):
            print(linspace[i][0],",",log_dens1[i]/(log_dens2[i]+log_dens1[i]),sep='')
    