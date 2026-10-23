# Independent check of switch (g): MTF gross everywhere + MTF (net) panel. Stdlib only; reads snapshot JSON only.
import json
d=json.load(open('/home/user/brokersdashboard/snapshot/db_snapshot_2026-10-23.json'))
cal={c['trade_date']:c for c in d['calendar']}
F=next(a['value'] for a in d['assumptions'] if a['key']=='mtf_net_factor')
G={};N={}
for x in d['parity_expected']:
    k,_,dt=x['key'].partition('|')
    if x['kind']=='daily' and k=='mtf_gross_cr': G[dt]=x['value']
    if x['kind']=='daily' and k=='mtf_net_cr': N[dt]=x['value']
n=ag=0
def cmp(name,m,c):
    global n,ag
    n+=1; ok=abs(m-c)/abs(c)<=1e-6 or abs(m-c)<=5.5e-7; ag+=ok
    print('%-44s mine %.9f claim %.6f %s'%(name,m,c,'AGREE' if ok else 'DISAGREE'))
# net = F * gross, every date
n+=1; assert set(G)==set(N); mx=max(abs(N[t]-F*G[t])/G[t] for t in G); ok=mx<=1e-9; ag+=ok
print('net==%.2f*gross on %d dates, max rel err %.2e %s'%(F,len(G),mx,'AGREE' if ok else 'DISAGREE'))
SPECIAL='2025-10-21'
def avg(dates,B): return sum(B[t] for t in dates)/len(dates)
def per(field,key,drop):
    return [t for t in G if cal[t][field]==key and not(drop and t==SPECIAL)]
# period claims: (label, field, key, drop, net, gross)
P=[('FY 2027','fy','FY 2027',0,1.894223,4.209385),('Q2 FY 2027','q_fy','Q2 FY 2027',0,2.025551,4.501224),
   ('FY 2027 October','fy_month','FY 2027 October',0,2.127991,4.728868),
   ('FY 2026 (ex 2025-10-21)','fy','FY 2026',1,1.402253,3.116117),('Q3 FY 2026 (ex)','q_fy','Q3 FY 2026',1,1.552563,3.450140),
   ('FY 2026 October (ex)','fy_month','FY 2026 October',1,1.516619,3.370264)]
for lab,f,k,drop,cn,cg in P:
    ds=per(f,k,drop); cmp(lab+' gross (n=%d)'%len(ds),avg(ds,G),cg); cmp(lab+' net',avg(ds,N),cn)
    cmp(lab+' net=0.45*gross claims',F*cg,cn)
# weekday stats on MTF dates
last=max(G); print('last MTF date',last)
def wd(day,m):
    ds=sorted(t for t in G if cal[t]['weekday']==day)
    return ds[-m:]
W=[('Monday',2.121798,4.715107,2.128263,4.729472,2.090619,4.645821),('Tuesday',2.113305,4.696233,None,None,None,None)]
for day,l_n,l_g,a3n,a3g,a10n,a10g in W:
    cmp(day+' latest net',N[wd(day,1)[0]],l_n); cmp(day+' latest gross',G[wd(day,1)[0]],l_g)
    if a3n:
        cmp(day+' avg3 net',avg(wd(day,3),N),a3n); cmp(day+' avg3 gross',avg(wd(day,3),G),a3g)
        cmp(day+' avg10 net',avg(wd(day,10),N),a10n); cmp(day+' avg10 gross',avg(wd(day,10),G),a10g)
# sensitivity: do last-10 windows contain the special date?
print('2025-10-21 in any weekday window:',any(SPECIAL in wd(x,10) for x in('Monday','Tuesday','Wednesday','Thursday','Friday')))
# Consolidated weekday: delta must equal MTF gross-net delta (rows' other segments unchanged)
for day,b,a in(('Monday',20.137207,22.730516),('Thursday',31.451797,34.047645)):
    t=wd(day,1)[0]; dm=G[t]-N[t]; da=a-b
    n+=1; ok=abs(da-dm)<=1.5e-6; ag+=ok
    print('Consolidated %-9s %s claimed d=%.6f  MTF gross-net d=%.9f %s'%(day,t,da,dm,'AGREE' if ok else 'DISAGREE'))
print('checked %d agree %d'%(n,ag))
