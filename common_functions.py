import re

#print the dataset as in the csv files, if 'number' is true it prints the element number
#input: the dataset to print (a dictionary with keys the schema elements and values the list of attribute elements), the boolean for printing the object number
def printDataset(dataset, number=False):
    print("PRINTING DATASET\n")
    print('SCHEMA\n')
    schema = [el for el in dataset]
    print(schema)
    print('\n')
    #number of objects, it is supposed that the first column is complete
    numElem = len(dataset[schema[0]])
    i=0
    while(i<numElem):
        if(number): print('OBJECT '+str(i)+'\n')
        row = '\''
        for elem in schema:
            try:
                row += str(dataset[elem][i])+"\', '"
            except:
                row += "\', '"
        print(row[:-3])
        print('\n\n')
        i+=1

#get a list with the name of the csv files
#input: txt file containing the list (ls CSV_POI > csv.txt), default 'csv.txt'
#output: list containing the name of the csv files
def getListCSV(csvList='csv.txt'):
    with open(csvList) as f:
        csv_files = f.readlines()
        return [e.rstrip() for e in csv_files]



#cast a list of strings into a list of floats
#input: the list of string elements to be cast, the default value for missing elements (blanks)
def castFloat(listElem, default):
    ret = []
    for elem in listElem:
        #the string is an integer or float
        if(re.match('^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$', elem)):
            ret.append(float(elem))
        else:
            ret.append(float(default))
    return ret

#cast a list of strings into a list of positive integers
#input: the list of string elements to be cast, the default value for missing elements (blanks)
def castInt(listElem, default):
    ret = []
    for elem in listElem:
        #the string is an integer or float
        if(re.match('^[0-9]+$', elem)):
            ret.append(int(elem))
        else:
            ret.append(int(default))
    return ret

#list of interesting categories for both csv and json files
#input: txt file with the interesting categories
#output: the list of interesting categories
def getInterestingCategories(interestingCategoriesFile='categories.txt'):
    ret = []
    try:
        with open(interestingCategoriesFile) as f:
            intCat = f.readlines()
            for elem in intCat:
                ret.append(elem.rstrip())
    except:
        pass
    return ret
