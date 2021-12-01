import csv
import common_functions as cf
import pandas as pd
import json

#read the csv files and modify the datasets according to the ETG
#input: single csv file name including relative path(string)
@ -180,19 +181,85 @@
    
    return dataset

def Read_JSON():
    #2892
    column_names = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    line=["","",False,"","","","","",0,"","","",0.0,0.0,"","","",0,"","",0]
    f = open('POI_Trentino.json', encoding="utf8")
    # returns JSON object as
    # a dictionary
    dataset=[]
    dataset_JSON=pd.DataFrame(columns=column_names)
    data = json.load(f)
    for i in range(2892):
        line=["","",False,"","","","","",0,"","","",0.0,0.0,"","","",0,"","",""]
        line[1]=data[str(i)]["content"]["objData"]["name"]["IT"]
        line[3]=data[str(i)]["content"]["objData"]["description"]["IT"]
        #+"\n"+data[str(i)]["content"]["objData"]["serviceDescription"]
        line[4]=data[str(i)]["content"]["objData"]["category"]
        if(data[str(i)]["content"]["poiData"]["contact"]!=None and data[str(i)]["content"]["poiData"]["contact"]["name"]!={} ):
            line[6]=data[str(i)]["content"]["poiData"]["contact"]["name"]
        if(data[str(i)]["content"]["poiData"]["timetable"] != {}):
            line[7]=data[str(i)]["content"]["poiData"]["timetable"]
        if(data[str(i)]["content"]["poiData"]["contact"]!=None):
            if(data[str(i)]["content"]["poiData"]["contact"]["phone"]!= None):
                line[9]=str(data[str(i)]["content"]["poiData"]["contact"]["phone"])
            line[10]=data[str(i)]["content"]["poiData"]["contact"]["url"]
        line[12]=data[str(i)]["content"]["poiData"]["location"]["coordinate"]["latitude"]
        line[13]=data[str(i)]["content"]["poiData"]["location"]["coordinate"]["longitude"]
        line[15]=data[str(i)]["content"]["poiData"]["location"]["addresses"]["IT"]["city"]
        line[17]=data[str(i)]["content"]["poiData"]["location"]["addresses"]["IT"]["postalCode"]
        street=data[str(i)]["content"]["poiData"]["location"]["addresses"]["IT"]["street"]
        if(has_numbers(street)):
            element2=street.split(" ")
            phrase=""
            c=0
            for elem in element2:
                if(elem.isdigit()):
                    line[20]=str(elem)
                    c=1
                else:
                    phrase+=elem+" "
            if(c==0):
                phrase=""
                element2=street.split(",")
                for elem in element2:
                    if(elem.isdigit()):
                        line[20]=str(elem)
                        c=1
                    else:
                        phrase+=elem+","
            if(c==0):
                phrase=""
                element2=street.split(".")
                for elem in element2:
                    if(elem.isdigit()):
                        line[20]=str(elem)
                        c=1
                    else:
                        phrase+=elem+"."
            line[19]=phrase       
        else:
            line[19]=street
        dataset.append(line)
    dataset_JSON=pd.DataFrame(dataset,columns=column_names)
    dataset_JSON.to_csv(r'myData.csv',sep=';',index=True)
    f.close()


#populate data with the values from the csv dataset
#just an example to test
datasetList = getCSV("CSV_POI/Comun_general_de_Fascia.csv")

# #list of csv file names
# print(cf.getListCSV())

dataset = createDataset(datasetList)

d=modifySchema(dataset)

#dataset = castDataset(d)

# cf.printDataset(dataset, True)

Read_JSON()