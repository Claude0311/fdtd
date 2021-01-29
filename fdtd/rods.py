import numpy as np
import matplotlib.pyplot as plt

def rows(pts:list, lineX:list, lineY:list, r:int, nx:int, ny:int) -> list:
    centerList = pts #array
    for y in range(ny):
        for x in lineX:
            centerList.append([x,y,r])
    for x in range(nx):
        for y in lineY:
            centerList.append([x,y,r])
    return centerList

def notRows(row1:list,row2:list):
    return [item for item in row1 if item not in row2]

def row2Co(pts:list, x0:int, dx:int, y0:int, dy:int) -> np.array:
    if len(pts)==3: 
        print("pts can't be len 3")
    return np.array(pts)*[dx,dy,1]+[x0,y0,0]

def createObs(pts:np.array, Nx:int, Ny:int, Nz=1) -> np.array:
    def eachXYZ(x,y,z):
        obstacle = np.zeros((Nx, Ny, Nz), dtype=bool)
        for [centerX,centerY,r] in pts:
            obstacle = np.logical_or(obstacle,(x-centerX)**2+(y-centerY)**2<r**2)
        return obstacle
    
    return np.fromfunction(eachXYZ, (Nx,Ny,Nz))

def showRods(obstacle:np.array):
    plt.imshow(obstacle)
    plt.show()


if __name__  == "__main__":
    alpha = 50
    r = alpha*0.18
    toalx = 7
    toaly = 8
    # pts = rows([],[3],[],r,toal,toal)
    pts = rows([],[3],[3],r,toalx,toaly)
    pts = notRows(pts,[[5,3,r],[6,3,r],[4,3,r]])
    allrows = rows([],range(toalx),[],r,toalx,toaly)
    pts = notRows(allrows,pts)
    pts.append([3.5,3,0.15*alpha])
    pts = row2Co(pts, alpha,alpha,alpha,alpha)
    obstacle = createObs(pts, alpha*(toalx+1), alpha*(toaly+1))
    np.save('obstacle.npy',obstacle)
    showRods(obstacle)