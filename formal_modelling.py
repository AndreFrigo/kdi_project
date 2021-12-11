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
    commune=filename.split("/")[1]
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
        dataset[elem].extend(oldDataset[elem])
    
    for elem in booleanString:
        dataset[elem].extend(cf.castBool(oldDataset[elem], False))
    
    return dataset

def Read_JSON(jsonFile="POI_Trentino.json"):
    #2892
    column_names = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    line=["","",False,"","","","","",0,"","","",0.0,0.0,"","","",0,"","",0]
    f = open(jsonFile, encoding="utf8")
    # returns JSON object as
    # a dictionary
    dataset=[]
    dataset_JSON=pd.DataFrame(columns=column_names)
    data = json.load(f)
    for i in range(2893):
        line=["","",False,"","","","","",0,"","","",0.0,0.0,"","","",0,"","",""]
        line[1]=data[str(i)]["content"]["objData"]["name"]["IT"]
        line[3]=data[str(i)]["content"]["objData"]["description"]["IT"]
        #+"\n"+data[str(i)]["content"]["objData"]["serviceDescription"]
        line[4]=data[str(i)]["content"]["objData"]["category"]
        if(data[str(i)]["content"]["poiData"]["contact"]!=None and data[str(i)]["content"]["poiData"]["contact"]["name"]!={} ):
            line[6]=data[str(i)]["content"]["poiData"]["contact"]["name"]["IT"]
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
    dataset2,teste = remove_name_duplicate_jaro(dataset)
    print("-------------------------------------------")
    dataset,teste2 = remove_name_duplicate_jaro(dataset2)
    print("teste "+str(teste2))
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

def remove_name_duplicate_jaro(oldDataset):
    #TODO: return the dataset with the necessary removal
    #In total we found 26 duplicates (after the removeNameDuplicates function)
    teste=False
    count=0
    true_dataset = {}
    for elem in oldDataset:
        true_dataset[elem]=[]
    no_duplicates=[]
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
    for i in range(0,len(oldDataset["ATT:Name"])):
        for j in range(i+1,len(oldDataset["ATT:Name"])-1):
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
                teste=True
                list_j=[]
                list_i=[]
                count+=1
                list_i.append(oldDataset["ATT:Id"][i]+", "+oldDataset["ATT:Name"][i])
                list_j.append(oldDataset["ATT:Id"][j]+", "+oldDataset["ATT:Name"][j])
                print(oldDataset["ATT:Name"][i] not in list_names_dataset)
                if(oldDataset["ATT:Name"][i] not in list_names_dataset):
                    print("done")
                    print(oldDataset["ATT:Name"][i])
                    print(list_names_dataset)
                    for elem in oldDataset:
                        true_dataset[elem].append(oldDataset[elem][i])
                    list_names_dataset.append(oldDataset["ATT:Name"][i])
                    list_names_dataset.append(oldDataset["ATT:Name"][j])
                    #if some element which are detected as similarity were add inside the Dataset they must be deleted
                if( oldDataset["ATT:Name"][j] in list_names_dataset):
                    if(oldDataset["ATT:Name"][j] in true_dataset["ATT:Name"]):
                        for elem in oldDataset:
                            true_dataset[elem].remove(oldDataset[elem][j])
                print("------"+str(i))
                print(similarity)
                print(oldDataset["ATT:Name"][i]+" / "+str(moti))
                print(oldDataset["ATT:Name"][j]+" / "+str(motj))
            else:
                if(oldDataset["ATT:Name"][i] not in list_names_dataset):
                    for elem in oldDataset:
                        true_dataset[elem].append(oldDataset[elem][i])
                    list_names_dataset.append(oldDataset["ATT:Name"][i])
                if(oldDataset["ATT:Name"][j] not in list_names_dataset):
                    for elem in oldDataset:
                        true_dataset[elem].append(oldDataset[elem][j])
                    list_names_dataset.append(oldDataset["ATT:Name"][j]) 
    print(count)
    # for i in range(0, len(list_i)):
    #     print("-----------------------")
    #     print(list_i[i])
    #     print(list_j[i])
    return true_dataset,teste

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
def save_CSV(datasets):
    column_names = ['ATT:Id','ATT:Name','ATT:ParkingArea','ATT:Description','ATT:Type','COM:Id','COM:Name','COM:OpeningHours','COM:Price','COM:Telephone','COM:Url','LOC:Id','LOC:Latitude','LOC:Longitude','ADD:Id','ADD:City','ADD:Commune','ADD:PostalCode','ADD:Province','ADD:Street','ADD:StreetNumber']
    dataset_JSON=pd.DataFrame(dataset,columns=column_names)
    dataset_JSON.to_csv(r'trentino_territory.csv',sep=';',index=False, encoding='utf-8-sig')

#BEGIN SCRIPT SECTION
dataset = mergeAllDatasets()
dataset = cleanDataset(dataset)
dataset = castDataset(dataset)
dataset = removeDuplicates(dataset)
save_CSV(dataset)
#cf.printDataset(dataset, True)

# for elem in dataset:
#     print(str(elem)+" "+str(len(dataset[elem])))