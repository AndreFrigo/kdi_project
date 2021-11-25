import csv
import common_functions as cf

#read the csv files and modify the datasets according to the ETG
#input: single csv file name including relative path(string)
#output: list containing the csv data
def getCSV(filename):
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
    newSchema = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description_breve','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    # print(newSchema)
    dataset = {}
    for elem in newSchema:
        dataset[elem]=[]
    
    #manually map the old schema to the new one
    if 'remoteId' in oldDataset: dataset['ATT:Id'].extend(oldDataset['remoteId'])
    if 'Titolo' in oldDataset: dataset['ATT:Name'].extend(oldDataset['Titolo'])
    if 'Descrizione' in oldDataset: dataset['ATT:Description'].extend(oldDataset['Descrizione'])
    if 'Descrizione breve' in oldDataset: dataset['ATT:Description_breve'].extend(oldDataset['Descrizione breve'])
    if 'Tipologia di luogo' in oldDataset: dataset['ATT:Type'].extend(oldDataset['Tipologia di luogo'])
    if 'lat' in oldDataset: dataset['LOC:Latitude'].extend(oldDataset['lat'])
    if 'lon' in oldDataset: dataset['LOC:Longitude'].extend(oldDataset['lon'])
    #TODO: map the address where? only 'address', 'indirizzo' and 'comune' from the csv
    if 'address' in oldDataset: dataset['ADD:Street'].extend(oldDataset['address'])
    if 'Comune' in oldDataset: dataset['ADD:Commune'].extend(oldDataset['Comune'])
    if 'Indirizzo' in oldDataset: dataset['ADD:City'].extend(oldDataset['Indirizzo'])
    #TODO: what to do with the 'Informazioni' column?
    #TODO: what to do with the 'Leggi le informazioni dettagliate' column?
    if 'Impianto gestito da' in oldDataset: dataset['COM:Name'].extend(oldDataset['Impianto gestito da'])
    if 'Indirizzo web' in oldDataset: dataset['COM:Url'].extend(oldDataset['Indirizzo web'])
    #TODO: what to do with the 'Email' column?
    if 'Telefono' in oldDataset: dataset['COM:Telephone'].extend(oldDataset['Telefono'])

    #list for columns that have no information (TODO: better filling of the dataset)
    noValues=['' for e in dataset['ATT:Id']]
    for elem in dataset:
        if(len(dataset[elem])==0): dataset[elem].extend(noValues)
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
    #TODO: descrizione breve
    stringList = ['ADD:City','ADD:Commune','ATT:Description','ATT:Description_breve','ATT:Id','COM:Id','LOC:Id','ADD:Id','ATT:Name','COM:Name','COM:OpeningHours','ADD:Province','ADD:Street','ADD:StreetNumber','COM:Telephone','ATT:Type','COM:Url']
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
datasetList = getCSV("../csv_datasets_KDI/CSV_POI/male.csv")

dataset = createDataset(datasetList)

d=modifySchema(dataset)

dataset = castDataset(d)

# cf.printDataset(dataset, True)
