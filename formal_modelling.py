import csv
import common_functions as cf
import pandas as pd

#read the csv files and modify the datasets according to the ETG
#input: single csv file name including relative path(string)
#output: list containing the csv data
commune=""
def getCSV(filename):
    global commune
    commune=filename.split("/")[1]
    dataset = []
    try:
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:
                dataset.append(row)
    except:
        pass
    return dataset

#create a dictionary containing the original data
#input: list containing the csv data
#output: dictionary with column name as key and a list of the values for each element for that column
def createDataset(datasetList):
    dataset = {}
    #dataset non empty
    if(len(datasetList)>0):
        #list containing the column name
        schema = datasetList[0]
        #create the key-list pairs in the dataset structure
        for elem in schema:
            dataset[elem]=[]
        # print(schema)
        #objects of the dataset (assuming one object for row), list containing the values for each column
        for row in datasetList[1:]:
            col = 0
            while(col<len(schema)):
                dataset[schema[col]].append(row[col])
                col+=1
    return dataset

#modify the schema of the dataset according to the ETG
#input: the dataset to modify
#output: the dataset with the correct schema (objects are not modified here!)
def modifySchema(oldDataset):
    #TODO: descrizione and descrizione breve, what to do? For now saved both in ATT
    newSchema = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    # print(newSchema)
    dataset = {}
    for elem in newSchema:
        dataset[elem]=[]
    
    #TODO:handle string scraping for description and address (oldDataset) and insert information in the right place of newDataset as the code above
    add = split_adress(oldDataset)

    #manually map the old schema to the new one
    if 'remoteId' in oldDataset: dataset['ATT:Id'].extend(oldDataset['remoteId'])
    if 'Titolo' in oldDataset: dataset['ATT:Name'].extend(oldDataset['Titolo'])
    if 'Tipologia di luogo' in oldDataset: dataset['ATT:Type'].extend(oldDataset['Tipologia di luogo'])
    if 'lat' in oldDataset: dataset['LOC:Latitude'].extend(oldDataset['lat'])
    if 'lon' in oldDataset: dataset['LOC:Longitude'].extend(oldDataset['lon'])
    dataset['ADD:Street'].extend(add['ADD:Street'])
    dataset['ADD:Commune'].extend(add['ADD:Commune'])
    dataset['ADD:City'].extend(add['ADD:City'])
    dataset['ADD:PostalCode'].extend(add['ADD:PostalCode'])
    dataset['ADD:Province'].extend(add['ADD:Province'])
    dataset['ADD:StreetNumber'].extend(add['ADD:StreetNumber'])
    #TODO: what to do with the 'Informazioni' column?
    #TODO: what to do with the 'Leggi le informazioni dettagliate' column?
    if 'Impianto gestito da' in oldDataset: dataset['COM:Name'].extend(oldDataset['Impianto gestito da'])
    if 'Telefono' in oldDataset: dataset['COM:Telephone'].extend(oldDataset['Telefono'])
    #put in url the indirizzo web, if it doesn't have the value then put the informazioni dettagliate
    if 'Indirizzo web' in oldDataset and 'Leggi le informazioni dettagliate' in oldDataset:
        length = len(oldDataset['Indirizzo web'])
        for i in range (0, length):
            indirizzoWeb = oldDataset['Indirizzo web'][i]
            informazioniDettagliate = oldDataset['Leggi le informazioni dettagliate'][i]
            if(indirizzoWeb):
                dataset["COM:Url"].append(indirizzoWeb)
            elif(informazioniDettagliate):
                dataset["COM:Url"].append(informazioniDettagliate)
            else:
                dataset["COM:Url"].append('')
    elif 'Indirizzo web' in oldDataset:
        dataset['COM:Url'].extend(oldDataset['Indirizzo web'])
    elif 'Leggi le informazioni dettagliate' in oldDataset:
        dataset['COM:Url'].extend(oldDataset['Leggi le informazioni dettagliate'])
    #if there are both descrizione breve and descrizione merge them, otherwise put the info known
    if 'Descrizione breve' in oldDataset and 'Descrizione' in oldDataset:
        length = len(oldDataset['Descrizione'])
        for i in range (0, length):
            descB = oldDataset['Descrizione breve'][i]
            desc = oldDataset['Descrizione'][i]
            if(descB and desc):
                dataset["ATT:Description"].append(str(descB)+" "+str(desc))
            elif(descB):
                dataset["ATT:Description"].append(descB)
            elif(desc):
                dataset["ATT:Description"].append(desc)
            else:
                dataset["ATT:Description"].append('')
    elif 'Desrizione breve' in oldDataset:
        dataset['ATT:Description'].extend(oldDataset['Descrizione breve'])
    elif 'Descrizione' in oldDataset:
        dataset['ATT:Description'].extend(oldDataset['Descrizione'])


    #list for columns that have no information (TODO: better filling of the dataset)
    noValues=['' for e in dataset['ATT:Id']]
    for elem in dataset:
        if(len(dataset[elem])==0): dataset[elem].extend(noValues)
    return dataset
def has_numbers(inputString):
     return any(char.isdigit() for char in inputString)
def split_adress(oldDataset):
    column_names=['ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    dataset_adress=[]
    city_list= pd.read_csv("./list_city.csv", usecols=["Name"])
    if 'address' in oldDataset:         
        #for each ligne split it 
        for address in oldDataset["address"]:
            list_adress=["","","0","","","0"]
            if(address!=""):
               
                #print("----------------")
                global commune
                #print(address)
                #print("commune: "+commune)
                list_adress[1]=commune.split(".")[0]
                value=address.split(",")
                #for each check if we have :
                for element in value:
                    # the postal code
                    number=element
                    number=number.replace(" ", "")
                    province=element
                    province=province.replace(" ", "")
                    #check if there is a number inside the text
                    if(has_numbers(element)):
                        element2=element.split(" ")
                        for elem in element2:
                            if(elem.isdigit() and int(elem)>38000):
                                #print("this element is a postal code:"+elem)
                                list_adress[2]=elem
                            if(elem.isdigit() and int(elem)<999):
                                #print("this element is a number of street:"+elem)
                                list_adress[5]=elem
                    # the street
                    if("Piazza" in element or "Via" in element or "Strada" in element or "Passo" in element):
                        #print("this element is the street:"+element)
                        list_adress[4]=element  
                    # the province
                    if(len(province)==2 and not province.isdigit()):
                        #print("this element is the province:"+province)
                        list_adress[3]=element
                    #city
                    if("Trentino" in element):
                        # print("this element is the region:"+province)
                        pass
                    element=element.replace(" ", "")
                    for city in city_list["Name"]:
                        city2=city
                        city=city.replace(" ", "")
                        if(city.lower() in element.lower()):
                            #print("this element is the city:"+city2)
                            list_adress[0]=city2
                    #commune
            # print(list_adress)
            dataset_adress.append(list_adress)
    dataset_adress=pd.DataFrame(dataset_adress,columns=column_names)
    # if 'Comune' in oldDataset:
    #     print("")

    # if 'Indirizzo' in oldDataset:
    #     print(oldDataset["Indirizzo"])
    
    return dataset_adress
    

#remove unuseful elements
#input: the dataset with the schema already aligned and the list of interesting category for the elements
#output: the dataset with only interesting elements inside 
def cleanDataset(oldDataset, interesting_categories):
    # create new dataset with the same schema
    dataset = {}
    for elem in oldDataset:
        dataset[elem]=[]
    for i in range(0, len(oldDataset['ATT:Id'])):
        if(oldDataset['ATT:Type'][i] in interesting_categories):
            for elem in oldDataset:
                dataset[elem].append(oldDataset[elem][i])
    return dataset


#modify the type of the elements in the dataset according to the type specified in the ETG, for default each element is a string
#nb the dictionary is passed by sharing and is a mutable object, so the modifications done inside the function are applied to the original dataset
#input: the dataset to modify
def castDataset(oldDataset):
    # create new dataset with the same schema
    dataset = {}
    for elem in oldDataset:
        dataset[elem]=[]
    
    #schema type list
    floatList = ['COM:Price','LOC:Latitude','LOC:Longitude']
    intList = ['ADD:PostalCode']
    stringList = ['ADD:City','ADD:Commune','ATT:Description','ATT:Id','COM:Id','LOC:Id','ADD:Id','ATT:Name','COM:Name','COM:OpeningHours','ADD:Province','ADD:Street','ADD:StreetNumber','COM:Telephone','ATT:Type','COM:Url']
    booleanString = ['ATT:ParkingArea']

    for elem in floatList:
        dataset[elem].extend(cf.castFloat(oldDataset[elem], -1))
    
    for elem in intList:
        dataset[elem].extend(cf.castInt(oldDataset[elem], -1))
    
    for elem in stringList:
        dataset[elem].extend(oldDataset[elem])
    
    for elem in booleanString:
        #TODO
        pass
    
    return dataset



#populate data with the values from the csv dataset
#just an example to test
datasetList = getCSV("CSV_POI/Comun_general_de_Fascia.csv")

# #list of csv file names
# print(cf.getListCSV())

# for elem in cf.getListCSV():
#     dataset = getCSV("CSV_POI/"+str(elem))

#     dataset = createDataset(datasetList)

#     dataset=modifySchema(dataset)

#     # dataset = cleanDataset(dataset, cf.getInterestingCategories())

#     dataset = castDataset(dataset)

#     # cf.printDataset(dataset, True)

dataset = createDataset(datasetList)

dataset=modifySchema(dataset)

dataset = cleanDataset(dataset, cf.getInterestingCategories())

dataset = castDataset(dataset)

cf.printDataset(dataset, True)
