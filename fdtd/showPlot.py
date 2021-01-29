import numpy as np
import matplotlib.pyplot as plt
import torch

def showEn(grid):
    period = grid.sources[0].period
    for detector in grid.detectors:
        plotEo(detector,period)
    for source in grid.sources:
        plotEi(source,period)
    plt.xlabel('n period')
    plt.ylabel('power(W/m)')
    plt.legend()
    plt.show()

def plotEi(source,period):
    ax = np.ones(period)/period
    Ez,H = source.getEH()
    power = Ez**2 + H**2
    power = np.sum(power,axis=1)
    power = np.convolve(power,ax,mode='valid')
    axx = np.arange(len(power))/period
    plt.plot(axx, power, label=source.name)
    plt.pause(0.02)

def plotEo(detector,period):
    ax = np.ones(period)/period
    Ez = torch.stack(detector.E[:])[:,:,2]
    if 'right' in detector.name:
        H = torch.stack(detector.H[:])[:,:,0]
    elif 'up' in detector.name:
        Ez = Ez[:-1]
        H = torch.stack(detector.H[:])[1:,:,1]
    elif 'left' in detector.name:
        Ez = Ez[:-1]
        H = -torch.stack(detector.H[:])[1:,:,0]
    elif 'down' in detector.name:
        H = -torch.stack(detector.H[:])[:,:,1]
    else: return
    power = np.array((Ez*H).to('cpu'))
    power = np.sum(power,axis=1)
    power = np.convolve(power,ax,mode='valid')
    axx = np.arange(len(power))/period
    print(detector.name,'Pavg',np.average(power[-5*period:]))
    plt.plot(axx, power, label=detector.name)