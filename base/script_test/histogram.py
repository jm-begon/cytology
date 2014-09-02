from __future__ import division
import cytomine

import os
import numpy as np
import math
import cv2

import matplotlib.pyplot as plt

import sys

from colour_deconvolution import *

#working_path = '/data/home/adeblire/tmp'
working_path = '/home/deb/Cytomine/tmp'
#dump_path = '/data/home/adeblire/dump'
dump_path = '/home/deb/TFE/Cluster_segmentation/dump_by_image'
#dump_path = '/home/deb/TFE/Cluster_segmentation/dump_by_image_blue'


#conn = cytomine.Cytomine('beta.cytomine.be', 'd8bee9aa-4d6e-4cb4-a7e8-2d3100f0ba24', 'a3227ede-6ec5-4711-b621-6c14b2f8da45', working_path, base_path = "/api/", verbose = True)




#annotations = conn.getAnnotations(id_project = 716498)
#annotations = conn.dumpAnnotations(annotations = annotations, get_image_url_func = cytomine.models.annotation.Annotation.get_annotation_alpha_crop_url, dest_path = dump_path, excluded_terms =[15109495,15109451,15109489, 15109483] , desired_zoom = 0)

#sys.exit(0)

color_analysis = False

shape_analysis = True



good_images = [
716516,
716522,
716528,
716534,
716547,
719625,
719660,
720965,
722807,
723911,
724858,
727250,
728066,
728391,
728581,
728667,
728675,
728709,
728733,
728744,
728783,
8120331,
8120343,
8120351,
8120370,
8120382,
8120392,
8120400,
8120408,
8120444,
8120497,
8122830,
8123101,
8123768,
8124013,
8124112,
8124821]

bad_images = [
728689,
728717,
728755,
728772,
8122590,
8122730,
8122868]

images = map(str,good_images)

images = os.listdir(dump_path)

cell_ids = ['675999', '933004', '676407', '676434', '676026', '676176', '676210', '676390', '676446']

individual_cell_ids = ['676407', '676434', '676176', '676210', '676390', '676446']

background_ids = ['8844862']
noise_ids = ['8844845']

terms_type = individual_cell_ids

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
                

MOD5 = np.array([[ 75.02805717,  78.44507242,  30.05846927], #blue cells with imageJ
                [ 48.09104103,  62.02717516,  37.36866958], # noise (verifier utilite)
                [  9.17867488,  10.89206473,   5.99225756]]) #background (verifier utilite)
                
                
MOD6 = np.array([[ 54.14126083,  68.8596259,   21.03817318], # from cells no cluster
                [ 48.09104103,  62.02717516,  37.36866958], # noise (verifier utilite)
                [  9.17867488,  10.89206473,   5.99225756]]) #background (verifier utilite)



histograms = np.zeros((1,255))

areas = []
circularities = []
convexities = []


for image in images :

    image_path = os.path.join(dump_path, image)
    
    terms = os.listdir(image_path)
    
    terms = list(set(terms) & set(terms_type))
    

    for t, term in enumerate(terms):

        term_path = os.path.join(image_path, term)

        annotations = os.listdir(term_path)
        
       

	
        for a, annotation in enumerate(annotations) :
        
            

            annotation_path = os.path.join(term_path, annotation)
	
            image = cv2.imread(annotation_path,-1)
            
            if shape_analysis :
            
                ### Shape analysis ###
            
                alpha = np.array(image[:,:,3])
                
                image = np.array(image[:,:,0:3])
                
                
                
                cell_contour, _ = cv2.findContours(alpha,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)              

                perimeter = cv2.arcLength(cell_contour[0],True)
                    
                area = cv2.contourArea(cell_contour[0])
                    
                if (perimeter != 0) and (area != 0):
                
                    circularity = 4*np.pi*area / (perimeter*perimeter)
                
                    convex_hull = cv2.convexHull(cell_contour[0])
                    
                    convex_area = cv2.contourArea(convex_hull)
                    
                    convexity = area / convex_area
                
                    circularities.append(circularity)
                
                    convexities.append(convexity)
                
                    areas.append(area)
                    
                    print area
                    
            
            if color_analysis :
            
                ### Color analysis ###            
            
                image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                       
                image = deconvolve_im_array(image, MOD6)[0]
                
                #HSV
                #image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                #saturation = cv2.split(image)[1]
            
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                
                hist, bins = np.histogram(image, 255,(0,255))
            
                histograms = np.append(histograms, np.array([hist]),0)
                
                
            print annotation_path
            
            
            
            



if color_analysis :

    histograms = np.sum(histograms, 0)
    width = 0.7*(bins[1]-bins[0])
    center = (bins[:-1]+bins[1:])/2
    plt.bar(center, histograms, align = 'center', width = width)
    plt.show()

if shape_analysis :

    
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


   
