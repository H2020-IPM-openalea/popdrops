############################################# Rapilly ############################################    
############################## 1mm rain Rapilly
from alinea.echap.imports_echap import *
# Initiate
g = adel_mtg()
scene_geometry = g.property('geometry')
convUnit = 0.01
pFA = 6.19e7

splashed_droplets = {}
for Ip in range(11):
    out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=Ip, output_by_triangle = True, convUnit = convUnit)
    rain_leaf = out_moy['Einc']
    exposed_S = out_tri['Einc']
    for id, val in exposed_S.iteritems():
        if Ip == 0:
            splashed_droplets[id] = []
        splashed_droplets[id].append((sum(pFA * np.array(val))*36)/100)

print splashed_droplets

df = DataFrame(splashed_droplets)
plt.plot(df)
plt.show()

############################### Mean event Rapilly
from alinea.echap.imports_echap import * 
# Initiate
g = adel_mtg()
scene_geometry = g.property('geometry')
pFA = 6.19e7
# Model
rain_interception_model = RapillyInterceptionModel()
# Weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'test_rain_interception.csv')
t_deb = "2001-07-06 21:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
splashed_droplets = {}
nbsteps = len(weather.data)
rain_timing = TimeControl(delay = 1, steps = nbsteps, model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# Intercept
for tc in timer:
    g = rain_interception(g, rain_interception_model, tc['rain'], label='LeafElement', geometry = 'geometry')
    rain = g.property('rain')
    for id, typ in rain.iteritems():
        splashed_droplets[id] = (typ['splashed_droplets']*36)/100

print splashed_droplets

############################### time to time event Rapilly
from alinea.echap.imports_echap import * 
# Initiate
g = adel_mtg()
scene_geometry = g.property('geometry')
pFA = 6.19e7
convUnit = 0.01
# Weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'test_rain_interception.csv')
t_deb = "2001-07-06 21:00:00"
weather = Weather(data_file=meteo01_filepath)
# Rain event
splashed_droplets = {}
event = weather.data['rain']
for i in range(len(event)):
    out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=1, output_by_triangle = True, convUnit = convUnit)
    rain_leaf = out_moy['Einc']
    exposed_S = out_tri['Einc']
    for id, val in exposed_S.iteritems():
        if i == 0:
            splashed_droplets[id] = []
        splashed_droplets[id].append(sum(pFA * np.array(val) * event[i]) * (36./100.))

print splashed_droplets

# Bar plot
nbr_drop12 = np.array(splashed_droplets[12])
# On remplace les nan par 0 [0 if x==Nan else x for x in Ndrop]
whereAreNaNs = np.isnan(nbr_drop12)
nbr_drop12[whereAreNaNs] = 0

N = len(nbr_drop12)
ind = np.arange(N) 
rect = plt.bar(ind, nbr_drop12)
plt.title('Time to time event Rapilly')
plt.ylabel('Number of droplets')

def autolabel(rects):
    # attach some text labels
    ti = 0
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, event[ti],
                ha='center', va='bottom')
        ti +=1

autolabel(rect)

plt.show()


############################################# Popdrops ###########################################
################################ 1mm rain Popdrops
from alinea.echap.imports_echap import * 
# Initiate
g = adel_mtg()
scene_geometry = g.property('geometry')
convUnit = 0.01
# Weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo01.csv')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = 1, model = rain_interception_model, weather = weather, start_date = t_deb)
time_control = rain_timing.next()
# RainInterception
Ndrop = {}
out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=1, output_by_triangle = True, convUnit = convUnit)
exposed_S_leaf = out_moy['Einc']
exposed_S = out_tri['Einc']

Ndroplets = {}
impacted_surface = {}

for rain in range(31):
    if rain > 0:
        size = 10000
        s_size = int(size)
        rdref=RainDist(5)
        pop = []
        ros=[]
    
        rd = RainDist(rain)
        pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
        ros = rd.ro
        popd = PopDrops(ros, pop, duration = 3600)

        for id, val in exposed_S.iteritems():
            Ndroplets[id] = popd.emited_droplets(np.array(val))
            impacted_surface[id] = popd.impacted_surface(np.array(val))

        for id, val in Ndroplets.iteritems():
            try:
                Ndrop[id].append(sum(val))
            except:
                Ndrop[id] = []
                Ndrop[id].append(sum(val))

for id, val in Ndrop.iteritems():
    Ndrop[id].insert(0, 0)

df = DataFrame(Ndrop)
plt.plot(df)
plt.show()


############################### time to time event Popdrops
from alinea.echap.imports_echap import * 
# Initiate
g = adel_mtg()
scene_geometry = g.property('geometry')
convUnit = 0.01
# Weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'test_rain_interception.csv')
t_deb = "2001-07-06 21:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = 10, model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# Intercept
Ndrop = {}
out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=1, output_by_triangle = True, convUnit = convUnit)
exposed_S_leaf = out_moy['Einc']
exposed_S = out_tri['Einc']
for tc in timer:
    if tc['rain'].dt > 0:
        event = tc['rain'].rain
        print event
        for rain in tc['rain'].rain:
            print rain
            size = 10000
            s_size = int(size)
            rdref=RainDist(5, rain_type="thunderstorm")
            pop = []
            ros=[]
            rd = RainDist(rain, rain_type="thunderstorm")
            pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
            ros = rd.ro
            popd = PopDrops(ros, pop, duration = 3600)

            Ndroplets = {}
            impacted_surface = {}
            for id, val in exposed_S.iteritems():
                Ndroplets[id] = popd.emited_droplets(np.array(val))
                impacted_surface[id] = popd.impacted_surface(np.array(val))

            for id, val in Ndroplets.iteritems():
                try:
                    Ndrop[id].append(sum(val))
                except:
                    Ndrop[id] = []
                    Ndrop[id].append(sum(val))

# Bar plot
nbr_drop12 = np.array(Ndrop[12])
# On remplace les nan par 0 [0 if x==Nan else x for x in Ndrop]
whereAreNaNs = np.isnan(nbr_drop12)
nbr_drop12[whereAreNaNs] = 0

N = len(nbr_drop12)
ind = np.arange(N) 
rect = plt.bar(ind, nbr_drop12)
plt.title('Time to time event Popdrops')
plt.ylabel('Number of droplets')

def autolabel(rects):
    # attach some text labels
    ti = 0
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, event[ti],
                ha='center', va='bottom')
        ti +=1

autolabel(rect)

plt.show()

        
       
########################################## test 
rain = 16.6
size = 100000
s_size = int(size)
rdref=RainDist(5)
pop = []
ros=[]
rd = RainDist(rain, rain_type="shower")
pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
ros = rd.ro
popd = PopDrops(ros, pop, duration = 3600)
Ndroplets = popd.emited_droplets(1)
Rc_roll = popd.Rc_roll(pi * 60. / 180.)

Ndroplets / 1e7

pFA = 6.19e7
(rain*pFA) / 1e7
##########################################


########################################## Popdrops year events one rain_type 1 m²
from alinea.echap.imports_echap import * 
# Year weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo00-01.csv')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = len(weather.data), model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# Rain event
Ndrop = []
rain_events = []
events = []
i = 0
for tc in timer:
    if tc['rain'].dt > 0:
        print i
        i +=1
        event = tc['rain'].rain
        events.append(event)
        for rain in event:
            rain_events.append(rain)
            size = 10000
            s_size = int(size)
            rdref = RainDist(5, rain_type='thunderstorm')
            pop = []
            ros = []
            rd = RainDist(rain, rain_type='thunderstorm')
            pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
            ros = rd.ro
            popd = PopDrops(ros, pop, duration = 3600)

            Ndroplets = popd.emited_droplets(1)
            Ndrop.append([rain, Ndroplets])

# Plot
data_rain = DataFrame(Ndrop)
plt.plot(data_rain[0], data_rain[1], 'bo')
plt.show()


########################################## Popdrops year events all rain_type 1 m²
from alinea.echap.imports_echap import * 
# Year weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo00-01.csv')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = len(weather.data), model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# Rain event
rain_type = ['shower', 'thunderstorm', 'widespread']
Ndrop = []
rain_events = []
events = []
for rain_ty in rain_type:
    i = 0
    for tc in timer:
        if tc['rain'].dt > 0:
            print i
            i +=1
            event = tc['rain'].rain
            events.append(event)
            for rain in event:
                rain_events.append(rain)
                size = 10000
                s_size = int(size)
                rdref = RainDist(5, rain_type=rain_ty)
                pop = []
                ros = []
                rd = RainDist(rain, rain_type=rain_ty)
                pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
                ros = rd.ro
                popd = PopDrops(ros, pop, duration = 3600)

                Ndroplets = popd.emited_droplets(1)
                Ndrop.append([rain_ty, rain, Ndroplets])

# Plot
data_rain = DataFrame(Ndrop)
df_shower = data_rain[0]=='shower'
df_thunderstorm = data_rain[0]=='thunderstorm'
df_widespread = data_rain[0]=='widespread'
plt.plot(df_shower[1], df_shower[2], 'bo')
plt.plot(df_thunderstorm[1], df_thunderstorm[2], 'bo')
plt.plot(df_widespread[1], df_widespread[2], 'bo')
plt.show()

# Hist intensités
hist, bins = np.histogram([value for value in rain_events if value > 0.5],bins = 100)
width = 0.7*(bins[1]-bins[0])
center = (bins[:-1]+bins[1:])/2
plt.bar(center, hist, align = 'center', width = width)
plt.show()

# Moyenne des intensités
mean_events = []
for evt in events:
    mean_events.append([len(evt), numpy.sum(evt)])

data_rain = DataFrame(mean_events)
df1 = data_rain[data_rain[1] > 0.4]
df = df1[df1[1] < 4]
#df = data_rain[data_rain[0] > 1]
# Hist intensités
hist, bins = np.histogram(df[0],bins = 100)
width = 0.7*(bins[1]-bins[0])
center = (bins[:-1]+bins[1:])/2
plt.bar(center, hist, align = 'center', width = width)
plt.show()




########################################## Popdrops year events all rain_type exposed_area
from alinea.echap.imports_echap import * 
# Initiate
g = adel_mtg()
scene_geometry = g.property('geometry')
convUnit = 0.01
# Year weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo00-01.csv')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = len(weather.data), model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# RainInterception
Ndrop = {}
Ndroplets = {}
impacted_surface = {}
events = []
rain_events = []
rain_type = ['shower', 'thunderstorm', 'widespread']
out_moy, out_tri, indices = turtle_interception(sectors='1', scene_geometry=scene_geometry, energy=1, output_by_triangle = True, convUnit = convUnit)
exposed_S_leaf = out_moy['Einc']
exposed_S = out_tri['Einc']

for rain_ty in rain_type:
    i = 0
    for tc in timer:
        if tc['rain'].dt > 0:
            print i
            i +=1
            event = tc['rain'].rain
            events.append(event)
            for rain in event:
                rain_events.append(rain)
                size = 100000
                s_size = int(size)
                rdref=RainDist(5, rain_type=rain_ty)
                pop = []
                ros=[]
                rd = RainDist(rain, rain_type=rain_ty)
                pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
                ros = rd.ro
                popd = PopDrops(ros, pop, duration = 3600)
                for id, val in exposed_S.iteritems():
                    Ndroplets[id] = popd.emited_droplets(np.array(val))
                for id, val in Ndroplets.iteritems():
                    try:
                        Ndrop[id].append([rain_ty, rain, sum(val)])
                    except:
                        Ndrop[id] = []
                        Ndrop[id].append([rain_ty, rain, sum(val)])


# Plot L12
data_rain = DataFrame(Ndrop[12])
df_shower = data_rain[data_rain[0]=='shower']
df_thunderstorm = data_rain[data_rain[0]=='thunderstorm']
df_widespread = data_rain[data_rain[0]=='widespread']
plt.plot(df_shower[1], df_shower[2], 'bo')
plt.plot(df_thunderstorm[1], df_thunderstorm[2], 'bo')
plt.plot(df_widespread[1], df_widespread[2], 'bo')
plt.show()




####################################################################################################
############################### Rapilly pour un event de 2, 1, 2 mm sur 2h
from alinea.echap.imports_echap import * 
# Initiate
pFA = 6.19e7
PEV = 0.4
PNOSPO = 0.24
# Rain event
event = [2, 1, 2]
splashed_droplets = (pFA * 1) * (1 - PEV - PNOSPO)
print splashed_droplets / 1e7
############################### popdrops pour un event de 2, 1, 2 mm sur 2h
from alinea.echap.imports_echap import * 
# Initiate
Ndroplets = []
# Intercept
event = [2., 1., 2.]
for rain in event:
    size = 10000
    s_size = int(size)
    rdref=RainDist(5, rain_type="shower")
    pop = []
    ros=[]
    rd = RainDist(rain, rain_type="shower")
    pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
    ros = rd.ro
    if rain == 1:
        popd = PopDrops(ros, pop, duration = 3600.)
    else:
        popd = PopDrops(ros, pop, duration = 3600./2.)
    Ndroplets.append(popd.emited_droplets(1) / 1e7)
print sum(Ndroplets)
############################### popdrops pour un event de 0.5, 2, 0.5 mm sur 2h
from alinea.echap.imports_echap import * 
# Initiate
Ndroplets = []
# Intercept
event = [0.5, 2., 0.5]
for rain in event:
    size = 10000
    s_size = int(size)
    rdref=RainDist(5, rain_type="shower")
    pop = []
    ros=[]
    rd = RainDist(rain, rain_type="shower")
    pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
    ros = rd.ro
    if rain == 2.:
        popd = PopDrops(ros, pop, duration = 3600.)
    else:
        popd = PopDrops(ros, pop, duration = 3600./2.)
    Ndroplets.append(popd.emited_droplets(1) / 1e7)
print sum(Ndroplets)
############################### popdrops pour un event de 1,1,1 mm sur 3h
from alinea.echap.imports_echap import * 
# Initiate
Ndroplets = []
# Intercept
event = [1, 1, 1]
for rain in event:
    size = 10000
    s_size = int(size)
    rdref=RainDist(5, rain_type="shower")
    pop = []
    ros=[]
    rd = RainDist(rain, rain_type="shower")
    pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
    ros = rd.ro
    popd = PopDrops(ros, pop, duration = 3600.)
    Ndroplets.append(popd.emited_droplets(1) / 1e7)
print sum(Ndroplets)




##################################################################################################
# Comparaison LAVA de Rapilly et rolling_fraction de Drops
from alinea.echap.imports_echap import * 
# Year weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo00-01.csv')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = len(weather.data), model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# Rain event
rain_type = ['shower', 'thunderstorm', 'widespread']
rolling_frac = []
rain_events = []
events = []
lavage = []

for rain_ty in rain_type:
    i = 0
    for tc in timer:
        if tc['rain'].dt > 0:
            print i
            i +=1
            event = tc['rain'].rain
            events.append(event)
            for rain in event:
                rain_events.append(rain)
                size = 1000
                s_size = int(size)
                rdref = RainDist(5, rain_type=rain_ty)
                pop = []
                ros = []
                rd = RainDist(rain, rain_type=rain_ty)
                pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
                ros = rd.ro
                popd = PopDrops(ros, pop, duration = 3600)

                rolling_fraction = popd.rolling_fraction(pi * 60 / 180)
                rolling_frac.append([rain_ty, rain, rolling_fraction])
                #lava = (rain / (LAI * 1e-4 + rain))
                #lavage.append([rain_ty, rain, lava])
# Plot
data_rain = DataFrame(rolling_frac)
#data_lava = DataFrame(lavage)
df_shower = data_rain[data_rain[0]=='shower']
df_thunderstorm = data_rain[data_rain[0]=='thunderstorm']
df_widespread = data_rain[data_rain[0]=='widespread']
plt.plot(df_shower[1], df_shower[2], 'bo')
plt.plot(df_thunderstorm[1], df_thunderstorm[2], 'bo')
plt.plot(df_widespread[1], df_widespread[2], 'bo')
plt.show()


# Comparaison LAVA de Rapilly et rolling_fraction de Drops
from alinea.echap.imports_echap import * 
# Year weather
meteo01_filepath = get_shared_data_path(['alinea/echap'], 'meteo00-01.csv')
t_deb = "2000-10-01 01:00:00"
weather = Weather(data_file=meteo01_filepath)
# Time control
rain_interception_model = RainInterceptionModel()
rain_timing = TimeControl(delay = 1, steps = len(weather.data), model = rain_interception_model, weather = weather, start_date = t_deb)
timer = TimeControler(rain = rain_timing)
# Rain event
rain_type = ['shower', 'thunderstorm', 'widespread']
rolling_frac = []
rain_events = []
events = []
lavage = []
for rain_ty in rain_type:
    i = 0
    for tc in timer:
        if tc['rain'].dt > 0:
            print i
            i +=1
            event = tc['rain'].rain
            events.append(event)
            rain = np.mean(event)
            rain_events.append(rain)
            size = 1000
            s_size = int(size)
            rdref = RainDist(5, rain_type=rain_ty)
            pop = []
            ros = []
            rd = RainDist(rain, rain_type=rain_ty)
            pop.extend(rd.dv_sample(int(s_size) * rd.ro / rdref.ro))
            ros = rd.ro
            popd = PopDrops(ros, pop, duration = 3600)

            rolling_fraction = popd.rolling_fraction(pi * 60 / 180)
            rolling_frac.append([rain_ty, rain, rolling_fraction])

            lava = (rain / (LAI * 1e-4 + rain)) * tc['rain'].dt
            lavage.append([rain_ty, rain, lava])

data_lava = DataFrame(lavage)
plt.plot(data_lava[1], data_lava[2], 'bo')
plt.show()