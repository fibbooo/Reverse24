# this has all the methods to test all teh cards, and also nicely display the results
import time
import pandas as pd
import testcards
import math
from functools import reduce
from collections import Counter
import matplotlib.pylab as plt


# This gets a card arrangement a and returns the next one, alphabetically
# insures that every combination of cards (which I call classes) shows up once
# i.e. 1,5,5,5 is the only version of that that will show up;
# 5,1,5,5 will not
# maxcount is the base, i.e. a's max value is maxcount
# because of teh way its coded, its smallest value is whatever you initialize a with
def greedy_unique_counter(a, maxcount):
    # Increments a, with a max of maxN
    if len(a) == 1:
        if a[0] == maxcount - 1:
            return -1
        else:
            return [a[0] + 1]
    b = -1
    a[b] = a[b] + 1
    if a[b] == maxcount:
        a = greedy_unique_counter(a[0:b], maxcount)
        if a == -1:
            return -1
        a.append(a[-1])
    return a


def test_all(numcards):
    # Test each arrangement of cards
    rowsdict = {}

    a = [1 for i in range(0, numcards)]
    while a != -1:  # generate all combinations of 1 through 13
        rowsdict[tuple(a)] = testcards.test_a(a)
        a = greedy_unique_counter(a, 14)

    return rowsdict


def rotate_sum(dictdict):
    # rotates a dictionary of dictionaries (i.e. makes inner key outer key)
    # and creates counts them based on new outer key
    # The weight is the number of times each class could be dealt out, i.e. based on the og outer key
    # ie weight is 24 if we have 4 unique cards, 1 if 4 cards that all match

    sumsdict = {}
    for key1, value1 in dictdict.items():
        weight = math.factorial(len(key1)) / \
                 (reduce((lambda x, y: x * y), map(math.factorial, Counter(key1).values())))
        # n choose k_1,k_2,..k_n, where sum k_i=numcards (notice that numcards= len key1)
        for key2, value2 in value1.items():
            # targetdict[key2].update({key1: value2})
            # The above line is for rotating the dictionary, but I just want some summary statistics
            # i.e. the value doesn't matter, just the count and the weighted count
            sumsdict[key2] = [sum(x) for x in zip(sumsdict.get(key2, [0, 0]), [1, weight])]
            # first entry is count per class, second entry is count per weight
            # there has to be a better way of component-wise adding up lists but I guess not
    return sumsdict


def pretty_results(sumsdict, numcards, numberofmax=10):
    # make a nice graph of all the things I care about
    # takes in a rotated-sum dictionary  explicitly from rotate_sum
    # num cards is number of cards that we're testing

    # Im aware that this function is far too long and pretty ugly
    # I don't really know how to improve it
    # breaking it up into a function for each subplot would do it, but each function is only used once, so
    # labels are commented out because they made it all wonky

    # first put it into a dataframe for ease of use
    sums = pd.DataFrame.from_dict(sumsdict, orient='index', columns=['CountClass', 'CountWeight']).sort_index()

    # normalize
    # Count weight is easy- divide by 13**numcards
    countWeightNormalizer = 13 ** numcards
    # Countclass- stars and bars- (13+numcards-1)! choose numcards
    countClassNormalizer = math.factorial(13 + numcards - 1) / (math.factorial(numcards) * math.factorial(13 - 1))

    sums['CountClass'] = sums['CountClass'] / countClassNormalizer
    sums['CountWeight'] = sums['CountWeight'] / countWeightNormalizer

    #Now we get to plot! On each graph,
    # class is default one, weight is default 2 (blue and orange respectively)
    # Setting up the figure
    fig, axs = plt.subplots(4, 2)
    fig.set_figheight(8)
    fig.set_figwidth(10)
    #I dont get how the zooming works, but this much is enough that theres detail,so
    fig.suptitle('Reverse 24', size=16)

    # Plotting integer answers
    xmin = -15
    xmax = 70
    intAnswers = sums[[x.is_integer() and xmin < x < xmax for x in sums.index]]
    xticks = [x for x in range(int(intAnswers.index.min()), int(intAnswers.index.max())) if x % 5 == 0]

    ymax = intAnswers.max()
    axs[0, 0].plot(intAnswers, '.')
    axs[0, 0].vlines(x=xticks, ymin=0, ymax=1, linestyles='dotted')
    axs[0, 0].set_xticks(xticks[::2])
    axs[0, 0].hlines(y=axs[0, 0].get_yticks()[2:-2], xmin=min(xticks), xmax=max(xticks), linestyles='dotted')

    axs[0, 0].set_title('Small Integer solutions ')
    #axs[0,0].set_xlabel('Number')
    #axs[0,0].set_ylabel('Chance a dealt hand has a solution')


    # Plot int differences
    intdifference = intAnswers['CountWeight'] - intAnswers['CountClass']
    axs[0, 1].plot(intdifference, 'r')
    axs[0, 1].vlines(x=xticks, ymin=intdifference.min() * 1.2, ymax=intdifference.max() * 1.2, linestyles='dotted')
    axs[0, 1].set_xticks(xticks[::2])
    axs[0, 1].hlines(y=axs[0, 1].get_yticks()[1:-1], xmin=min(xticks), xmax=max(xticks), linestyles='dotted')

    axs[0, 1].set_title('(Weight-Class) \n for each small integer solution')
    #axs[0,1].set_xlabel('Number')
    #axs[0,1].set_ylabel('Difference in chance of Weight-Class')
    # Plotting every single value looks bad; this 'smooths it out' by grouping by nearest int
    # Creating a histogram, using likelyhood of getting that number as its weight
    # All buckets are all the results that fall larger than that integer
    # this does mean that reading any given column is absolutely useless, becuase of the way the things doublecount
    # the rightway to do it would probably be to do the summary statistics all over again, and keep track to only
    # count each class the correct number of times (i duplicate a class if say it can make both .2 and .4)
    # But the distribution is still interesting, I think
    # It summarizes the 'tail' of the data in the leftmost and rightmost buckets
    histmin = -50
    histmax = 500
    histprep = sums[(sums.index > histmin) & (sums.index < histmax)]
    histprep = histprep.append(
        pd.DataFrame([sums[sums.index <= histmin].sum(), sums[sums.index >= histmax].sum()],
                     columns=['CountClass', 'CountWeight'], index=[histmin, histmax]))

    n = histmax - histmin
    axs[1, 0].hist(histprep.index, bins=n, weights=histprep['CountClass'])
    # axs[1, 0].plot(sums) #this just looks very messy
    # a bucket for every single entry. Also messy because bucket size changes. Also takes forever
    # axs[1, 0].hist(sums.index,bins=sums.index, weights=sums['CountClass'])
    axs[1, 0].set_title('Histogram by Int')
    axs[1, 0].set_yscale('log')
    #axs[1,0].set_xlabel('Number')
    #axs[1,0].set_ylabel('Non-independent sum of probability')

    # Same plot, but for weights instead of class; the 'duplicity' shows up more, in that the sums are well above 1!
    axs[1, 1].hist(histprep.index, bins=int(n), weights=histprep['CountWeight'],
                   color='orange')
    axs[1, 1].set_title('Histogram by Int')
    axs[1, 1].set_yscale('log')
    #axs[1,1].set_xlabel('Number')
    #axs[1,1].set_ylabel('Non-independent sum of probability')

    # histogram of counts, i.e. buckets by how many times a number is hit
    axs[2, 0].hist(sums.transpose())
    axs[2, 0].set_title('Chance succeed vs Count')
    axs[2, 0].set_yscale('log')
    axs[2, 0].hlines(y=axs[2, 0].get_yticks()[2:-2], xmin=0,
                     xmax=axs[2, 0].get_xticks()[-2], linestyles='dotted')
    axs[2,0].set_xlabel('Chance that a N game is solveable')
    axs[2,0].set_ylabel('Count N')

    # Plot the most common answers, as a bar graph, so that its directly comparable
    # I do slightly fancy manipulations to insure top 10 of both weights and calsses show up
    commonIndices = set(sums.nlargest(numberofmax, 'CountClass').index)
    commonIndices = commonIndices.union(sums.nlargest(numberofmax, 'CountWeight').index)
    commonIndices = commonIndices.union([24])  # Specifically to test the 24 game hypothesis. rarely pushes an error
    commonAnswers = sums.transpose()[commonIndices].transpose()
    commonAnswers = commonAnswers.sort_values('CountClass', ascending=False)
    ylow = commonAnswers.min().min()  # take minimum of both columns
    yhigh = commonAnswers.max().max()  # the maximum value

    commonAnswers.plot.bar(ax=axs[2, 1], legend=False)

    axs[2, 1].set_title('Chance of most common Answers, and 24 ')
    axs[2, 1].set_ylim([ylow * .9, min([yhigh * 1.1, 1])])
    axs[2, 1].hlines(y=axs[2, 1].get_yticks()[1:-1], xmin=min(axs[2, 1].get_xticks()),
                     xmax=max(axs[2, 1].get_xticks()), linestyles='dotted')



    #Plot the most common answers as a scatter plot.
    #I'd like to take the difference of weights and counts but i think all the other graphs are more important;
    #they're pretty close most of the time I think
    commonIndices = set(sums.nlargest(numberofmax * 5, 'CountClass').index)
    commonIndices = commonIndices.union(sums.nlargest(numberofmax * 5, 'CountWeight').index)
    commonAnswers = sums.transpose()[commonIndices].transpose()
    commonAnswers = commonAnswers.sort_values('CountClass', ascending=False)
    xmin = math.floor(min(commonAnswers.index))
    xmin = xmin - xmin % 5
    xmax = math.ceil(max(commonAnswers.index))
    xmax = xmax + 5 - xmax % 5
    xticks = range(xmin, xmax, 5)

    ylow = commonAnswers.min().min()  # take minimum of both columns
    yhigh = commonAnswers.max().max()  # the maximum value
    numIndices=len(commonIndices)

    axs[3, 0].plot(commonAnswers, '.')

    axs[3, 0].set_ylim([ylow * .9, min([yhigh * 1.1, 1])])
    axs[3, 0].vlines(x=xticks, ymin=0, ymax=ymax * 1.2, linestyles='dotted')
    axs[3, 0].set_xticks(xticks[::2])
    axs[3, 0].set_title(str(numIndices)+' most likely targets ')
    axs[3, 0].hlines(y=axs[3, 0].get_yticks()[1:-1], xmin=min(axs[3, 0].get_xticks()),
                     xmax=max(axs[3, 0].get_xticks()), linestyles='dotted')

    handles, labels = axs[2, 1].get_legend_handles_labels()
    labels = ['By Class, i.e. \n [1,1,1,1] counts once, \n [1,2,3,4] counts once',
              'By Weight i.e. \n [1,1,1,1] counts once \n [1,2,3,4] counts 24 times']
    axs[3, 1].axis('off')
    axs[3, 1].legend(handles, labels, prop={'size': 8}, loc='center')

    plt.tight_layout()

    fig.subplots_adjust(top=0.88 )

    return plt


def main(numcards):
    # The function you call.
    # Give it the number of cards and it'll do its thing!
    start_time = time.time()
    rowsdict = test_all(numcards)
    t = (time.time() - start_time)
    print('Data generated in %s seconds ---' % t)
    sumsdict = rotate_sum(rowsdict)
    fig = pretty_results(sumsdict, numcards, numberofmax=10)

    plt.show()
    t = (time.time() - start_time)
    print("Total of %s seconds ---" % t)


main(4)
