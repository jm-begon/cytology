from colour_deconvolution import *
from otsu_threshold_with_mask import otsu_threshold_with_mask
import numpy as np
import cv2
import copy

from scipy.ndimage.measurements import label
from scipy.ndimage.filters import maximum_filter, minimum_filter

import sys

import pylab as p

import matplotlib.pyplot as plt

MOD = np.array([[ 56.24850493,  71.98403122,  22.07749587], #purple cells
                [ 48.09104103,  62.02717516,  37.36866958], # noise (verifier utilite)
                [  9.17867488,  10.89206473,   5.99225756]]) #background (verifier utilite)
                
MOD2 = np.array([[ 56.24850493,  71.98403122,  22.07749587], # purple cells
                [ 48.09104103,  62.02717516,  37.36866958], #noise (verifier utilite)
                [ 69.64641874,  73.26343918,  28.26597167]]) #blue cells from find_stain_blue_annotations.py
                
MOD3 = np.array([[ 56.24850493,  71.98403122,  22.07749587], # purple cells
                [ 112.99788,  106.09229,  65.80882], #black noise in blue cells with imageJ
                [ 135.45236,  136.64374,  43.72887]]) #blue cells with imageJ
                
MOD4 = np.array([[ 0,  0,  0], # purple cells
                [ 112.99788,  106.09229,  65.80882], #black noise in blue cells with imageJ
                [ 135.45236,  136.64374,  43.72887]]) #blue cells with imageJ


MOD5 = np.array([[ 75.02805717,  78.44507242,  30.05846927], #blue cells with blue cells sample
                [ 48.09104103,  62.02717516,  37.36866958], # noise (verifier utilite)
                [  9.17867488,  10.89206473,   5.99225756]]) #background (verifier utilite)
                
MOD6 = np.array([[ 54.14126083,  68.8596259,   21.03817318], # from cells no cluster
                [ 48.09104103,  62.02717516,  37.36866958], # noise (verifier utilite)
                [  9.17867488,  10.89206473,   5.99225756]]) #background (verifier utilite)


cell_max_area = 3000
cell_min_area = 300
cell_min_circularity = 0.7

        
border = 7


#deconvolve_dir('./blue_annotations', './blue_annotations_processed', MOD3, 2)

#sys.exit()

dump_path = './dump_by_image'
dump_path = './lol'
#dump_path = './captures'
processed_dump_path = './dump_by_image_processed_with_cluster_seg'
#processed_dump_path = './captures_processed'
processed_dump_path = './inclusions_processed'

illustration_path = "./illustrations"

window_name ='Processing...' 
cv2.namedWindow(window_name)

struct_elem = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
struct_elem_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))



i=0

folders = [
716583,
728791,
728799,
8122696,
8123591,
8124538,
728689,
728717,
728755,
728772,
8122590,
8122730,
8122868,
8123992]

folders = ['716534']
#folders = map(str, folders)

folders = os.listdir(dump_path)

clusters_id = ['676026','677599','933004']
individual_cell_ids = ['676407', '676434', '676176', '676210', '676390', '676446']

individual_cell_without_inclusion_ids = ['676407', '676176', '676446']

term_type = clusters_id

areas = []
circularities = []
convexities = []

for folder in folders:

    folder_path = os.path.join(dump_path, folder)

    subfolders = os.listdir(folder_path)
    
    #subfolders = list(set(subfolders) & set(term_type)) #only clusters
    
    for subfolder in subfolders :
    
        subfolder_path = os.path.join(folder_path, subfolder)    
    
        images = os.listdir(subfolder_path)
        
        
        for image in images :
                    
            image_path = os.path.join(subfolder_path, image)
            
            np_image = cv2.imread(image_path, 1)
            
            dest = illustration_path +"/" + image +"-1-"+"original.png"
            cv2.imwrite(dest, np_image)
            
            temp0 =  cv2.cvtColor(np_image, cv2.COLOR_BGR2RGB)
                   
            im_dec = deconvolve_im_array(temp0, MOD)[0]
            
            illustration_temp =  cv2.cvtColor(im_dec, cv2.COLOR_RGB2BGR)
            dest = illustration_path +"/" + image +"-2-"+ "deconv.png"
            cv2.imwrite(dest, illustration_temp)
            
            #temp2 = deconvolve_im_array(temp0, MOD4)[0]
            
            #temp3 = deconvolve_im_array(temp0, MOD6)[0]
            
            if (False) :
            
                temp = cv2.cvtColor(temp, cv2.COLOR_RGB2HSV)
            
                saturation = cv2.split(temp)[1]
            
                #Global thresholding on saturation, min of otsu thresholds of manual annotations (see find_threshold.py)
                _, binary = cv2.threshold( saturation, 120, 255, cv2.THRESH_BINARY) 
            
                #Adaptative thresholding on saturation
                _, otsu_binary = cv2.threshold( saturation, 128, 255, cv2.THRESH_BINARY| cv2.THRESH_OTSU)
            
            else :
             
                #GRAY#

                #Global thresholding on gray image 
                temp = cv2.cvtColor(im_dec, cv2.COLOR_RGB2GRAY)
                #temp2 = cv2.cvtColor(temp2, cv2.COLOR_RGB2GRAY)
                #temp3 = cv2.cvtColor(temp3, cv2.COLOR_RGB2GRAY)
                
                dest = illustration_path +"/" + image +"-3-"+ "deconv-gray.png"
                cv2.imwrite(dest, temp)
                
                _, binary = cv2.threshold( temp, 120, 255, cv2.THRESH_BINARY_INV)
                #_, binary2 = cv2.threshold( temp2, 100, 255, cv2.THRESH_BINARY_INV)
                #_, binary3 = cv2.threshold( temp3, 150, 255, cv2.THRESH_BINARY_INV)
                
                dest = illustration_path +"/" + image +"-4-"+ "binary.png"
                cv2.imwrite(dest, binary)
            
                #Adaptative thresholding on gray image
                #_, otsu_binary = cv2.threshold( temp, 128, 255, cv2.THRESH_BINARY_INV| cv2.THRESH_OTSU) 

            
            
            #If there is cells, apply otsu thresholding
            #binary = cv2.bitwise_and(binary, otsu_binary)

            binary = cv2.copyMakeBorder(binary, border, border, border, border, cv2.BORDER_REPLICATE)
            #binary2 = cv2.copyMakeBorder(binary2, border, border, border, border, cv2.BORDER_REPLICATE)
            #binary3 = cv2.copyMakeBorder(binary3, border, border, border, border, cv2.BORDER_REPLICATE)
            
            
            #Remove holes in cells in the binary image
            binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,struct_elem, iterations = 1)
            #binary2 = cv2.morphologyEx(binary2,cv2.MORPH_CLOSE,struct_elem, iterations = 1)
            #binary3 = cv2.morphologyEx(binary3,cv2.MORPH_CLOSE,struct_elem, iterations = 1)
            
            #Remove small objects in the binary image
            binary = cv2.morphologyEx(binary,cv2.MORPH_OPEN,struct_elem, iterations = 3)
            #binary2 = cv2.morphologyEx(binary2,cv2.MORPH_OPEN,struct_elem, iterations = 3) 
            #binary3 = cv2.morphologyEx(binary3,cv2.MORPH_OPEN,struct_elem, iterations = 3)  

            
            #Union architectural paterns
            binary = cv2.morphologyEx(binary,cv2.MORPH_CLOSE,struct_elem, iterations = 10)
            #binary2 = cv2.morphologyEx(binary2,cv2.MORPH_CLOSE,struct_elem, iterations = 10)
            #binary3 = cv2.morphologyEx(binary3,cv2.MORPH_CLOSE,struct_elem, iterations = 10)
           
            binary = binary[border:-border, border:-border]
            #binary2 = binary2[border:-border, border:-border]
            #binary3 = binary3[border:-border, border:-border]
            
            dest = illustration_path +"/" + image +"-5-"+ "binary-morph.png"
            cv2.imwrite(dest, binary)
            
            binary_copy = copy.copy(binary)
                           
            contours = cv2.findContours(binary_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(np_image, contours[0], -1, (0,255,0),3 )
            
            #contours2 = cv2.findContours(binary2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.drawContours(np_image, contours2[0], -1, (0,0,255),3 )
            
            #contours3 = cv2.findContours(binary3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.drawContours(np_image, contours3[0], -1, (255,0,0),3 )
            
            
            ## Cluster segmentation ##
            
            
            
            #blur = cv2.GaussianBlur(temp, (9,9), 2)
            
            #blur = cv2.medianBlur(temp, 9)
            
            otsu_threshold, internal_binary = otsu_threshold_with_mask(temp,binary, cv2.THRESH_BINARY_INV)
            
            dest = illustration_path +"/" + image +"-6-"+ "otsu.png"
            cv2.imwrite(dest, internal_binary)
            
            internal_binary_copy = copy.copy(internal_binary)
            
           
            
            contours2, hierarchy = cv2.findContours(internal_binary_copy, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            
            
            
            
            #filling inclusions without filling inter-cell space
        
            mask = np.zeros(internal_binary.shape)
            
            
            
            for i, contour in enumerate(contours2):
                        

            
                if (hierarchy[0, i, 3] != -1): #internal contour
                                        
                    convex_hull = cv2.convexHull(contour)
                
                    convex_area = cv2.contourArea(convex_hull)
                
                    perimeter = cv2.arcLength(convex_hull,True)
                    
                     
                
                    circularity = 4*np.pi*convex_area / (perimeter*perimeter)
                
                    #cv2.drawContours(np_image, contour, -1, (0,255,255), -1)
                    
                    
                    
                    if (convex_area < cell_max_area/10):
                
                        #removing small objects

                        cv2.drawContours(internal_binary, [convex_hull], -1, 255, -1)
                    

                
                    if (convex_area < cell_max_area/2) and (circularity > 0.8):
                
                        #removing potential inclusions
                    
                    
                        cv2.drawContours(internal_binary, [convex_hull], -1, 255, -1)
                        #cv2.drawContours(np_image, [convex_hull], -1, (0,255,255), -1)
            
            
            dest = illustration_path +"/" + image +"-7-"+ "otsu_filled.png"
            cv2.imwrite(dest, internal_binary)
            
            internal_binary = cv2.morphologyEx(internal_binary,cv2.MORPH_CLOSE,struct_elem, iterations = 1)
            
            
            
            internal_binary = cv2.morphologyEx(internal_binary,cv2.MORPH_OPEN,struct_elem, iterations = 2)
            
            dest = illustration_path +"/" + image +"-8-"+ "otsu_filled_morph.png"
            cv2.imwrite(dest, internal_binary)

            
            
            
            
            
            
            dt = cv2.distanceTransform(internal_binary, cv2.cv.CV_DIST_L2, 3)
            
            
            dt = dt[0]
            
            
            

            
            
            dt = ((dt - np.min(dt)) / (np.max(dt) - np.min(dt)) * 255).astype(np.uint8)
            
            #hist, bins = np.histogram(dt, np.max(dt),(0,np.max(dt)))
            
            #width = 0.7*(bins[1]-bins[0])
            #center = (bins[:-1]+bins[1:])/2
            #plt.bar(center, hist, align = 'center', width = width)
            #plt.show()
            
            #_, markers = cv2.threshold( dt, 100, 255, cv2.THRESH_BINARY)
            
            
            
            
            im_dec[internal_binary == 0] = (255,255,255)
            im_dec = cv2.dilate(im_dec,struct_elem)
            
            
            local_min_ind = maximum_filter(dt, (9,9) ) == dt
            
            markers = np.zeros(dt.shape).astype(np.uint8)
            
            markers[local_min_ind] = 255
            
            markers[internal_binary == 0] = 0
            
            markers = cv2.dilate(markers,struct_elem, iterations = 2)
            
            markers = markers.astype(np.int32)
            
            markers, nb_labels = label(markers, np.ones((3,3)))
            
            borders = cv2.dilate(internal_binary,struct_elem, iterations = 1)
            
            markers[borders == 0] = 0
            
            borders = borders - internal_binary
            
            markers[borders == 255] = nb_labels+2
            
            markers = cv2.copyMakeBorder(markers, border, border, border, border, cv2.BORDER_CONSTANT, value = nb_labels+2)
            
            im_dec = cv2.copyMakeBorder(im_dec, border, border, border, border, cv2.BORDER_CONSTANT, value = (255,255,255))
            
            cv2.watershed(im_dec, markers)
            
            markers = markers[border:-border, border:-border]
            
            mask = np.zeros(markers.shape).astype(np.uint8)
                        
            
            for l in range(1,nb_labels + 1) :
                
                mask[markers == l] = 255
                
                #mask = cv2.dilate(mask, struct_elem)
                
                #cv2.imshow('lol', mask)
                #cv2.waitKey(500)
                
                cell_contour, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)              

                perimeter = cv2.arcLength(cell_contour[0],True)
                
                area = cv2.contourArea(cell_contour[0])
                
                
                
                circularity = 4*np.pi*area / (perimeter*perimeter)
                
                convex_hull = cv2.convexHull(cell_contour[0])
                
                convex_perimeter = cv2.arcLength(convex_hull,True)
                
                convex_area = cv2.contourArea(convex_hull)
                
                convexity = area / convex_area

                convex_circularity = 4*np.pi*convex_area / (convex_perimeter*convex_perimeter) 
                
                             
                
                circularities.append(convex_circularity)
                
                convexities.append(convexity)
                
                areas.append(area)
                              
                #print "area =", area
                #print "circularity :", circularity
                #print "convexity :", convexity
                
                if  (cell_min_area < area < cell_max_area) and (convex_circularity > cell_min_circularity) : 
                
                    cv2.drawContours(np_image, [convex_hull], -1, (0,255,0), 1)
                    
                else : 
                
                    cv2.drawContours(np_image, cell_contour[0], -1, (0,0,255), 1)
                    
                
                mask[:,:] = 0
            

            
            #print markers
            
            #markers[ markers == -1] = nb_labels+1
            
            #np_image[markers == -1] = (0,255,255)
            
            
           


            
            #internal_contours = cv2.findContours(internal_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            #cv2.drawContours(np_image, internal_contours[0], -1, (0,255,255),2 )
            
            #markers_contours = cv2.findContours(markers, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            #cv2.drawContours(np_image, markers_contours[0], -1, (0,255,255),3 )
            
            
            #edges = cv2.Canny(edges, otsu_threshold, int(otsu_threshold) / 3)
            
            #edges = cv2.Canny(blur, 50, 50 / 3)
            
            #edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            #cv2.drawContours(edges, contours[0], -1, (0,255,0),3 )
            
            
            

            dir_path = processed_dump_path +"/"+ folder + "/" + subfolder
            
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            
            dest = dir_path +"/" + image
            
            
            
            print i
            print dest

            i = i+1
            cv2.imwrite(dest, np_image)
            
            dest = illustration_path +"/" + image +"-9-"+ "final.png"
            cv2.imwrite(dest, np_image)

if False :

    hist, bins = np.histogram(areas,100)
    width = 0.7*(bins[1]-bins[0])
    center = (bins[:-1]+bins[1:])/2
    plt.bar(center, hist, align = 'center', width = width)
    plt.show()

    hist, bins = np.histogram(circularities,100)
    width = 0.7*(bins[1]-bins[0])
    center = (bins[:-1]+bins[1:])/2
    plt.bar(center, hist, align = 'center', width = width)
    plt.show()

    hist, bins = np.histogram(convexities,100)
    width = 0.7*(bins[1]-bins[0])
    center = (bins[:-1]+bins[1:])/2
    plt.bar(center, hist, align = 'center', width = width)
    plt.show()
            
   
        
        
        
