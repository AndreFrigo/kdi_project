import csv



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
    newSchema = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Description_breve','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    print(newSchema)
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

    return dataset
    


#modify the type of the elements in the dataset according to the type specified in the ETG, for default each element is a string
#nb the dictionary is passed by sharing and is a mutable object, so the modifications done inside the function are applied to the original dataset
#input: the dataset to modify
def castDataset(dataset):
    pass



#populate data with the values from the csv dataset
datasetList = getCSV("test.csv")

createDataset(datasetList)

dataset = createDataset(datasetList)
# for col in dataset:
#     print("-----"+col+"-----")
#     for elem in dataset[col]:
#         print(type(elem))

modifySchema(dataset)


