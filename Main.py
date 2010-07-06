if __name__ == '__main__':
    from SeltenGame import *

    (sg, payoffs) = seltenGameSim()
    print sg(2,1)
    print
    (sg, payoffs) = seltenGameSim(2,[3,3],[5,4])
    print sg(3,1)
