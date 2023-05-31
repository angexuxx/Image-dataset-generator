import bpy
import math
import os
import random
import csv
import numpy as np
from numpy import dot,arccos,rad2deg,arctan2
from numpy.linalg import norm
from math import pi

import bmesh
from mathutils.bvhtree import BVHTree
#from fpdf import FPDF
#from PIL import Image
import time
import sys
from mathutils import Euler
from numpy.random import choice
import uuid

def randomcolor (mat):   #assigning random color
        mat.use_nodes = True
        nodes=mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)
            
        node_output = nodes.new(type='ShaderNodeOutputMaterial')
        node_input = nodes.new(type='ShaderNodeBsdfDiffuse') 
        node_input.inputs[0].default_value = (random.uniform(0.2,0.8),random.uniform(0.2,0.8),random.uniform(0.2,0.8),1)
        node_input.inputs[1].default_value =  random.uniform(0.3,0.7)
        links = mat.node_tree.links 
        links.new(node_output.inputs[0],node_input.outputs[0])
        
        

def spherical(vector):
    rotation = 0.0 if vector[0]==0 else arctan2(vector[1],vector[0])*180/pi
    inclination = arccos(vector[2]/norm(vector))*180/pi
    inclination = 90-inclination
    return round(rotation),round(inclination) 

#check objects that are intersecting
def intersection_check(obj_now,objects_meshes):
    intersection=False
    #check every object for intersection with every other object
    
    for obj_next in range(len(objects_meshes)):
    
        if obj_now == obj_next:
            continue
        #create bmesh objects
        bm1 = bmesh.new()
        bm2 = bmesh.new()

        #fill bmesh data from objects
        bm1.from_mesh(objects_meshes[obj_now].data)
        bm2.from_mesh(objects_meshes[obj_next].data)            

        bm1.transform(objects_meshes[obj_now].matrix_world)
        bm2.transform(objects_meshes[obj_next].matrix_world) 

        #make BVH tree from BMesh of objects
        obj_now_BVHtree = BVHTree.FromBMesh(bm1)
        obj_next_BVHtree = BVHTree.FromBMesh(bm2)           

        #get intersecting pairs
        inter = obj_now_BVHtree.overlap(obj_next_BVHtree)
        #print(inter)

        #if list is empty, no objects are touching
        if inter != []:
            #print("Object "+str(obj_now) + " and Object " + str(obj_next) + " are touching!")
            intersection=True
            break
       
        
    return intersection

name = ['Circle','Zero','Camara','Plano','Suelo','Cilindro','Curva','Modificadores','Highrise_1.004','Highrise_2.004','Highrise_3.004','Highrise_4.004','Highrise_5.004','Highrise_6.004','Highrise_7.004','Highrise_8.004','Highrise_9.004','Highrise_10.004','Highrise_11.004','Highrise_12.004','Highrise_13.004','Highrise_14.004','Highrise_15.004','Highrise_16.004','Highrise_17.004','Highrise_18.004','Highrise_19.004']# Name to be excluded 
meshnot = ['Circle','Zero','Camara','Plano','Suelo','Cilindro','Curva','Modificadores','Highrise_1.004','Highrise_2.004','Highrise_3.004','Highrise_4.004','Highrise_5.004','Highrise_6.004','Highrise_7.004','Highrise_8.004','Highrise_9.004','Highrise_10.004','Highrise_11.004','Highrise_12.004','Highrise_13.004','Highrise_14.004','Highrise_15.004','Highrise_16.004','Highrise_17.004','Highrise_18.004','Highrise_19.004']
matnot = ['CubeM','FlatM','M1','M2','M3','M4','M5','M6','M7','M8','M9','M10','M11','M12','M13','M14','M15','M16','M17','M18','M19','balcony','capa','capa1','terrado','Material']

typeObjects=["04468005",
"03991062",
"03790512",
"03710193",
"02958343",
"02924116"]

outputdataset = 'D:\\outputdataset'
shapenet='D:\\ShapeNetCore.v2'


csvfilewrite='datasetdetail.csv'


numIter=1
cameraIter=1
lightIter=10

obcounter=0


print('************************************file writer*********************')
csvfile  = open(os.path.join(outputdataset,csvfilewrite), "a", newline='') 
#filewriter = csv.writer(csvfile, dialect = 'excel')  

for numofobjects in [1]:
    print('================= num of objects: {} ========================='.format(numofobjects)) 
    
    for iter in range(numIter):
        
        objects = []
        file_location = []
        file_exist = []
        shapenet_class = []
        shapenet_subclass = []
     
        start = time.time()
       
        print('**************************deleting scene*************************')
        bpy.context.scene.use_nodes = True
        to_remove = [block for block in bpy.data.objects if (block.type == 'MESH' and block.name not in name)]
        to_remove=[]
        for block in to_remove:
            #block.user_clear()
            bpy.data.objects.remove(block,do_unlink=True)
        
        print('----------deleted objects------------')
        
        
        to_remove = [block for block in bpy.data.meshes if block.name not in meshnot]
        to_remove=[]
        for block in to_remove:
            #block.user_clear()
            bpy.data.meshes.remove(block,do_unlink=True)
            
        
        print('----------deleted meshes------------')

        to_remove = [block for block in bpy.data.materials  if block.name not in matnot]
        to_remove=[]
        for block in to_remove:
            #block.user_clear()
            bpy.data.materials.remove(block,do_unlink=True)
            
        

        print('----------deleted material------------')

        to_remove = [block for block in bpy.data.textures]
        to_remove=[]
        for block in to_remove:
            #block.user_clear()
            bpy.data.textures.remove(block,do_unlink=True)
            
        

        print('----------deleted texture------------')

        to_remove = [block for block in bpy.data.images]
        to_remove=[]
        for block in to_remove:
            #block.user_clear()
            bpy.data.images.remove(block,do_unlink=True)
        

        
        print('*******************object loaded************************')       
        object_location = []
        objects_meshes = []
        meshes=[]
        cases = []
    
        scene=bpy.context.scene
    
        print('*******************Selecting random background************************')
            
        cubeM = bpy.data.materials['CubeM']
        flatM = bpy.data.materials['FlatM']
        
        
        scene = bpy.data.scenes["Scene"]
 
        floor_dir='D:\\Images' 
        temperature=0
        camera=bpy.data.objects['Camera']
       
     
        intervals=[0,1,2,2,2]
        
        for iter in range(numIter):
            
            interval=random.choice(intervals)
            
            if interval==0:
                temperature=random.randrange(3500,6000,100)
            elif interval==1:
                temperature=random.randrange(6000,10000,100)
            elif interval==2:
                temperature=random.randrange(10000,13200,200)
                
            bpy.context.view_layer.objects.active = camera
            bpy.context.active_object.select_set(state=True)
            camara.constraints["Seguir trayectoria"].offset_factor = random.randrange(0.0,1.0,0.05)
            
            bpy.context.view_layer.update()
            
            floor_images=random.choice([x[2] for x in os.walk(floor_dir)][0])
            floor_path=os.path.join(floor_dir,floor_images)
        
            
            floor_image=bpy.data.images.load(floor_path)
            floor_name=os.path.basename(floor_path)[:3]
            
            
            
            cubemat=bpy.data.objects['Cilindro'].material_slots[0].material
            flatmat=bpy.data.objects['Suelo'].material_slots[0].material
            
            cubeM.node_tree.nodes['BSDF Difuso'].inputs[1].default_value = random.uniform(0.3,0.7)
            
            cubeM.node_tree.nodes["Cuerpo negro"].inputs[0].default_value = temperature
            #cubeM.node_tree.nodes["Cuerpo negro"].inputs[0].default_value = 9000
            
            flatM.node_tree.nodes['BSDF Difuso'].inputs[1].default_value = random.uniform(0.3,0.7)
            flatmat.node_tree.nodes['Imagen'].image=floor_image
                
            print('***********************setting the light**********************')

            
            L1=bpy.data.lights["Area"]
            
            #changing lights strength can be done here
            L1_Location = random.randrange(300,350,10)/10.0 
            L1_Intensity=0.0
            bpy.data.objects["Area"].location[2] = L1_Location
           
            L1_Intensity=random.randrange(900,950,5)
           
            #L1_Temprature=random.randrange(2000,6500,100)
            L1_Temprature=5500
            
            L1.node_tree.nodes["Emission"].inputs[1].default_value=L1_Intensity
            L1.node_tree.nodes["Cuerpo negro"].inputs[0].default_value=L1_Temprature
            
            
            #Image1
            L1.cycles.cast_shadow=True

            print('*************moving camera and lights********************')
             #camera
            
            CameraPosition=str(camara.location[0])+str(camara.location[1])+'-'+str(camara.location[2])
            
            Zero=bpy.data.objects["Zero"]
            Zero1=bpy.data.objects["Zero1"]
            light = bpy.data.objects['Area']
           
            
            CameraRotationX=random.randrange(80,90.0,5.0)
            CameraRotationY=0.0
            CameraRotationZ=0.0
            
            CameraRotation  = str(CameraRotationX)+'_'+ str(CameraRotationY)+'_'+str(CameraRotationZ)
            Zero1.rotation_euler=(math.radians(CameraRotationX),math.radians(CameraRotationY),math.radians(CameraRotationZ))

            ini=0
            fi=36
          
            
            for j in range(lightIter):  
                
                LightRotationZ=random.randrange(ini,fi,5)
                
                ini=fi
                fi+=36
                LightRotationX=random.randrange(0.0,50.0,5.0)
        
                LightRotationY=0.0
                
                Zero.rotation_euler=(math.radians(LightRotationX),math.radians(LightRotationY),math.radians(LightRotationZ))
                
                cameraPosition=bpy.data.objects['Camera'].matrix_world.to_translation()
                centerPosition=bpy.data.objects['Zero1'].matrix_world.to_translation()
                lightPosition=bpy.data.objects['Area'].matrix_world.to_translation()
                lightPosition1[2]=0
                vc=cameraPosition-centerPosition
                vl=lightPosition-centerPosition
                vl1=lightPosition1-centerPosition
                
                cos=(vc[0]*vl[0]+vc[1]*vl[1])/(sqrt(vc[0]**2+vc[1]**2)*sqrt(vl[0]**2+vl[1]**2))
                pan=int(math.degrees(math.acos(cos)))
                
                cos=(vl[0]*vl1[0]+vl[1]*vl1[1]+vl[2]*vl1[2])/(sqrt(vl[0]**2+vl[1]**2+vl[2]**2)*sqrt(vl1[0]**2+vl1[1]**2+vl1[2]**2))
                tilt=int(math.degrees(acos(cos)))
              
                bpy.context.view_layer.update()
                
                #identifier=object_name+'_'+background_name+'_'+str(rotation)+'_'+str(inclination)+'_'+str(L1_Temprature)
                identifier= '{:05d}'.format(obcounter)+"_"+floor_name+'_'+str(pan)+'_'+str(tilt)+'_'+str(L1_Temprature)
                scene.node_tree.nodes['Img'].file_slots[0].path=os.path.join('\\'+identifier+'_#')
                scene.node_tree.nodes['Sha'].file_slots[0].path=os.path.join('\\'+identifier+'_#')
                scene.node_tree.nodes['Ref'].file_slots[0].path=os.path.join('\\'+identifier+'_#')
                
               
                bpy.ops.render.render(use_viewport=True)
                
                
                #filewriter.writerow([identifier, shapenet_class,shapenet_subclass,background_name,floor_name,object_location,str(L1_Intensity),str(L1_Temprature),str(L1_Location),LightRotation,wall,str(wallRotationZ),CameraRotation])
            obcounter+=1
        end = time.time()
        print('***********************************************')
        print(end-start)
        print('***********************************************')  
                    
            



