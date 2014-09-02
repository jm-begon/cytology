
try:
    import Image, ImageStat
except:
    from PIL import Image, ImageStat
    
import sys


import time
from time import localtime, strftime

from cytomine.cytomine import Cytomine
from cytomine.models.annotation import AlgoAnnotationTerm
from cytomine_utilities.reader import Bounds, CytomineReader
from cytomine_utilities.wholeslide import WholeSlide
from cytomine_utilities.objectfinder import ObjectFinder
from cytomine_utilities.utils import Utils
import os
import numpy as np
import cv, cv2
from colour_deconvolution import deconvolve_im_array
import socket
from shapely.wkt import loads

#working_path = '/home/deb/Cytomine/tmp' 
working_path = '/data/home/adeblire/tmp' 

image_id = 37167157  #37167109 #37167205 #37167288 #728799 #8120497  # 8123101 8123591 8120392  728755 728783 8120370
software_id = 9432223
predict_term = 9444456 # "To Classify" term
size_zone = 4096

#PARAMETERS
zoom = 1
MOD = np.array([[ 56.24850493,  71.98403122,  22.07749587],
                [ 48.09104103,  62.02717516,  37.36866958],
                [  9.17867488,  10.89206473,   5.99225756]])
                

struct_elem = np.array( [[0, 0, 1, 1, 1, 1, 1, 0, 0],
 			 [0, 1, 1, 1, 1, 1, 1, 1, 0],
 			 [1, 1, 1, 1, 1, 1, 1, 1, 1],
 			 [1, 1, 1, 1, 1, 1, 1, 1, 1],
 			 [1, 1, 1, 1, 1, 1, 1, 1, 1],
 			 [1, 1, 1, 1, 1, 1, 1, 1, 1],
 			 [1, 1, 1, 1, 1, 1, 1, 1, 1],
 			 [0, 1, 1, 1, 1, 1, 1, 1, 0],
 			 [0, 0, 1, 1, 1, 1, 1, 0, 0]], dtype = np.uint8)

struct_elem = np.array( [[0, 0, 1, 1, 1, 0, 0],
                         [0, 1, 1, 1, 1, 1, 0],
                         [1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1],
                         [0, 1, 1, 1, 1, 1, 0],
                         [0, 0, 1, 1, 1, 0, 0],], dtype = np.uint8)


#struct_elem = np.array( [[0, 1, 1, 1, 0],
#                         [1, 1, 1, 1, 1],
#                         [1, 1, 1, 1, 1],
#                         [1, 1, 1, 1, 1],
#                         [0, 1, 1, 1, 0]], dtype = np.uint8)

#struct_elem = np.array( [[0, 1, 0],
#                         [1, 1, 1],
#                         [0, 1, 0]], dtype = np.uint8)


#struct_elem = cv2.getStructuringElement(cv2.MORPH_CROSS,(9,9))

start_time = time.time()

conn = Cytomine('beta.cytomine.be', 'd8bee9aa-4d6e-4cb4-a7e8-2d3100f0ba24', 'a3227ede-6ec5-4711-b621-6c14b2f8da45', working_path, base_path = "/api/", verbose = True)

print "Create Job and UserJob..."
image_instance = conn.get_image_instance(image_id)

image_height = image_instance.height
image_width = image_instance.width

user_job = conn.add_user_job(software_id, image_instance.project)
#Switch to job Connection
conn.set_credentials(str(user_job.publicKey), str(user_job.privateKey))
job = conn.get_job(user_job.job)
job = conn.update_job_status(job, status_comment = "Create software parameters values...")
#job_parameters_values = conn.add_job_parameters(user_job.job, conn.getSoftware(id_software), pyxit_parameters)
job = conn.update_job_status(job, status = job.RUNNING, progress = 0, status_comment = "Loading data...")


print "Connecting to Cytomine server"
whole_slide = WholeSlide(conn.get_image_instance(image_id, True))
print "Done"

download_time = 0
colordec_time = 0
contour_time = 0
upload_time = 0

#Initiate the reader object which browse the whole slide image with tiles of size tile_size
reader = CytomineReader(conn, whole_slide, window_position = Bounds(0,0, size_zone, size_zone), zoom = zoom, overlap = 0)

cv_image = cv.CreateImageHeader((reader.window_position.width, reader.window_position.height), cv.IPL_DEPTH_8U, 1)

wsi=0

geometries = []

k = 0

while True:
    
    start = time.time()
    #if wsi == 1 : break
    #browse the whole slide imagefrom client.cytomine import Cytomine
    read = False
    while (not read) :
        print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
        try : 

            reader.read(async = False)
            read = True    
        except socket.error :
	
	    print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
            print socket.error
            time.sleep(1)
            continue  

        except socket.timeout :

            print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
            print socket.timeout
            time.sleep(1)
            continue

    download_time = download_time + time.time() - start

    image = reader.data # image rgb
    
    #Get statistics about the current tile
    posx,posy,poswidth,posheight = reader.window_position.x, reader.window_position.y, reader.window_position.width,reader.window_position.height
#    print "Tile zoom: %d posx: %d posy: %d poswidth: %d posheight: %d" % (zoom, posx, posy, poswidth, posheight)
    tilemean = ImageStat.Stat(image).mean
#    print "Tile mean pixel values: %d %d %d" % (tilemean[0],tilemean[1],tilemean[2])
    tilevar = ImageStat.Stat(image).var
#    print "Tile variance pixel values: %d %d %d" % (tilevar[0],tilevar[1],tilevar[2])
    tilestddev = ImageStat.Stat(image).stddev
#    print "Tile stddev pixel values: %d %d %d" % (tilestddev[0],tilestddev[1],tilestddev[2])   
    extrema = ImageStat.Stat(image).extrema
#    print extrema
#    print "extrema: min R:%d G:%d B:%d" % (extrema[0][0],extrema[1][0],extrema[2][0])

    #Criteria to determine if tile is empty is specific to this H&E application
    #if (tilemean[0] > 215) and (tilemean[1] > 215) and (tilemean[2] > 215):
    #if (extrema[0][0] > 100) or (extrema[1][0] > 100) or (extrema[2][0] > 100):
    if (tilestddev[0] < 10) and (tilestddev[1] < 10) and (tilestddev[2] < 10):
        print "Tile empty"
    else:
        #This tile is not empty, we process it
        #posx,posy,poswidth,posheight = reader.window_position.x, reader.window_position.y, reader.window_position.width,reader.window_position.height
        #print "Tile zoom: %d posx: %d posy: %d poswidth: %d posheight: %d" % (zoom, posx, posy, poswidth, posheight)
        
        
        image = np.array(image)
        
        start = time.time()
        #Colourdeconvolution
        image = deconvolve_im_array(image, MOD)
        colordec_time = colordec_time + time.time() - start

        #Static thresholding on the gray image
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold( image, 120, 255, cv2.THRESH_BINARY_INV)
        
        #Remove holes in cells in the binary image
        binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,struct_elem, iterations = 1)
        
        #Remove small objects in the binary image
        binary = cv2.morphologyEx(binary,cv2.MORPH_OPEN,struct_elem, iterations = 3) 
        
        #Union architectural paterns
        binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,struct_elem, iterations = 7) # /2 for zoom 2
        #binary = cv2.dilate(binary, struct_elem, iterations = 10)
        #binary = cv2.erode(binary, struct_elem, iterations = 10)

        #binary = cv2.dilate(binary,struct_elem)
	
        cv.SetData(cv_image, binary.tostring())
        
        start = time.time()
        #Convert and transfer annotations
        components = ObjectFinder(cv_image).find_components()
        components = whole_slide.convert_to_real_coordinates(whole_slide, components, reader.window_position, reader.zoom)
        geometries.extend(Utils().get_geometries(components))
        
        contour_time = contour_time + time.time() - start
        
        
        
        print "Uploading annotations..."
        print "Number of geometries: %d" % len(geometries)
        
        start = time.time()
        for geometry in geometries:
            
           
            p = loads(geometry)
            
            minx, miny, maxx, maxy = int(p.bounds[0]), int(p.bounds[1]), int(p.bounds[2]), int(p.bounds[3])
            
            if maxx > image_width or maxy > image_height : continue #out of image
             
            k = k + 1            
 
            uploaded = False
            while(not uploaded) :
                try : 
                    print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
                    print "Uploading geometry %s" % geometry
                    annotation = conn.add_annotation(geometry, image_id)
                    uploaded = True
                except socket.error : 
                    print socket.error
                    time.sleep(1)
                    
                except socket.timeout :
     
                    print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
                    print socket.timeout
                    time.sleep(1)
                    continue

                #print annotation
                if annotation:
                    annotated = False
                    while(not annotated):
                        try :
                            conn.add_annotation_term(annotation.id, predict_term, predict_term, 1.0, annotation_term_model = AlgoAnnotationTerm)
                            annotated = True
                        except socket.error : 
                            print socket.error
                            time.sleep(1)
                        except socket.timeout :

                            print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())
                            print socket.timeout
                            time.sleep(1)
                            continue

        geometries = []
        upload_time = upload_time + time.time() - start
    wsi+=1
    print "Number of zones processed: %d " % wsi
    #if wsi == 1: break
    if not reader.next(): break #end of browsing the whole slide


#As we used tiles, some regions are probably broken, we use union to merge them

print "TIME : %s" %strftime("%Y-%m-%d %H:%M:%S", localtime())

union_term=predict_term # "To classify" term
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
start_union = time.time()
unioncommand = "groovy -cp \"union/lib/*\" union/union4.groovy http://%s %s %s %d %d %d %d %d %d %d %d %d %d" %('beta.cytomine.be', user_job.publicKey, user_job.privateKey, image_id, job.userJob, union_term, union_minlength, union_bufferoverlap, union_minPointForSimplify, union_minPoint, union_maxPoint, union_nbzonesWidth, union_nbzonesHeight)
print unioncommand
os.system(unioncommand)
end_union = time.time()
print "Elapsed time UNION: %d s" %(end_union-start_union)


job = conn.update_job_status(job, status = job.TERMINATED, progress = 100, status_comment =  "Segmentation test job complete")
end_time = time.time()
print "Elapsed time SEGMENTATION: %d s" %(end_time-start_time)
print "download time : ", download_time, " s"
print "colordec time : ", colordec_time, " s"
print "contour time : ", contour_time, " s"
print "upload time : ", upload_time, " s"
print "number of ROI : ", k
print "job:", job.userJob
print "image:", image_id

print "END."


sys.exit()	








	




