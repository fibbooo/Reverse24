# This module implements everything needed to test a series of cards
# #A series of cards is a list of numbers, i.e. [5,5,5,1]
# It has 1 public methods: testA(cards, flag='count'),
# which outputs a dictionary \ where the key is the value the cards evaluate to
# and the entries are counts (if flag is string its instead human-readable strings of how you get there)
# By default, it checks all permutations of the cards,


# The first 3 methods are used for generating the correct parenthesis list
# A parentheses list is a list of numcards-1 numbers, where each number is less than or equal to its index
# and it satisfies a 'lexographic' rule to prevent over counting
# To convert from a parentheses list to actual parenthesis
# Working from the last element i to the first, put a parentheses around elements i and i+1

# the only thing I'm thinking about adding to this file is a test to
# reduce the number of elements in zip[parenthesis, multiplication], because many give the same result
# id do this by just trying probably 30 examples, 'with noise', and if they give the same answers for all of them
# then to remove it from the stack
# I expect that that would give me about a 3x speed up for the 4 number case, based on testAll functionality in 'main'

from itertools import permutations, product


def __index_counter(a):
    # takes in a list and increments it so that the nth index max is n and the min is 0
    b = -1
    a[b] = a[b] + 1
    while a[b] == len(a) + b + 1:
        a[b] = 0
        b = b - 1
        if b == -len(a) - 1:
            return -1
        a[b] = a[b] + 1
    return a


def __lexographic(a):
    # That order is
    # When you are parenthesising two groups that have already been parenthesised,
    # it has to go left group then right group
    # i.e. [0,1,0] and [0,0,2] both make (()())
    # (To be clear, we're taking the lists in reverse order, so the third item is the innermost parenthesis)
    # [0,1,0] is the 'gramatically correct' choice because it groups the 0 before the 1.

    # Heres how im going to do it:
    # im gonna make another list. It starts with all 0's
    # Then, each parenthesis groups 2 elements.
    # If one element is 0, or the grouping has the smaller number first, its good
    # smaller than or equal for one less comparison
    # and it gets labled as n, where this is the nth item grouped (i.e. negative index)
    testparen = [0 for i in range(0, len(a) + 1)]
    for c in range(1, len(a) + 1):
        b = -c  # i want it to increment in the other direction and this was easiest
        if testparen[a[b]] <= testparen[a[b] + 1] or testparen[a[b] + 1] == 0:
            testparen[a[b]] = -b;
            testparen.pop(a[b] + 1)
        else:
            return False
    return True


def __paren_options(length):
    # Generates all the options of parenthisis
    # The trick is to notice
    # 1)parenthesis always group 2 adjacent elements.
    # So, ill be building up a list of where the left parenthesis
    # is and it just groups it and the item one larger than it,
    # with the last item in teh list being the first parenthisis applied, and then the list is one shorter
    # i.e. [0,1,0]=[0,0,2]=(()())
    # 2)To prevent repeats, there is a lexographic order

    k = []
    testparen = [0 for i in range(0, length)]
    while testparen != -1:

        if __lexographic(testparen):
            k.append(testparen.copy())
        testparen = __index_counter(testparen)

    return k


# _____________________

# this cell takes care of the multiplications that I do

# 0 is a +, 1 is *, 2 is -, 3 is divide, for the 3 operations
# So now, take in the multholder and the string, and try all 5 operations on them
# (((ab)c)d)
# ((ab)(cd))
# ((a(bc))d)
# (a((bc)d))
# (a(b(cd))

# The next 2 methods have to do with how multiplication is done

def __operate(multstring, a, b):
    if multstring == '+':
        return a + b
    if multstring == '*':
        return a * b
    if multstring == '-':
        return a - b
    if multstring == '/' and b != 0:
        return a / b
    # if if a bad character of divide by 0. this is supposed to be 'a ridiculous number'
    return [False]  # my bad way of attempting to get the equaltity to never work
    # This will probably raise a crazy error, but I don't know how else to do it
    # since False==0


def __do_mult(aList, multList, p):
    # a is the number string
    # m is the multiply string
    # p is a parenstring
    # also, it recursivly comes to the answer
    # dad suggested that since i'm looking for all the outputs anyway
    # I just always make it return the 'partial dictionary' or intermediate results
    # but I already wrote it this way

    # Remember parentheses are built backwards, so multiplication is going to to
    # Returns a list as opposed to a float to make sure that we can distinguish 0 from false
    if len(aList) == 1:
        return aList  # final case. Returns the number, packaged as a list, to distinguish from False
    if multList[-1] == '/' and aList[p[-1] + 1] == 0:  # divide by 0
        return False
    else:
        aList[p[-1]] = __operate(multList[-1], aList[p[-1]], aList[p[-1] + 1])
        aList.pop(p[-1] + 1)
    # operates the 2 items together
    return __do_mult(aList, multList[0:-1], p[0:-1])


def __human_readable(a_list, m, p):
    # Makes a human readable string. for the operations performed
    # modifies the passed string,
    # no i dont understand when copies or references are passed, i just bugfix it till it does work
    if len(a_list) == 1:
        return a_list[0]
    else:
        a_list[p[-1]] = '(' + str(a_list[p[-1]]) + m[-1] + str(a_list[p[-1] + 1]) + ')'
        a_list.pop(p[-1] + 1)
    # operates the 2 items together
    # the m[0:-1] shortens m by one.
    # can't useu pop because that just returns m[-1]
    return __human_readable(a_list, m[0:-1], p[0:-1])


def test_a(b, flag='count'):
    # The only public method!
    # Tests all teh arithmatic operations you get from A
    result = {}
    for a in permutations(b):
        for p in __paren_options(len(a) - 1):
            multoption = product(*[('+', '*', '-', '/') for x in range(0, len(a) - 1)])  # remake the iterable each time
            for m in multoption:
                # a is modified over the computation, so listify it (its passed as a tuple)
                temp = __do_mult(list(a), m, p)
                if temp != False:  # makes sure we don't divide by 0
                    # We have to 'unpackage' temp both times it appears
                    if flag == 'string':
                        holder = result.get(temp[0])
                        if holder is None:
                            result[temp[0]] = [__human_readable(list(a), m, p)]
                        else:
                            result[temp[0]] = holder + [__human_readable(list(a), m, p)]

                    else:
                        result[temp[0]] = result.get(temp[0], 0) + 1
                # print(temp[0],'=', humanReadable(list(a),m,p)) #For debugging
    return result

#Test functions:

#print(test_a([5, 5, 5, 1], flag='string')[24])
#print(sorted(test_a([5, 5, 5, 1], flag='count').keys()))

# I chose numbers to make a 'divide by 0' impossible. If theres no division by 0, there should be
# (count card permutations)*(count multstrings)*(count parenstrings) options
# for 4, thats
# (4!)*(4^3)*5=7680
#for 5 cards, thats
#5!*4^4*15=460,800
#and maybe im overcounting 1? a shame.
#print(sum(test_a([2, 5, 8, 12]).values()))
#print(sum(test_a([1,11,111,1111,17]).values()))
