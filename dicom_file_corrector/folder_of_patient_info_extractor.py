import os 
import utils.cloud_creator as cc 
import Iterative_closest_point as icp
import numpy as np


def obtain_translations_from_patients_folder(path_to_patients_folder: str, non_icp_translations = None) -> dict: 
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
    dict_paths_of_folder = create_dict_of_path_from_folder_of_patient(path_to_patients_folder) 
    if non_icp_translations != None : 
        for i in range(len(patients[i])) : 
            non_icp_translations = np.reshape(non_icp_translations, (3,1))
            dict_patient_translation[patients[i]] = non_icp_translations[i]
    else : 
        for i in range(len(dict_paths_of_folder['list_path_series0'])) : 
            path_series0 = dict_paths_of_folder['list_path_series0'][i] 
            path_RTPLAN = dict_paths_of_folder['list_path_RTPLAN'][i] 
            image_cloud = cc.create_image_point_cloud_from_dicom_series_folder(path_series0)
            source_cloud = cc.create_source_point_cloud_from_rtplan(path_RTPLAN)
            image_cloud = cc.z_flip_image_point_cloud(image_cloud)
            translation = icp.determine_icp_translation(image_cloud, source_cloud)
            dict_patient_translation[patients[i]] = translation 

    return dict_patient_translation

def create_dict_of_path_from_folder_of_patient(path_to_patients_folder: str) -> dict: 
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
        path_study = os.path.join(path_patient, 'study0')
        path_series0 = os.path.join(path_study, 'series0')
        path_series2 = os.path.join(path_study, 'series2')
        path_RTPLAN = os.path.join(path_series2, 'RTPLAN0.dcm')
        dict_path['list_path_series0'] += [path_series0, ]
        dict_path['list_path_RTPLAN'] += [path_RTPLAN, ]

    return dict_path
