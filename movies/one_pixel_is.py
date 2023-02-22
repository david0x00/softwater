import numpy as np

mtx = np.array([
    [1535.10668 / 1.5, 0, 954.393136 / 1.5],
    [0, 1530.80529 / 1.5, 543.030187 / 1.5],
    [0,0,1]
])

newcameramtx = np.array([
    [1559.8905 / 1.5, 0, 942.619458 / 1.5],
    [0, 1544.98389 / 1.5, 543.694259 / 1.5],
    [0,0,1]
])

inv_camera_mtx = np.linalg.inv(newcameramtx)

dist = np.array([[0.19210016, -0.4423498, 0.00093771, -0.00542759, 0.25832642 ]])

camera_to_markers_dist = 57.055 #cm

x = 1
y = 0
coord_2d = np.array([[x],
                        [y],
                        [1]])
coord_3d = np.matmul(inv_camera_mtx, coord_2d) * camera_to_markers_dist
print("x = " + str(coord_3d[0][0]))
print("y = " + str(coord_3d[1][0]))

# conclusion - 1 pixel is about 1/2 a mm
