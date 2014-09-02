import com.vividsolutions.jts.io.*
import com.vividsolutions.jts.geom.*
import be.cytomine.client.models.*
import be.cytomine.client.*
import be.cytomine.client.collections.*;

int i = 0
def cytomineHost =  args[i++]
def cytominePublicKey = args[i++]
def cytominePrivateKey = args[i++]

def image = args[i++]
def user = args[i++]
def term = args[i++]
def minIntersectLength = Double.parseDouble(args[i++])
def bufferLength = Double.parseDouble(args[i++])

def minPointForSimplify = Long.parseLong(args[i++])
def minPoint = Long.parseLong(args[i++])
def maxPoint = Long.parseLong(args[i++])


println "cytomineHost=$cytomineHost; cytominePublicKey=$cytominePublicKey; cytominePrivateKey=$cytominePrivateKey;"
println "image=$image; user=$user; term=$term; minIntersectLength=$minIntersectLength; bufferLength=$bufferLength;"

Cytomine cytomine = new Cytomine(cytomineHost, cytominePublicKey, cytominePrivateKey, "./");

unionPicture(cytomine,image,user,term,bufferLength,minIntersectLength,minPointForSimplify,minPoint,maxPoint)


public void unionPicture(def cytomine,def image, def user, def term,def bufferLength, def minIntersectLength,def minPointForSimplify,def minPoint,def maxPoint) {
     //makeValidPolygon(image,user)

     //http://localhost:8080/api/algoannotation/union?idImage=8120370&idUser=11974001&idTerm=9444456&minIntersectionLength=10&bufferLength=0&area=2000

    def unionedAnnotation = []

     boolean restart = true

     int max = 100
     while(restart && (max>0)) {
         def result = unionArea(cytomine,image,user,term,bufferLength,minIntersectLength)
         restart = result.restart
         unionedAnnotation.addAll(result.unionedAnnotation)
         max--
     }

    unionedAnnotation.unique()

    println "SIMPLIFY NOW"
    unionedAnnotation.each { idAnnotation ->
        try {
            Annotation based = getAnnotation(cytomine,idAnnotation)

            if(based && new WKTReader().read(based.get('location')).getNumPoints()>minPointForSimplify) {
                println "simplifyAnnotation=" + based.getId()
                cytomine.simplifyAnnotation(idAnnotation,minPoint,maxPoint)
            }

            /*def annotation = AnnotationDomain.getAnnotationDomain(idAnnotation)
            if(annotation && annotation.location.getNumPoints()>10000) {
                println  annotation.id + "=" + annotation.location.getNumPoints()
                def simplified = simplifyGeometryService.simplifyPolygon(annotation.location.toText())
                annotation.location = simplified.geometry
                algoAnnotationService.saveDomain(annotation)
            }*/
        }catch(Exception e) {
            println e
        }
    }
 }


 private def unionArea(def cytomine,def image, def user, def term,def bufferLength, def minIntersectLength) {
     println "unionArea..."
     List intersectAnnotation = intersectAnnotation(cytomine,image,user,term,bufferLength,minIntersectLength)

     println "intersectAnnotation=$intersectAnnotation"
     println intersectAnnotation.size()

     boolean mustBeRestart = false
     def unionedAnnotation = []

     intersectAnnotation.each {
         HashMap<Long, Long> removedByUnion = new HashMap<Long, Long>(1024)

             long idBased = it[0]
             //check if annotation has be deleted (because merge), if true get the union annotation
             if (removedByUnion.containsKey(it[0]))
                 idBased = removedByUnion.get(it[0])

             long idCompared = it[1]
             //check if annotation has be deleted (because merge), if true get the union annotation
             if (removedByUnion.containsKey(it[1]))
                 idCompared = removedByUnion.get(it[1])

             Annotation based
             Annotation compared

             based = getAnnotation(cytomine,idBased)
             compared = getAnnotation(cytomine,idCompared)

             if (based && compared && based.get('id') != compared.get('id')) {
                 mustBeRestart = true

                 basedLocation = new WKTReader().read(based.get('location'))
                 comparedLocation = new WKTReader().read(compared.get('location'))

                 if(bufferLength) {
                     basedLocation = basedLocation.buffer(bufferLength)
                     comparedLocation = comparedLocation.buffer(bufferLength)
                 }

                 basedLocation = combineIntoOneGeometry([basedLocation,comparedLocation])
                 basedLocation = basedLocation.union()

                 if(bufferLength) {
                     basedLocation =  basedLocation.buffer(-bufferLength)
                 }

                 based.set('location',basedLocation.toText())

                 //based.location = simplifyGeometryService.simplifyPolygon(based.location.toText()).geometry
                 //based.location = based.location.union(compared.location)
                 removedByUnion.put(compared.get('id'), based.get('id'))

                 //save new annotation with union location
                 unionedAnnotation << based.get('id')
//                 if(based.get('algoAnnotation')) {
                     //TODO: UPDATE  based
                 println "edit ${based.getId()}"
                 cytomine.editAnnotation(based.getId(),based.get('location'))
                     //algoAnnotationService.saveDomain(based)
                     //remove old annotation with data
                     //TODO: DELETE COMPARED
                 println "delete ${compared.getId()}"
                 cytomine.deleteAnnotation(compared.getId())

//                     AlgoAnnotationTerm.executeUpdate("delete AlgoAnnotationTerm aat where aat.annotationIdent = :annotation", [annotation: compared.id])
//                     algoAnnotationService.removeDomain(compared)
 //                } else {
 //                    algoAnnotationService.saveDomain(based)
 //                    //remove old annotation with data
 //                    AnnotationTerm.executeUpdate("delete AnnotationTerm aat where aat.userAnnotation.id = :annotation", [annotation: compared.id])
 //                    algoAnnotationService.removeDomain(compared)
 //                }
                  println "ok"

             }
     }
     return [restart: mustBeRestart, unionedAnnotation : unionedAnnotation]
 }


//TODO: create getAnnotationDomain

static Annotation getAnnotation(def cytomine, def id) {
     try {
         return cytomine.getAnnotation(id)
     } catch(Exception e) {
         return null
     }
}

static Geometry combineIntoOneGeometry( def geometryCollection ){
     GeometryFactory factory = new GeometryFactory();

     // note the following geometry collection may be invalid (say with overlapping polygons)
     GeometryCollection geometryCollection1 =
          (GeometryCollection) factory.buildGeometry( geometryCollection );

     return geometryCollection1.union();
 }

 private List intersectAnnotation(def cytomine, def image, def user, def term, def bufferLength, def minIntersectLength) {
     def data = []
     println "intersectAnnotation..."

     def filters = [:]
     filters.put("user",user);
     filters.put("image",image);
     filters.put("term",term);
     filters.put("showTerm","true");
     filters.put("showWKT","true");

     AnnotationCollection annotations = cytomine.getAnnotations(filters);

     println "annotations=${annotations.size()}"
     println "annotations=${annotations.toURL()}"

     def annotationsMap = [:]
     for(int i=0;i<annotations.size();i++) {
         def annotation = annotations.get(i)
         annotationsMap.put(annotation.getId(),new WKTReader().read(annotation.get('location')).buffer(bufferLength))
     }

     println "annotationsMap=${annotationsMap.size()}"

     annotationsMap.eachWithIndex { current,indice ->

         def currentGeom = current.value
         if(indice%50==0) {
             println "$indice/${annotationsMap.size()}"
         }
         annotationsMap.each { compared ->
             if(current.key < compared.key) {
                 def comparedGeom = compared.value

                 def intersectGeom = comparedGeom.intersection(currentGeom)
                 if(intersectGeom.getLength()>=minIntersectLength) {
                     data << [compared.key,current.key]
                 }
             }
         }
     }
     data
 }