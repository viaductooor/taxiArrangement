import csv
import xlrd
import xlwt

HOME = r'C:\Users\John Smith\Desktop\Taxi\files'
REGION_OUT = HOME+r'\region_out.csv'
TRIPS = HOME+r'\trips.xls'
m  = {}
r1 = csv.reader(open(REGION_OUT,'r'))
i = 0
for row in r1:
    if i> 0:
        new = int(row[4])
        origin = int(row[0])
        m[new] = origin
    i += 1

#recover trips
sheet_trips = xlrd.open_workbook(TRIPS).sheet_by_index(0)
wb_origintrips = xlwt.Workbook()
sheet_oritintrips = wb_origintrips.add_sheet('sheet0')
cols_origintrips = ['no','location_node','destination_node','location_lat','location_lon','destination_lat','destination_lon','time']
for i in range(len(cols_origintrips)):
    sheet_oritintrips.write(0,i,cols_origintrips[i])
for i in range(1,sheet_trips.nrows):
    row = sheet_trips.row_values(i)
    sheet_oritintrips.write(i,0,row[0])
    sheet_oritintrips.write(i,1,m.get(row[1]))
    sheet_oritintrips.write(i,2,m.get(row[2]))
    sheet_oritintrips.write(i,3,row[3])
    sheet_oritintrips.write(i,4,row[4])
    sheet_oritintrips.write(i,5,row[5])
    sheet_oritintrips.write(i,6,row[6])
    sheet_oritintrips.write(i,7,row[7])
wb_origintrips.save(HOME+r'\trips_1.xls')

#recover


