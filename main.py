import networkx as nx
import xlrd
import csv
import numpy as np
import xlwt
from entity import Passenger
from entity import Taxi
import time
import matplotlib as plt
HOME = r'C:\Users\John Smith\Desktop\Taxi\files'
TRIPS = HOME + r'\trips_1.xls'
TRAVELTIME = HOME + r'\traveltime.xlsx'
REGION = HOME+r'\region_out.csv'
LOG = HOME+r'\log.xls'


def read_trips(url):
    map = {}
    table = xlrd.open_workbook(url).sheet_by_index(0)
    for i in range(1,table.nrows):
        t = xlrd.xldate_as_tuple(table.cell(i,7).value,0)
        min = t[4]
        row = table.row_values(i)
        no = row[0]
        loc = row[1]
        dest = row[2]
        passenger = Passenger(location=loc,destination=dest,waittime=min,number = no)
        if min < 10:#TEST
            if map.get(min,-1) == -1:
                l = []
                l.append(passenger)
                map[min] = l
            else:
                map.get(min).append(passenger)
    return map

def read_traveltime(url):
    m = {}
    graph = nx.Graph()
    table = xlrd.open_workbook(url).sheet_by_index(0)
    for i in range(1,table.nrows):
        row = table.row_values(i)
        origin = int(row[0])
        dest = int(row[1])
        weight = float(row[3])
        graph.add_weighted_edges_from([(origin,dest,weight)])
        graph[origin][dest]['volume'] = 0
    return graph

def read_region_map(url):
    m = {}
    i = 0
    reader = csv.reader(open(url,'r'))
    for row in reader:
        if i>0:
            node = int(row[0])
            region  = int(row[3])
            m[node] = region
        i += 1
    return m

def true_trip(graph,origin,dest):
    if graph.has_node(origin) and graph.has_node(dest):
        if nx.has_path(graph, origin,dest) and origin != dest:
            return True
    return False

def similarity(proute,troute,regionmap):
    if len(troute) == 0:
        #if the taxi has no passenger, the similarity should be assigned the highest value
        return 0.7
    else:
        mat1 = np.zeros((100,100))
        mat2 = np.zeros((100,100))
        for i in range(len(proute)-1):
            rstart = regionmap.get(proute[i])
            rend = regionmap.get(proute[i+1])
            mat1[rstart][rend] = 1
        for i in range(len(troute)-1):
            rstart = regionmap.get(troute[i])
            rend = regionmap.get(troute[i+1])
            mat2[rstart][rend] = 1
        for i in range(100):
            mat1[i][i] = 0
            mat2[i][i] = 0
        sum1 = np.sum(mat1)
        sum2 = np.sum(mat2)
        multisum = np.sum(mat1*mat2)
        return 0.5*(multisum/sum1+multisum/sum2)

trips = read_trips(TRIPS)
graph = read_traveltime(TRAVELTIME)
region_map = read_region_map(REGION)
taxi_list = []

# workbook = xlwt.Workbook()
# sheet_i = 0
# cols = ['time_minute','time_second','taxi_no','location','passenger_num','passenger_1','passenger_2','passenger_3']
# cols2 = ['time_minute','time_second','passenger_num','taxi_num']
# cols_sheet = ['taxi_02','taxi_03','taxi_04','taxi_05','taxi_06','taxi_07','taxi_08']
# sheet_index = [1,2,3,4,5,6,7]
# sheets = []
# for i in cols_sheet:
#     sheets.append(workbook.add_sheet(i,cell_overwrite_ok=True))
# sheet_overall = workbook.add_sheet('overall')
# for i in range(len(cols_sheet)-1):
#     for j in range(len(cols)):
#         sheets[i].write(0, i, cols[j])
# for i in range(len(cols2)):
#     sheet_overall.write(0,i,cols2[i])

#write volume
Taxi.volume_sheet.write(0, 0, 'init')
Taxi.volume_sheet.write(0, 1, 'end')
volume_head_i = 1
for edge in graph.edges():
    init = edge[0]
    end = edge[1]
    Taxi.volume_sheet.write(volume_head_i, 0, init)
    Taxi.volume_sheet.write(volume_head_i, 1, end)
    volume_head_i += 1

similarity_threshold = 0.5
time = {'minute':0,'second':0}
for p in trips.get(time['minute']):
    origin = p.location
    dest = p.destination
    if true_trip(graph,origin,dest):
        taxi = Taxi(graph,3,p.location)
        taxi.add_passenger(p)
        taxi_list.append(taxi)

while Passenger.on_taxi_num>0:
    time['second']+=1
    if time['second'] == 60:
        time['second'] = 0
        time['minute'] += 1

    print('time',time,'passenger_num',Passenger.on_taxi_num,'taxi_num',len(taxi_list))
    for taxi in taxi_list:
        taxi.forward()

    ##write to xls
    # sheet_i += 1
    # for i in range(len(sheets)):
    #     taxi1 = taxi_list[sheet_index[i]]
    #     sheet = sheets[i]
    #     sheet.write(sheet_i,0,time['minute'])
    #     sheet.write(sheet_i,1,time['second'])
    #     sheet.write(sheet_i,2,taxi1.no)
    #     sheet.write(sheet_i,3,taxi1.location)
    #     sheet.write(sheet_i,4,len(taxi1.passenger_list))
    #     for i in range(len(taxi1.passenger_list)):
    #         sheet.write(sheet_i,5+i,taxi1.passenger_list[i].no)
    # sheet_overall.write(sheet_i,0,time['minute'])
    # sheet_overall.write(sheet_i,1,time['second'])
    # sheet_overall.write(sheet_i,2,Passenger.on_taxi_num)
    # sheet_overall.write(sheet_i,3,len(taxi_list))

    t = time['minute'] * 60 + time['second']
    Taxi.volume_index = 1
    if(t<250):
        for edge in graph.edges():
            init = edge[0]
            end = edge[1]
            volume = graph[init][end]['volume']
            Taxi.volume_sheet.write(Taxi.volume_index, t + 2, volume)
            Taxi.volume_index += 1


    if time['second'] == 0:
        if trips.get(time['minute'])!=None:
            for p in trips.get(time['minute']):
                origin = p.location
                dest = p.destination
                if true_trip(graph,origin,dest):
                    proute = nx.shortest_path(graph,p.location,p.destination)
                    max_sim = 0
                    selected_taxi = None
                    #similarity
                    for t in taxi_list:
                        if region_map.get(t.location) == region_map.get(p.location) and len(t.passenger_list) < t.seat_num:
                            sim = similarity(proute,t.route,region_map)
                            if sim > max_sim:
                                max_sim = sim
                                selected_taxi = t
                    if max_sim > similarity_threshold:
                        selected_taxi.add_passenger(p)
                        #print(selected_taxi.no)#############################
                        #print('pick taxi:',t.no)
                        # if p.no == 836:
                        #     print('selected taxi:',p.no,selected_taxi.no)
                    else:
                        taxi = Taxi(graph,3,p.location)
                        taxi.add_passenger(p)
                        taxi_list.append(taxi)
                        #print('add taxi:',taxi.no)
                        # if p.no == 836:
                        #     print('new taxi:',p.no,taxi.no)
#workbook.save(LOG)
Taxi.volume_workbook.save(HOME+r'\volume.xls')



#print(similarity([29,2246,3950],[29,2246,3950],region_map))

