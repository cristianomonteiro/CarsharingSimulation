import numpy as np

def binarySearchAggregated(x, search_list):
    search_list.sort()
    
    left = 0 # Determines the starting index of the list we have to search in
    right = len(search_list)-1 # Determines the last index of the list we have to search in
    mid = int((right + left)/2)

    while search_list[mid] != x and right > left : # If this is not our search element or it there isn't in the list
        # If the current middle element is less than x then move the left next to mid
        # Else we move right next to mid
        if  search_list[mid] < x:
            left = mid + 1
        else:
            right = mid - 1
            
        mid = int((right + left)/2)
    
    return max(0, mid)

def generateTicks(arrayData, secondArrayData=None):
    axisData = arrayData.copy()
    #If the Figure is composed by more than one plot
    if secondArrayData != None:
        axisData.extend(secondArrayData)
    
    minValue = min(axisData)
    maxValue = max(axisData)
    
    numTicks = 6
    if maxValue < 100:
        numTicks = 10
    elif maxValue < 1000:
        numTicks = 9
    
    if len(axisData) < numTicks:
        ticks = [round(x) for x in axisData]
    else:
        #If all values are integers, arange distribute the integer values better
        if all(x == int(x) for x in axisData):
            rangeTicks = maxValue - minValue
            stepTicks = round(rangeTicks/numTicks)
            #If the number of ticks generated will be 30% greater than the expected
            if rangeTicks/stepTicks > numTicks * 1.3:
                stepTicks += 1
            ticks = list(np.arange(start=minValue, stop=maxValue, step=stepTicks))
            ticks.append(maxValue)
        else:
            ticks = np.linspace(start=minValue, stop=maxValue, num=numTicks, endpoint=True)
            ticks = [round(x) for x in ticks]

    #Remove the penultimate item if it is so close to the last
    thresholdPercent = 0.7
    if len(ticks) >= 3 and ticks[-1] - ticks[-2] <= (ticks[-2] - ticks[-3]) * thresholdPercent:
        del ticks[-2]
        ticks = np.linspace(start=minValue, stop=maxValue, num=numTicks, endpoint=False)
        ticks = [round(x) for x in ticks]
        ticks.append(maxValue)
    
    return ticks
