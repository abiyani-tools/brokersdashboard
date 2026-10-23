# Independent check of switch (d): drop special sessions from period averages. Stdlib only; reads snapshot JSON only.
import json,re
R='/home/user/brokersdashboard/snapshot/'
d=json.load(open(R+'db_snapshot_2026-10-23.json'))
f=json.load(open(R+'facts_reviewed_2026-10-23.json'))
Q=['Q3 FY 2025','Q4 FY 2025','Q1 FY 2026','Q2 FY 2026','Q3 FY 2026','Q4 FY 2026','Q1 FY 2027']
cols=dict(zip(Q,'FGHIJKM'))
seed={}
for x in d['facts']:
    m=re.match(r'excel:Working sheet - Angel One!([A-Z]+)(\d+)$',x['source_ref'])
    if m: seed[(m.group(1),int(m.group(2)))]=x['value']
new={(x['metric'],x['period_key']):x['value'] for x in f['facts'] if x['metric'] in('revmix_fo','revmix_cash','revmix_comm') and x['period_key'] in Q}
row={'fo':(15,6,'revmix_fo'),'cash':(16,7,'revmix_cash'),'comm':(17,8,'revmix_comm')}
TI={q:seed[(cols[q],99)] for q in Q}
def orders(s,q):
    o=seed[(cols[q],row[s][1])]
    if s=='comm' and q=='Q3 FY 2026': o=35
    return o
tr={s:{q:(seed[(cols[q],rm)]*TI[q]/orders(s,q), new[(mk,q)]*TI[q]/orders(s,q)) for q in Q} for s,(rm,ro,mk) in row.items()}
def avg(s,qs): return (sum(tr[s][q][0] for q in qs)/len(qs), sum(tr[s][q][1] for q in qs)/len(qs))
est_fo=avg('fo',Q[3:6]); est_cash=avg('cash',Q[4:7])
def ratio(s,q):
    if s=='comm': return 0.061/0.06
    if s=='fo': b,a=tr['fo'][q] if q in Q[:6] else est_fo
    if s=='cash': b,a=tr['cash'][q] if q in Q else est_cash
    return a/b
def e10(a):
    ts=[]
    for q in ('Q2 FY 2026','Q3 FY 2026','Q4 FY 2026'):
        o6,o7,o8=seed[(cols[q],6)],seed[(cols[q],7)],seed[(cols[q],8)]
        if q=='Q3 FY 2026' and a: o8=35
        ts.append(o6/(o6+o7+o8))
    return sum(ts)/3
ra=e10(True)/e10(False)
cal={c['trade_date']:c for c in d['calendar']}
special={dt for dt,c in cal.items() if c['special_session']}
# (c) volume ratios
md={(x['dataset'],x['trade_date']):x for x in d['market_daily'] if x['metric']=='contracts'}
lake={x['trade_date']:x for x in d['market_daily_lake'] if x['dataset']=='bse_fo' and x['metric']=='contracts'}
FROZEN=18962859
vr={dt:(md[('nse_fo',dt)]['value']+lake[dt]['value'])/(md[('nse_fo',dt)]['value']+FROZEN) for dt in lake}
pe={}
for x in d['parity_expected']:
    p=x['key'].split('|')
    if x['kind']=='daily' and len(p)==2 and p[0] in('fo_rev_mn','cash_rev_mn','comm_rev_mn','mtf_gross_cr'): pe[(p[0].split('_')[0],p[1])]=x['value']
D={}   # (seg,date)->(value Rs cr after a+b+c, q, fy, fym)
for (s,dt),v in pe.items():
    c=cal[dt]; q=c['q_fy']; b=v
    if s=='mtf': D[(s,dt)]=b; continue
    b/=10
    if s=='comm': b*=36/35
    if s=='fo':
        if q=='Q3 FY 2026': b*=381/380
        elif dt>='2026-04-01': b*=ra
    b*=ratio(s,q)
    if s=='fo': b*=vr.get(dt,1.0)
    D[(s,dt)]=b
print('special sessions in calendar:',sorted(special))
print('in daily series:',sorted({dt for (s,dt) in D if dt in special}),'| per seg:',{s:sorted(dt for (ss,dt) in D if ss==s and dt in special) for s in('fo','cash','comm','mtf')})
def seg_avg(s,key,field,drop):
    v=[val for (ss,dt),val in D.items() if ss==s and cal[dt][field]==key and not(drop and dt in special)]
    return sum(v)/len(v),len(v)
def adr(key,field,drop):
    a={s:seg_avg(s,key,field,drop)[0] for s in('fo','cash','comm','mtf')}
    a['cons']=a['fo']+a['cash']+a['comm']+a['mtf']; return a
claims={
 ('FY 2027','fy'):({'cons':None},None),
}
CL={ # (period,field): {seg:(before,after)}
 ('FY 2026','fy'):{'cons':(15.555597,15.597885),'fo':(9.513241,9.547485),'cash':(1.709086,1.713904),'comm':(1.216053,1.220379),'mtf':(3.117217,3.116117)},
 ('Q3 FY 2026','q_fy'):{'cons':(15.945517,16.122550),'fo':(9.559822,9.698682),'cash':(1.661333,1.679983),'comm':(1.275227,1.293745),'mtf':(3.449134,3.450140)},
 ('FY 2026 October','fy_month'):{'cons':(16.293960,16.850336),'fo':(9.933101,10.375291),'cash':(1.684168,1.742192),'comm':(1.305592,1.362591),'mtf':(3.371099,3.370264)},
}
n=ag=0
def cmp(name,m,c,tol=5e-7):   # claims rounded to 6dp -> half-ulp 5e-7 absolute; use rel<=1e-6 or abs<=5.5e-7
    global n,ag
    n+=1; rd=abs(m-c)/abs(c); ok=rd<=1e-6 or abs(m-c)<=5.5e-7; ag+=ok
    print('%-34s mine %.9f claim %.6f rel %.2e %s'%(name,m,c,rd,'AGREE' if ok else 'DISAGREE'))
for (p,fld),segs in CL.items():
    b=adr(p,fld,False); a=adr(p,fld,True)
    print(p,'days(fo,cash,comm,mtf) before',[seg_avg(s,p,fld,False)[1] for s in('fo','cash','comm','mtf')],'after',[seg_avg(s,p,fld,True)[1] for s in('fo','cash','comm','mtf')])
    for s,(cb,ca) in segs.items():
        cmp(f'{p} {s} before',b[s],cb); cmp(f'{p} {s} after',a[s],ca)
for p,fld in (('FY 2027','fy'),('Q2 FY 2027','q_fy'),('FY 2027 October','fy_month')):
    b=adr(p,fld,False); a=adr(p,fld,True)
    n+=1; ok=all(abs(a[s]-b[s])<=1e-12 for s in b); ag+=ok
    print(p,'no change:',ok,'cons %.9f'%b['cons'])
print('n',n,'agree',ag)
