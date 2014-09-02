#! /usr/bin/env python

import Image
import numpy as np
import os
import math

import time

def deconvolve_im_array(im_array, MOD_vectors):

    #MOD = np.zeros((3,3))
    cos = np.zeros((3,3))
      
    #MOD[0, :] = OD_vector
    MOD = MOD_vectors
    tic = time.time()
    
    # check for alpha mask
    alpha_mask = None
    if (im_array.shape[2] == 4):
        alpha_mask = im_array[:,:,3]
        im_array = im_array[:,:,0:3]

    # normalise vector
    norm = np.sqrt( (MOD**2).sum(axis=1) )
    for i in range(3):
        if (norm[i] != 0.0):
            cos[i, :] = MOD[i, :] / norm[i]
    
    # translation matrix
    if ((cos[1, 0] == 0.0) and (cos[1, 1] == 0.0) and (cos[1, 2] == 0.0)):
        # 2nd colour is unspecified
	    cos[1, 0] = cos[0, 2]
	    cos[1, 1] = cos[0, 0]
	    cos[1, 2] = cos[0, 1]

    if ((cos[2, 0] == 0.0) and (cos[2, 1] == 0.0) and (cos[2, 2] == 0.0)):
        # 3rd colour is unspecified
	    if ((cos[0, 0]**2 + cos[1, 0]**2) > 1):
		    print "Colour_3 has a negative R component."
		    cos[2, 0] = 0.0
	    else:
		    cos[2, 0] = np.sqrt(1.0 - cos[0, 0]**2 - cos[1, 0]**2)

	    if ((cos[0, 1]**2 + cos[1, 1]**2) > 1):
		    print "Colour_3 has a negative G component."
		    cos[2, 1] = 0.0
	    else:
		    cos[2, 1] = np.sqrt(1.0 - cos[0, 1]**2 - cos[1, 1]**2)

	    if ((cos[0, 2]**2 + cos[1, 2]**2) > 1):
		    print "Colour_3 has a negative B component."
		    cos[2, 2] = 0.0
	    else:
		    cos[2, 2] = np.sqrt(1.0 - cos[0, 2]**2 - cos[1, 2]**2)

    leng = np.sqrt( (cos[2, :]**2).sum() )
    if (leng != 0.0):
        cos[2, :] = cos[2, :] / leng

    cos[cos == 0.0] = 0.001

    print cos
    
    # process image array
    M = cos
    D = np.linalg.inv(M)

    log255 = math.log(255.0)
    
    RGB = -255 * np.log((im_array.astype(np.float) + 1) / 255.0) / log255
    C = np.einsum('ijk,kn', RGB, D)
    c = np.exp(-(C - 255.0) * log255 / 255.0)
    c[c>255] = 255
    c[c<0] = 0
    
    stains = []
    for k in range(3):
        stains.append(np.uint8(np.around(255.0 - (  (255.0 - c[:,:,k]).reshape(c[:,:,0].shape+(1,)) * M[k,:].reshape((1,1,3))  )  )))

    # return deconvoluted image with pre existing alpha mask
    if (alpha_mask != None):
        return np.dstack( (stains[0], alpha_mask.astype(np.uint8)) )
    else:
        return stains[0]

def deconvolve_dir(src_dir, dest_dir, OD_vector):
    
    if (src_dir == dest_dir):
        print "src_dir and dest_dir must be different ! ABORTING"
        return
    
    for c in os.listdir(src_dir):
        if (not os.path.exists(os.path.join(dest_dir, c))):
            os.mkdir(os.path.join(dest_dir, c))
        for _file in os.listdir(os.path.join(src_dir, c)):
            try:
                im_src = Image.open(os.path.join(src_dir, c, _file))
                im_src.verify()
            except IOError:
                print "warning filename %s is not an image" % os.path.join(src_dir, c, _file)
            
            im_src = Image.open(os.path.join(src_dir, c, _file))
            #TODO check image type
            
            im_src = np.array(im_src, dtype = np.float)
            print im_src.shape
            im_dest = deconvolve_im_array(im_src, OD_vector)
            
            if (im_dest.shape[2] == 4):
                im_dest = Image.fromarray(im_dest, 'RGBA')
            else:    
                im_dest = Image.fromarray(im_dest, 'RGB')
            
            im_dest.save(os.path.join(dest_dir, c, _file), "PNG")
            
            test = Image.open(os.path.join(dest_dir, c, _file))
            print test.mode

            
if __name__ == "__main__":

    deconvolve_dir("../images/tempo", "../images/tempo2", np.array([10.9504722101427, 255.0, 255.0]))



