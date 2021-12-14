import csv
import common_functions as cf
import pandas as pd
import json
import geopy.distance
from math import floor, ceil

#read the csv files and modify the datasets according to the ETG
#input: single csv file name including relative path(string)
#output: list containing the csv data
commune=""
def getCSV(filename):
    global commune
    commune=filename.split("/")[2]
    if("_1" in commune):
        commune=commune.replace('_1','')
    dataset = []
    try:
        with open(filename,encoding='utf8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:
                dataset.append(row)
    except:
        print(filename)
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
    newSchema = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    # print(newSchema)
    dataset = {}
    for elem in newSchema:
        dataset[elem]=[]
    
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
            list_adress=["","","","","",""]
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
def cleanDataset(oldDataset, interesting_categories=cf.getInterestingCategories()):
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
        dataset[elem].extend(cf.castString(oldDataset[elem], ''))
    
    for elem in booleanString:
        dataset[elem].extend(cf.castBool(oldDataset[elem], False))
    
    return dataset

def Read_JSON(jsonFile="POI_Trentino.json"):
    #2892
    column_names = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    line=["","","","","","","","","","","","","","","","","","","","",""]
    f = open(jsonFile, encoding="utf8")
    # returns JSON object as
    # a dictionary
    dataset=[]
    dataset_JSON=pd.DataFrame(columns=column_names)
    data = json.load(f)
    for i in range(2893):
        line=["","","","","","","","","","","","","","","","","","","","",""]
        line[1]=str(data[str(i)]["content"]["objData"]["name"]["IT"])
        line[3]=str(data[str(i)]["content"]["objData"]["description"]["IT"])
        #+"\n"+data[str(i)]["content"]["objData"]["serviceDescription"]
        line[4]=str(data[str(i)]["content"]["objData"]["category"])
        if(data[str(i)]["content"]["poiData"]["contact"]!=None and data[str(i)]["content"]["poiData"]["contact"]["name"]!={} ):
            line[6]=str(data[str(i)]["content"]["poiData"]["contact"]["name"]["IT"])
        if(data[str(i)]["content"]["poiData"]["timetable"] != {}):
            line[7]=str(data[str(i)]["content"]["poiData"]["timetable"])
        if(data[str(i)]["content"]["poiData"]["contact"]!=None):
            if(data[str(i)]["content"]["poiData"]["contact"]["phone"]!= None):
                line[9]=str(data[str(i)]["content"]["poiData"]["contact"]["phone"])
            line[10]=str(data[str(i)]["content"]["poiData"]["contact"]["url"])
        line[12]=str(data[str(i)]["content"]["poiData"]["location"]["coordinate"]["latitude"])
        line[13]=str(data[str(i)]["content"]["poiData"]["location"]["coordinate"]["longitude"])
        line[15]=str(data[str(i)]["content"]["poiData"]["location"]["addresses"]["IT"]["city"])
        line[17]=str(data[str(i)]["content"]["poiData"]["location"]["addresses"]["IT"]["postalCode"])
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
            line[19]=str(phrase)       
        else:
            line[19]=str(street)
        dataset.append(line)
    dataset_JSON=pd.DataFrame(dataset,columns=column_names)
    # dataset_JSON.to_csv(r'myData.csv',sep=';',index=True)
    f.close()
    return cf.createDatasetJson(dataset_JSON)

#merge two datasets and return the one obtained, they must have the final schema
#input: the two datasets to merge 
#output: the dataset obtained
def mergeDatasets(dataset1, dataset2):
    schema = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    #check that they have the correct schema
    for elem in schema:
        if elem not in dataset1 or elem not in dataset2:
            print("Error: the schema is different\n")
            return {}
    for key in dataset1:
        dataset1[key].extend(dataset2[key])
    return dataset1
    

#reads all the datasets and merge them in a dictionary
#input: relative path to json file (default: POI_Trentino.json), relative path to the CSV list (default: csv.txt), relative path to csv folder (default CSV_POI/)
#output: the dictionary with the merged datasets with the final schema
def mergeAllDatasets(jsonDataset="POI_Trentino.json", csvList="csv.txt", csvFolder="./CSV_POI/"):
    #open the JSON dataset, modify its schema and store it in the dictionary
    dataset= Read_JSON(jsonDataset)
    #read the CSVs, modify their schema and store them in the dictionary
    csvList = cf.getListCSV(csvList)
    for csv in csvList:
        c = getCSV(csvFolder+str(csv))
        c = createDataset(c)
        c = modifySchema(c)
        dataset = mergeDatasets(dataset, c)
    return dataset

#remove the duplicates from a dataset with the final schema
#input: the dataset to analyze
#output: the dataset without duplicates
def removeDuplicates(oldDataset):
    #remove elements with exactly the same name
    dataset = removeNameDuplicates(oldDataset)
    #remove duplicates based on jaro similarity
    dataset = remove_name_duplicate_jaro(dataset)
    return dataset

#remove the elements with the exact same name
def removeNameDuplicates(oldDataset):
    #use the attraction name to find duplicates (61 attraction with the same name that are the same entities)
    l = oldDataset["ATT:Name"]
    s = set([x for x in l if l.count(x) > 1])
    dataset = {}
    for elem in oldDataset:
        dataset[elem]=[]
    duplicates={}
    for elem in s:
        duplicates[elem]=0
    for i in range(0, len(oldDataset["ATT:Name"])):
        #if that attraction is a duplicate add it only if it was not added before
        name = oldDataset["ATT:Name"][i]
        if(name in s):
            if(duplicates[name]==0):
                #add the element to the dataset
                for elem in oldDataset:
                    dataset[elem].append(oldDataset[elem][i])
                #increase the counter of buplicates added
                duplicates[name]+=1
            #if it is already added do nothing
        else:
            for elem in oldDataset:
                dataset[elem].append(oldDataset[elem][i])
    return dataset

def remove_coordinate_duplicate(oldDataset):
    #x=Lat y=Long
    duplicate=[]
    list_index_id=[]
    for i in range(0, len(oldDataset)-1):
        if(len(str(oldDataset["LOC:Latitude"][i]))>=9):
            for j in range(i+1,len(oldDataset)):
                if(len(str(oldDataset["LOC:Latitude"][j]))>=9):
                    coordinate_1=(oldDataset["LOC:Latitude"][i],oldDataset['LOC:Longitude'][i])
                    coordinate_2=(oldDataset["LOC:Latitude"][j],oldDataset['LOC:Longitude'][j])
                    if(geopy.distance.distance(coordinate_1,coordinate_2).kilometers<1):
                        print("-----"+str(i))
                        print(geopy.distance.distance(coordinate_1,coordinate_2).kilometers)
                        list_j=[]
                        list_i=[]
                        for elem in oldDataset:
                            list_i.append(oldDataset[elem][i])
                            list_j.append(oldDataset[elem][j])
                        print(list_i)
                        print(list_j)
                        if(j not in list_index_id):
                            duplicate.append(list_j)
                            list_index_id.append(j)
#solve entity duplicates
#input dictionary with the two entities (with final schema)
#output: dictionary with the entity that will be stored 
def solveConflict(conflicts):
    # print("SOLVE CONFLICT BETWEEN "+conflicts["ATT:Name"][0] + " and " + conflicts["ATT:Name"][1])
    
    ret = {}
    for elem in conflicts:
        ret[elem]=[]
    
    #decide what to do for each attribute

    #for the different ids I don't care, keep the first
    first = ['ATT:Id', 'COM:Id', 'LOC:Id', 'ADD:Id']
    for elem in first:
        ret[elem].append(conflicts[elem][0])
    
    #for name it's not a problem, just discard if it is like 'csvimput_'
    if('csvimport' in conflicts["ATT:Name"][0]):
        ret["ATT:Name"].append(conflicts["ATT:Name"][1])
    else:
        ret["ATT:Name"].append(conflicts["ATT:Name"][0])
    
    #for parking area (bool) keep true if at least one of them is true
    ret["ATT:ParkingArea"].append(conflicts["ATT:ParkingArea"][0] or conflicts["ATT:ParkingArea"][1])
    
    #for description keep the longer
    if(len(conflicts["ATT:Description"][0]) >= len(conflicts["ATT:Description"][1])):
        ret["ATT:Description"].append(conflicts["ATT:Description"][0])
    else:
        ret["ATT:Description"].append(conflicts["ATT:Description"][1])
    
    #keep the value of the first element if they exists
    firstIfExist=['ATT:Type', 'COM:Name', 'COM:OpeningHours', 'COM:Url']
    for elem in firstIfExist:
        if(conflicts[elem][0] != ""):
            ret[elem].append(conflicts[elem][0])
        else:
            ret[elem].append(conflicts[elem][1])
    if(conflicts["COM:Price"][0] != -1):
        ret["COM:Price"].append(conflicts["COM:Price"][0])
    else:
        ret["COM:Price"].append(conflicts["COM:Price"][1])
    
    #for telephone keep both if they are not the same 
    #TODO: maybe do a function to compare exactly the telephone number?
    if(conflicts["COM:Telephone"][0] != conflicts["COM:Telephone"][1]):
        if(conflicts["COM:Telephone"][0] != "" and conflicts["COM:Telephone"][1] != ""):
            ret["COM:Telephone"].append(str(conflicts["COM:Telephone"][0]) + ", " + str(conflicts["COM:Telephone"][1]))
        elif(conflicts["COM:Telephone"][0] != ""):
            ret["COM:Telephone"].append(str(conflicts["COM:Telephone"][0]))
        elif(conflicts["COM:Telephone"][1] != ""):
            ret["COM:Telephone"].append(str(conflicts["COM:Telephone"][1]))
    else:
        ret["COM:Telephone"].append(str(conflicts["COM:Telephone"][0]))
    
    #for latitude and longitude I keep the one with more digits choosing them in block
    if(len(str(conflicts["LOC:Latitude"][0])) >= len(str(conflicts["LOC:Latitude"][1]))):
        ret["LOC:Latitude"].append(conflicts["LOC:Latitude"][0])
        ret["LOC:Longitude"].append(conflicts["LOC:Longitude"][0])
    else:
        ret["LOC:Latitude"].append(conflicts["LOC:Latitude"][1])
        ret["LOC:Longitude"].append(conflicts["LOC:Longitude"][1])
    
    #for the address elements i choose them in block as before choosing the one with more filled elements
    address = ['ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    cont0 = 0
    cont1 = 0
    for elem in address:
        if(str(conflicts[elem][0]) != "-1" and str(conflicts[elem][0]) != ""):
            cont0 += 1
        if(str(conflicts[elem][1]) != "-1" and str(conflicts[elem][1]) != ""):
            cont1 += 1
    if(cont0 >= cont1):
        for elem in address:
            ret[elem].append(conflicts[elem][0])
    else:
        for elem in address:
            ret[elem].append(conflicts[elem][1])

    return ret
        

def remove_name_duplicate_jaro(oldDataset):
    #TODO: find out if it really deletes only duplicates
    #In total we found 26 duplicates (after the removeNameDuplicates function)
    count=0
    list_j=[]
    list_i=[]
    true_dataset = {}
    for elem in oldDataset:
        true_dataset[elem]=[]
    list_names_dataset=[]
    #words that need to be delete to have a good similarity
    #this one contains all the word that seems parasite
    deletewords=['centro','sci',' di ','fondo','lago ','malga','cascata','percorso','il ','area','campitello','passo',
        'panorama',' col ',' san ','pozza','trekking',' al ','rifugio','sasso','dolomiti','park','noleggio','ufficio','skipass',
        ' bar ','ristorante','campeggio','camping','sport',' delle ','passeggiata','sentiero','dosso','itinerario','monte','scuola',
        'italiana','palaghiaccio','comunale','castello','baita','piramidi', 'monte', 'itinerario', 'malga', 'canyoning', 
        'torrente', 'giro', 'palestra', 'artificiale', 'naturale', 'panorama']
    #sometimes we can have this problem:"Trekking delle cave" and "Trekking del Vajolet" and it' doesn't delete del and delle
    importantwords=[' delle ',' del ']
    for i in range(0,len(oldDataset["ATT:Name"])-1):
        for j in range(i+1,len(oldDataset["ATT:Name"])):
            moti=oldDataset["ATT:Name"][i].lower()
            motj=oldDataset["ATT:Name"][j].lower()
            #delete parasite words
            for word in deletewords:
                #only delete the word if it's inside the 2 names so that we can make the difference when the word is a parasite and when it help to distinguish between 2 names
                #ex :Centro sci di fondo Canazei and Dolomiti Park Canazei Belvedere if we don't add the if it will only keep canazei and will think it's similar
                if (word in moti and word in motj or word in importantwords):
                    moti=moti.replace(word,' ')
                    motj=motj.replace(word,' ')
            similarity=round(jaro_distance(moti,motj),6)
            # exceptions
            if('corno' in moti or 'corno' in motj): similarity=0
            if('venegiota' in moti or 'venegiota' in motj): similarity=0
            if('bondo' in moti or 'bondo' in motj): similarity=0
            if(similarity>0.90):
                #it means that the two elements "are the same"
                stri=''
                strj=''
                for e in oldDataset:
                    stri += str(e) + ": "+str(oldDataset[e][i])+", "
                    strj += str(e) + ": "+str(oldDataset[e][j])+", "
                list_i.append(stri)
                list_j.append(strj)
                count+=1
                # print(oldDataset["ATT:Name"][i] not in list_names_dataset)
                if(oldDataset["ATT:Name"][i] not in list_names_dataset):
                    # print("done")
                    # print(oldDataset["ATT:Name"][i])
                    # print(list_names_dataset)
                    for elem in oldDataset:
                        true_dataset[elem].append(oldDataset[elem][i])
                    list_names_dataset.append(oldDataset["ATT:Name"][i])
                    list_names_dataset.append(oldDataset["ATT:Name"][j])
                    #if some element which are detected as similarity were add inside the Dataset they must be deleted
                #we can use name since there are no duplicates
                #first remove both elements, then add the single one (can be made of combination between the two)
                namei = oldDataset["ATT:Name"][i]
                namej = oldDataset["ATT:Name"][j]
                if(namej in list_names_dataset and namei in list_names_dataset):
                    if(namej in true_dataset["ATT:Name"] and namei in true_dataset["ATT:Name"]):
                        indexj = true_dataset["ATT:Name"].index(namej)
                        compare = {}
                        for elem in oldDataset:
                            compare[elem]=[]
                            compare[elem].append(oldDataset[elem][j])
                            del true_dataset[elem][indexj]
                        indexi = true_dataset["ATT:Name"].index(namei)
                        #elements to compare (duplicates)
                        for elem in oldDataset:
                            compare[elem].append(oldDataset[elem][i])
                            del true_dataset[elem][indexi]
                        toAdd = solveConflict(compare)                        
                        for elem in oldDataset:
                            true_dataset[elem].append(toAdd[elem][0])
                # if(namej in list_names_dataset):
                #     if(namej in true_dataset["ATT:Name"]):
                #         #index of the element to remove from the true dataset
                #         indexj = true_dataset["ATT:Name"].index(namej)
                #         for elem in oldDataset:
                #             del true_dataset[elem][indexj]
                # print("------"+str(i))
                # print(similarity)
                # print(oldDataset["ATT:Name"][i]+" / "+str(moti))
                # print(oldDataset["ATT:Name"][j]+" / "+str(motj))
            else:
                if(oldDataset["ATT:Name"][i] not in list_names_dataset):
                    for elem in oldDataset:
                        true_dataset[elem].append(oldDataset[elem][i])
                    list_names_dataset.append(oldDataset["ATT:Name"][i])
                if(oldDataset["ATT:Name"][j] not in list_names_dataset):
                    for elem in oldDataset:
                        true_dataset[elem].append(oldDataset[elem][j])
                    list_names_dataset.append(oldDataset["ATT:Name"][j]) 
    # print(count)
    # for i in range(0, len(list_i)):
    #     print("-----------------------")
    #     print(list_i[i])
    #     print(list_j[i])
    return true_dataset

def jaro_distance(s1, s2): 
    # If the s are equal
    if (s1 == s2):
        return 1.0
    # Length of two s
    len1 = len(s1)
    len2 = len(s2)
    # Maximum distance upto which matching
    # is allowed
    max_dist = floor(max(len1, len2) / 2) - 1
    # Count of matches
    match = 0
    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)
    # Traverse through the first
    for i in range(len1):
        # Check if there is any matches
        for j in range(max(0, i - max_dist),
                       min(len2, i + max_dist + 1)):   
            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break
    # If there is no match
    if (match == 0):
        return 0.0
    # Number of transpositions
    t = 0
    point = 0
    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):
 
            # Find the next matched character
            # in second
            while (hash_s2[point] == 0):
                point += 1
 
            if (s1[i] != s2[point]):
                t += 1
            point += 1
    t = t//2
    # Return the Jaro Similarity
    return (match/ len1 + match / len2 +
            (match - t) / match)/ 3.0

#try to add Postal Code where they are missed based on the commune information of the other elements
#input: the dataset
def addPostalCode(dataset):
    postalCodes = {}
    length = len(dataset["ATT:Id"])
    for i in range(0, length):
        com = dataset["ADD:Commune"][i]
        pc = dataset["ADD:PostalCode"][i]
        if(com != "" and pc > 10000 and com not in postalCodes):
            #save this mapping
            postalCodes[com] = pc
    for i in range(0, length):
        com = dataset["ADD:Commune"][i]
        pc = dataset["ADD:PostalCode"][i]
        if(com != "" and pc < 10000 and com in postalCodes):
            #add the postal code
            dataset["ADD:PostalCode"][i] = postalCodes[com]
    return dataset

#assign IDs to each entity
#input: the dataset already with the final schema, cleaned, casted and without attraction duplicates
#output: the dataset with correct ids assigned to it
def assignId(dataset):
    length = len(dataset["ATT:Id"])
    #Location
    cont = 0
    #keys pairs of loc and lon, values the ids assigned
    locations = {}
    for i in range(0, length):
        lat = str(dataset["LOC:Latitude"][i])
        lon = str(dataset["LOC:Longitude"][i])
        if (lat,lon) not in locations:
            locations[(lat,lon)] = cont
            cont +=1
        # else:
            # print("Couple "+str((lat,lon)) + "already exists, id: "+str(locations[(lat,lon)]))
        dataset["LOC:Id"][i] = str(locations[(lat,lon)])
    
    #Address
    cont = 0
    address = {}
    for i in range (0, length):
        a = (str(dataset['ADD:City'][i]), str(dataset['ADD:Commune'][i]), str(dataset['ADD:PostalCode'][i]), str(dataset['ADD:Province'][i]), str(dataset['ADD:Street'][i]), str(dataset['ADD:StreetNumber'][i]))
        if a not in address:
            address[a] = cont
            cont +=1
        # else:
        #     print("Couple "+str(a) + "already exists, id: "+str(address[a]))
        dataset["ADD:Id"][i] = str(address[a])
    
    #Attraction
    cont = 0
    for i in range(0, length):
        dataset["ATT:Id"][i] = str(cont)
        cont +=1
    
    #Company
    cont = 0
    companies = {}
    for i in range(0, length):
        com = (str(dataset['COM:Name'][i]), str(dataset['COM:OpeningHours'][i]), str(dataset['COM:Price'][i]), str(dataset['COM:Telephone'][i]), str(dataset['COM:Url'][i]))
        if com not in companies:
            companies[com] = cont
            cont += 1
        # else:
        #     print("Couple "+str(com) + "already exists, id: "+str(companies[com]))
        dataset["COM:Id"][i] = str(companies[com])
    
    return dataset

def save_CSV(dataset):
    
    column_names = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    dataset_JSON=pd.DataFrame(dataset,columns=column_names)
    #dataset_JSON.to_csv(r'dataset.csv',sep=';',index=False, encoding='utf-8-sig')
    #location
    dataset_location=pd.DataFrame(dataset_JSON[['LOC:Id','LOC:Latitude','LOC:Longitude']])
    dataset_location.drop_duplicates(subset="LOC:Id",keep='first',inplace=True)
    dataset_location.to_csv(r'location.csv',sep=';',index=False, encoding='utf-8-sig')
    #addresse    
    dataset_addresse=pd.DataFrame(dataset_JSON[['ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']])
    dataset_addresse.drop_duplicates(subset="ADD:Id",keep='first',inplace=True)
    dataset_addresse.to_csv(r'addresse.csv',sep=';',index=False, encoding='utf-8-sig')
    #attraction
    dataset_attraction=dataset_JSON[['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','LOC:Id','ADD:Id']]
    dataset_attraction.to_csv(r'attraction.csv',sep=';',index=False, encoding='utf-8-sig')
    #company
    dataset_JSON['LOC:Id']=len(dataset['ATT:Id'])*['']
    dataset_JSON['ADD:Id']=len(dataset['ATT:Id'])*['']
    dataset_company=pd.DataFrame(dataset_JSON[['COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','ADD:Id']])
    dataset_company.drop_duplicates(subset="COM:Id",keep='first',inplace=True)
    dataset_company.to_csv(r'company.csv',sep=';',index=False, encoding='utf-8-sig')

#BEGIN SCRIPT SECTION
dataset = mergeAllDatasets()
dataset = cleanDataset(dataset)
dataset = castDataset(dataset)
dataset = removeDuplicates(dataset)
dataset = addPostalCode(dataset)
dataset = assignId(dataset)
# cf.printDataset(dataset, False)
save_CSV(dataset)
