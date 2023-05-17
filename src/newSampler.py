
from dumpObject import dobj
import newUtilities
import random
import math
import pandas as pd 
from collections import Counter
import os

# -----------OPTIONS ------------
# First we provide the necessary options to run

#This is the full path to the folder where convo as .txt files are stored [clean childes files]
convoFolderPath = r'C:\Users\saile\OneDrive\Desktop\wordModelling\cleanChildes'

#This is the number of convos to feed the child per day
convoPerInteraction = 2

# This is the number of interaction per one simulation.
totalInteractionPerSimulation =10

# This is the number of simulation per iteration. All iterations data are averaged.
totalSimulationPerIteration = 5

# This flag if set to true will print averaged numbers to the console.
printAveragedNumbers = True

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

# ----------- INPUT VALIDATION -----------#
# For now validation will be part of the function that takes that input.

def sampleGroupForXdays():

    #Get all convo that are to be used for sampling
    listOfAllConvos = newUtilities.getAllFilePath(convoFolderPath)
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
    convoPointer = 0

    lastBaseSample = None

    baseSimulation = []

    #Now Start Sampling books and apply all options per sampling.
    while interaction <= totalInteractionPerSimulation:
        #Do the sampling.
        if convoPointer == convoLen:
            break

        #To store a list convo files to perform base sampling
        newBaseList = []
        tempNewConvos = convoPerInteraction

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
        
        if notEnough:
            break
        global outputLog
        outputLog += " Doing sampling for Interaction: " + str(interaction) + "\n"

        outputLog += "These inputs were used in samplings: \n"
        for links in newBaseList:
            outputLog += "    " + links + " \n"

        #Generate base sampling 
        baseSampling = newUtilities.SampleConversation(newBaseList, lemitize, stopList)

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

    # Save the result as a sampling is complete.
    samplingResult = dobj()
    samplingResult.baseSimulation = baseSimulation

    return samplingResult

def SampleGroupForXDaysNTimes():

    # This list only stores average unique and total numbers as we are going to average n numbers of samples.
    baseIterationNumbers = []

    ntimes = 0
    last_ExposureMatrix_of_eachSimulations = []

    while ntimes < totalSimulationPerIteration:
        ntimes += 1
        simulationResult = sampleGroupForXdays()
        matrixToPrint = simulationResult.baseSimulation[len(simulationResult.baseSimulation)-1].matrixDf
        matrixToPrint = newUtilities.findAndAppendLearntDay(matrixToPrint, learnThreshold)
        print(matrixToPrint)
        last_ExposureMatrix_of_eachSimulations.append(matrixToPrint)

        #Loop and average
        print(" \n" + str(ntimes) + " simulation done. \n")


        for days in range(0, totalInteractionPerSimulation):

            if len(baseIterationNumbers) == days:

                # Creating objet to store uniqe and total words for each day 
                # for all three types of samplings and storing them to revalent list
                baseDobj = dobj()
                baseDobj.totalWordCount = 0
                baseDobj.uniqueWordCount = 0

                baseIterationNumbers.append(baseDobj)

            #Adding all day1's and day2's .... dayN's unique and total word count together for all three sampling types.
            # We divide this total number by n times to calculate the average 

            #Example:

            # simulation 1 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 2 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 3 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 4 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # simulation 5 =    [day1        ,day2 ,       day3,         day4 ,       day5] #
            # ++(summation)=  ------------------------------------------------------------------

            #ITERATION Numbers =[Sum(day1's) ,sum(day2's) , sum(day3's), sum(day4's) ,sum(day5's)] #

            baseIterationNumbers[days].totalWordCount += simulationResult.baseSimulation[days].totalWordCount
            baseIterationNumbers[days].uniqueWordCount += simulationResult.baseSimulation[days].uniqueWordCount
    
    # Here we divide above summation to calculate average
    print("\n Averaging iterations \n")
    for dayx in range(0, totalInteractionPerSimulation):
        baseIterationNumbers[dayx].totalWordCount = math.floor(baseIterationNumbers[dayx].totalWordCount / totalSimulationPerIteration)

        baseIterationNumbers[dayx].uniqueWordCount = math.floor(baseIterationNumbers[dayx].uniqueWordCount / totalSimulationPerIteration)

    print(outputLog)
    
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