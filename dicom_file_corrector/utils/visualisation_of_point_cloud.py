import matplotlib.pyplot as plt
import numpy as np

def superposed_point_cloud(data_point_cloud_1: np.array, data_point_cloud_2: np.array,
                           label_point_cloud_1: np.array, label_point_cloud_2: np.array) -> None:
    """
    This method show the shape and appearance of 2 point cloud on the same figure 
    
    :param data_point_cloud_1 : the data of a point cloud obtain with point_cloud.py
    :param data_point_cloud_2 : the data of a point cloud obtain with point_cloud.py
    :label_point_cloud_1 : the label of a point cloud obtain with point_cloud.py
    :label_point_cloud_2 : the label of a point cloud obtain with point_cloud.py

    :return : None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(data_point_cloud_1[0], data_point_cloud_1[1], data_point_cloud_1[2], label=label_point_cloud_1)
    ax.scatter(data_point_cloud_2[0], data_point_cloud_2[1], data_point_cloud_2[2], label=label_point_cloud_2)
    ax.set_xlabel('X[mm]')
    ax.set_ylabel('Y[mm]')
    ax.set_zlabel('Z[mm]')
    plt.legend()
    plt.show()

def graphe_nuage_point(data_point_cloud: np.array) -> None:
    """
    This method show the shape of a point cloud
    
    :param data_point_cloud : the data of a point cloud obtain with point_cloud.py

    :return : none
    """

    fig = plt.figure()
    ax = fig.add_subplot(111,projection = '3d')
    ax.scatter(data_point_cloud[0], data_point_cloud[1], data_point_cloud[2])
    ax.set_xlabel('X[mm]')
    ax.set_ylabel('Y[mm]')
    ax.set_zlabel('Z[mm]')
    plt.show()