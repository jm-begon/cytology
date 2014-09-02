#Effectue un filtrage et une classification par aire des annotations. 


from cytomine.cytomine import Cytomine
from cytomine.models.annotation import AlgoAnnotationTerm

from shapely.wkt import loads

import numpy as np
import socket
import time


job_id = 59008611 #job de colordec segmentation
image_id = 37167157 

working_path = '/data/home/adeblire/tmp' 

cell_max_area = 2000 #aire max en pixel, à changer en m
cell_min_area = 600  #aire min en pixel, à changer en m
cell_min_circularity = 0.7 #circularité min
cluster_min_cell_nb = 3 #nombre minimum de cellules pour constituer un cluster

start_time = time.time()

conn = Cytomine('beta.cytomine.be', 'd8bee9aa-4d6e-4cb4-a7e8-2d3100f0ba24', 'a3227ede-6ec5-4711-b621-6c14b2f8da45', working_path, base_path = "/api/", verbose = False)


print "Create Job and UserJob..."
image_instance = conn.getImageInstance(image_id)
software_id = 18104673
user_job = conn.addUserJob(software_id, image_instance.project)
#Switch to job Connection
conn.set_credentials(str(user_job.publicKey), str(user_job.privateKey))
job = conn.getJob(user_job.job)
job = conn.update_job_status(job, status_comment = "Create software parameters values...")
#job_parameters_values = conn.add_job_parameters(user_job.job, conn.getSoftware(id_software), pyxit_parameters)
job = conn.update_job_status(job, status = job.RUNNING, progress = 0, status_comment = "Loading data...")

print "downloading annotations ..."

dowloaded = False

while (not dowloaded) :
    
    try : 
        
        annotations = conn.get_annotations(id_user = job_id, id_image = image_id, showWKT=True)
        dowloaded = True
        
    except socket.error :
        
        print socket.error
        time.sleep(1)
        
#temps de traitements        
upload_time = 0
classification_time = 0
nb_rejected = 0
nb_cells = 0
nb_aggregates = 0
nb_clusters = 0
nb_annotations = len(annotations.data())

for i, annotation in enumerate(annotations.data()):
   
    print i,"/",nb_annotations
    
    start = time.time()
    
    p = loads(annotation.location)
    
    circularity = 4*np.pi*p.area / (p.length*p.length)
    
    if p.area < cell_min_area : 
        nb_rejected = nb_rejected +1
        continue #noise 
    
    elif cell_min_area <= p.area <= cell_max_area :
     
        if circularity > cell_min_circularity :
        
            predict_term = 15054765 # Cell to classify
            nb_cells = nb_cells + 1
            
            
        else : 
            nb_rejected = nb_rejected +1
            continue #noise 
            
    elif cell_max_area < p.area < cluster_min_cell_nb*cell_max_area : 
        
        predict_term = 28792193 # aggregate to segment
        nb_aggregates = nb_aggregates + 1
    
    else : 
        
        predict_term = 15054705 # Architectural patern to classify
        nb_clusters = nb_clusters + 1
        
    uploaded = False
    
    end = time.time()
    
    classification_time = classification_time + end - start
    
    start = time.time()
    
    while(not uploaded):   
        
        try :
        
            new_annotation = conn.addAnnotation(annotation.location, annotation.image)
            uploaded = True
            
        except socket.error :
            
            print socket.error
            time.sleep(1)
    
    annotated = False
    
    while(not annotated):
    
        try :    
            
            conn.addAnnotationTerm(new_annotation.id, predict_term, predict_term, 1.0, annotation_term_model = AlgoAnnotationTerm)
            annotated = True
        except socket.error :
        
            print socket.error
            time.sleep(1)
            
    end = time.time()
    
    upload_time = upload_time + end - start
            
end_time = time.time()



job = conn.update_job_status(job, status = job.TERMINATED, progress = 100, status_comment =  "job complete")

print "Job : ", job.userJob
print " Image : ", image_id 
print "TOTAL TIME  : ", end_time - start_time, " s"
print "Classification time : ", classification_time, " s"
print "Annotations upload time : ", upload_time, "s"
print "Cells : ", nb_cells
print "Clusters : ", nb_clusters
print "Aggregates : ", nb_aggregates
print "Rejected :", nb_rejected
print "TOTAL : " ,nb_annotations
print "END"

