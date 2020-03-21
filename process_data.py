import string

# reads HTML file from one of the againstcovid websites, parses it into a dictionary
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

# processes a tab-separated file containing travel data. somewhat hacky currently to capture a couple different formats
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

# load sg and tw againstcovid data
tables = dict()
tables['sg'] = make_table('sg-data.txt')
tables['tw'] = make_table('tw-data.txt')

# load sg and tw travel data
travel = dict()
travel['sg_in'] = process('sg-jan-20-travel.txt')
travel['sg_out'] = process('sg-outbound.csv')
travel['tw_in'] = process('tw-jan-20-travel.txt')
travel['tw_out'] = process('tw-outbound.csv')

origins = dict()
# if 'Singap' appears in nationality or patient description we assume they are returning from an outbound trip
origins['sg_out'] = [r['Origin'] for r in tables['sg'] if 'Imported' in r['Source'] and ('Singap' in r['Patient'] or 'Singap' in r['Nationality'])]
# otherwise we assume they are a visitor
origins['sg_in']  = [r['Origin'] for r in tables['sg'] if 'Imported' in r['Source'] and 'Singap' not in r['Patient'] and 'Singap' not in r['Nationality']]
# if 'Taiwa' appears in nationality or patient description we assume they are returning from an outbound trip; currently the data doesn't have patient descriptions so second check likely does nothing
origins['tw_in']  = [r['Origin'] for r in tables['tw'] if 'Imported' in r['Source'] and 'Taiwa' not in r['Patient'] and 'Taiwa' not in r['Nationality']]
origins['tw_out'] = [r['Origin'] for r in tables['tw'] if 'Imported' in r['Source'] and ('Taiwa' in r['Patient'] or 'Taiwa' in r['Nationality'])]

import collections
from math import sqrt

# make a list of all the countries occuring in any travel data
countries = set()
for k, v in travel.items():
  countries = countries | v.keys()
# list of possible sources
sources = ['sg_in', 'sg_out', 'tw_in', 'tw_out']
# initialize alpha and lambda values
alpha = dict()
for s in sources:
  alpha[s] = 1.0
lam = dict()
for c in countries:
  lam[c] = 1.0
# aggregate origin data into a counts dictionary
counts = collections.defaultdict(int)
for k, v in origins.items():
  counts[k] = collections.Counter(v)

# run alternating maximization to compute the MLE estimates for alpha and lambda
import numpy as np
for _ in range(100):
  # alpha update
  for s in sources:
    num, den = 0.0, 0.0
    for c in travel[s].keys():
      num += counts[s][c]
      den += lam[c] * travel[s][c]
    alpha[s] = num / den
  # normalize so that average is 3e-4 (causes lambda to match up with estimates total cases based on deaths)
  alpha_mean = np.mean([a for a in alpha.values()])
  for s in sources:
    alpha[s] = alpha[s] * 3e-4 / alpha_mean
  # lambda update
  for c in countries:
    num, den = 0.0, 0.0
    for s in sources:
      if c in travel[s].keys():
        num += counts[s][c]
        den += alpha[s] * travel[s][c]
    lam[c] = num / den

prev = dict()
for k, v in origins.items():
  cur_countries = travel[k].keys()
  prev[k+'_prev'] = dict()
  prev[k+'_count_est'] = dict()
  for c in cur_countries:
    prev[k+'_prev'][c]    = counts[k][c] / (alpha[k] * travel[k][c])
    est = travel[k][c] * alpha[k] * lam[c]
    # estimated count, plus or minus one standard deviation
    # useful for comparing to actual count to see if fluctuations across regions are compatible with small-N noise
    prev[k+'_count_est'][c] = '[%.1f, %.1f, %.1f]' % (max(0, est - sqrt(est)), est, est + sqrt(est))
  prev[k+'_count'] = counts[k]

# overall estimate
prev['all'] = lam

import pandas as pd
df = pd.DataFrame(prev)
df.to_csv('tw-sg-data.csv')
