# Life Insurance / Annuity Calculator App

This Flask app predicts either the gross monthly premium amount for whole and term life insurance or the gross annuity cost for the user.
You can input your age, sex, state, and insurance desires (amount insured, term or whole life, length of term) and the app will produce an estimate of the price.

## Process

### Conception
Inspired by my mother's career as a demographer and by my own actuarial and data science pursuits, I began to look at US Census data. (https://www2.census.gov/programs-surveys/popest/datasets/)
My first project idea was to create a life table using the latest census data combined with mortality data.
The CDC does publish public mortality data by year with information on the age of the deceased, which can be downloaded and processed to get a death total for each year cohort. (https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm#Mortality_Multiple)
While I was able to calculate a life table for the entire US, state residency information was not available on the public dataset, plus Census counts were not available for ages over 100.
I would have to make some assumptions about populations over 100 and adjust death counts for those ages to get a reasonable estimate for mortality probabilities at those ages, which I was uncomfortable doing.

### Census National Vital Statistics Report
Some more online research led me to the National Vital Statistics Reports' report on U.S. State Life Tables, 2021, published on August 21, 2024. (https://www.cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-07.pdf)
The report presents a report on the complete period life tables for each of the 50 states and the District of Columbia by sex, provides links to the online repository storing all the tables,
and describes the methodology used to create the estimates.
The methodology used to calculate the life tables was similar to what I was trying to do on my own: 
data from the CDC Vital Statistics files was used for death counts and compared to state specific population estimates from the U.S. Census Bureau.
In addition, these life tables made mathematical adjustments to the death rate to get the probability of death, incorporated more complete Medicare data for the higher age ranges,
and used a Kannisto logistic model to smooth death rates at 85-99 and to predict death rates at the highest ages (100+).

### Construction of Life Table
A life table for a given state and sex can be easily downloaded from the online repository. Next, the Kannisto logistic model that the NVSR methodology uses can be reverse engineered by transforming
the probabilites back into death rates and fitting the logit of these rates to linear regression. With this model, the probabilities for all ages can be obtained, as well as
survivors, number of deaths, person-years lived, and life expectancy.

### Functions for Annuities
To calculate annuities, I created functions that takes a given life table and uses actuarial formulas to discount annuity payments for each year of the annuity.
In order to obtain the annuity values for monthly or other payment structures, the three term Woolhouse approximation with the approximated force of mortality was computed.
Calculations for death benefits as well as term and deferred annuities of different payment structures and discounted at different interest rates are all built in to the function logic.

### Flask App
Finally, a simple flask app was designed with the help of AI for html and flask code generation, which allows the user to choose which product they would like an estimate for,
input their information, and receive a price estimate for either an annuity or a life insurance premium.
