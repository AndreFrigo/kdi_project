import re

#print the dataset as in the csv files, if 'number' is true it prints the element number
def printDataset(dataset, number=False):
    print("PRINTING DATASET\n\n")
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