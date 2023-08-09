import file_and_folder_corrector
import utils.cloud_creator as cc
import Iterative_closest_point as icp
import folder_of_patient_info_extractor as fopie
import utils.visualization_of_point_cloud as vis

#Correction of one patient with the ICP algorithm
path_main_directory = r'C:\Users\user_name\container_of_project\project_location\project_name'
path_destination = r'C:\Users\jonat\new_location'
patient_path = r'C:\Users\user_name\container_of_project\project_location\project_name\patient' 
patient_series0_path = r'C:\Users\user_name\container_of_project\project_location\project_name\patient\study0\series_for_image' 
patient_rtplan_path = r'C:\Users\user_name\container_of_project\project_location\project_name\patient\study0\series_for_rtplan\RTPLAN0.dcm' 

#if the translation is already known, those 4 lines are not necessary
image_point_cloud = cc.create_image_point_cloud_from_dicom_series_folder(patient_series0_path) 
source_point_cloud = cc.create_source_point_cloud_from_rtplan(patient_rtplan_path) 
inverse_image_point_cloud = cc.z_flip_image_point_cloud(image_point_cloud) 
translation = icp.determine_icp_translation(inverse_image_point_cloud, source_point_cloud)

file_and_folder_corrector.patient_corrector(path_main_directory,patient_path, path_destination, translation[0][0], translation[1][0], translation[2][0],'CorrectedPatient')

#To verify that the point cloud are align
transform_image_point_cloud = icp.apply_transformation_on_image_cloud(image_point_cloud, source_point_cloud)
vis.visualization_of_superposed_point_cloud(transform_image_point_cloud, source_point_cloud, 'Image Point Cloud', 'Source Point Cloud')



#Correction of a folder of patient with the icp algorithm
folder_of_patient_path = r'C:\Users\user_name\container_of_project\project_location\project_name\folder_of_patient' 
patients_translations = fopie.obtain_translations_from_patients_folder(folder_of_patient_path) 

file_and_folder_corrector.patient_folder_corrector(path_main_directory, path_destination, folder_of_patient_path, patients_translations)

#Correction of a folder of patient with known translation
list_of_translation = [] #of course, in reality, this list is not empty 
patients_translations = fopie.obtain_translations_from_patients_folder(folder_of_patient_path, list_of_translation) 

file_and_folder_corrector.patient_folder_corrector(path_main_directory, path_destination,folder_of_patient_path, patients_translations)