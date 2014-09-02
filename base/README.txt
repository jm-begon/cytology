src_finale: code online analyse 

pour chaque lame, lancer les scripts suivants:

1) color_dec_segmentation_whole_slide
struct_element le même pour nettoyage et fusion des composantes proches des agrégats
2) area_preclassification.py: encoder id du job de color deconv. paramètres de taille en pixels. annotations récupérées en zoom 0.
3) cluster_segmentation_wholeslide.py: term_to_segment=clusters & agrégats.
(! imread renvoit bgra, à convertir)
otsu_threshold_with_mask: construit vecteur ligne avec tous les pixels appartenant au masque, calcule seuil et iamge seuillée.
calcule enveloppe convexe pour calculer circularité de l'allule générale ()
4) cells classification / cluster classification: 
cells: récupère annotations d'arearclassification et clustersegmentation, à lancer 1 fois pour chaque
remplit pixels n'appartenant pas au masque par du blanc pour correspondre au modele de classification appris sur des images avec blanc autour du masque


!! object_finder: find_contours EXTERNAL
-------------------------------

scripts:

histogram: parcourt un répertoire de cellules individuelles avec un sous-répertoire par image, et un sous-répertoire par terme au sein de chaque image, trace histogrammes des aires, périmètre, circularité, etc. + histogramme moyen de l'intensité niveaux de gris

mean_OD: parcourt répertoire, temp:absorbance en chaque pixel de toute l'image, multiplié par le masque binaire (pour ne pas tenir compte du background), calcule moyenne par rapport au nbre de pixels du masque, puis moyenne pour toutes les images (chaque image pèse pour 1 indépendamment de sa taille pour ne pas favoriser annotations très grandes)

color_deconvolution: cette version retourne les 3 stains (utilisés par les scripts), alors que la version utilisée online utilise une version de color_deconvolution.py qui ne retourne que le stain d'intérêt

cluster_segmentation_inclusions_filling: chaîne de processing de clusters en local
