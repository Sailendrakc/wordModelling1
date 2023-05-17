import newUtilities
import random
import re

# Path of folder that contains raw childes files
inFolder = r'C:\Users\saile\OneDrive\Desktop\wordModelling\childesRAW'

# Path of destination folder where clean childes should be stored
outFolder = r'C:\Users\saile\OneDrive\Desktop\wordModelling\childOnly'

# Set this to True inorder to exclude vocab spoken by child
excludeChildVocab = False

#Set this to true to exclude vocab spoken by other than child
excludeNonChildVocab = True

# This function take a folder containing raw conversations and cleans accordingly.
# one input file == 1 conversation == 1 output file.
def cleaner(inputFolder, outFolder, subfiles):
    listOfTxtFiles =  newUtilities.getAllFilePath(inputFolder, subfiles, '.cha')
    print(listOfTxtFiles)

    #now open them line by line and clean it and put in outfut folder.
    for filee in listOfTxtFiles:
        childLineToFile(filee, outFolder)

# This function extracts the lines of conversation and puts into a file
def childLineToFile(path, outFolder = outFolder):
    with open(path, "r", encoding = 'utf-8') as file1:
        print(".Opening File: " + path + "\n")

        # This variable stores the vocab we are interested in
        exposedWords = ''

        #This variable stores age of child, so we can save age information in file name.
        ageStr = ''

        #Go line by line and clean
        for line in file1:
            if ageStr == '' and line.startswith('@ID:') and 'CHI' in line:
                ageStr = line.split('|')[3].replace(';', 'Y').replace('.', 'M')
                ageStr += 'D'
                
            if line.startswith('*'):
                if excludeChildVocab == True and line.startswith('*CHI:'):
                    continue

                if excludeNonChildVocab == True and line.startswith('*CHI:') == False:
                    continue

                words = re.sub(r'[^a-zA-Z\s]', '', line).split()# split the sentence into words
                if(len(words) == 0):
                    continue
                cleanLine = " ".join(words[1:])
                if cleanLine == '':
                    continue
                exposedWords += cleanLine + '\n'
    

        if(ageStr == ''):
            print("Cannot extract age for: " + path)
            return
        if exposedWords.strip() == '':
            print("Empty convo, ignoring..")
            return
        #Make a file out of childWords
        newFileName = outFolder + "/"+ ageStr + "_"+str(random.randint(1000, 10000))+ ".txt"
        with open(newFileName, "w", encoding = 'utf-8') as outfile:
            outfile.write(exposedWords)
        print("... One convo extracted ... \n")
        
 

# Calling of main function and cleaning raw childes.
cleaner(inFolder, outFolder, True)