import pandas as pd
import numpy as np
import requests
import io
from sklearn.linear_model import LinearRegression

def get_life_table(state, sex):
    url = f'https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/NVSR/73-07/{state}{sex}.xlsx'
    response = requests.get(url)
    life_table = pd.read_excel(io.BytesIO(response.content), header=2, nrows=100).drop(columns='Unnamed: 0')
    qx85 = life_table['qx'].loc[85:]
    mx85 = qx85 / (1 - 0.5 * qx85)
    logit_mx85 = np.log(mx85 / (1 - mx85))
    ages = pd.DataFrame(logit_mx85.index, columns=['age'])
    lm = LinearRegression().fit(ages, logit_mx85)
    logit_mx100_119 = lm.predict(np.arange(100, 120, 1).reshape(-1, 1))
    mx100_119 = np.exp(logit_mx100_119) / (1 + np.exp(logit_mx100_119))
    qx100_119 = pd.Series(mx100_119 / (1 + 0.5 * mx100_119), index=range(100, 120))
    lx100_119 = list([life_table['lx'][99] * (1 - life_table['qx'][99])])
    for x in range(101, 120):
        lx100_119.append(lx100_119[-1] * (1 - qx100_119[x - 1]))
    lx100_119 = pd.Series(lx100_119, index=range(100, 120))
    dx100_119 = lx100_119.subtract(lx100_119.shift(-1), fill_value=0)
    Lx100_119 = lx100_119 - 0.5 * dx100_119
    Tx100_119 = Lx100_119.loc[::-1].cumsum()
    ex100_119 = Tx100_119 / lx100_119
    life_table_100_119 = pd.concat([qx100_119, lx100_119, dx100_119, Lx100_119, Tx100_119, ex100_119], axis=1)
    life_table_100_119.columns = ['qx', 'lx', 'dx', 'Lx', 'Tx', 'ex']
    life_table = pd.concat([life_table, life_table_100_119])
    return life_table

def deferred_annuity(table, age, deferred, period = 1, interest = 0.05):
    deferred_annuity = sum(table['annuity_contribution'].loc[(age + deferred):]) / (1/(1 + interest))** deferred
    ux_plusdeferred_approx = 0.5 * (np.log(table['px'][age + deferred - 1]) + np.log(table['px'][age + deferred]))
    deferred_annuity = deferred_annuity - (period - 1)/(2 * period) - (period**2 - 1)/(12 * period**2)*(np.log(1 + interest) + ux_plusdeferred_approx)
    return deferred_annuity

def annuity_calculator_2(life_table, age, term = None, deferred = None, period = 1, interest = 0.05):
    table = life_table.copy().loc[age:]
    table['qx'] = table['dx'] / table['lx']
    table['px'] = 1 - table['qx']
    table['survival'] = table['px'].cumprod()
    table['discount'] = (1 / (1 + interest)) ** (np.array(table.index) - age)
    table['annuity_contribution'] = table['survival'].shift(1, fill_value= 1) * table['discount']
    annuity = sum(table['annuity_contribution'])
    px_minus_1 = 1 - (life_table['dx'].loc[age-1] / life_table['lx'].loc[age -1])
    ux_approx = 0.5 * (np.log(px_minus_1) + np.log(table['px'][age]))
    annuity = annuity - (period - 1)/(2 * period) - (period**2 - 1)/(12 * period**2)*(np.log(1 + interest) + ux_approx)
    if (term != None) and (deferred == None):
        annuity = (annuity - (1/(1 + interest))** term * table['survival'][age + term] *
                   deferred_annuity(table = table, age = age, deferred = term, period = period, interest = interest))
    if (term == None) and (deferred != None):
        annuity = ((1/(1 + interest))** deferred * table['survival'][age + deferred] *
                   deferred_annuity(table = table, age = age, deferred = deferred, period = period, interest = interest))
    if (term != None) and (deferred != None):
        annuity = ((1/(1 + interest))** deferred * table['survival'][age + deferred] *
                   deferred_annuity(table = table, age = age, deferred = deferred, period = period, interest = interest) -
                   (1/(1 + interest))** (deferred + term) * table['survival'][age + deferred + term] *
                   deferred_annuity(table = table, age = age, deferred = (deferred + term), period = period, interest = interest))
    return annuity

def death_benefit_value_calculator(life_table, age, term = None, deferred = None, period = 365, interest = 0.05):
    d = (interest/(1 + interest))
    if (term == None) and (deferred == None):
        benefit_value = (1 - d * annuity_calculator_2(life_table, age, period = period, interest = interest))
    if (term != None) and (deferred == None):
        benefit_value = (1 - d * annuity_calculator_2(life_table, age, term = term, period= period, interest = interest) -
                         (d/interest) ** term * life_table['lx'][age + term]/life_table['lx'][age])
    if (term == None) and (deferred != None):
        benefit_value = (d * annuity_calculator_2(life_table, age, term = deferred, period= period, interest = interest) +
                         (d/interest) ** deferred * life_table['lx'][age + deferred]/life_table['lx'][age] -
                         d * annuity_calculator_2(life_table, age, period = period, interest = interest))
    if (term != None) and (deferred != None):
        benefit_value = (d * annuity_calculator_2(life_table, age, term = deferred, period= period, interest = interest) +
                         (d/interest) ** deferred * life_table['lx'][age + deferred]/life_table['lx'][age] -
                         d * annuity_calculator_2(life_table, age, term = deferred + term, period= period, interest = interest) -
                         (d/interest) ** (deferred + term) * life_table['lx'][age + deferred + term]/life_table['lx'][age])
    return benefit_value