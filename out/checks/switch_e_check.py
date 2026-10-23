# Independent check of switch (e): projected cash days use monthly cash share. Stdlib only; snapshot JSON only.
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
new={(x['metric'],x['period_key']):x['value'] for x in f['facts'] if x['metric']=='revmix_cash' and x['period_key'] in Q}
TI={q:seed[(cols[q],99)] for q in Q}
tr={q:(seed[(cols[q],7)]*TI[q]/seed[(cols[q],7)] if False else seed[(cols[q],16)]*TI[q]/seed[(cols[q],7)], new[('revmix_cash',q)]*TI[q]/seed[(cols[q],7)]) for q in Q}
est=(sum(tr[q][0] for q in Q[4:])/3, sum(tr[q][1] for q in Q[4:])/3)
cal={c['trade_date']:c for c in d['calendar']}
pe={x['key'].split('|')[1]:x['value'] for x in d['parity_expected'] if x['kind']=='daily' and x['key'].startswith('cash_rev_mn|')}
# BEFORE (a+b+c+d) cash, Rs Mn
before={}
for dt,v in pe.items():
    q=cal[dt]['q_fy']; b,a=tr[q] if q in Q else est
    before[dt]=v*a/b
# monthly share facts
mon={}
for x in d['facts']+f['facts']:
    if x['metric']=='share_cash' and x['period_type']=='M': mon[x['period_key']]=(x['value'],x['fact_id'])
print('FY2027 monthly cash shares:',{k:v for k,v in mon.items() if k.startswith('FY 2027')})
n=ag=0
def chk(name,ok,info=''):
    global n,ag
    n+=1; ag+=bool(ok); print('%-52s %s %s'%(name,'AGREE' if ok else 'DISAGREE',info))
for k,v,i in (('FY 2027 July',0.171,544),('FY 2027 August',0.17,527),('FY 2027 September',0.162,561)):
    chk('fact '+k,abs(mon[k][0]-v)<=1e-12 and mon[k][1]==i,str(mon[k]))
chk('no FY 2027 October monthly share','FY 2027 October' not in mon)
# month order from calendar
order=[]
for dt in sorted(cal):
    m=cal[dt]['fy_month']
    if not order or order[-1]!=m: order.append(m)
def mshare(m):
    i=order.index(m)
    while i>=0:
        if order[i] in mon: return mon[order[i]][0],order[i]
        i-=1
Q1S=0.174
after={}; changed=[]
for dt,v in before.items():
    q=cal[dt]['q_fy']
    if q in Q: after[dt]=v; continue
    s,src=mshare(cal[dt]['fy_month'])
    after[dt]=v*s/Q1S
    if abs(after[dt]-v)>1e-15: changed.append(dt)
print('projected-day months used:',sorted({(cal[dt]['fy_month'],mshare(cal[dt]['fy_month'])) for dt in before if cal[dt]['q_fy'] not in Q}))
chk('78 cash days change',len(changed)==78,'n=%d %s..%s'%(len(changed),min(changed),max(changed)))
chk('range 2026-07-01..2026-10-21',(min(changed),max(changed))==('2026-07-01','2026-10-21'))
chk('all dates >=2026-07-01 are changed (no gaps)',all(dt in changed for dt in before if dt>='2026-07-01'))
def adr(dic,key,fld):
    v=[x for dt,x in dic.items() if cal[dt][fld]==key]; return sum(v)/len(v)/10
CL=[('FY 2027','fy',2.005320,1.958058),('Q2 FY 2027','q_fy',1.934712,1.863740),('FY 2027 October','fy_month',2.129202,1.982360)]
for p,fl,cb,ca in CL:
    b=adr(before,p,fl); a=adr(after,p,fl)
    for nm,m,c in (('before',b,cb),('after',a,ca)):
        rd=abs(m-c)/c; chk(f'cash {p} {nm}',rd<=1e-6 or abs(m-c)<=5.5e-7,'mine %.9f claim %.6f rel %.2e'%(m,c,rd))
for p,fl,c in (('FY 2027','fy',-0.047262),('Q2 FY 2027','q_fy',-0.070972),('FY 2027 October','fy_month',-0.146841)):
    dl=adr(after,p,fl)-adr(before,p,fl); chk(f'cons delta {p} (=cash; others unchanged)',abs(dl-c)<=1.5e-6,'mine %.9f claim %.6f'%(dl,c))
chk('Oct ratio 0.162/0.174-1 = -6.8966%',abs((0.162/0.174-1)*100+6.8966)<5e-5,'%.6f%%'%((0.162/0.174-1)*100))
for p,fl in (('FY 2026','fy'),('Q3 FY 2026','q_fy'),('FY 2026 October','fy_month')):
    chk(f'cash {p} unchanged',abs(adr(after,p,fl)-adr(before,p,fl))<=1e-12,'%.9f'%adr(after,p,fl))
print('n',n,'agree',ag)
