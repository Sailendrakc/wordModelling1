
from dumpObject import dobj
import newUtilities
import random
import math
import pandas as pd 
from collections import Counter
import os
import time

# -----------OPTIONS ------------
# First we provide the necessary options to run

# This is the full path to the folder where books as .txt files are stored
bookFolderPath = r'C:\Users\saile\OneDrive\Desktop\wordModelling\Books'

#This is the full path to the folder where convo as .txt files are stored [clean childes files]
convoFolderPath = r'C:\Users\saile\OneDrive\Desktop\wordModelling\cleanChildes'

#This is the number of books to feed the child per day
booksPerInteraction = 0

#This is the number of convos to feed the child per day
convoPerInteraction = 3

# This is the number of interaction per one simulation.
totalInteractionPerSimulation =3

# This is the number of simulation per iteration. All iterations data are averaged.
totalSimulationPerIteration = 5

# This flag if set to true will print averaged numbers to the console.
printAveragedNumbers = False

# When This flag is set to true, lemitize will be performed, when false, stemmizing will be performed,
# when None, no lemitize or stemming will be performed.
lemitize = True

#This set will act as stopList. Meaning we will ignore any words that are here in this set. 
stopList = {'a', 'the', 'an'}

# This is the age of child, it is an integer
childAge =3

#------------ PRORAM VARIABLES -----------#
#When true, the averaged exposure matrix will be saved as csv.
saveExposureMatrixAsCSV = True

#This is the exposure threshold.
learnThreshold = 10

# Set this true and the program will save one additional minified version of DTM. 
# This minified version will contain unique words, learnt day and average exposure per day.
saveMinifiedDTM = True

# This stores the list of simulations that are sampled using above options
outputLog = 'Program Start \n'

# This stores the list of test logs.
testLog = ''
printTestLog = True

# ----------- INPUT VALIDATION -----------#
# For now validation will be part of the function that takes that input.

def sampleGroupForXdays():

    #Get all convo and books that are to be used for sampling
    listOfAllBooks =  newUtilities.getAllFilePath(bookFolderPath)
    listOfAllConvos = newUtilities.getAllFilePath(convoFolderPath)

    #All books can be used but there can be age filter for conversation so not all convos can be sampled.
    listOfBooks = listOfAllBooks
    listOfConvos = []

    # Only select convos with child of certain age
    for baseName in listOfAllConvos:
        filename = os.path.basename(baseName)
        if 'Y' in filename:
            year = int(filename.split('Y')[0])

            if year == childAge:
                listOfConvos.append(baseName)


    #Randomize the conversation list to sample
    random.shuffle(listOfConvos)

    #Sampling variables
    interaction = 1
    convoLen = len(listOfConvos)
    bookLen = len(listOfBooks)
    convoPointer = 0
    bookPointer = 0

    lastBaseSample = None

    baseSimulation = []

    #Now Start Sampling books and apply all options per sampling.
    while interaction <= totalInteractionPerSimulation:
        #Do the sampling.

        if bookPointer == bookLen or convoPointer == convoLen:
            break

        #To store a list convo files to perform base sampling
        newBaseList = []
        tempNewConvos = convoPerInteraction
        tempNewBooks = booksPerInteraction
        notEnough = False

        # Generate a list of convo files to perform base sampling
        while tempNewConvos > 0:
            newBaseList.append(listOfConvos[convoPointer])
            convoPointer += 1
            tempNewConvos -=1
            if convoPointer == convoLen:
                notEnough = True
                print('Not enought convo to sample, sampling wiil stop')
                break

        while tempNewBooks > 0:
            newBaseList.append(listOfBooks[bookPointer])
            bookPointer += 1
            tempNewBooks -= 1
            if bookPointer == bookLen:
                notEnough = True
                print('Not enought book to sample, sampling wiil stop')
                break
               
        if notEnough:
            break
        global outputLog
        outputLog += " Doing sampling for Interaction: " + str(interaction) + "\n"

        outputLog += "These inputs were used in samplings: \n"
        for links in newBaseList:
            outputLog += "    " + links + " \n"

        time11 = time.time()
        #Generate base sampling 
        baseSampling = newUtilities.SampleConversation(newBaseList, lemitize, stopList)
        time12 = time.time()

        global testLog
        testLog += " sample convo time taken: " + str(time12-time11) + " \n"

        #Perform analysis for later creation of DTM.

        #create the df for exposure count
        baseSampling.matrixDf = pd.DataFrame(columns = ['Interaction', 'transcipt'])
        #baseSampling.matrixDf = baseSampling.matrixDf.append({'Day': day, 'transcipt': baseSampling.allWordString}, ignore_index = True)

        #Vectorize it.
        word_count = Counter(baseSampling.allWordList)
        baseSampling.matrixDf = pd.DataFrame.from_dict(word_count, orient='index', columns=['Interaction : ' + str(interaction)])

        # Sample yesterday sampling and todays sampling for all three kinds of samplings
        finalBaseSampling = newUtilities.sampleTwoSamplings(baseSampling, lastBaseSample)
        outputLog += "BASE: tokens: " + str(finalBaseSampling.totalWordCount) + " and types (unique) : " + str(finalBaseSampling.uniqueWordCount) + "\n"


        lastBaseSample = finalBaseSampling
        outputLog += "sampling for interaction " + str(interaction) + " is done. \n"
        outputLog += " \n"

        # Store the samplings
        baseSimulation.append(finalBaseSampling)
        
        interaction += 1

    return baseSimulation

def SampleGroupForXDaysNTimes():

    # This list only stores average unique and total numbers as we are going to average n numbers of samples.
    baseIterationNumbers = []

    ntimes = 0
    last_ExposureMatrix_of_eachSimulations = []

    while ntimes < totalSimulationPerIteration:
        ntimes += 1
        
        time11 = time.time()
        simulationResult = sampleGroupForXdays()
        time12 = time.time()

        global testLog
        testLog += " whole sampling of x days time taken: " + str(time12-time11) + " \n"

        actualInteractionsPerThisSimulation = len(simulationResult)

        if actualInteractionsPerThisSimulation != totalInteractionPerSimulation:
            print("Actual interactions per simulation is only (due to not enough input): " 
                  + str(actualInteractionsPerThisSimulation) + " instead of: " + str( totalInteractionPerSimulation ))

        matrixToPrint = simulationResult[actualInteractionsPerThisSimulation -1].matrixDf
        matrixToPrint = newUtilities.findAndAppendLearntDay(matrixToPrint, learnThreshold)
        print(matrixToPrint)
        last_ExposureMatrix_of_eachSimulations.append(matrixToPrint)

        #Loop and average
        print(" \n" + str(ntimes) + " simulation done. \n")


        for days in range(0, actualInteractionsPerThisSimulation):

            if len(baseIterationNumbers) == days:

                # Creating objet to store uniqe and total words for each day 
                # for all three types of samplings and storing them to revalent list
                baseDobj = dobj()
                baseDobj.totalWordCount = 0
                baseDobj.uniqueWordCount = 0

                baseIterationNumbers.append(baseDobj)

            #Adding all day1's and day2's .... dayN's unique and total word count together.
            # We divide this total number by n times to calculate the average 

            #Example:

            # simulation 1 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 2 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 3 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 4 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 5 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # ++(summation)=  ------------------------------------------------------------------

            #ITERATION Numbers =[Sum(day1's) ,sum(day2's) , sum(day3's), sum(day4's) ,sum(day5's)] #

            baseIterationNumbers[days].totalWordCount += simulationResult[days].totalWordCount
            baseIterationNumbers[days].uniqueWordCount += simulationResult[days].uniqueWordCount
    
    # Here we divide above summation to calculate average
    # So,  #ITERATION Numbers =[Sum(day1's) ,sum(day2's) , sum(day3's), sum(day4's) ,sum(day5's)] 
    # Every items of #ITERATION Numbers are being divided by total number of simulation.
    print("\n Averaging iterations \n")
    divisor = totalSimulationPerIteration
    for dayx in range(0, actualInteractionsPerThisSimulation):
        baseIterationNumbers[dayx].totalWordCount = baseIterationNumbers[dayx].totalWordCount / divisor
        baseIterationNumbers[dayx].uniqueWordCount = baseIterationNumbers[dayx].uniqueWordCount / divisor 

    print(outputLog)
    if printTestLog:
        print("########################### \n")
        print(testLog)

    #Saving in CSV
    mainExposureMatrix = None
    if saveExposureMatrixAsCSV:
        mainExposureMatrix = newUtilities.dfUnion(last_ExposureMatrix_of_eachSimulations)
        print("Saving the averaged exposure matrix as csv")
        mainExposureMatrix.to_csv("averagedExposureMatrix.csv")

    if saveMinifiedDTM:
        if mainExposureMatrix is None:
            mainExposureMatrix = newUtilities.dfUnion(last_ExposureMatrix_of_eachSimulations)
        print("Saving the minified version of DTM")
        columns_to_keep =  list(mainExposureMatrix.columns[-2:])
        minifiedDTM = mainExposureMatrix[columns_to_keep]

        minifiedDTM.to_csv("mini_avgExposureMatrix.csv")
   
    #Now graph and save the simulations
    newUtilities.graphsimulationData([[baseIterationNumbers, "baseCurve"]], True)


SampleGroupForXDaysNTimes()