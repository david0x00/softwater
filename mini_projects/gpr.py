import numpy as np

def generate_noisy_points(n=10, noise_variance=1e-6):
    np.random.seed(777)
    X = np.random.uniform(-3., 3., (n, 1))
    print(X)
    y = np.sin(X) + np.random.randn(n, 1) * noise_variance**0.5
    print(y)
    return X, y


def kernel(x, y, l2):
    sqdist = np.sum(x**2,1).reshape(-1,1) + \
             np.sum(y**2,1) - 2*np.dot(x, y.T)
    return np.exp(-.5 * (1/l2) * sqdist)


import matplotlib.pylab as plt
X, y = generate_noisy_points()
plt.plot(X, y, 'x')
plt.show()

Xtest, ytest = generate_noisy_points(100)
Xtest.sort(axis=0)

n = len(Xtest)
K = kernel(Xtest, Xtest)
L = np.linalg.cholesky(K + noise_var*np.eye(n))
f_prior = np.dot(L, np.random.normal(size=(n, n_samples)))