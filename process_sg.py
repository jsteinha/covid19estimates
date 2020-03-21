import string
#f = open('sg-data.txt')
#f = open('tw-data.txt')

tables = dict()
def make_table(name):
  f = open(name)
  table_rows = []
  table_cols = ['Case', 'Patient', 'Age', 'Gender', 'Nationality', 'Status', 'Source', 'Origin', 'SympToConf', 'DaysToRecover', 'SymptomsOn', 'ConfirmedOn', 'RecoveredOn', 'DisplayedSymptoms']
  
  
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
  
  begun = False
  in_row = False
  for line in f:
    t = line.rstrip(' \n').lstrip(' ')
    #if '<table class="table table-striped table-dashboard table-dashboard-one" id="casesTable">' in t:
    if '</thead>' in t:
      begun = True
    if not begun:
      continue
    if '</table>' in t:
      break
    elif '<tr>' in t:
      table_row = []
      in_row = True
    elif '</tr>' in t:
      table_rows.append(dict(zip(table_cols, table_row)))
      in_row = False
    elif in_row:
      start, mid, end = strip_td(t)
      if start:
        table_col = ''
      if len(table_row) >= 7:
        mid = mid.lower()
      table_col += mid
      if end:
        table_row.append(table_col)
  return table_rows

def process(name):
  f = open(name)
  out = dict()
  for line in f:
    toks = line.rstrip('\n').lower().split('\t')
    if len(toks) < 2:
      continue
    if len(toks) == 3:
      toks = [toks[0], toks[2]]
    if len(toks[1]) == 0:
      continue
    toks[1] = int(toks[1].replace(',', ''))
    if toks[0] in out.keys():
      out[toks[0]] = max(out[toks[0]], toks[1])
    else:
      out[toks[0]] = toks[1]
  return out

#f = open('sg-jan-20-travel.txt')
#f = open('tw-jan-20-travel.txt')
#f = open('tourism-all.txt')
#f = open('tw-outbound.csv')
#f = open('sg-outbound.csv')

tables = dict()
tables['sg'] = make_table('sg-data.txt')
tables['tw'] = make_table('tw-data.txt')

travel = dict()
travel['sg_in'] = process('sg-jan-20-travel.txt')
travel['sg_out'] = process('sg-outbound.csv')
travel['tw_in'] = process('tw-jan-20-travel.txt')
travel['tw_out'] = process('tw-outbound.csv')

  

#tourism0 = { 'china' 	        :  3416475,
#             'indonesia' 	    :  3021429,
#             'india' 	        :  1442242,
#             'malaysia'       : 	1253992,
#             'australia' 	    :  1107215,
#             'japan' 	        :  829664,
#             'philippines' 	  :  778135,
#             'united states' 	:  643162,
#             'south korea' 	  :  629451,
#             'vietnam' 	      :  591600,
#             'united kingdom' :	588863,
#             'thailand' 	    :  545601,
#             'hong kong' 	    :  473113,
#             'taiwan' 	      :  422935,
#             'germany' 	      :  356797 }

denom = { 'sg_in' : 0.5/6.2, 'sg_out'  : 5/73.0,
          'tw_in' : 0.15/6.2, 'tw_out' : 1.5/73.0,
        }
origins = dict()
#origins['sg_all'] = [r['Origin'] for r in table_rows if 'Imported' in r['Source']]
origins['sg_in']  = [r['Origin'] for r in tables['sg'] if 'Imported' in r['Source'] and 'Singap' not in r['Patient'] and 'Singap' not in r['Nationality']]
origins['sg_out'] = [r['Origin'] for r in tables['sg'] if 'Imported' in r['Source'] and ('Singap' in r['Patient'] or 'Singap' in r['Nationality'])]
origins['tw_in']  = [r['Origin'] for r in tables['tw'] if 'Imported' in r['Source'] and 'Taiwa' not in r['Patient'] and 'Taiwa' not in r['Nationality']]
origins['tw_out'] = [r['Origin'] for r in tables['tw'] if 'Imported' in r['Source'] and ('Taiwa' in r['Patient'] or 'Taiwa' in r['Nationality'])]
#origins = [r['Origin'] for r in table_rows if 'Imported' in r['Source'] and 'Taiwa' not in r['Patient'] and 'Taiwa' not in r['Nationality']]
#import matplotlib.pyplot as plt

import collections
from math import sqrt
counts = collections.defaultdict(int)

countries = set()
for k, v in travel.items():
  countries = countries | v.keys()
sources = ['sg_in', 'sg_out', 'tw_in', 'tw_out']
alpha = dict()
for s in sources:
  alpha[s] = 1.0
lam = dict()
for c in countries:
  lam[c] = 1.0
for k, v in origins.items():
  counts[k] = collections.Counter(v)

import numpy as np
for _ in range(100):
  # alpha update
  for s in sources:
    num, den = 0.0, 0.0
    for c in travel[s].keys():
      num += counts[s][c]
      den += lam[c] * travel[s][c]
    alpha[s] = num / den
  # normalize so that average is 3e-4
  alpha_mean = np.mean([a for a in alpha.values()])
  for s in sources:
    alpha[s] = alpha[s] * 5e-4 / alpha_mean
  # lambda update
  for c in countries:
    num, den = 0.0, 0.0
    for s in sources:
      if c in travel[s].keys():
        num += counts[s][c]
        den += alpha[s] * travel[s][c]
    lam[c] = num / den

prev = dict()
prev_hi = dict()
prev_lo = dict()
for k, v in origins.items():
  countries = travel[k].keys()
  #countries = counts[k].keys() & travel[k].keys()
  prev[k] = dict()
  prev[k+'_pred'] = dict()
  prev_hi[k] = dict()
  prev_lo[k] = dict()
  for c in countries:
    prev[k][c]    = counts[k][c] / (alpha[k] * travel[k][c])
    prev_hi[k][c] = (counts[k][c] + sqrt(counts[k][c])) / (alpha[k] * travel[k][c])
    prev_lo[k][c] = (counts[k][c] - sqrt(counts[k][c])) / (alpha[k] * travel[k][c])
    prev[k+'_pred'][c] = travel[k][c] * alpha[k] * lam[c]
  prev[k+'_count'] = counts[k]

prev['all'] = lam

import pandas as pd
df = pd.DataFrame(prev)
df.to_csv('tw-sg-data.csv')


#l = range(len(x.keys()))
#plt.bar(l, x.values(), align='center')
#plt.xticks(l, x.keys())
#
#countries = x.keys() & tourism.keys()
#prevalence = dict()
#prev_low = dict()
#prev_high = dict()
#from math import sqrt
#denom = 365.0 # 31.0
#for c in countries:
#  prevalence[c] = 100 * x[c] / (5 * (tourism[c] / denom))
#  prev_low[c] = 100 * (x[c] - sqrt(x[c])) / (5 * (tourism[c] / denom))
#  prev_high[c] = 100 * (x[c] + sqrt(x[c])) / (5 * (tourism[c] / denom))

