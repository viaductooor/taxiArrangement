import networkx as nx
import xlwt
class Taxi:
    number = 0
    volume_workbook = xlwt.Workbook()
    volume_sheet = volume_workbook.add_sheet('link_volume',cell_overwrite_ok=True)
    volume_index = 1

    def __init__(self, graph, seat_num, location):
        Taxi.number += 1
        self.no = Taxi.number
        self.seat_num = seat_num
        self.location = location
        self.passenger_list = []
        self.route = []
        self.route_cursor = 0
        self.departure_time = 0
        self.time_to_nextnode = 0
        self.passenger_num = 0
        self.graph = graph

    def init_log(self):
        Taxi.volume_sheet.write(0,0,'init')
        Taxi.volume_sheet.write(0,1,'end')
        i = 1
        for edge in self.graph.edges():
            init = edge[0]
            end  = edge[1]
            Taxi.volume_sheet.write(i,0,init)
            Taxi.volume_sheet.write(i,1,end)
            i += 1

    def log(self,time):
        for edge in self.graph.edges():
            init = edge[0]
            end  = edge[1]
            volume = self.graph[init][end]['volume']
            Taxi.volume_sheet.write(Taxi.volume_index,time+2,volume)



    def forward(self):
        # no need to change route, just go forward and drop passengers if needed
        if len(self.passenger_list) == 0:
            pass
        else:
            self.departure_time += 1
            if self.departure_time > self.time_to_nextnode:
                self.route_cursor += 1
                self.location = self.route[self.route_cursor]

                #change volume when taxi leaves the former link
                pre_init = self.route[self.route_cursor-1]
                pre_end = self.route[self.route_cursor]
                if self.graph[pre_init][pre_end]['volume']>0:
                    self.graph[pre_init][pre_end]['volume'] -= 1

                self.drop_passenger()
                if len(self.passenger_list) != 0:  # if not reachs the destination
                    pres = self.route[self.route_cursor]
                    try:
                        next = self.route[self.route_cursor + 1]
                    except IndexError:
                        print(self.no)
                        print(self.route)
                        print(self.route_cursor)
                        for p in self.passenger_list:
                            print(p.destination)
                    self.time_to_nextnode = self.graph[pres][next]['weight']
                    self.departure_time = 0

                    #change volume when taxi runs on another link
                    self.graph[pres][next]['volume'] += 1
                    self.graph[pres][next]['total_volume'] += 1

                else: # if reaches the destination
                    self.departure_time = 0
                    self.route = []
                    self.route_cursor = 0

    def cmp(self,passenger):
        origin = self.location
        dest = passenger.destination
        return nx.shortest_path_length(self.graph,origin,dest,'weight')

    def drop_passenger(self):
        resl = []
        drop_num = len(self.passenger_list)
        for p in self.passenger_list:
            if p.destination != self.location:
                resl.append(p)
                drop_num -= 1
        Passenger.on_taxi_num -= drop_num
        self.passenger_list = resl
        #print('taxi:', self.no, 'drop_location:',self.location,'drop_num:',drop_num,'pass_num:',len(self.passenger_list),'passenger_on_taxi:',Passenger.on_taxi_num)

    def get_recent_link(self):
        former = self.route[self.route_cursor]
        next = self.route[self.route_cursor+1]
        return (former,next)

    def nodelist_to_route(self,list):
        l = [list[0]]
        for i in range(len(list)-1):
            l.extend(nx.shortest_path(self.graph,list[i],list[i+1],'weight')[1:])
        return l

    def add_passenger(self, passenger):
        #add passenger and sort them by traveltime
        self.passenger_list.append(passenger)
        self.passenger_list.sort(key=self.cmp)

        #update route
        route = None
        if self.location == passenger.location and self.departure_time == 0:
            #the taxi can pick the passenger immediately
            rl = [self.location]
            for pa in self.passenger_list:
                rl.append(pa.destination)
            try:
                route = self.nodelist_to_route(rl)
                Passenger.on_taxi_num += 1
                self.route = route
                self.route_cursor = 0
                self.departure_time = 0
                self.time_to_nextnode = self.graph[self.route[0]][self.route[1]]['weight']
                self.graph[route[0]][route[1]]['total_volume'] += 1
                self.graph[route[0]][route[1]]['volume'] += 1
            except nx.NetworkXNoPath:
                self.passenger_list.remove(passenger)
                raise nx.NetworkXNoPath
        elif self.departure_time != 0:
            #self.departureTime != 0
            #the taxi has to run a while to pick the passenger first
            nextNode = self.route[self.route_cursor+1]
            rl = [nextNode,passenger.location]
            for pa in self.passenger_list:
                rl.append(pa.destination)
            try:
                self.route = self.nodelist_to_route(rl)
                self.route = [self.location,]+self.route
                self.route_cursor = 0
                Passenger.on_taxi_num += 1
                if self.no == 491:
                    print('location:',passenger.location,'destination:',passenger.destination)
                    print('route after:',self.route)
            except nx.NetworkXNoPath as e:
                self.passenger_list.remove(passenger)
                raise e
        else:
            # 1.self.location != passenger.location
            # 2.self.departureTime == 0
            r1 = [self.location,passenger.location]
            for pa in self.passenger_list:
                r1.append(pa.destination)
            try:
                self.route = self.nodelist_to_route(r1)
                self.route_cursor = 0
                Passenger.on_taxi_num += 1
            except nx.NetworkXNoPath as e:
                self.passenger_list.remove(passenger)
                raise nx.NetworkXNoPath


class Passenger:
    on_taxi_num = 0
    def __init__(self, location, destination, waittime,number):
        self.location = location
        self.destination = destination
        self.waittime = waittime
        self.status = 0
        self.no = number
