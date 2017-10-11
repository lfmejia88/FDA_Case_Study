# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 22:31:52 2017

@author: mejialu
"""
import json,urllib
import pandas as pd
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
from scipy import stats

data = pd.DataFrame()
years = ['2013','2014','2015','2016']
months = ['03','06','09','12']

print 'Loading data from API'

for i in years: 
    for j in months:
        url = urllib.urlopen('https://api.fda.gov/drug/event.json?search=receivedate:['+i+j+'01+TO+'+i+j+'30]&limit=100').read()
        load = json_normalize(json.loads(url),'results')
        data = data.append(load)
    print i + ' data loaded'
    
print 'All data has been loaded'
print 'Exctracting features and creating aditional datasets'
        
# Extracting Patient features
data.reset_index(inplace=True)
patient_features = ['patientsex','patientweight','patientonsetage','patientonsetageunit','drug','reaction']

for i in patient_features:
    pfeat = pd.Series([d.get(i) for d in data['patient']])
    data = pd.concat([data, pfeat], axis=1)
    data = data.rename(columns = {0:i})

#Creating Reactions Dataset 
reactions = pd.DataFrame()
for i,item in enumerate(data['reaction']):
    react = pd.DataFrame(item)   
    react = react.assign(safetyreportid = data['safetyreportid'][i], occurcountry = data['occurcountry'][i], date = data['receivedate'][i])
    reactions = reactions.append(react)

#Creating Drugs Dataset     
drugs = pd.DataFrame()
for i,item in enumerate(data['drug']):
    drug = pd.DataFrame(item)     
    drug = drug.assign(safetyreportid = data['safetyreportid'][i], occurcountry = data['occurcountry'][i], patientonsetage = data['patientonsetage'][i], patientonsetageunit = data['patientonsetageunit'][i])
    drugs = drugs.append(drug)

### Data Analysis   

#Plotting Seriosness of events in top 10 countries by number of reports
top_10_country = data['safetyreportid'].groupby(data['occurcountry']).count().sort_values(axis=0,ascending=False)[:10]
columnscr = ["occurcountry","seriousnesscongenitalanomali","seriousnessdisabling","seriousnesslifethreatening","seriousnessdeath","seriousnesshospitalization","seriousnessother"]
serious = pd.DataFrame(data[list(columnscr)].values)  
serious.columns = columnscr
serious= serious[serious['occurcountry'].isin(top_10_country.index.tolist())]
country_serious = serious.groupby(serious['occurcountry']).count()
plt.style.use('fivethirtyeight')
country_serious.plot.bar()


#Patient Age Distribution by Medicine
top_10_medicines = drugs['medicinalproduct'].value_counts()[:10]
age = drugs[drugs['medicinalproduct'].isin(top_10_medicines.index.tolist())]
age = age[age['patientonsetageunit'] == '801'] 
age['patientonsetage'] = age['patientonsetage'].astype('float64')
age = age.reset_index()
age_med = age.pivot_table(index=age.index, columns='medicinalproduct', values='patientonsetage')
age_med.plot.box()


