# Independent check of switch (f): per-quarter commodity take rate. Stdlib only; snapshot JSON only.
import json,re
R='/home/user/brokersdashboard/snapshot/'
d=json.load(open(R+'db_snapshot_2026-10-23.json'))
f=json.load(open(R+'facts_reviewed_2026-10-23.json'))
seed={}
for x in d['facts']:
    m=re.match(r'excel:Working sheet - Angel One!([A-Z]+)(\d+)$',x['source_ref'])
    if m: seed[(m.group(1),int(m.group(2)))]=x['value']
seed[('J',8)]=35   # switch a
Qn=['Q2 FY 2025','Q3 FY 2025','Q4 FY 2025','Q1 FY 2026','Q2 FY 2026','Q3 FY 2026','Q4 FY 2026','Q1 FY 2027']
cols=dict(zip(Qn,'EFGHIJKM'))
mix={x['period_key']:x['value'] for x in f['facts'] if x['metric']=='revmix_comm' and x['period_key'] in Qn}
rate={q:mix[q]*seed[(cols[q],99)]/seed[(cols[q],8)] for q in Qn}
BASE=0.061*seed[('J',99)]/35
print('rates',{q:round(r,4) for q,r in rate.items()},'base',BASE)
n=ag=0
def cmp(name,m,c,atol=5.5e-7):
    global n,ag
    rd=abs(m-c)/abs(c) if c else abs(m); ok=rd<=1e-6 or abs(m-c)<=atol; n+=1; ag+=ok
    print('%-44s mine %.9f claim %.6f rel %.2e %s'%(name,m,c,rd,'AGREE' if ok else 'DISAGREE'))
CR={'Q2 FY 2025':24.3878,'Q3 FY 2025':24.177,'Q4 FY 2025':25.0025,'Q1 FY 2026':23.2852,'Q2 FY 2026':23.2535,'Q3 FY 2026':23.3141,'Q4 FY 2026':22.1793,'Q1 FY 2027':22.9392}
for q,c in CR.items():
    rd=abs(rate[q]-c)/c; ok=rd<=5e-6; n+=1; ag+=ok   # claims at 4 dp -> half-ulp ~2e-6 rel
    print('%-44s mine %.6f claim %.4f rel %.2e %s'%('rate '+q,rate[q],c,rd,'AGREE' if ok else 'DISAGREE'))
cal={c['trade_date']:c for c in d['calendar']}
special={dt for dt,c in cal.items() if c['special_session']}
pe={x['key'].split('|')[1]:x['value'] for x in d['parity_expected'] if x['kind']=='daily' and x['key'].startswith('comm_rev_mn|')}
def qr(dt):
    q=cal[dt]['q_fy']
    if q in rate: return rate[q]
    fy=int(q[-4:]); qq=int(q[1])
    return rate['Q2 FY 2025'] if (fy,qq)<(2025,2) or (fy,qq)==(2025,1) else rate['Q1 FY 2027']
before={dt:v/10*36/35*0.061/0.06 for dt,v in pe.items()}
after={dt:v*qr(dt)/BASE for dt,v in before.items()}
chg=[dt for dt in before if abs(after[dt]-before[dt])>1e-15]
print('comm days',len(before),'changed',len(chg),'unchanged quarters',sorted({cal[dt]['q_fy'] for dt in before if dt not in chg}))
for nm,m,c in (('comm days total',len(before),660),('comm days changed',len(chg),596)):
    n+=1; ok=m==c; ag+=ok; print(nm,m,c,'AGREE' if ok else 'DISAGREE')
n+=1; ok={cal[dt]['q_fy'] for dt in before if dt not in chg}=={'Q3 FY 2026'}; ag+=ok; print('only Q3 FY26 unchanged',ok)
def adr(dic,key,fld):
    drop=key.startswith('FY 2026') or key=='Q3 FY 2026'
    v=[x for dt,x in dic.items() if cal[dt][fld]==key and not(drop and dt in special)]
    return sum(v)/len(v)
# NB: before[] already /10 (Rs cr); adr returns Rs cr
for p,fl,cb,ca in (('FY 2027','fy',1.607408,1.581557),('Q2 FY 2027','q_fy',1.669814,1.642960),('FY 2027 October','fy_month',2.000169,1.968001),
                   ('FY 2026','fy',1.220379,1.200323),('Q3 FY 2026','q_fy',1.293745,1.293745),('FY 2026 October','fy_month',1.362591,1.362591)):
    b=adr(before,p,fl); a=adr(after,p,fl)
    cmp(f'comm {p} before',b,cb); cmp(f'comm {p} after',a,ca); cmp(f'cons delta {p} (=comm delta)',a-b,ca-cb,1.05e-6)  # claim = diff of two 6dp-rounded values
r=22.9392/23.3141-1; print('ratio pct',r*100)
n+=1; ok=abs(rate['Q1 FY 2027']/BASE-1-(-0.016082))<5e-7; ag+=ok; print('ratio -1.6082%',rate['Q1 FY 2027']/BASE-1,'AGREE' if ok else 'DISAGREE')
for p,fl in (('FY 2027','fy'),('Q2 FY 2027','q_fy'),('FY 2027 October','fy_month')):
    n+=1; ok=abs(adr(after,p,fl)/adr(before,p,fl)-rate['Q1 FY 2027']/BASE)<1e-12; ag+=ok; print(p,'ratio = Q1FY27 rate/base',ok)
print('n',n,'agree',ag)
