from cytomine.cytomine import Cytomine
from time import localtime, strftime
import time
import os
import sys
annotation_job_id =34707377 
image_id = 8120497

software_id = 18699052 # Union

#working_path = '/home/deb/Cytomine/tmp' 
working_path = '/data/home/adeblire/tmp' 

conn = Cytomine('beta.cytomine.be', 'd8bee9aa-4d6e-4cb4-a7e8-2d3100f0ba24', 'a3227ede-6ec5-4711-b621-6c14b2f8da45', working_path, base_path = "/api/", verbose = False)

print "Create Job and UserJob..."
image_instance = conn.get_image_instance(image_id)
user_job = conn.addUserJob(software_id, image_instance.project)
#Switch to job Connection
conn.set_credentials(str(user_job.publicKey), str(user_job.privateKey))
job = conn.getJob(user_job.job)
job = conn.update_job_status(job, status_comment = "Create software parameters values...")
#job_parameters_values = conn.add_job_parameters(user_job.job, conn.getSoftware(id_software), pyxit_parameters)
job = conn.update_job_status(job, status = job.RUNNING, progress = 0, status_comment = "Processing...")


union_term= 9444456 # "To classify" term
union_minlength=2 # we consider merging polygons that have at least 20 pixels in common, default=20
union_bufferoverlap=5 # for each polygon, we look in a surrounding region of 5 pixels
union_area=2000
union_minPointForSimplify=10000  #if an annotation has more than x points after union, it will be simplified
union_minPoint=1000 #minimum number of points for simplified annotation
union_maxPoint=3000 #maximum number of points for simplified annotation
union_nbzonesWidth=10 #an image is divided into this number of horizontal grid cells
union_nbzonesHeight=10 #an image is divided into this number of vertical grid cells
print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
print "Union of polygons for job %d and image %d, term: %d, minlength: %d, bufferoverlap: %d, union area: %d" %(job.userJob,image_id,union_term,union_minlength,union_bufferoverlap,union_area)
start = time.time()
unioncommand = "groovy -cp \"union/lib/*\" union/union4.groovy http://%s %s %s %d %d %d %d %d %d %d %d %d %d" %('beta.cytomine.be',KEY , KEY, image_id, annotation_job_id, union_term, union_minlength, union_bufferoverlap, union_minPointForSimplify, union_minPoint, union_maxPoint, union_nbzonesWidth, union_nbzonesHeight)
print unioncommand
os.system(unioncommand)
end = time.time()
print "Elapsed time UNION: %d s" %(end-start)


job = conn.update_job_status(job, status = job.TERMINATED, progress = 100, status_comment =  "Segmentation test job complete")


print "job:", job.userJob
print "image:", image_id

print "END."
sys.exit()
