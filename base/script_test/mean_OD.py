import os
import numpy as np
import math
from PIL import Image

def annotations_mean_OD(dump_path, terms = None, verbose = False):

    log255 = math.log(255)

    if terms :
	    terms = map(str, terms)
    else:
	    terms = os.listdir(dump_path)

    terms_mean_OD = np.zeros((len(terms), 3))

    for t, term in enumerate(terms):

        term_path = os.path.join(dump_path, term)

        annotations = os.listdir(term_path)

        annotations_mean_OD = np.zeros((len(annotations), 3))

        if verbose :

	        print "processing term %s... " % term
	
        for a, annotation in enumerate(annotations) :

	        annotation_path = os.path.join(term_path, annotation)
		
	        pil_image = Image.open(annotation_path)

	        np_image = np.array(pil_image).astype(np.float)

	        mask = np_image[:,:,3] / 255

	        mask_area = np.sum(mask)

	        temp =  (-((255.0*np.log((np_image[:,:,0:3]+1)/255.0))/log255))

	        temp[:,:,0] = temp[:,:,0] * mask
	        temp[:,:,1] = temp[:,:,1] * mask
	        temp[:,:,2] = temp[:,:,2] * mask

	        temp = np.sum(temp, axis = 0)

	        temp = np.sum(temp, axis = 0)

	        mean_OD = temp/mask_area

	        annotations_mean_OD[a,:] = mean_OD

        terms_mean_OD[t,:] = np.mean(annotations_mean_OD, axis = 0)

        if verbose :
	        
	        print 'mean OD of %s =' % term, terms_mean_OD[t,:] #TO DO area weighting ?

    stain = np.mean(terms_mean_OD, axis = 0)

    if verbose :
	    print 'mean OD =', stain

    return stain

if __name__ == "__main__":

    import sys

    annotations_mean_OD(int(sys.argv[1]))
	
