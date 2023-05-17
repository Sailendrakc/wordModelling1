
from dumpObject import dobj
import os
import glob
import string
import matplotlib.pyplot as plt
import pandas as pd 
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

#Lemetizer and Stemmer
wordnet_lemmatizer = WordNetLemmatizer()
porter_stemmer = PorterStemmer()

nltk.download('wordnet')
nltk.download('omw-1.4')

# this function returns token, typecount and type set ( unique word list) from a  text file file
def readTxtData(path: str, lemmatize) -> dobj:
        
        if(type(path) is not str):
             raise Exception("Some paths in lists are not valid path. Path should be string")

        if path is None or not os.path.exists(path):
            raise Exception("Please provide a valid path.")

        #Object to store text attributes like token, types and unique word set
        wordSet = dobj()
        wordSet.totalWordCount = 0
        wordSet.uniqueWordCount = 0

        #Raw words is the list that contains all the words from file
        wordSet.rawWords = []

        # Open file
        with open(path, "r") as file1:

            #Create a dictionary to replae the punctuation from the sentence.
            punc = str.maketrans('','', string.punctuation)

            # Remove apostrophie from make trans dictionary so it wont be translated to None.
            apostrophieUnicode = 39
            del punc[apostrophieUnicode]

            # Read and extract into a set
            for line in file1:
                word_list_from_line = refineLine(line, punc, lemmatize)
                wordSet.rawWords.extend(word_list_from_line)

        wordSet.uniqueWordSet = set(wordSet.rawWords)
        wordSet.uniqueWordCount = len(wordSet.uniqueWordSet)
        wordSet.totalWordCount = len(wordSet.rawWords)

        # Return the set
        return wordSet

#This method is used to remove whitespaces and punctuation from a string and it returns a list of words.
# If lemmatize is set to false, the words will be stemmized, as default, lemmatize is set to true.
def refineLine(line: str, punctuationDict: dict = None, lemmatize = None) -> list:

    punc = punctuationDict
    if punctuationDict is None:
        punc = str.maketrans('','', string.punctuation)

        # Remove apostrophie from make trans dictionary so it wont be translated to None.
        apostrophieUnicode = 39
        del punc[apostrophieUnicode]

    wordList =  line.lower().strip("' ").translate(punc).split()
    if lemmatize == None:
        return wordList
    else:
        if lemmatize:
            lemmatizeList = []
            for word in wordList:
                lemmatizeList.append(wordnet_lemmatizer.lemmatize(word))
            return lemmatizeList
        else:
            stemmizedList = []
            for word in wordList:
                stemmizedList.append(porter_stemmer.stem(word))
            return stemmizedList

# this function gets all the .txt files inside a given folder
def getAllFilePath(pathOfFolder: str, recursive = False ,extension = '.txt') -> list:
        if pathOfFolder is None or not os.path.exists(pathOfFolder):
            raise Exception("Please provide a valid path.")

        extensionString = "/*"+ extension
        if recursive:
            extensionString = "/**" + extensionString

        files = glob.glob(pathOfFolder + extensionString, recursive = recursive)
        poolOfFiles = []
        # loop through list of files
        for f in files:
            poolOfFiles.append(f)

        return poolOfFiles


# this function takes a list of txt files and samples it.
def SampleConversation(paths : list, lemitize = None, stoplist = {}) -> dobj:
        # read all the files and sample them

        subSample = []

        for path in paths:
            subSample.append(readTxtData(path, lemitize))

        #Now subsample contains word count and unique word count ( number of token and types)
        #We can caluclate average or whatever from this data.

        finalsample = dobj()
        finalsample.uniqueWordSet = {}
        finalsample.totalWordCount = 0
        finalsample.inputs = paths;
        finalsample.allWordList = []

        
        for elem in subSample:
            finalsample.allWordList.extend(elem.rawWords)

        finalsample.allWordList = [word for word in finalsample.allWordList if word not in stoplist]
        finalsample.uniqueWordSet = set(finalsample.allWordList)    #.difference(set(stoplist))
        finalsample.uniqueWordCount = len(finalsample.uniqueWordSet)
        finalsample.totalWordCount  = len(finalsample.allWordList)

        return finalsample


def sampleTwoSamplings(sample1, sample2):

    if sample1 is None:
        return sample2

    if sample2 is None:
        return sample1
        
    finalsample = dobj()
    
    finalsample.totalWordCount = sample1.totalWordCount + sample2.totalWordCount
    finalsample.uniqueWordSet = set().union(sample1.uniqueWordSet).union(sample2.uniqueWordSet)
    finalsample.uniqueWordCount = len(finalsample.uniqueWordSet)

    #Also combine the dataframe.
    if hasattr(sample1, 'matrixDf') and hasattr(sample2, 'matrixDf') == False:
        finalsample.matrixDf = sample1.matrixDf

    if hasattr(sample2, 'matrixDf') and hasattr(sample1, 'matrixDf') == False:
        finalsample.matrixDf = sample2.matrixDf

    if hasattr(sample1, 'matrixDf') and hasattr(sample2, 'matrixDf'):
        finalsample.matrixDf = pd.merge(sample1.matrixDf, sample2.matrixDf, left_index=True, right_index=True, how='outer')
        finalsample.matrixDf = finalsample.matrixDf.fillna(0)
        finalsample.matrixDf = finalsample.matrixDf.astype(int)

    return finalsample


# This function will graph a simulation(list of [daily samples, label]) or list of simulations.
# All simulations should have equal number of samplings in them. 
def graphsimulationData(simulationDataList, plot = False, saveasCSV= False, savingFileName = 'graphData.csv'):
    if simulationDataList == None or len(simulationDataList) < 1:
        raise Exception("Please pass a valid simulation data list to plot")
    print("Graphing data")
    #Prepare data
    days = None
    try:
        days = range(1, len(simulationDataList[0][0]) + 1)
    except:
        raise Exception("Please put valid data and label for graphing. It should be a list of list like, [[graphngdata1, lable1], [graphingdata2, label2]]." +
            "Labels should not be same")

    plt.xlabel('Days')
    plt.ylabel('Words')

    fieldsForCSV = {}

    for simulations in simulationDataList:
        dailyUniqueWordCountList =[]
        dailyTotalWordCountList = []

        for sample in simulations[0]:
            dailyUniqueWordCountList.append(sample.uniqueWordCount)
            dailyTotalWordCountList.append(sample.totalWordCount)
        _label = ''
        try:
           _label = simulations[1]
        except:
            raise Exception("Please put valid label for graphing. It should be a list of list like, [[graphngdata1, lable1], [graphingdata2, label2]]." +
            "Labels should not be same and should start with an alphabet and not like '_dog' ")
        if saveasCSV:
            fieldsForCSV[_label] = dailyUniqueWordCountList
        #Plot
        if plot:
            print(_label)
            plt.plot(days, dailyUniqueWordCountList, label = _label) #or use totalWords to plot total words 
            plt.legend(loc="upper left")
    
    if plot:
        plt.show()

    #Save as csv
    if saveasCSV:
        # dictionary of lists  
        df = pd.DataFrame(fieldsForCSV) 
        # saving the dataframe 
        df.to_csv(savingFileName) 
        print(savingFileName + " file saved!")


#This takes exposure dataframe and calculates on which day a token reached exposure threshold and appends it in new column.
def findAndAppendLearntDay(df, threshold):
    # Loop through each row and column in reverse order
    learntDay = []
    average = []
    realIndex = 0
    for index, row in df.iterrows():
        days = 0 
        rawThres = 0
        thresholdReached = False
        for column in reversed(df.columns):
            rawThres +=  row[column]
            days += 1
            if rawThres >= threshold:
                thresholdReached = True
                break
        if thresholdReached == True:
            learntDay.append(days)
        else:
            learntDay.append(0)

        row_list = row.values.tolist()
        del row_list[0]
        avg = sum(row_list) / len(row_list)
        average.append(avg);
        realIndex += 1

    df = df.assign(Learned_Day = learntDay)
    df = df.assign(avg_exposure_perDay = average)
    return df


# This method will take list of dataframes and combines them and averages the word count.
# Use this method to combine and average the result of exposure count matrix.
def dfUnion(dfList):
    mainMatrix = 0
    listLen = len(dfList)
    for i in range(listLen):
        elem = dfList[i]
        if i == 0:
            mainMatrix = elem
            continue
        else: 
            merged_df = pd.concat([mainMatrix, elem], axis='columns').fillna(0)
            merged_df = merged_df.groupby(level=0, axis=1).sum()
            mainMatrix = merged_df

    numeric_cols = mainMatrix.select_dtypes(include=['int', 'float']).columns
    #numeric_cols = mainMatrix.iloc[:, 1:]
    mainMatrix[numeric_cols] = mainMatrix[numeric_cols] / listLen

    return mainMatrix