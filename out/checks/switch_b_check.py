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
new={}
for x in f['facts']:
    if x['metric'] in('revmix_fo','revmix_cash','revmix_comm') and x['period_key'] in Q: new[(x['metric'],x['period_key'])]=x['value']
row={'fo':(15,6,'revmix_fo'),'cash':(16,7,'revmix_cash'),'comm':(17,8,'revmix_comm')}
TI={q:seed[(cols[q],99)] for q in Q}
def orders(s,q,a=True):
    o=seed[(cols[q],row[s][1])]
    if s=='comm' and q=='Q3 FY 2026': o=35 if a else 36
    return o
tr={}  # tr[s][q]=(before,after)
for s,(rm,ro,mk) in row.items():
    tr[s]={}
    for q in Q:
        b=seed[(cols[q],rm)]*TI[q]/orders(s,q); a=new[(mk,q)]*TI[q]/orders(s,q)
        tr[s][q]=(b,a)
        print(s,q,'mix',seed[(cols[q],rm)],'->',new[(mk,q)],'TR %.6f -> %.6f ratio %.9f'%(b,a,a/b))
# ratio per segment/quarter ('Q2 FY 2027+' = estimate)
def avg(s,qs):
    return (sum(tr[s][q][0] for q in qs)/len(qs), sum(tr[s][q][1] for q in qs)/len(qs))
est_fo=avg('fo',Q[3:6]); est_cash=avg('cash',Q[4:7])
print('FO est',est_fo,est_fo[1]/est_fo[0]); print('cash est',est_cash,est_cash[1]/est_cash[0])
def ratio(s,q):
    if s=='comm':
        return 0.061/0.06
    if s=='fo':
        if q in Q[:6]: b,a=tr['fo'][q]
        else: b,a=est_fo
    if s=='cash':
        if q in Q: b,a=tr['cash'][q]
        else: b,a=est_cash
    return a/b
# switch a
def e10(a):
    ts=[]
    for q in ('Q2 FY 2026','Q3 FY 2026','Q4 FY 2026'):
        o6,o7=seed[(cols[q],6)],seed[(cols[q],7)]
        o8=seed[(cols[q],8)]
        if q=='Q3 FY 2026' and a: o8=35
        ts.append(o6/(o6+o7+o8))
    return sum(ts)/3
# E50 = avg of 9 months = I,J,K x3 months each
ra=e10(True)/e10(False); print('E50 ratio a',ra, 'q3 ratio',381/380)
cal={c['trade_date']:c for c in d['calendar']}
pe={}
for x in d['parity_expected']:
    p=x['key'].split('|')
    if x['kind']=='daily' and len(p)==2 and p[0] in('fo_rev_mn','cash_rev_mn','comm_rev_mn'): pe[(p[0],p[1])]=x['value']
rows=[]  # (seg,date,before,after,q,fy,fym)
for (k,dt),v in pe.items():
    c=cal[dt]; s=k.split('_')[0]; q=c['q_fy']
    b=v
    if s=='comm': b*=36/35
    if s=='fo':
        if q=='Q3 FY 2026': b*=381/380
        elif dt>='2026-04-01': b*=ra
    r=ratio(s,q)
    rows.append((s,dt,b,b*r,q,c['fy'],c['fy_month'],r))
import collections
def adr(s,key,idx):
    v=[(r[2],r[3]) for r in rows if r[0]==s and r[idx]==key]
    return len(v),sum(a for a,_ in v)/len(v)/10,sum(b for _,b in v)/len(v)/10
claims={('comm','FY 2027'):(1.581057,1.607408),('comm','Q2 FY 2027'):(1.642440,1.669814),('comm','FY 2027 October'):(1.967379,2.000169),
('fo','FY 2027'):(9.293706,9.287777),('fo','Q2 FY 2027'):(8.505598,8.500172),('fo','FY 2027 October'):(6.750116,6.745811),
('cash','FY 2027'):(2.064588,2.005320),('cash','Q2 FY 2027'):(1.965533,1.934712),('cash','FY 2027 October'):(2.163120,2.129202)}
idxm={'FY 2027':5,'Q2 FY 2027':4,'FY 2027 October':6}
n=ag=0;mine={}
def cmp(name,m,c):
    global n,ag
    n+=1; rd=abs(m-c)/abs(c); ok=rd<=1e-6; ag+=ok
    print('%-40s mine %.9f claim %.9f rel %.2e %s'%(name,m,c,rd,'AGREE' if ok else 'DISAGREE'))
for (s,p),(cb,ca) in claims.items():
    nd,b,a=adr(s,p,idxm[p]); mine[(s,p)]=(b,a)
    print(s,p,'days',nd)
    cmp(f'{s} {p} before',b,cb); cmp(f'{s} {p} after',a,ca)
for p,c in (('FY 2027',-0.038846),('Q2 FY 2027',-0.008872),('FY 2027 October',-0.005435)):
    dl=sum(mine[(s,p)][1]-mine[(s,p)][0] for s in('fo','cash','comm'))
    print(p,'unrounded delta',dl,'(rounded-claims delta %.6f)'%sum(claims[(s,p)][1]-claims[(s,p)][0] for s in('fo','cash','comm')))
    # delta tolerance: 6dp rounding of components; use abs tol 3e-6 as table rounding
    n+=1; ok=abs(dl-c)<=1.5e-6+1e-12; ag+=ok
    print('  delta vs claim %.6f: abs diff %.2e'%(c,abs(dl-c)),'AGREE(<=1.5e-6 abs, rounding)' if ok else 'DISAGREE')
# explicit factor claims
cmp('comm daily ratio',0.061/0.06,1.016666667)
cmp('cash Q1FY27 TR before',tr['cash']['Q1 FY 2027'][0],0.09*14337/67); 
cmp('cash est TR after',est_cash[1],16.5122); cmp('cash est TR before',est_cash[0],16.7752)
cmp('fo ratio FY27',est_fo[1]/est_fo[0],1-0.000638)
cmp('fo Q3FY26 ratio',tr['fo']['Q3 FY 2026'][1]/tr['fo']['Q3 FY 2026'][0],0.443/0.44)
ch=sum(1 for r in rows if r[0]=='cash' and abs(r[7]-1)>1e-12); tot=sum(1 for r in rows if r[0]=='cash')
print('cash days changed',ch,'of',tot); n+=1; ag+=(ch==385 and tot==509)
print('cash unchanged q',sorted({r[4] for r in rows if r[0]=='cash' and abs(r[7]-1)<=1e-12}))
print('n',n,'agree',ag)
