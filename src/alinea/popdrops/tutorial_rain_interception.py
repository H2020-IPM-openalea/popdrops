from alinea.echap.wheat_mtg import adel_mtg
from alinea.astk.caribu_interface import turtle_interception
from alinea.astk.plantgl_utils import get_area_and_normal



#from alinea.popdrops.Rain import *
#from alinea.weather.global_weather import *

#from alinea.astk.TimeControl import * 


#data_file='E:/openaleapkg/echap/src/alinea/echap_wralea/Data/meteo01.csv'
#weather = Weather(data_file)
#rain_model = RainInterceptionModel()



start = "2000-10-01 01:00:00"
end = "2000-10-10 01:00:00"
g = adel_mtg()
scene_geometry = g.property('geometry')

#rain_timing = rain_model.timing(weather, start, end)
#time_control = TimeControlSet(rain=1)
Ip=1#mm.h-1 <=> kg / m2 / h-1 caribu should return projected exposed area instead
conv=0.01
out_moy, out_tri = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=Ip, output_by_triangle = True, convUnit = conv)
rain_leaf = out_moy['Einc'] #kg water per leaf triangle per h



areas, normals = get_area_and_normal(scene_geometry)