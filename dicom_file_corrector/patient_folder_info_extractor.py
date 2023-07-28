import os
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

def file_paths_from_patient_folder(path_to_patient: str) -> dict:
    """
    This method extract the path of every file in a patient folder 

    :param path_to_patient : the path leading to the patient

    :return : a dictionnary associating the title of the file as keys and the
    path to it as value 
    """   
    study = os.listdir(path_to_patient)[0]
    path_to_study = os.path.join(path_to_patient, study)   
    series = os.listdir(path_to_study)
    path_series0 = os.path.join(path_to_study, series[0])
    path_series1=os.path.join(path_to_study, series[1])
    path_series2=os.path.join(path_to_study, series[2])
    path_series3=os.path.join(path_to_study, series[3])
    rtdose = os.listdir(path_series1)[0]
    path_rtdose = os.path.join(path_series1, rtdose)
    rtplan = os.listdir(path_series2)[0]
    path_rtplan = os.path.join(path_series2, rtplan)
    rtstru = os.listdir(path_series3)[0]
    path_rtstruct = os.path.join(path_series3, rtstru)
    return {series[0]:path_series0, rtdose:path_rtdose, rtplan:path_rtplan, rtstru: path_rtstruct}

def series_paths_from_patient_folder(path_to_patient: str) -> dict:
    """
    This method extract the path of every series in a patient folder 

    :param path_to_patient : the path leading to the patient

    :return : a dictionnary associating a title of the path as keys and the
    path to ithe serie as value 
    """   
    study = os.listdir(path_to_patient)[0]
    path_to_study = os.path.join(path_to_patient, study)   
    series = os.listdir(path_to_study)
    path_series0 = os.path.join(path_to_study, series[0])
    path_series1=os.path.join(path_to_study, series[1])
    path_series2=os.path.join(path_to_study, series[2])
    path_series3=os.path.join(path_to_study, series[3])
    return {'Path_to_series0':path_series0, 'Path_to_series1':path_series1, 'Path_to_series2':path_series2,'Path_to_series3':path_series3}
