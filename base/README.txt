src_finale: code online analyse 

pour chaque lame, lancer les scripts suivants:

1) color_dec_segmentation_whole_slide
struct_element le m�me pour nettoyage et fusion des composantes proches des agr�gats
2) area_preclassification.py: encoder id du job de color deconv. param�tres de taille en pixels. annotations r�cup�r�es en zoom 0.
3) cluster_segmentation_wholeslide.py: term_to_segment=clusters & agr�gats.
(! imread renvoit bgra, � convertir)
otsu_threshold_with_mask: construit vecteur ligne avec tous les pixels appartenant au masque, calcule seuil et iamge seuill�e.
calcule enveloppe convexe pour calculer circularit� de l'allule g�n�rale ()
4) cells classification / cluster classification: 
cells: r�cup�re annotations d'arearclassification et clustersegmentation, � lancer 1 fois pour chaque
remplit pixels n'appartenant pas au masque par du blanc pour correspondre au modele de classification appris sur des images avec blanc autour du masque


!! object_finder: find_contours EXTERNAL
-------------------------------

scripts:

histogram: parcourt un r�pertoire de cellules individuelles avec un sous-r�pertoire par image, et un sous-r�pertoire par terme au sein de chaque image, trace histogrammes des aires, p�rim�tre, circularit�, etc. + histogramme moyen de l'intensit� niveaux de gris

mean_OD: parcourt r�pertoire, temp:absorbance en chaque pixel de toute l'image, multipli� par le masque binaire (pour ne pas tenir compte du background), calcule moyenne par rapport au nbre de pixels du masque, puis moyenne pour toutes les images (chaque image p�se pour 1 ind�pendamment de sa taille pour ne pas favoriser annotations tr�s grandes)

color_deconvolution: cette version retourne les 3 stains (utilis�s par les scripts), alors que la version utilis�e online utilise une version de color_deconvolution.py qui ne retourne que le stain d'int�r�t

cluster_segmentation_inclusions_filling: cha�ne de processing de clusters en local
