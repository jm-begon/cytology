#classification des clusters

from shapely.geometry.polygon import Polygon
import sys
import cytomine
from cytomine.models import *
from shapely.wkt import loads
import numpy as np
from pyxit.data import build_from_dir
import os
import cv2


import cytomine
import pickle
import socket
import time


image_id = 37167157
job_id = 62531467 # job d'area classification

model_job_data = 2017481
model_filepath = "/tmp/model-thyroid-clusters-artefacts-gray-aug2013.pkl"
term_to_classify = 15054705 #architechtural partern to classify

gray = False

id_software = 933864

print "Opening connection to cytomine server"
conn = cytomine.Cytomine('beta.cytomine.be', 
'd8bee9aa-4d6e-4cb4-a7e8-2d3100f0ba24', 
'a3227ede-6ec5-4711-b621-6c14b2f8da45',
    base_path = '/api/', 
    working_path = '/tmp/', 
    verbose= False)

print "Create Job and UserJob..."
image_instance = conn.getImageInstance(image_id)
user_job = conn.addUserJob(id_software, image_instance.project)

#Switch to job Connection
conn.set_credentials(str(user_job.publicKey), str(user_job.privateKey))

job = conn.getJob(user_job.job)

#job = conn.update_job_status(job, status_comment = "Create software parameters values...")
#job_parameters_values = conn.add_job_parameters(user_job.job, conn.getSoftware(id_software), parameters)

job = conn.update_job_status(job, status = job.RUNNING, progress = 0, status_comment = "Loading data...")

start_time = time.time()

downloaded = False
while (not downloaded) :

    try :

        annotations = conn.get_annotations(id_user = job_id, id_image = image_id, id_term = term_to_classify, showWKT=True)
        downloaded = True

    except socket.error :

        print socket.error
        time.sleep(1)


nb_annotations = len(annotations.data())

folder_name = "./crops" +"-cluster-" +str(job_id) + "/0/"

if not os.path.exists(folder_name):
    os.makedirs(folder_name)




start = time.time()

#Téléchargement et pré traitement des crops d'annotation

annotation_mapping = {}
for i, annotation in enumerate(annotations.data()):
    
    url = annotation.get_annotation_alpha_crop_url(term_to_classify, desired_zoom = 0)
    
    filename = folder_name + str(i) + ".png"

    annotation_mapping[annotation.id] = filename 

    if os.path.exists(filename) : 
        
        print "Downloaded ............. ", i,"/",nb_annotations

        continue

    downloaded = False

    while (not downloaded) :

        try : 

            conn.fetch_url_into_file(url, filename, False, True)

            downloaded = True

        except socket.error:

            print socket.error
          
            time.sleep(1)
    
        except socket.timeout :

            print socket.timeout

            time.sleep(1)
  

    np_image = cv2.imread(filename, -1)
    
    if np_image is not None :
    
        alpha = np.array(np_image[:,:,3])
    
        image = np.array(np_image[:,:,0:3])
    
    else : 
        
        print "reading error"

        continue
    
    image[alpha == 0] = (255,255,255)

    if gray :
	
	image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    cv2.imwrite(filename, image)
    
   
    print "Downloaded ............. ", i,"/",nb_annotations
    
download_time = time.time() - start
   

#Classification des crops

print "Building attributes from ", os.path.dirname(os.path.dirname(folder_name))

start = time.time()
X, y = build_from_dir(os.path.dirname(os.path.dirname(folder_name)))
extraction_time = time.time() - start


fp = open(model_filepath, "r")

start = time.time()

classes = pickle.load(fp)
pyxit = pickle.load(fp)

y_proba = pyxit.predict_proba(X)
y_predict = classes.take(np.argmax(y_proba, axis=1), axis=0)
y_rate = np.max(y_proba, axis=1)

prediction_time = time.time() - start

job = conn.update_job_status(job, status = job.RUNNING, progress = 95, status_comment =  "Publishing results...")


start = time.time()

#Upload des annotations

for k, annotation in enumerate(annotations.data()) :
    
    print k


    filename = annotation_mapping[annotation.id]
    
    j = np.where(X == filename)[0][0]

    uploaded = False

    while (not uploaded) : 
        
        try : 

            new_annotation = conn.addAnnotation(annotation.location, image_id)
          
            uploaded = True

        except socket.error : 

            print socket.error

            time.sleep(1)
        except socket.timeout :

            print socket.timeout

            time.sleep(1)


            
    if new_annotation:

        annotated = False
        
        while(not annotated):
            
            try :

                conn.addAnnotationTerm(new_annotation.id, int(y_predict[j]), int(y_predict[j]), y_rate[j], annotation_term_model = AlgoAnnotationTerm)

                annotated = True

            except socket.error :
         
                print socket.error
         
                time.sleep(1)
            except socket.timeout :

                print socket.timeout

                time.sleep(1)

upload_time = time.time() - start

end_time = time.time()

job = conn.update_job_status(job, status = job.TERMINATED, progress = 100, status_comment =  "Finish Job..")

print "number of annotations : ", nb_annotations
print "TOTAL time : ", end_time - start_time, " s"
print "download time : ", download_time, " s"
print "extraction time : ", extraction_time, " s"
print "prediction time : ", prediction_time, "s"
print "upload time : ", upload_time, " s"
print "job : ", job.userJob
print "image : ", image_id
 




