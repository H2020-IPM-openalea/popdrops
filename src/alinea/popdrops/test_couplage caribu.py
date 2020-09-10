from alinea.caribu.CaribuScene import CaribuScene as cs
from openalea.plantgl import *
from alinea.pdfDrops.pesticide import *

s = [Sphere() for i in range(2)]
m = [Material(Color3(150,0,0)), Material(Color3(100,150,0))]
s = [Translated(-5,0,0,s[0]),Translated(-3,0,1,s[1])]
shapes = [Shape(sp,m[i]) for i,sp in enumerate(s)]
scene = Scene(shapes) #scene is a lis of shapes with id

caribu=cs()

#caribu.setLigth(1,0,0,-1)
t = Tesselator()
ids = caribu.add_Shapes(scene,t) # ids is dict key = scene id, value = caribu id

caribu.run()

eiInf = caribu.getOutput('EiInf')
eiSup = caribu.getOutput('EiSup')
area = caribu.getOutput('Area')

frac = (eiInf + eiSup) * area





