import re

#print the dataset as in the csv files
def printDataset(dataset):
    print("PRINTING DATASET")
    schema = [el for el in dataset]
    print(schema)
    #number of objects, it is supposed that the first column is complete
    numElem = len(dataset[schema[0]])
    i=0
    while(i<numElem):
        row = '\''
        for elem in schema:
            try:
                row += str(dataset[elem][i])+"\', '"
            except:
                row += "\', '"
        print(row[:-1])
        i+=1



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