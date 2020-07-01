# this has all the methods to test all teh cards, and also nicely display the results
import time
import pandas as pd
import testcards
import math
from functools import reduce
from collections import Counter
import matplotlib.pylab as plt


# This gets each card arrangement
# orders them by size, smallest to largest
def greedyUniqueCounter(a, maxN):
    # Incriments a, with a max of maxN
    if (len(a) == 1):
        if (a[0] == maxN - 1):
            return (-1)
        else:
            return ([a[0] + 1])
    b = -1;
    a[b] = a[b] + 1
    if (a[b] == maxN):
        a = greedyUniqueCounter(a[0:b], maxN)
        if (a == -1):
            return (-1)
        a.append(a[-1])
        return (a)
    return (a)


def testAll(numcards):
    # Test each arrangement of cards
    rowsdict = {}
    keys = []

    a = [1 for i in range(0, numcards)]
    while (a != -1):  # generate all combinations of 1 through 13
        rowsdict[tuple(a)] = testcards.test_a(a)
        a = greedyUniqueCounter(a, 14)

    return (rowsdict)


def rotate_sum(dictdict):
    # rotates a dictionary of dictionaries (i.e. makes inner key outer key), and creates summary statistics
    # The weight is the number of times each class could be dealt out
    # ie 24 if we have 4 unique cards, 1 if 4 cards that all match

    sumsdict = {}
    for key1, value1 in dictdict.items():
        weight = math.factorial(len(key1)) / (reduce((lambda x, y: x * y), map(math.factorial, Counter(key1).values())))
        for key2, value2 in value1.items():
            # targetdict[key2].update({key1: value2}) #This code is for rotating the dictionary, but I just want some summary statistics instead
            sumsdict[key2] = [sum(x) for x in zip(sumsdict.get(key2, [0, 0]), [1, weight])]
            # first entry is count per class, second entry is count per weight
    return sumsdict


# This cell is the useful post processing I'll want for visualization.
# THIS CELL IS HALF DONE!
# it gives results based on chance of dealing it out, mostly, but not quite;
# im not accounting for any duplicity at all, but I'm also not rearraning my numbers, soo....
# I'd say these results are like idk within spitting distance of the real answer
# dictdict is a dictionary of dictionaries
def pretty_results(sumsdict, numcards, numberofmax=10):
    # make a nice graph of all the things I care about
    # takes in a rotated-sum dictionary  explicitly from rotate_sum
    # num cards is number of cards that we're testing

    # Im aware that this function is an absolute mess
    # I don't really know how to improve it
    # breaking it up into lots of little functions would do it, but each function is only used once, so

    #first put it into a dataframe for ease of use
    sums = pd.DataFrame.from_dict(sumsdict, orient='index', columns=['CountClass', 'CountWeight']).sort_index()

    # normalize
    # Count weight is easy- divide by 13**numcards
    countWeightNormalizer = 13 ** numcards
    # Countclass- stars and bars- (13+numcards-1)! choose numcards
    countClassNormalizer = math.factorial(13 + numcards - 1) / (math.factorial(numcards) * math.factorial(13 - 1))

    sums['CountClass'] = sums['CountClass'] / countClassNormalizer
    sums['CountWeight'] = sums['CountWeight'] / countWeightNormalizer
    print('The chance of 24 is \n %s' % sums.transpose()[24])
    # All the post processing happens twice now, once for the 'class' and once for the 'weight'
    # class is default color (blue, probably? i dont care), weight is orange (default second color)

    # Setting up the figure
    fig, axs = plt.subplots(3, 2)
    fig.set_figheight(5)
    fig.set_figwidth(8)
    fig.suptitle('Reverse 24')

    # Plotting integer answers
    xmin = -15
    xmax = 70
    intAnswers = sums[[x.is_integer() and xmin < x < xmax for x in sums.index]]
    xticks = [x for x in range(int(intAnswers.index.min()), int(intAnswers.index.max())) if x % 5 == 0]

    ymax = intAnswers.max()
    axs[0, 0].plot(intAnswers, '.')
    axs[0, 0].vlines(x=xticks, ymin=0, ymax=ymax * 1.2, linestyles='dotted')
    axs[0, 0].set_xticks(xticks[::2])
    axs[0, 0].set_title('Small Integer solutions ')
    axs[0, 0].hlines(y=axs[0, 0].get_yticks()[2:-2], xmin=min(xticks), xmax=max(xticks), linestyles='dotted')

    intdifference = intAnswers['CountWeight'] - intAnswers['CountClass']
    axs[0, 1].plot(intdifference, 'r')
    axs[0, 1].vlines(x=xticks, ymin=intdifference.min() * 1.2, ymax=intdifference.max() * 1.2, linestyles='dotted')
    axs[0, 1].set_xticks(xticks[::2])
    axs[0, 1].hlines(y=axs[0, 1].get_yticks()[1:-1], xmin=min(xticks), xmax=max(xticks), linestyles='dotted')

    axs[0, 1].set_title('(Weight-Class) for each small integer solution')

    # Creating a histogram, using weights to speed it up
    # All buckets are all teh results that fall larger than that integer
    # It summarizes the 'tail' of the data in the leftmost and rightmost buckets
    histmin = -50
    histmax = 500
    histprep = sums[(sums.index > histmin) & (sums.index < histmax)]
    histprep = histprep.append(
        pd.DataFrame([sums[sums.index <= histmin].sum(), sums[sums.index >= histmax].sum()],
                     columns=['CountClass', 'CountWeight'], index=[histmin, histmax]))

    n = histmax - histmin
    # i suspect this is the part that takes the longest:
    axs[1, 0].hist(histprep.index, bins=n, weights=histprep['CountClass'])
    axs[1, 0].set_title('Histogram by Int')
    axs[1, 0].set_yscale('log')

    axs[1, 1].hist(histprep.index, bins=int(n), weights=histprep['CountWeight'],
                   color='orange')  # this \should\ always be an integer, but doing this prevents it flagging it as an error
    axs[1, 1].set_title('Histogram by Int')
    axs[1, 1].set_yscale('log')

    # histogram of counts, i.e. buckets by how many times a number is hit
    axs[2, 0].hist(sums.transpose())
    axs[2, 0].set_title('target value Count ')
    axs[2, 0].set_yscale('log')
    axs[2, 0].hlines(y=axs[2, 0].get_yticks()[2:-2], xmin=0,
                     xmax=axs[2, 0].get_xticks()[-2], linestyles='dotted')

    commonIndices = set(sums.nlargest(numberofmax, 'CountClass').index)
    commonIndices = commonIndices.union(sums.nlargest(numberofmax, 'CountWeight').index)
    commonIndices = commonIndices.union([24])  # Specifically to test the 24 game hypothesis
    commonAnswers = sums.transpose()[commonIndices].transpose()
    commonAnswers = commonAnswers.sort_values('CountClass', ascending=False)

    commonAnswers.plot.bar(ax=axs[2, 1], legend=False)
    axs[2, 1].set_title('CommonAnswers, and 24 ')
    axs[2, 1].hlines(y=axs[2, 1].get_yticks()[1:-1], xmin=min(axs[2, 1].get_xticks()),
                     xmax=max(axs[2, 1].get_xticks()), linestyles='dotted')

    handles, labels = axs[2, 1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right')

    fig.tight_layout()
    return (plt)


def main(numcards):
    start_time = time.time()
    rowsdict = testAll(numcards)
    t = (time.time() - start_time)
    print('Data generated in %s seconds ---' % t)
    sumsdict = rotate_sum(rowsdict)
    fig = pretty_results(sumsdict, numcards, numberofmax=10)

    plt.show()
    t = (time.time() - start_time)
    print("Total of %s seconds ---" % t)


main(3)
