def receiverSim(lam, cost_c, cost_nc):
    if lam <= 0.: raise ValueError("Lambda parameter must be positive")
    if lam > .5: raise ValueError("Unable to handle lambda parameter > .5")
    if cost_c <= 0. or cost_nc <= 0.: raise ValueError("Cost parameter must be positive")
    if cost_c >= cost_nc: raise ValueError("Cost for combinatorial must be less than that for non-combinatorial")
    
    n = cost_nc + (cost_nc - cost_c) / lam
    
    #maxp_c = (n - cost_c) / n
    #halfp_c = (n / 2. - cost_c) / n
    #maxp_nc = (n - cost_nc) / n
    #halfp_nc = (n / 2. - cost_nc) / n
    
    maxp_c = 1.
    halfp_c = (n / 2. - cost_c) / (n - cost_c)
    maxp_nc = (n - cost_nc) / (n - cost_c)
    halfp_nc = (n / 2. - cost_nc) / (n - cost_c)

    def fillIn(full, half):
        return ((full, half, half,   0.),
                (half, full,   0., half),
                (half,   0., full, half),
                (  0., half, half, full))
    
    return (fillIn(maxp_c, halfp_c), fillIn(maxp_nc, halfp_nc))
           
def senderSim0(maxp=1.):
    maxp = float(maxp)
    if maxp < 0.: raise ValueError("Max payoff must be nonnegative")
    
    return ((     maxp, maxp / 2., maxp / 2.,        0.),
            (maxp / 2.,      maxp,        0., maxp / 2.),
            (maxp / 2.,        0.,      maxp, maxp / 2.),
            (       0., maxp / 2., maxp / 2.,      maxp))
    

def senderSim1(maxp=1.):
    maxp = float(maxp)
    if maxp < 0.: raise ValueError("Max payoff must be nonnegative")
    
    return ((       0., maxp / 2., maxp / 2.,      maxp),
            (maxp / 2.,      maxp,        0., maxp / 2.),
            (maxp / 2.,        0.,      maxp, maxp / 2.),
            (       0., maxp / 2., maxp / 2.,      maxp))
            
def senderSim2(maxp=1.):
    maxp = float(maxp)
    if maxp < 0.: raise ValueError("Max payoff must be nonnegative")
    
    return ((     maxp, maxp / 2., maxp / 2.,        0.),
            (     maxp, maxp / 2.,        0., maxp / 2.),
            (maxp / 2.,        0., maxp / .2,      maxp),
            (       0.,      maxp, maxp / 2., maxp / 2.))
