import os 
import utils.point_cloud_array_creator as pc 
import Iterative_closest_point as icp
import shutil

def empty_copy(old_patient_folder_path: str, destination_path: str,title: str) -> None: 
    """
    This method create a copy of a patient dicom folder with no dicom file in it

    :param old_patient_folder_path : the path of the patient file to be copy  
    :param destination_path : the path of the destination of the copyt 
    :param title : the new title of the patient folder 

    :return : None 
    """
    new_patient_folder_path = os.path.join(destination_path,title)
    shutil.copytree(old_patient_folder_path,new_patient_folder_path) 
    study=os.listdir(new_patient_folder_path)[0]
    study_path = os.path.join(new_patient_folder_path, study)
    series = os.listdir(study_path)
    for serie in range(len(series)) : 
        serie_path=os.path.join(study_path, series[serie])
        if serie == 0 : 
            images = os.listdir(serie_path) 
            for image in range(len(images)) : 
                image_path = os.path.join(serie_path, images[image])
                os.remove(image_path) 
        else : 
            file_name = os.listdir(serie_path)[0] 
            path_to_dicom_file = os.path.join(serie_path, file_name) 
            os.remove(path_to_dicom_file)

def patients_folder_translation(path_to_patients_folder: str,non_icp_translations=None) -> dict: 
    """
    This method takes a folder of patient and create a dictionnary that associate 
    a patient with the translation that is necessary to register his 2 point cloud in a 
    case of z inverted position. 

    :param path_to_patients_folder : the path of the folder containing all the patients 
    that need a correction 
    :param non_icp_translations: a list of translation vector obtain by another way than icp

    :return : a dictionnary with all the patient as keys and the translation needed as 
    values
    """
    patients = os.listdir(path_to_patients_folder)
    dict_patient_translation = {} 
    dict_paths_of_folder = dict_path_folder_of_patient(path_to_patients_folder) 
    if non_icp_translations != None : 
        for i in range(len(patients[i])) : 
            dict_patient_translation[patients[i]] = non_icp_translations[i]
    else : 
        for i in range(len(dict_paths_of_folder['list_path_series0'])) : 
            path_series0 = dict_paths_of_folder['list_path_series0'][i] 
            path_RTPLAN = dict_paths_of_folder['list_path_RTPLAN'][i] 
            image_cloud = pc.image_point_cloud(path_series0)
            source_cloud = pc.source_point_cloud(path_RTPLAN)
            image_cloud = pc.flip_image_point_cloud(image_cloud)
            translation = icp.icp_translation(image_cloud,source_cloud)
            dict_patient_translation[patients[i]] = translation 
    
    return dict_patient_translation

def dict_path_folder_of_patient(path_to_patients_folder: str) -> dict: 
    """
    This method takes a folder with many patient and put , in a dictionnary, all the series0 and
    the RTPLAN file of patients. Note that we have to have all the CT files in the series0 and the RT 
    plan in the series2.

    :param path_to_patient_folder : The complete path of the folder containing all the patient

    :return : a dictionnary with a key for the path of the series0 of all the patient and a key for the 
    path of the RTPLAN of all the patient. 
    """

    dict_path = {} 
    dict_path['list_path_series0'] = []
    dict_path['list_path_RTPLAN'] = []
    patients = os.listdir(path_to_patients_folder) 
    for patient in range(len(patients)) : 
        path_patient = os.path.join(path_to_patients_folder, patients[patient])
        path_study = os.path.join(path_patient,'study0')
        path_series0 = os.path.join(path_study,'series0')
        path_series2 = os.path.join(path_study,'series2')
        path_RTPLAN = os.path.join(path_series2,'RTPLAN0.dcm')
        dict_path['list_path_series0'] += [path_series0, ]
        dict_path['list_path_RTPLAN'] += [path_RTPLAN, ]
    
    return dict_path



