import string
f = open('sg-filt.txt')

table_rows = []
table_cols = ['Case', 'Patient', 'Age', 'Gender', 'Nationality', 'Status', 'Source', 'Origin', 'SympToConf', 'DaysToRecover', 'Symptoms', 'ConfirmedOn', 'RecoveredOn']

def mb(t, s):
  return t[:len(s)] == s
def me(t, s):
  return t[-len(s):] == s
def strip_td(t):
  start = False
  end = False
  if mb(t, '<td'):
    start = True
    t = t[t.index('>')+1:]
  if me(t, '</td>'):
    end = True
    t = t[:-5]
  return start, t, end

for line in f:
  t = line.rstrip(' \n').lstrip(' ')
  if '<tr>' in t:
    table_row = []
  elif '</tr>' in t:
    table_rows.append(dict(zip(table_cols, table_row)))
  else:
    start, mid, end = strip_td(t)
    if start:
      table_col = ''
    if len(table_row) >= 7:
      mid = mid.lower()
    table_col += mid
    if end:
      table_row.append(table_col)

f = open('jan-20.txt')
tourism = dict()
for line in f:
  toks = line.rstrip('\n').lower().split('\t')
  toks[1] = int(toks[1].replace(',', ''))
  tourism[toks[0]] = toks[1]
  

tourism0 = { 'china' 	        :  3416475,
             'indonesia' 	    :  3021429,
             'india' 	        :  1442242,
             'malaysia'       : 	1253992,
             'australia' 	    :  1107215,
             'japan' 	        :  829664,
             'philippines' 	  :  778135,
             'united states' 	:  643162,
             'south korea' 	  :  629451,
             'vietnam' 	      :  591600,
             'united kingdom' :	588863,
             'thailand' 	    :  545601,
             'hong kong' 	    :  473113,
             'taiwan' 	      :  422935,
             'germany' 	      :  356797 }


origins0 = [r['Origin'] for r in table_rows if 'Imported' in r['Source']]
origins = [r['Origin'] for r in table_rows if 'Imported' in r['Source'] and 'Singap' not in r['Patient'] and 'Singap' not in r['Nationality']]
import matplotlib.pyplot as plt
import collections
x = collections.Counter(origins)
l = range(len(x.keys()))
plt.bar(l, x.values(), align='center')
plt.xticks(l, x.keys())

countries = x.keys() & tourism.keys()
prevalence = dict()
prev_low = dict()
prev_high = dict()
from math import sqrt
for c in countries:
  prevalence[c] = 100 * x[c] / (5 * (tourism[c] / 31.0))
  prev_low[c] = 100 * (x[c] - sqrt(x[c])) / (5 * (tourism[c] / 31.0))
  prev_high[c] = 100 * (x[c] + sqrt(x[c])) / (5 * (tourism[c] / 31.0))

