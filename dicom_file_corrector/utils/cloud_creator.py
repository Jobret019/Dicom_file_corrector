import numpy as np
import os 
import pydicom

def z_flip_image_point_cloud(image_cloud: np.array) -> np.array:
    """
    This method flip an image point cloud relative to the z axis 
    
    :param image_cloud : the image cloud to flip 
    :return : an image point cloud with the z inverted
    """
    inversion_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]])
    inverse_image_cloud = np.dot(inversion_matrix, image_cloud ) 
    return inverse_image_cloud 

def create_image_point_cloud_from_dicom_series_folder(path_to_serie: str) -> np.array:
    """
    This method create an array of 3 array (x,y,z position) with all the position in mm of 
    the pixels with the highest radiodensity value which correspond to source position in an image 
    
    :param path_to_serie : complete path of the serie containing all the CT files
    :return : an array with array of x, y and z coordinates in patient 
    """    
    max = 0
    index_x = 0
    index_y = 0
    position_x = 0
    position_y = 0
    position_z = 0
    points_coordinate = []
    list_x_position = np.array([])
    list_y_position = np.array([])
    list_z_position = np.array([])

    paths = os.listdir(path_to_serie)
    pixel_positions_x,pixel_positions_y,_ = express_pixel_position_in_patient_coordinate(os.path.join(path_to_serie, paths[0]))

    for i in range(len(paths)) : 
        complete_path = os.path.join(path_to_serie, paths[i])
        data = get_image_hu_data_from_file(complete_path)
        if max <= np.max(data) :
            max = np.amax(data) 

    for i in range(len(paths)) : 
        complete_path = os.path.join(path_to_serie,paths[i])
        open_dicom = pydicom.dcmread(complete_path)
        data = get_image_hu_data_from_file(complete_path)
        maximum_HU_pixels_indexs = np.where(data == max)
        position_z = open_dicom.ImagePositionPatient[2]
        for j in range(len(maximum_HU_pixels_indexs[0])) : 
            index_x = maximum_HU_pixels_indexs[1][j]
            index_y = maximum_HU_pixels_indexs[0][j]
            position_x = pixel_positions_x[index_x]
            position_y = pixel_positions_y[index_y]
            list_x_position = np.append(list_x_position, position_x)
            list_y_position = np.append(list_y_position, position_y)
            list_z_position = np.append(list_z_position, position_z)

    points_coordinate=np.array([list_x_position, list_y_position, list_z_position])     

    return points_coordinate


def create_source_point_cloud_from_rtplan(path_to_plan: str) -> np.array:
    """
    This method create an array of 3 array (x,y,z position) with all the position of the sources given by the 
    RTPLAN file.  
    
    :param path_to_plan : complete path of the RTPLAN file
    :return : an array with array of x, y and z coordinates in patient
    """    
    list_source_position = []
    open_plan = pydicom.dcmread(path_to_plan)
    aplication_setups = open_plan.ApplicationSetupSequence

    for i in range(len(aplication_setups)) :
        source_position = express_source_position_in_patient_coordinate(path_to_plan, i) 
        if source_position == None : 
            list_source_position += []       
        elif len(source_position) == 2 :
            list_source_position += [np.array(source_position[0]), ]
            list_source_position += [np.array(source_position[1]), ]
        else : 
            list_source_position += [np.array(source_position),]
    list_source_position = np.array(list_source_position)  

    new_list_source_position=[] 
    Position_x = np.array([])
    Position_y = np.array([])
    Position_z = np.array([])
    for i in range(len(list_source_position)) : 
        Position_x = np.append(Position_x, list_source_position[i][0])
        Position_y = np.append(Position_y, list_source_position[i][1])
        Position_z = np.append(Position_z, list_source_position[i][2])
    new_list_source_position += [np.array(Position_x), ]
    new_list_source_position += [np.array(Position_y), ]
    new_list_source_position += [np.array(Position_z), ]
    source_coordinates = np.array(new_list_source_position)

    return source_coordinates

def get_image_hu_data_from_file(path_to_image_file: str) -> np.array:
    """
    This method create a 2D array with all the value of radiodensity in HU associated with every pixel 
    of a CT image 
    
    :param path_to_image_file : complete path of an CT image file
    :return : a 2d array of radiodensity value
    """
    open_dicom = pydicom.dcmread(path_to_image_file)
    rescale_slop = open_dicom.RescaleSlope
    rescale_intercept = open_dicom.RescaleIntercept
    pixel_data = open_dicom.pixel_array 
    data = pixel_data*rescale_slop+rescale_intercept
    return data

def express_pixel_position_in_patient_coordinate(path_to_image_file: str) -> tuple[list, list, float]: 
    """
    This method express the xyz position of the pixels in an image slice in the patient coordinate 
    system (mm).
    
    :param path_to_image_file : complete path of an CT image file
    :return: two arrays of the positions of x and y in mm for all the pixels  and a float for the 
    position in z 
    """
    open_dicom = pydicom.dcmread(path_to_image_file)
    orientation = open_dicom.ImageOrientationPatient
    position = open_dicom.ImagePositionPatient
    pixel_spacing = open_dicom.PixelSpacing
    columns = open_dicom.Columns
    rows = open_dicom.Rows

    Xx, Xy, Xz, Yx, Yy, Yz = orientation[0], orientation[1], orientation[2], orientation[3], orientation[4], orientation[5]
    Sx, Sy, Sz = position[0], position[1], position[2]
    deltai, deltaj = pixel_spacing[0], pixel_spacing[1]

    M = [[Xx*deltai, Yx*deltaj, 0, Sx],
         [Xy*deltai, Yy*deltaj, 0, Sy],
         [Xz*deltai, Yz*deltaj, 0, Sz],
         [0, 0, 0, 1]] 
    position = np.empty((columns,rows),dtype = object)
    position_X = np.empty(columns,dtype = object)
    position_Y = np.empty(rows,dtype = object)

    for i in range(columns) : 
        for j in range(rows) : 
            vecteur = np.array([i, j, 0, 1]) 
            position[i][j] = np.dot(M,vecteur)
            position[i][j] = np.delete(position[i][j], 3)
            position_Y[j] = position[0][j][1]
        position_X[i] = position[i][0][0]

    position_Z=position[1][1][2]

    return position_X, position_Y, position_Z

def express_source_position_in_patient_coordinate(path_to_plan: str, setup_number: int) -> np.array:
    """
    This method extract the position of a source in a RTPLAN dicom files .
    
    :param path_to_plan : complete path of an RTPLAN file
    :param setup_number : the setup number of the source 
    :return: 1 or 2 array of source xyz position in mm 
    """
    open_plan = pydicom.dcmread(path_to_plan)
    application_setup = open_plan.ApplicationSetupSequence

    if hasattr(application_setup[setup_number], 'ChannelSequence') : 
        channel_sequence = application_setup[setup_number].ChannelSequence
        Control_point = channel_sequence[0].BrachyControlPointSequence
        if len(Control_point) == 4 : 
            source_position_2 = Control_point[2].ControlPoint3DPosition 
        elif len(Control_point) == 2 : 
            source_position_2 = None

        source_position_1 = Control_point[0].ControlPoint3DPosition 

        if source_position_2 == None : 
            return source_position_1
        else : 
            return source_position_1, source_position_2 

    else : 
        pass