import pandas as pd

class func:

    def __init__(self, keys, domains, rules, handle = None, shifts = None):

        #There are clearly more efficient ways of doing this 
        #and such a class probably already exists, etc, but it's faster for stubbing to just make one
        
        self.keys = keys
        self.domains = domains
        self.rules = rules
        self.handle = handle
        if shifts == None:
            self.shifts = {key:0 for key in self.keys}

    def eval(self, x):

        for key in self.keys: #wildly inefficient
            if x >= self.domains[key][0]:
                if x < self.domains[key][1]:
                    return self.rules[key](x-self.shifts[key])
  
    def plot(self): #Assumes intervals are in order, but again, this code is not supposed to be good

        alist = []
        blist = []

        for key in self.keys:
            alist.append(self.domains[key][0])
            blist.append(self.domains[key][1])

        a = min(alist)
        b = max(blist)

        domain = range(a, b)
        outputs = [self.eval(x) for x in range(a,b)]
        return pd.DataFrame({'input': list(domain), 'output': outputs, 'function': [self.handle]*len(outputs)})
    
    # display.plot()

f_pwl = func(
    keys = [0, 1], 
    domains = {0: [0,100], 1: [100, 150]}, 
    rules = {0: lambda t: 200 - t, 1: lambda t: 300 - 2*t},
    handle = 'f'
)

g_pwl = func(
    keys = [0, 1],
    domains = {0: [0,100], 1: [100, 200]}, 
    rules = {0: lambda t: 150 - t/2, 1: lambda t: 200 - t},
    handle = 'g'
)

g_pwl2 = func(
    keys = [0, 1], 
    domains = {0: [0,100], 1: [100, 250]}, 
    rules = {0: lambda t: 150 - t/2, 1: lambda t: 180 - 4*t/5},
    handle = 'g'
)

class AMM:

  def __init__(self, x_virt, y_virt, x_real, y_real, f = f_pwl, g = g_pwl2):
    
    #functions that take virtual balance x (resp y) to virtual balance y (resp x)
    self.functions = {'x': f, 'y': g} 

    #virtual balances
    self.v_balance = {'x': x_virt, 'y': y_virt}

    #real balances
    self.r_balance = {'x': x_real, 'y': y_real}

    self.balance_history = [(*self.v_balance.values(), *self.r_balance.values())]

  def sell(self, delta1, currency1 = 'x'): 

    currency2 = list(({'x', 'y'} - {currency1}))[0]

    a = self.functions[currency1].eval(self.v_balance[currency1])
    b = self.functions[currency1].eval(self.v_balance[currency1] + delta1)  #throws error if outside of domain
    
    delta2 = b - a

    self.v_balance[currency1] += delta1
    self.r_balance[currency1] += delta1

    self.v_balance[currency2] = a + delta2 # This is important for logic involving different buy/sell AMMs (should check/discuss)
    self.r_balance[currency2] += delta2

    self.balance_history.append((*self.v_balance.values(), *self.r_balance.values()))

    return -delta2, currency2
  
  def extend_x(self, f_ext, m):

    fx = self.functions['x']

    for k in fx.keys:
      fx.domains[k][0] += m
      fx.domains[k][1] += m
      fx.shifts[k] = m
  
    fx.keys = fx.keys + [len(fx.keys)]
    fx.domains[fx.keys[-1]] = [0,m]
    fx.rules[fx.keys[-1]] = f_ext
    fx.shifts[fx.keys[-1]] = 0

  def display(self):
    x_res = self.functions['x'].plot()
    y_res = self.functions['y'].plot()
    df = pd.concat([x_res, y_res])
    return df