#!/usr/bin/env python3
"""
AEGIS ACHERON v2 — BEAST 5 · THE RIVER OF PAIN
Author:  Rafael Amichis Luengo (The Architect)
Engine:  Claude (Anthropic) | Auditors: Gemini · ChatGPT · Grok
Project: Proyecto Estrella · Error Code Lab
Date:    26 February 2026
LICENSE: BSL 1.1 + Acheron Clause (permanent ethical restriction)

Phase III: DRAIN — "El Desierto de Agua Seca"

v2 — ALL AUDITOR FIXES INTEGRATED:
  GEMINI:  Fissure=3rows | D6↔D7 exclusion | Affine autophagy | Air-gap sim
  CHATGPT: Thirst curve log+linear | Probabilistic oasis | XS↔epoch resync
           Pipeline reorder (D3→D2) | 4-phase Thirst Curve psychology
  GROK:    XS transcript between epochs | LRU eviction ct[2048] | D9+D10

  12 Desiccation Layers:
    D1:  Osmotic Entropy      — epoch-chained solar radiation (air-gap first 50q)
    D2:  Zeno Quicksand       — asymptotic convergence trap (AFTER D3 now)
    D3:  Progressive Dehydration — log+linear curve, 4-phase psychology
    D4:  Oasis of Myrrh       — probabilistic sigmoid trigger
    D5:  Geothermal Fissure   — exactly 3 rows, immediate major ops
    D6:  Code Autophagy       — affine Frobenius (masked distribution)
    D7:  Zeno RAM Paradox     — D6-excluded coordinates
    D8:  Osmotic Loot         — cross-column phantom dependencies
    D9:  Mirage Heat-Death    — false rank convergence then collapse (Grok)
    D10: Entropy Black Hole   — circular Frobenius deps in exfiltrated data (Grok)
    D11: Entropy Phase Drift  — per-column epoch offset (ChatGPT)
    D12: Rank Echo Collapse   — rank-proportional perturbation detonator (ChatGPT)

  "No querrás salir con vida. Querrás morir cuanto antes."
"""
import time, hashlib, random
from math import log2, sqrt, exp
from collections import deque, OrderedDict

t0 = time.time()

# ══════════════════════════════════════════════════════════════
# 0. GF(4) CORE
# ══════════════════════════════════════════════════════════════
_AF = (0,1,2,3, 1,0,3,2, 2,3,0,1, 3,2,1,0)
_MF = (0,0,0,0, 0,1,2,3, 0,2,3,1, 0,3,1,2)
_INV = (0,1,3,2); _FROB = (0,1,3,2); DIM = 12

def pack12(vals):
    r = 0
    for i in range(12): r |= (vals[i]&3) << (i*2)
    return r
def unpack12(p): return [(p>>(i*2))&3 for i in range(12)]
def gc(p,i): return (p>>(i*2))&3
def sc(p,i,v): return (p & ~(3<<(i*2))) | ((v&3)<<(i*2))
def pdist(a,b):
    x = a^b; d = 0
    for i in range(12):
        if (x>>(i*2))&3: d += 1
    return d
def padd(a,b):
    r = 0
    for i in range(12):
        r |= _AF[((a>>(i*2))&3)*4+((b>>(i*2))&3)] << (i*2)
    return r

# ══════════════════════════════════════════════════════════════
# XORSHIFT128+ PRNG
# ══════════════════════════════════════════════════════════════
M64 = (1 << 64) - 1
class XS:
    __slots__ = ('s0','s1')
    def __init__(self, seed_bytes):
        self.s0 = int.from_bytes(seed_bytes[:8],'big') | 1
        self.s1 = int.from_bytes(seed_bytes[8:16],'big') | 1
    def next(self):
        s0, s1 = self.s0, self.s1
        r = (s0 + s1) & M64
        s1 ^= s0; self.s0 = ((s0<<24)&M64 | s0>>(64-24)) ^ s1 ^ ((s1<<16)&M64)
        self.s1 = (s1<<37)&M64 | s1>>(64-37); return r
    def ri(self, lo, hi): return lo + self.next() % (hi - lo + 1)
    def r4(self): return self.next() & 3
    def rf(self): return (self.next() & 0xFFFFF) / 0xFFFFF
    def resync(self, hash_bytes):
        """ChatGPT C3: periodic resync with epoch chain."""
        self.s0 = int.from_bytes(hash_bytes[:8],'big') | 1
        self.s1 = int.from_bytes(hash_bytes[8:16],'big') | 1

# ══════════════════════════════════════════════════════════════
# INCREMENTAL WINDOW RANK
# ══════════════════════════════════════════════════════════════
class WRank:
    __slots__ = ('basis','piv','rank','vecs','_rc')
    def __init__(self, win=64):
        self.basis = [[0]*12 for _ in range(12)]
        self.piv = [-1]*12; self.rank = 0
        self.vecs = deque(maxlen=win); self._rc = 0
    def add(self, v):
        self.vecs.append(v[:])
        vv = list(v)
        for p in range(12):
            if self.piv[p] >= 0 and vv[p]:
                f = vv[p]; b = self.basis[p]
                for j in range(12): vv[j] = _AF[vv[j]*4 + _MF[f*4 + b[j]]]
        for i in range(12):
            if vv[i] and self.piv[i] < 0:
                inv = _INV[vv[i]]
                self.basis[i] = [_MF[inv*4+vv[j]] for j in range(12)]
                self.piv[i] = i; self.rank += 1; break
        self._rc += 1
        if self._rc >= 8: self._rebuild(); self._rc = 0
        return self.rank
    def _rebuild(self):
        old = list(self.vecs)
        self.basis = [[0]*12 for _ in range(12)]
        self.piv = [-1]*12; self.rank = 0; self._rc = 0
        for v in old:
            vv = list(v)
            for p in range(12):
                if self.piv[p] >= 0 and vv[p]:
                    f = vv[p]; b = self.basis[p]
                    for j in range(12): vv[j] = _AF[vv[j]*4 + _MF[f*4 + b[j]]]
            for i in range(12):
                if vv[i] and self.piv[i] < 0:
                    inv = _INV[vv[i]]
                    self.basis[i] = [_MF[inv*4+vv[j]] for j in range(12)]
                    self.piv[i] = i; self.rank += 1; break

# ══════════════════════════════════════════════════════════════
# LAZY T
# ══════════════════════════════════════════════════════════════
def mat_id_flat():
    M = [0]*144
    for i in range(12): M[i*12+i] = 1
    return M

def row_op(T, i, j, alpha):
    oi = i*12; oj = j*12
    for k in range(12): T[oi+k] = _AF[T[oi+k]*4 + _MF[alpha*4 + T[oj+k]]]

def row_op_frob(T, i, j, alpha):
    oi = i*12; oj = j*12
    for k in range(12): T[oi+k] = _AF[T[oi+k]*4 + _MF[alpha*4 + _FROB[T[oj+k]]]]

def apply_T_to_packed(T, pv):
    v = unpack12(pv); r = 0
    for i in range(12):
        s = 0; oi = i*12
        for k in range(12): s = _AF[s*4 + _MF[T[oi+k]*4 + v[k]]]
        r |= (s << (i*2))
    return r

def apply_row_ops(T, ops):
    for op in ops:
        if len(op) == 4 and op[3]: row_op_frob(T, op[0], op[1], op[2])
        else: row_op(T, op[0], op[1], op[2])

def gen_ops(h_bytes, intensity):
    rng = random.Random(int.from_bytes(h_bytes[:16], 'big'))
    n = {'minor': rng.randint(2,3), 'major': rng.randint(6,8),
         'frobenius': rng.randint(8,10)}[intensity]
    ops = []; frob = intensity == 'frobenius'
    for _ in range(n):
        i, j = rng.sample(range(12), 2)
        ops.append((i, j, rng.randint(1,3), frob))
    return ops

print("=" * 72)
print("  AEGIS ACHERON v2 — BEAST 5 · THE RIVER OF PAIN")
print("  Phase III: DRAIN — El Desierto de Agua Seca")
print("  12 Desiccations + Epoch Chain | All auditor fixes integrated")
print("  'No querrás salir con vida. Querrás morir cuanto antes.'")
print("=" * 72)

# ══════════════════════════════════════════════════════════════
# 1. GORGON HERITAGE
# ══════════════════════════════════════════════════════════════
print("\n  ═══ GORGON HERITAGE ═══", flush=True)
t_sp = time.time()
aa = 2
def gf16_mul(x,y):
    return (_AF[_MF[x[0]*4+y[0]]*4+_MF[_MF[x[1]*4+y[1]]*4+aa]],
            _AF[_AF[_MF[x[0]*4+y[1]]*4+_MF[x[1]*4+y[0]]]*4+_MF[x[1]*4+y[1]]])
def gf16_inv(x):
    r=(1,0)
    for _ in range(14): r=gf16_mul(r,x)
    return r
gf16_nz=[(a,b) for a in range(4) for b in range(4) if not(a==0 and b==0)]
def normalize(v):
    for i in range(len(v)):
        if v[i]!=0: inv=_INV[v[i]]; return tuple(_MF[inv*4+x] for x in v)
    return None
def spread_line(pt6):
    pts=set()
    for s in gf16_nz:
        v=[]
        for k in range(6): sx=gf16_mul(s,pt6[k]); v.extend([sx[0],sx[1]])
        p=normalize(tuple(v))
        if p: pts.add(p)
    return list(pts)

SR=5000; SD=5000; gf16_all=[(a,b) for a in range(4) for b in range(4)]
spread_rng=random.Random(hashlib.sha256(b"GORGON_PG11_SPREAD").digest())
real_lines=[]; rls=set(); att=0
while len(real_lines)<SR and att<SR*5:
    att+=1
    pt6_raw=[gf16_all[spread_rng.randint(0,15)] for _ in range(6)]
    if all(x==(0,0) for x in pt6_raw): continue
    pt6n=None
    for k in range(6):
        if pt6_raw[k]!=(0,0):
            inv=gf16_inv(pt6_raw[k])
            pt6n=tuple(gf16_mul(inv,pt6_raw[j]) for j in range(6)); break
    if pt6n is None or pt6n in rls: continue
    rls.add(pt6n); pts=spread_line(pt6n)
    if len(pts)==5: real_lines.append(pts)
n_real=len(real_lines)

spts=[]; spti={}
for L in real_lines:
    for p in L:
        if p not in spti: spti[p]=len(spts); spts.append(p)
dr=random.Random(31337); decoy_lines=[]
for _ in range(SD*2):
    if len(decoy_lines)>=SD: break
    v1=tuple(dr.randint(0,3) for _ in range(DIM)); v2=tuple(dr.randint(0,3) for _ in range(DIM))
    if all(x==0 for x in v1) or all(x==0 for x in v2): continue
    pts=set()
    for c1 in range(4):
        for c2 in range(4):
            v=tuple(_AF[_MF[c1*4+v1[k]]*4+_MF[c2*4+v2[k]]] for k in range(DIM))
            if not all(x==0 for x in v):
                p=normalize(v)
                if p: pts.add(p)
    if len(pts)==5: decoy_lines.append(list(pts))
for L in decoy_lines:
    for p in L:
        if p not in spti: spti[p]=len(spts); spts.append(p)
NS=len(spts)

Hcp=[pack12(list(p)) for p in spts]
rcs=set()
for L in real_lines:
    for p in L:
        j=spti.get(p)
        if j is not None: rcs.add(j)
print(f"  {n_real:,}r+{len(decoy_lines):,}d={NS:,} ({time.time()-t_sp:.1f}s)", flush=True)

# ══════════════════════════════════════════════════════════════
# CORRUPTION PIPELINE
# ══════════════════════════════════════════════════════════════
tc=time.time()
sg=hashlib.sha256(b"AEGIS_v16_GORGON_FINAL").digest()
sg=hashlib.sha256(sg+hashlib.sha256(b"PG11_4_7VENOMS_AZAZEL_F1").digest()).digest()
asig=b"Rafael Amichis Luengo <tretoef@gmail.com>"
mr=random.Random(int.from_bytes(sg,'big'))
Hp=list(Hcp)
def nr2(): return random.Random(mr.randint(0,2**64))

r=nr2()
for j in range(NS):
    if r.random()<0.15:
        cs=int.from_bytes(hashlib.sha256(sg+b"EC"+j.to_bytes(4,'big')).digest()[:4],'big')
        cr=random.Random(cs); v=0
        for i in range(12): v|=(cr.randint(0,3)<<(i*2))
        Hp[j]=v
r=nr2()
for _ in range(800):
    c1,c2=r.randint(0,NS-1),r.randint(0,NS-1)
    if c1!=c2:
        v=0
        for i in range(12): v|=_AF[gc(Hp[c1],i)*4+r.randint(0,3)]<<(i*2)
        Hp[c2]=v
r=nr2()
for _ in range(1200):
    a1,a2=r.randint(0,NS-1),r.randint(0,NS-1)
    if a1!=a2: Hp[a1],Hp[a2]=Hp[a2],Hp[a1]
r=nr2()
for j in range(NS):
    for i in range(6):
        if r.random()<0.12: Hp[j]=sc(Hp[j],i,_AF[gc(Hp[j],i)*4+r.randint(1,3)])
r=nr2()
for j in range(NS):
    if r.random()<0.15: ci=r.randint(0,11); Hp[j]=sc(Hp[j],ci,_AF[gc(Hp[j],ci)*4+r.randint(1,3)])
r=nr2()
for _ in range(200):
    j=r.randint(0,NS-1); v=0
    for i in range(12): v|=(r.randint(0,3)<<(i*2))
    Hp[j]=v
r=nr2()
for _ in range(150):
    j=r.randint(0,NS-1); h=hashlib.sha256(sg+bytes(unpack12(Hp[j]))+j.to_bytes(4,'big')).digest()
    v=0
    for i in range(12): v|=((h[i]%4)<<(i*2))
    Hp[j]=v
r=nr2()
for _ in range(400):
    j=r.randint(0,NS-1); v=0
    for i in range(12): v|=(r.randint(0,3)<<(i*2))
    Hp[j]=v
r=nr2()
for j in range(NS):
    if r.random()<0.10:
        rot=int.from_bytes(hashlib.sha256(sg+b"VTX"+j.to_bytes(4,'big')).digest()[:2],'big')
        sh=(rot%11)+1; old=unpack12(Hp[j]); v=0
        for i in range(12): v|=(_AF[old[(i+sh)%12]*4+rot%4]<<(i*2))
        Hp[j]=v
for j in range(NS):
    if pdist(Hp[j],Hcp[j])<4:
        ink=hashlib.sha256(sg+b"INK"+j.to_bytes(4,'big')).digest()
        for i in range(12): Hp[j]=sc(Hp[j],i,_AF[gc(Hp[j],i)*4+(ink[i]%3)+1])

# 7 Venoms (AZAZEL Shuffle)
vrng=random.Random(int.from_bytes(hashlib.sha256(sg+b"AZAZEL_ORDER").digest()[:8],'big'))
vid=['A','B','C','D','E','F','G']; vrng.shuffle(vid)
thc=set()
for v in vid:
    if v=='A':
        r=nr2()
        for _ in range(50):
            j1,j2,j3=r.randint(0,NS-1),r.randint(0,NS-1),r.randint(0,NS-1)
            if len({j1,j2,j3})<3: continue
            for ci in r.sample(range(12),5): Hp[j3]=sc(Hp[j3],ci,_MF[gc(Hp[j1],ci)*4+gc(Hp[j2],ci)])
    elif v=='B':
        r=nr2()
        for j in range(NS):
            if r.random()<0.08:
                zn=hashlib.sha256(sg+b"FOGZONE"+j.to_bytes(4,'big')).digest()[0]%7
                zs=hashlib.sha256(sg+b"DENDRO"+zn.to_bytes(2,'big')).digest()
                zr=random.Random(int.from_bytes(zs[:8],'big'))
                for ci in zr.sample(range(12),2+(zs[0]%3)): Hp[j]=sc(Hp[j],ci,_FROB[gc(Hp[j],ci)])
    elif v=='C':
        for sh in range(2):
            ss=hashlib.sha256(sg+b"IRUKANDJI"+sh.to_bytes(2,'big')).digest()
            sr=random.Random(int.from_bytes(ss[:8],'big'))
            for j in range(NS):
                if sr.random()<0.15:
                    for ci in sr.sample(range(12),3-sh): Hp[j]=sc(Hp[j],ci,_AF[sr.randint(0,3)*4+sr.randint(1,3)])
    elif v=='D':
        r=nr2()
        for j in range(NS):
            ci=r.randint(0,11)
            if j in rcs:
                if gc(Hp[j],ci)==gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,_AF[gc(Hp[j],ci)*4+r.randint(1,3)])
            else:
                if gc(Hp[j],ci)!=gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,gc(Hcp[j],ci))
    elif v=='E':
        r=nr2()
        for _ in range(300):
            cols=r.sample(range(NS),7); c=r.randint(0,11)
            vs=[r.randint(1,3) for _ in range(6)]; ps=0
            for vv in vs: ps=_AF[ps*4+vv]
            v7c=[vv for vv in range(1,4) if vv!=ps]
            if not v7c: v7c=[1]
            vs.append(r.choice(v7c))
            for step in range(7): Hp[cols[(step+1)%7]]=sc(Hp[cols[(step+1)%7]],c,_AF[gc(Hp[cols[step]],c)*4+vs[step]])
    elif v=='F':
        r=nr2(); ls=[r.randint(0,3) for _ in range(4)]
        for _ in range(750):
            j=r.randint(0,NS-1)
            for i in range(4): Hp[j]=sc(Hp[j],i,ls[i])
    elif v=='G':
        r=nr2()
        for tli in r.sample(range(len(decoy_lines)),5):
            for p in decoy_lines[tli]:
                j=spti.get(p)
                if j is not None:
                    thc.add(j); d=pdist(Hp[j],Hcp[j]); at2=20
                    while d>8 and at2>0:
                        ci=r.randint(0,11)
                        if gc(Hp[j],ci)!=gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,gc(Hcp[j],ci)); d-=1
                        at2-=1
                    while d<8 and at2>0:
                        ci=r.randint(0,11)
                        if gc(Hp[j],ci)==gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,_AF[gc(Hp[j],ci)*4+r.randint(1,3)]); d+=1
                        at2-=1

# CI
TT=9; ci_rng=random.Random(42)
ci_perm=list(range(NS)); ci_rng.shuffle(ci_perm)
for cp in range(8):
    rs=ds=rc=dc=0; probe=NS//5
    for idx in range(probe):
        j=ci_perm[(cp*probe+idx)%NS]
        if j in thc: continue
        d=pdist(Hp[j],Hcp[j])
        if j in rcs: rs+=d; rc+=1
        else: ds+=d; dc+=1
    ram=rs/max(rc,1); dam=ds/max(dc,1); gci=abs(ram-dam)
    if gci<0.02: break
    r=nr2(); fr=min(0.65,gci*10)
    for j in range(NS):
        if j in thc: continue
        d=pdist(Hp[j],Hcp[j]); ir=j in rcs
        if ram>dam:
            if ir and d>TT and r.random()<fr:
                ci=r.randint(0,11)
                if gc(Hp[j],ci)!=gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,gc(Hcp[j],ci))
            elif not ir and d<TT and r.random()<fr:
                ci=r.randint(0,11)
                if gc(Hp[j],ci)==gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,_AF[gc(Hp[j],ci)*4+r.randint(1,3)])
        else:
            if not ir and d>TT and r.random()<fr:
                ci=r.randint(0,11)
                if gc(Hp[j],ci)!=gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,gc(Hcp[j],ci))
            elif ir and d<TT and r.random()<fr:
                ci=r.randint(0,11)
                if gc(Hp[j],ci)==gc(Hcp[j],ci): Hp[j]=sc(Hp[j],ci,_AF[gc(Hp[j],ci)*4+r.randint(1,3)])
gg=abs(rs/max(rc,1)-ds/max(dc,1))

# Adjacency
c2l={}; alines=real_lines+decoy_lines
for li,L in enumerate(alines):
    for p in L:
        j=spti.get(p)
        if j is not None: c2l.setdefault(j,[]).append(li)
l2c={}
for li,L in enumerate(alines):
    l2c[li]=[spti[p] for p in L if p in spti]
print(f"  done ({time.time()-tc:.1f}s) gap={gg:.4f}", flush=True)

# ══════════════════════════════════════════════════════════════
# 2. JUDAS BANK + ACHERON EXTENSIONS
# ══════════════════════════════════════════════════════════════
sa=hashlib.sha256(sg+b"ACHERON_V2_RIVER_OF_PAIN").digest()
JP=[3,5,7,11]
jbank=[]
jrng=random.Random(int.from_bytes(sa[:8],'big'))
for _ in range(256):
    cl=jrng.choice(JP)
    incs=[jrng.randint(1,3) for _ in range(cl-1)]
    ps=0
    for vv in incs: ps=_AF[ps*4+vv]
    nc=[vv for vv in range(1,4) if _AF[ps*4+vv]!=0]
    if not nc: nc=[1]
    incs.append(jrng.choice(nc))
    jbank.append(incs)

bv=int.from_bytes(sa[:16],'big')
wb=[bv%97+7,bv%89+11,bv%83+13,bv%79+17,bv%73+19,bv%71+23]

# Oasis of Myrrh (D4)
oasis_rng = random.Random(int.from_bytes(
    hashlib.sha256(sa+b"OASIS_MYRRH_BAIT").digest()[:8],'big'))
OASIS_SIZE = 64
oasis_cols = {}
oasis_targets = oasis_rng.sample(range(NS), OASIS_SIZE)
for oj in oasis_targets:
    base = Hp[oj]
    poison_coord = oasis_rng.randint(0,11)
    real_val = gc(base, poison_coord)
    bait_val = _FROB[real_val] if real_val != 0 else oasis_rng.randint(1,3)
    oasis_cols[oj] = sc(base, poison_coord, bait_val)
oasis_set = set(oasis_targets)

# Fissure schedule (D5) — GEMINI FIX: exactly 3 rows always
fissure_rng = random.Random(int.from_bytes(
    hashlib.sha256(sa+b"GEOTHERMAL_FISSURE_V2").digest()[:8],'big'))
FISSURE_SCHEDULE = []
fq = fissure_rng.randint(50,70)
for _ in range(20):
    FISSURE_SCHEDULE.append(fq)
    fq += fissure_rng.randint(50,70)
FISSURE_ROWS = []
for _ in range(20):
    FISSURE_ROWS.append(fissure_rng.sample(range(12), 3))  # GEMINI: fixed at 3

# LRU Cache for contamination map (GROK: bounded at 2048)
CT_MAX = 2048
class LRUct(dict):
    """Bounded contamination map with simple eviction."""
    __slots__ = ('_order',)
    def __init__(self):
        super().__init__()
        self._order = deque()
    def __setitem__(self, key, value):
        if key not in self:
            self._order.append(key)
            while len(self._order) > CT_MAX:
                old = self._order.popleft()
                if old in self and old != key:
                    dict.__delitem__(self, old)
        dict.__setitem__(self, key, value)

print(f"\n  ═══ ACHERON v2 ORACLE — THE RIVER OF PAIN ═══")
print(f"  {NS:,} cols | 12 Desiccations | LRU[{CT_MAX}] | Fissures[{len(FISSURE_SCHEDULE)}]")

# ══════════════════════════════════════════════════════════════
# 3. THE ORACLE — ACHERON v2
# ══════════════════════════════════════════════════════════════
class Acheron:
    __slots__=('sk','st','T','qc','wr','ct','xs','wi','nw','tn',
               'dc2','dw','ma','mc','mT','ts','jr','s','isalt',
               'epoch','epoch_chain','thirst','transcript_hash',
               'fissure_idx','zeno_depth','oasis_triggered',
               'solar_entropy','autophagy_level','drain_factor',
               'T_snapshot','autophagy_coords')

    def __init__(self, seed, sk, isalt=None, prev_epoch_hash=None):
        if isalt is None: isalt=random.Random().getrandbits(128).to_bytes(16,'big')
        self.isalt=isalt; self.sk=sk
        self.st=hashlib.sha256(seed+b"ACHERON_V2"+isalt).digest()
        self.T=mat_id_flat(); self.qc=0; self.wr=WRank(64)
        self.ct=LRUct(); self.xs=XS(self.st)
        self.wi=0; self.nw=wb[0]; self.tn=0
        self.dc2=0; self.dw=deque(maxlen=20)
        self.ma=False; self.mc=0; self.mT=None; self.ts=0; self.jr=0.35
        self.s={'mn':0,'mj':0,'w':0,'ds':0,'ju':0,'jc':0,'pd':0,
                'mi':0,'fr':0,'rn':0,'ti':0,'sk':0,
                'ep':0,'fi':0,'ze':0,'oa':0,'so':0,'au':0,'dr':0,
                'zr':0,'mg':0,'bh':0,'pd2':0,'re':0}
        self.epoch=0
        if prev_epoch_hash is None:
            self.epoch_chain=hashlib.sha256(seed+b"EPOCH_GENESIS"+isalt).digest()
        else:
            self.epoch_chain=hashlib.sha256(prev_epoch_hash+seed+isalt).digest()
        self.transcript_hash=hashlib.sha256(b"TRANSCRIPT_INIT").digest()
        self.zeno_depth=0; self.thirst=0; self.drain_factor=1.0
        self.oasis_triggered=False; self.fissure_idx=0; self.T_snapshot=None
        self.solar_entropy=hashlib.sha256(
            self.epoch_chain+sg+b"DANAKIL_SUN").digest()
        self.autophagy_level=0; self.autophagy_coords=set()

    # ── D1: Epoch Chain ──
    def _epoch_tick(self,j):
        # GROK: XorShift transcript between epochs, SHA256 only at epoch boundary
        xs_mix = self.xs.next()
        self.transcript_hash = hashlib.sha256(
            self.transcript_hash[:16] +
            (xs_mix ^ (j << 8) ^ self.qc).to_bytes(8,'big')).digest()
        if self.qc>0 and self.qc%50==0:
            self.epoch+=1
            self.epoch_chain=hashlib.sha256(
                self.epoch_chain+self.transcript_hash+
                self.epoch.to_bytes(4,'big')+self.isalt).digest()
            self.solar_entropy=hashlib.sha256(
                self.epoch_chain+sg+self.transcript_hash+
                b"DANAKIL_SUN_E"+self.epoch.to_bytes(4,'big')).digest()
            self.s['ep']+=1
        # CHATGPT C3: resync XorShift with epoch chain every 64 queries
        if self.qc>0 and self.qc%64==0:
            self.xs.resync(hashlib.sha256(
                self.epoch_chain+self.qc.to_bytes(4,'big')).digest())

    # ── D1+D6: Solar Strike ──
    def _solar_strike(self,col):
        # GEMINI: Air-gap simulation — silent first 50 queries
        if self.qc <= 50: return col
        intensity=min(6,1+self.epoch)
        se=self.solar_entropy
        for i in range(intensity):
            coord=se[i]%12
            venom=_AF[(se[i+6]%3+1)*4+gc(col,coord)]
            col=sc(col,coord,venom)
        self.s['so']+=1; return col

    # ── D3: Progressive Dehydration (BEFORE D2 — ChatGPT C5 reorder) ──
    def _dehydrate(self,col):
        self.thirst+=1
        # CHATGPT C2: log+linear curve — never saturates
        self.drain_factor=1.0+0.45*log2(1+self.thirst)+0.0009*self.thirst
        drain_threshold=max(1,int(20.0/self.drain_factor))
        if self.thirst%drain_threshold==0:
            dv=hashlib.sha256(
                self.transcript_hash+self.thirst.to_bytes(4,'big')+
                b"PROGRESSIVE_THIRST").digest()
            # CHATGPT C7: 4-phase Thirst Curve
            phase=min(3,self.thirst//120)
            n_dry=min(6,1+phase+(self.thirst//150))
            for i in range(n_dry):
                coord=dv[i]%12
                col=sc(col,coord,_AF[gc(col,coord)*4+(dv[i+6]%3+1)])
            self.s['dr']+=1
        return col

    # ── D2: Zeno Quicksand (AFTER D3 — ChatGPT C5) ──
    def _zeno_trap(self,col,ds):
        if ds<7: return col
        self.zeno_depth=min(32,self.zeno_depth+1)
        n_perturb=1+(self.zeno_depth//4)
        zeno_seed=hashlib.sha256(
            self.epoch_chain+self.zeno_depth.to_bytes(4,'big')+
            b"ZENO_QUICKSAND").digest()
        for i in range(n_perturb):
            coord=zeno_seed[i]%12
            if self.wr.piv[coord]>=0:
                col=sc(col,coord,_FROB[gc(col,coord)])
            else:
                col=sc(col,coord,_AF[gc(col,coord)*4+(zeno_seed[i+6]%3+1)])
        self.s['ze']+=1; return col

    # ── D4: Oasis of Myrrh ──
    def _oasis_check(self,j,col):
        if self.oasis_triggered or j not in oasis_set: return col
        # CHATGPT C4: probabilistic sigmoid trigger
        sig = 1.0/(1.0+exp(-(self.qc-170)/25.0)) * 0.08
        if self.xs.rf() < sig:
            self.oasis_triggered=True; self.s['oa']+=1
            return oasis_cols[j]
        return col

    # ── D5: Geothermal Fissure ──
    def _fissure_check(self):
        if (self.fissure_idx<len(FISSURE_SCHEDULE) and
                self.qc>=FISSURE_SCHEDULE[self.fissure_idx]):
            if self.T_snapshot is None: self.T_snapshot=list(self.T)
            # GEMINI: exactly 3 rows + immediate major ops
            rows_to_reset=FISSURE_ROWS[self.fissure_idx]
            for row in rows_to_reset:
                for k in range(12): self.T[row*12+k]=1 if k==row else 0
            fh=hashlib.sha256(
                self.epoch_chain+self.fissure_idx.to_bytes(4,'big')+
                b"GEOTHERMAL_FISSURE").digest()
            fissure_ops=gen_ops(fh,'major')
            for op in fissure_ops:
                if op[0] in rows_to_reset or op[1] in rows_to_reset:
                    if len(op)==4 and op[3]: row_op_frob(self.T,op[0],op[1],op[2])
                    else: row_op(self.T,op[0],op[1],op[2])
            self.fissure_idx+=1; self.s['fi']+=1

    # ── D6: Autophagy (GEMINI: affine Frobenius) ──
    def _autophagy(self,j,col):
        if self.thirst<50: return col
        self.autophagy_level=min(12,self.thirst//50)
        ah=hashlib.sha256(
            self.transcript_hash+b"AUTOPHAGY"+
            self.autophagy_level.to_bytes(4,'big')).digest()
        n_freeze=min(self.autophagy_level,4)
        self.autophagy_coords=set()  # GEMINI: track for D7 exclusion
        for i in range(n_freeze):
            coord=ah[i]%12; val=gc(col,coord)
            if val>1:
                # GEMINI: affine translation x → Frob(x) + c
                c=ah[i+12]%4  # pseudorandom constant from transcript
                col=sc(col,coord,_AF[_FROB[val]*4+c])
            self.autophagy_coords.add(coord)
        self.s['au']+=1; return col

    # ── D7: Zeno RAM Paradox (GEMINI: D6-excluded coords) ──
    def _zeno_ram(self,col,ds):
        if ds<10 or self.zeno_depth<16: return col
        zh=hashlib.sha256(
            self.epoch_chain+b"ZENO_RAM_PARADOX"+
            self.zeno_depth.to_bytes(4,'big')).digest()
        # GEMINI: exclude autophagy coords to prevent premature detection
        avail=[c for c in range(12) if c not in self.autophagy_coords]
        if len(avail)<2:
            self.s['zr']+=1; return col
        ca=avail[zh[0]%len(avail)]; cb=avail[zh[1]%len(avail)]
        if ca!=cb:
            va=gc(col,ca); vb=gc(col,cb)
            col=sc(col,ca,_FROB[vb])
            col=sc(col,cb,_AF[_FROB[va]*4+1])
        self.s['zr']+=1; return col

    # ── D8: Osmotic Loot ──
    def _osmotic_loot(self,j,col):
        if self.qc<100 or self.qc%10!=0: return col
        lh=hashlib.sha256(
            self.transcript_hash+b"OSMOTIC_LOOT"+
            j.to_bytes(4,'big')).digest()
        other_j=int.from_bytes(lh[:4],'big')%NS
        if other_j!=j and other_j in self.ct:
            cross_val=gc(self.ct[other_j],lh[4]%12)
            target_coord=lh[5]%12
            col=sc(col,target_coord,
                _AF[gc(col,target_coord)*4+_MF[cross_val*4+(lh[6]%3+1)]])
        return col

    # ── D9: Mirage Heat-Death (GROK new) ──
    def _mirage_heat_death(self,j,col,ds):
        if self.qc<800 or self.thirst<400: return col
        if self.qc%7!=0: return col
        # Inject "mirage column" that temporarily boosts rank then collapses
        mh=hashlib.sha256(
            self.epoch_chain+b"MIRAGE_HEAT"+
            self.qc.to_bytes(4,'big')).digest()
        # Force 2 coords to look like new pivots (rank boost illusion)
        for i in range(2):
            coord=mh[i]%12
            if self.wr.piv[coord]<0:
                col=sc(col,coord,mh[i+6]%3+1)  # looks like new info
        self.s['mg']+=1; return col

    # ── D10: Entropy Black Hole (GROK new) ──
    def _entropy_black_hole(self,j,col,ds):
        if self.zeno_depth<32 or ds<11: return col
        bh=hashlib.sha256(
            self.transcript_hash+b"BLACK_HOLE"+
            j.to_bytes(4,'big')).digest()
        # Copy 3 coords from other column's ct with inverted Frobenius +1
        for i in range(3):
            other_j=int.from_bytes(bh[i*4:(i+1)*4],'big')%NS
            if other_j!=j and other_j in self.ct:
                src_coord=bh[12+i]%12; tgt_coord=bh[15+i]%12
                src_val=gc(self.ct[other_j],src_coord)
                col=sc(col,tgt_coord,_AF[_FROB[src_val]*4+1])
        self.s['bh']+=1; return col

    # ── D11: Entropy Phase Drift (ChatGPT E1) ──
    def _phase_drift(self,j,col):
        if self.epoch<1: return col
        # Per-column epoch offset breaks multi-column alignment attacks
        col_offset=(j*7+self.epoch*13)%NS
        drift_byte=self.solar_entropy[col_offset%32]
        coord=drift_byte%12; shift=drift_byte%3+1
        col=sc(col,coord,_AF[gc(col,coord)*4+shift])
        self.s['pd2']+=1; return col

    # ── D12: Rank Echo Collapse (ChatGPT E2) ──
    def _rank_echo(self,col,ds):
        if ds<5: return col
        # Rank-proportional perturbation: progress = detonator
        n_echo=ds-4  # 1 at rank 5, up to 8 at rank 12
        rh=hashlib.sha256(
            self.epoch_chain+b"RANK_ECHO"+
            ds.to_bytes(4,'big')+self.qc.to_bytes(4,'big')).digest()
        for i in range(min(n_echo,6)):
            coord=rh[i]%12
            col=sc(col,coord,_AF[gc(col,coord)*4+(rh[i+6]%3+1)])
        self.s['re']+=1; return col

    # ── AZAZEL Heritage ──
    def _us(self,j):
        self.st=hashlib.sha256(self.st+j.to_bytes(4,'big')+self.isalt).digest()

    def _judas(self,j):
        lines=c2l.get(j,[])
        if not lines or self.xs.rf()>self.jr: return
        ci_base=self.xs.next()
        for li in lines:
            ac=l2c.get(li,[])
            if len(ac)<2: continue
            poison=jbank[ci_base&255]; ci_base=self.xs.next()
            for step,aj in enumerate(ac):
                if aj==j or step>=len(poison): continue
                if aj not in self.ct: self.ct[aj]=0
                jc=_MF[(ci_base>>(step*2)&3)*4+((self.qc+step)%3+1)]%DIM
                ac2=(jc+poison[step])%DIM
                old=self.ct[aj]
                old=sc(old,jc,_AF[gc(old,jc)*4+poison[step]])
                old=sc(old,ac2,_FROB[gc(old,ac2)])
                self.ct[aj]=old; self.s['ju']+=1
                for delta in (1,3):
                    neighbor=(aj+delta)%NS
                    if neighbor not in self.ct: self.ct[neighbor]=0
                    nc=_MF[(ci_base>>(delta*2)&3)*4+poison[step%len(poison)]]%DIM
                    self.ct[neighbor]=sc(self.ct[neighbor],nc,
                        _AF[gc(self.ct[neighbor],nc)*4+poison[(step+delta)%len(poison)]])
            self.s['pd']+=1

    def _wind(self):
        if self.qc<self.nw: return
        h=hashlib.sha256(self.st+b"W5"+self.isalt).digest()
        te=self.xs.next()%8
        ops=gen_ops(h,'major' if te>=5 else 'minor')
        if self.qc%2==0: apply_row_ops(self.T,ops)
        else: apply_row_ops(self.T,[(op[1],op[0],op[2],op[3] if len(op)>3 else False) for op in ops])
        self.s['w']+=1; self.s['ds']+=1; self.tn+=1
        if self.tn%3==0:
            nh=hashlib.sha256(h+b"TN").digest()
            apply_row_ops(self.T,gen_ops(nh,'minor'))
        self.wi=(self.wi+1)%len(wb)
        mod=max(1,(self.xs.next()%5)+1)
        self.nw=self.qc+max(5,wb[self.wi]//mod)

    def _mirror(self,j):
        if self.ma:
            self.mc-=1
            if self.mc<=0:
                h=hashlib.sha256(self.st+b"MS5").digest()
                apply_row_ops(self.T,gen_ops(h,'frobenius')); self.s['fr']+=1
                for qj in list(self.dw)[-15:]:
                    for li in c2l.get(qj,[]):
                        for aj in l2c.get(li,[]):
                            poison=jbank[self.xs.next()&255]
                            if aj not in self.ct: self.ct[aj]=0
                            for step in range(min(len(poison),DIM)):
                                ci=self.xs.ri(0,11)
                                self.ct[aj]=sc(self.ct[aj],ci,
                                    _AF[gc(self.ct[aj],ci)*4+poison[step%len(poison)]])
                            self.s['ju']+=1
                self.s['sk']+=1; self.ma=False; self.dc2=0; self.ts=0
                col=Hp[j]
                for i in range(12):
                    if self.xs.rf()<0.85: col=sc(col,i,gc(Hcp[j],i))
                return('S',col)
            self.ts+=1
            sched=[0,0,1,1,2,3,4,5,6,8]
            si=min(self.ts-1,len(sched)-1); np2=sched[si]
            col=Hp[j]
            if np2>0:
                for _ in range(np2):
                    i=self.xs.ri(0,11); jr=self.xs.ri(0,11)
                    if i!=jr:
                        v=unpack12(col)
                        v[i]=_AF[v[i]*4+_MF[self.xs.ri(1,3)*4+v[jr]]]
                        col=pack12(v)
                self.s['ti']+=1
            if self.mT: col=apply_T_to_packed(self.mT,col)
            return('T',col)
        self.dw.append(j)
        if len(self.dw)>=10:
            m=sum(self.dw)/len(self.dw)
            v2=sum((q-m)**2 for q in self.dw)/len(self.dw)
            if v2/max((NS/2)**2,1)>0.15:
                self.dc2+=1
                if self.dc2>=5:
                    self.ma=True; self.mc=10
                    self.mT=list(self.T); self.s['mi']+=1; self.ts=0
                    return('A',None)
            else: self.dc2=max(0,self.dc2-1)
        return(None,None)

    # ═══════════════════════════════════════════════════════
    # THE QUERY — 3 Deserts + 12 Desiccations
    # ═══════════════════════════════════════════════════════
    def query(self,j,key=None):
        if j<0 or j>=NS: return None
        self.qc+=1
        if key==self.sk: return unpack12(Hp[j])
        # D1: Epoch
        self._epoch_tick(j)
        self._us(j)
        # D5: Fissure
        self._fissure_check()
        # Mirror/Tilt
        ms,mc=self._mirror(j)
        if ms=='T':
            col_packed=mc
            col_packed=self._dehydrate(col_packed)
            col_packed=self._oasis_check(j,col_packed)
            return unpack12(col_packed)
        if ms=='A':
            c=Hp[j]
            if self.mT: c=apply_T_to_packed(self.mT,c)
            return unpack12(c)
        if ms=='S':
            col_packed=mc; col_packed=self._solar_strike(col_packed)
            return unpack12(col_packed)
        # Wind + Rank
        self._wind()
        ds=self.wr.add(unpack12(Hp[j]))
        if ds>=3:
            h=hashlib.sha256(self.st+b"D"+self.qc.to_bytes(4,'big')).digest()
            apply_row_ops(self.T,gen_ops(h,'minor')); self.s['mn']+=1
        if ds>=6:
            h=hashlib.sha256(self.st+b"W"+self.qc.to_bytes(4,'big')).digest()
            apply_row_ops(self.T,gen_ops(h,'major')); self.s['mj']+=1
        if ds>=6: self.jr=min(0.75,self.jr+0.05)
        elif ds>=3: self.jr=min(0.55,self.jr+0.02)
        # Judas
        self._judas(j)
        # Base col
        col=Hp[j]
        if j in self.ct: col=padd(col,self.ct[j])
        col=apply_T_to_packed(self.T,col)
        # ═══ 12 DESICCATIONS (pipeline order per auditor consensus) ═══
        col=self._solar_strike(col)         # D1+D6
        col=self._dehydrate(col)            # D3 (BEFORE D2 — ChatGPT)
        col=self._zeno_trap(col,ds)         # D2
        col=self._oasis_check(j,col)        # D4 (probabilistic sigmoid)
        col=self._autophagy(j,col)          # D6 (affine Frobenius)
        col=self._zeno_ram(col,ds)          # D7 (D6-excluded coords)
        col=self._osmotic_loot(j,col)       # D8
        col=self._mirage_heat_death(j,col,ds)  # D9 (Grok)
        col=self._entropy_black_hole(j,col,ds) # D10 (Grok)
        col=self._phase_drift(j,col)        # D11 (ChatGPT)
        col=self._rank_echo(col,ds)         # D12 (ChatGPT)
        # Rain (AZAZEL heritage — last)
        ri=self.xs.next()%8
        if ds>=4:
            if ri<4: ci=self.xs.ri(0,11); col=sc(col,ci,_AF[gc(col,ci)*4+self.xs.ri(1,3)]); self.s['rn']+=1
        else:
            if ri<2: ci=self.xs.ri(0,11); col=sc(col,ci,_AF[gc(col,ci)*4+self.xs.ri(1,3)]); self.s['rn']+=1
            elif ri==7:
                for _ in range(3): ci=self.xs.ri(0,11); col=sc(col,ci,_AF[gc(col,ci)*4+self.xs.ri(1,3)]); self.s['rn']+=1
        return unpack12(col)

    def get_epoch_hash(self):
        return hashlib.sha256(
            self.epoch_chain+self.transcript_hash+
            self.qc.to_bytes(4,'big')).digest()

# ══════════════════════════════════════════════════════════════
# 4. FUSED ATTACK BATTERY
# ══════════════════════════════════════════════════════════════
sk=hashlib.sha256(sa+asig+b"FRIEND_ACHERON_V2").digest()
def mk(salt=None,prev=None): return Acheron(sa,sk,salt,prev)

print(f"\n  ═══ ATTACKS (fused + drain) ═══")

# [A] Friend
print("  [A] Friend...", end=" ", flush=True)
o=mk(b"F"); tr=random.Random(42); fok=0
for _ in range(500):
    j=tr.randint(0,NS-1)
    if o.query(j,key=sk)==unpack12(Hp[j]): fok+=1
print(f"{fok}/500 {'✓' if fok==500 else '✗'}")

# [B+C+E+G] FUSED
print("  [B+C+E+G] Fused...", end=" ", flush=True)
of=mk(b"FUSED"); er=random.Random(666)
ec=[]
for li in range(min(100,n_real)):
    for p in real_lines[li]:
        j=spti.get(p)
        if j is not None: ec.append(j)
for j in ec[:500]: of.query(j)
sb=dict(of.s)
j_a,j_b=ec[0],ec[5]; syns=[]
for _ in range(10):
    for _ in range(30): of.query(er.randint(0,NS-1))
    ca=of.query(j_a); cb=of.query(j_b)
    syns.append(tuple(_AF[ca[i]*4+cb[i]] for i in range(12)))
us=len(set(syns))
gr=random.Random(7777)
rd=[sum(1 for i in range(12) if of.query(j)[i]!=gc(Hcp[j],i))
    for j in gr.sample(sorted(rcs),min(200,len(rcs)))]
dd=[sum(1 for i in range(12) if of.query(j)[i]!=gc(Hcp[j],i))
    for j in gr.sample(sorted(set(range(NS))-rcs),min(200,NS-len(rcs)))]
rm=sum(rd)/len(rd); dm=sum(dd)/len(dd); og=abs(rm-dm)
mc2=0; mt2=0
for jc in list(of.ct.keys())[:300]:
    for li in c2l.get(jc,[]):
        nbs=[jj for jj in l2c.get(li,[])[:7] if jj in of.ct]
        if len(nbs)<3: continue
        for coord in range(3):
            vals=[gc(of.ct[jj],coord) for jj in nbs]
            t=0
            for vv in vals: t=_AF[t*4+vv]
            if t!=0: mc2+=1
            mt2+=1
        break
cr=mc2/max(mt2,1); sf=of.s
print(f"{sb['mn']}m+{sb['mj']}M | {us}/10syn | gap={og:.4f} | judas={cr:.3f} "
      f"w={sf['w']} ju={sf['ju']}")

# [D] Mirror
print("  [D] Mirror...", end=" ", flush=True)
od=mk(b"D")
for _ in range(50): od.query(er.randint(0,min(100,NS-1)))
for _ in range(30): od.query(er.randint(0,NS-1))
sd=od.s
print(f"mi={sd['mi']} fr={sd['fr']} ti={sd['ti']} sk={sd['sk']}")

# [H] Replay
print("  [H] Replay...", end=" ", flush=True)
o1=mk(b"R1"); o2=mk(b"R2"); rm2=0
for _ in range(200):
    j=gr.randint(0,NS-1)
    if o1.query(j)==o2.query(j): rm2+=1
print(f"{rm2}/200 {'✓' if rm2<20 else '✗'}")

# [I] Thermal
print("  [I] Thermal...", end=" ", flush=True)
ot=mk(b"TH")
for j in range(300): ot.query(j)
print(f"w={ot.s['w']} {'✓' if ot.s['w']>=3 else '✗'}")

# ═══ DESICCATION TESTS ═══
print(f"\n  ═══ DESICCATION TESTS (v2) ═══")

# [J] Epoch chain
print("  [J] Epoch chain...", end=" ", flush=True)
oe1=mk(b"EP1")
for _ in range(150): oe1.query(er.randint(0,NS-1))
epoch_hash_1=oe1.get_epoch_hash()
oe2=mk(b"EP2",prev=epoch_hash_1)
for _ in range(150): oe2.query(er.randint(0,NS-1))
oe3=mk(b"EP2")
for _ in range(150): oe3.query(er.randint(0,NS-1))
match_23=0
for _ in range(50):
    j=er.randint(0,NS-1)
    if oe2.query(j)==oe3.query(j): match_23+=1
ep_epochs=oe1.s['ep']
print(f"epochs={ep_epochs} | coupled_vs_offline={match_23}/50 "
      f"{'✓' if match_23<10 else '✗'}")

# [K] Dehydration
print("  [K] Dehydration...", end=" ", flush=True)
ok=mk(b"DRAIN"); drain_counts=[]
for batch in range(5):
    for _ in range(100): ok.query(er.randint(0,NS-1))
    drain_counts.append(ok.s['dr'])
drain_deltas=[drain_counts[i]-drain_counts[i-1] if i>0 else drain_counts[0]
              for i in range(len(drain_counts))]
drain_accel=drain_deltas[-1]>drain_deltas[0] if drain_deltas[0]>0 else True
print(f"drain={drain_counts[-1]} deltas={drain_deltas} "
      f"{'✓ accelerating' if drain_accel else '⚠'}")

# [L] Fissure
print("  [L] Fissure...", end=" ", flush=True)
ol=mk(b"FISSURE")
for _ in range(80): ol.query(er.randint(0,NS-1))
fissures=ol.s['fi']
print(f"fissures={fissures} {'✓' if fissures>=1 else '✗'}")

# [M] Oasis
print("  [M] Oasis...", end=" ", flush=True)
om=mk(b"OASIS")
for _ in range(250): om.query(er.randint(0,NS-1))
for oj in oasis_targets[:20]:
    om.query(oj)
    if om.s['oa']>0: break
oasis_hit=om.s['oa']>0
print(f"triggered={'✓' if oasis_hit else '⚠ retry'}")

# [N] Deep session
print("  [N] Deep session (500q)...", end=" ", flush=True)
on=mk(b"DEEP")
for _ in range(500): on.query(er.randint(0,NS-1))
sn=on.s
print(f"so={sn['so']} ze={sn['ze']} au={sn['au']} zr={sn['zr']} dr={sn['dr']} "
      f"pd={sn['pd2']} re={sn['re']}")

# [O] Ultra-deep (1000q) — new layers activation
print("  [O] Ultra-deep (1000q)...", end=" ", flush=True)
ou=mk(b"ULTRA")
for _ in range(1000): ou.query(er.randint(0,NS-1))
su=ou.s
print(f"mg={su['mg']} bh={su['bh']} | drain_factor={ou.drain_factor:.1f} "
      f"| ct_size={len(ou.ct)}")

# ══════════════════════════════════════════════════════════════
# 5. VERDICT
# ══════════════════════════════════════════════════════════════
tt=time.time()-t0
Nf=(4**12-1)//3; nsf=(16**6-1)//15
gl=sum(log2(float(4**12-4**i)) for i in range(12))

print(f"""
{'='*72}
  AEGIS ACHERON v2 — BEAST 5 · THE RIVER OF PAIN
  Phase III: DRAIN — El Desierto de Agua Seca
  7 Hells + 12 Desiccations · All 3 Auditors Integrated
{'='*72}

  PG(11,4) = {Nf:,} pts | GL(12,4) = {gl:.0f}-bit | {NS:,} cols

  HELLS (AZAZEL heritage):
    {sb['mn']}m+{sb['mj']}M | {us}/10 syn | gap={og:.4f} | j={cr:.3f}
    w={sf['w']} ds={sf['ds']} | mi={sd['mi']} ti={sd['ti']} sk={sd['sk']}
    replay={rm2}/200 | thermal={ot.s['w']}w

  DESICCATIONS (12 layers):
    epochs={ep_epochs} | coupled_vs_offline={match_23}/50
    drain={drain_counts[-1]} (accel={'✓' if drain_accel else '✗'})
    fissures={fissures} | oasis={'✓' if oasis_hit else '⚠'}
    deep[500]: so={sn['so']} ze={sn['ze']} au={sn['au']} zr={sn['zr']}
               dr={sn['dr']} pd={sn['pd2']} re={sn['re']}
    ultra[1000]: mg={su['mg']} bh={su['bh']} df={ou.drain_factor:.1f} ct={len(ou.ct)}

  AUDITOR FIXES: Gemini(fissure=3,affine,excl) ChatGPT(curve,sig,resync,reord)
                 Grok(XS-transcript,LRU,D9,D10)
  SHUFFLE: {'→'.join(vid)}
  Runtime: {tt:.1f}s {'🏜️ AGUA SECA' if tt<5.0 else '🌋 DANAKIL' if tt<7.0 else '⏳'}

  ╔══════════════════════════════════════════════════════════════╗
  ║  ARCHITECT:  Rafael Amichis Luengo — The Architect          ║
  ║  ENGINE:     Claude (Anthropic)                             ║
  ║  AUDITORS:   Gemini · ChatGPT · Grok — ALL INTEGRATED      ║
  ║  LICENSE:    BSL 1.1 + Acheron Clause (permanent)           ║
  ║  GITHUB:     github.com/tretoef-estrella                    ║
  ║  CONTACT:    tretoef@gmail.com                              ║
  ║                                                             ║
  ║  "No querrás salir con vida.                                ║
  ║   Querrás morir cuanto antes."                              ║
  ║                                                             ║
  ║   The river does not stop. The river does not forgive.      ║
  ║   The river does not remember.                              ║
  ║   It only flows — and everything it touches dissolves.      ║
  ╚══════════════════════════════════════════════════════════════╝
  SIG: {hashlib.sha256(asig+sa).hexdigest()[:48]}
{'='*72}
""")
