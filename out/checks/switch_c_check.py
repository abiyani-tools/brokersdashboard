# Independent check of switch (c): BSE F&O frozen days -> real totals. Stdlib only; reads snapshot JSON only.
import json,re
R='/home/user/brokersdashboard/snapshot/'
d=json.load(open(R+'db_snapshot_2026-10-23.json'))
f=json.load(open(R+'facts_reviewed_2026-10-23.json'))
# ---- (a),(b) F&O before-adjustments, same as switch_b_check.py ----
Q=['Q3 FY 2025','Q4 FY 2025','Q1 FY 2026','Q2 FY 2026','Q3 FY 2026','Q4 FY 2026','Q1 FY 2027']
cols=dict(zip(Q,'FGHIJKM'))
seed={}
for x in d['facts']:
    m=re.match(r'excel:Working sheet - Angel One!([A-Z]+)(\d+)$',x['source_ref'])
    if m: seed[(m.group(1),int(m.group(2)))]=x['value']
new={(x['period_key']):x['value'] for x in f['facts'] if x['metric']=='revmix_fo' and x['period_key'] in Q}
TI={q:seed[(cols[q],99)] for q in Q}
tr={q:(seed[(cols[q],15)]*TI[q]/seed[(cols[q],6)], new[q]*TI[q]/seed[(cols[q],6)]) for q in Q}
est=[sum(tr[q][i] for q in Q[3:6])/3 for i in (0,1)]
def fo_ratio_b(q): return tr[q][1]/tr[q][0] if q in Q[:6] else est[1]/est[0]
def e10(a):
    ts=[]
    for q in ('Q2 FY 2026','Q3 FY 2026','Q4 FY 2026'):
        o6,o7,o8=seed[(cols[q],6)],seed[(cols[q],7)],seed[(cols[q],8)]
        if q=='Q3 FY 2026' and a: o8=35
        ts.append(o6/(o6+o7+o8))
    return sum(ts)/3
ra=e10(True)/e10(False)
cal={c['trade_date']:c for c in d['calendar']}
pe={x['key'].split('|')[1]:x['value'] for x in d['parity_expected'] if x['kind']=='daily' and x['key'].startswith('fo_rev_mn|')}
# ---- market volumes ----
md={(x['dataset'],x['trade_date']):x for x in d['market_daily'] if x['metric']=='contracts'}
lake={x['trade_date']:x for x in d['market_daily_lake'] if x['dataset']=='bse_fo' and x['metric']=='contracts'}
FROZEN=18962859
imp=sorted(dt for (ds,dt),x in md.items() if ds=='bse_fo' and x['status']=='imputed')
print('imputed bse_fo days',len(imp),imp[0],imp[-1],'| lake days',len(lake),'| same set',imp==sorted(lake))
print('other imputed rows:',sorted({(ds,x['status']) for (ds,dt),x in md.items() if x['status']!='ok'}))
print('all imputed values == frozen:',all(md[('bse_fo',dt)]['value']==FROZEN for dt in imp))
exp={'2026-09-29':27311202,'2026-09-30':152837325,'2026-10-01':512976127,'2026-10-05':26843978,'2026-10-06':27015960,
 '2026-10-07':162293562,'2026-10-08':459891587,'2026-10-09':18761074,'2026-10-12':26038276,'2026-10-13':40228045,
 '2026-10-14':174459443,'2026-10-15':493485755,'2026-10-16':24749231,'2026-10-19':32609976,'2026-10-21':188513714}
vr={}
for dt in imp:
    nse=md[('nse_fo',dt)]['value']; real=lake[dt]['value']
    vr[dt]=(nse+real)/(nse+FROZEN)
    print(dt,'NSE',nse,'BSE real',real,'ratio %.9f'%vr[dt])
rows=[]
for dt,v in pe.items():
    c=cal[dt]; q=c['q_fy']; b=v
    if q=='Q3 FY 2026': b*=381/380
    elif dt>='2026-04-01': b*=ra
    b_ = b*fo_ratio_b(q)   # Q1 FY27+ uses the projected-rate ratio (0.999362095)
    # switch (a) on Oct-Dec 2025 only uses J8; (b) ratios per quarter as in switch_b_check
    rows.append((dt,q,c['fy'],c['fy_month'],b_,b_*vr.get(dt,1.0)))
def adr(key,idx):
    v=[(r[4],r[5]) for r in rows if r[idx]==key]
    return len(v),sum(a for a,_ in v)/len(v)/10,sum(b for _,b in v)/len(v)/10
n=ag=0
def cmp(name,m,c,tol=1e-6):
    global n,ag
    n+=1; rd=abs(m-c)/abs(c); ok=rd<=tol; ag+=ok
    print('%-44s mine %.9f claim %.9f rel %.2e %s'%(name,m,c,rd,'AGREE' if ok else 'DISAGREE'))
cl={'FY 2027':(9.287777,9.785974,5),'Q2 FY 2027':(8.500172,8.572370,4),'FY 2027 October':(6.745811,11.673365,6)}
idx={'FY 2027':2,'Q2 FY 2027':1,'FY 2027 October':3}
mine={}
for p,(cb,ca,_) in cl.items():
    nd,b,a=adr(p,idx[p]); mine[p]=(b,a); print(p,'days',nd)
    cmp(p+' before',b,cb,5e-7); cmp(p+' after',a,ca,5e-7)   # claims rounded to 6dp
for p,c in (('FY 2027',0.498196),('Q2 FY 2027',0.072198),('FY 2027 October',4.927554)):
    dl=mine[p][1]-mine[p][0]; n+=1; ok=abs(dl-c)<=1.5e-6; ag+=ok
    print(p,'F&O delta %.7f claim %.6f'%(dl,c),'AGREE' if ok else 'DISAGREE')
chg=[dt for dt,r in vr.items() if abs(r-1)>1e-12]
n+=1; ag+=(len(chg)==15); print('days changed',len(chg),'of',len(rows),'F&O days; outside set changed:',sum(1 for r in rows if r[0] not in vr and r[5]!=r[4]))
lo,hi=min(vr.values()),max(vr.values()); cmp('ratio min',lo,0.998659758,5e-9); cmp('ratio max',hi,5.390308547,5e-9)
print('min on',min(vr,key=vr.get),'max on',max(vr,key=vr.get))
n+=1; k=sum(lake[dt]['value']==exp[dt] for dt in exp)==15 and sorted(exp)==sorted(lake); ag+=k; print('lake values/dates match task list',k)
print('n',n,'agree',ag)
