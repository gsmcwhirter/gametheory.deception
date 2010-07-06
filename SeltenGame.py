import itertools
import functools

def seltenGame(numAspects, stateLists, stateTuples, messageLists, messageTuples, numActions,
               payoffsReceiver, payoffsSender, defaultWeight):

    sender_urns = [[[defaultWeight for k in messageLists[j]] for j in range(numAspects)] for i in range(len(stateTuples))]
    receiver_urns = [[[defaultWeight for k in stateLists[i]] for j in messageLists[i]] for i in range(numAspects)]

    print urns

def seltenGameSetup(numAspects, numStates, numMessages):
    if len(numStates) != numAspects:
        raise ValueError('numStates should have the same length as the value of numAspects')

    if len(numMessages) != numAspects:
        raise ValueError('numMessages should have the same length as the value of numAspects')

    stateLists = [range(i) for i in numStates]
    stateTuples = list(apply(itertools.product, stateLists))

    numActions = len(stateTuples)

    messageLists = [range(i) for i in numMessages]
    messageTuples = list(apply(itertools.product, messageLists))

    return (functools.partial(seltenGame, numAspects, stateLists, stateTuples, messageLists, messageTuples, numActions),
            stateTuples,
            messageTuples)

def seltenGameSim(numAspects = 2, numStates = [2,2], numMessages = [2,2]):
    (sg, stateTuples, messageTuples) = seltenGameSetup(numAspects, numStates, numMessages)

    payoffs = lambda z, x, y: float(len([1 for i in range(len(x)) if x[i] == y[i]])) / float(z)
    payoffs = functools.partial(payoffs, numAspects)

    return (functools.partial(sg, payoffs), payoffs)

def seltenGameDist(numAspects = 2, numStates = [2,2], numMessages = [2,2]):
    (sg, stateTuples, messageTuples) = seltenGameSetup(numAspects, numStates, numMessages)

    payoffs = lambda z, x, y: float(abs(z.index(x) - z.index(y))) / float(len(z) - 1)
    payoffs = functools.partial(payoffs, stateTuples)

    return (functools.partial(sg, payoffs), payoffs)
