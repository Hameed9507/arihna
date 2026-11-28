import json,re,subprocess,numpy as np
W=json.load(open('words_raw.json'))
strip=lambda s:re.sub(r'[،,.؟:]','',s)
lines=[l.split() for l in open('in/text.txt',encoding='utf8').read().strip().split('\n')]
D=[];LINE=[]
for li,l in enumerate(lines):
    toks=[strip(t) for t in l if strip(t)]
    i=0
    while i<len(toks):
        if toks[i]=='اغفر' and i+1<len(toks) and toks[i+1]=='لي': D.append('اغفر لي');i+=2
        elif toks[i]=='فصل' and toks[i+1]=='لها': D.append('فصلِّها');i+=2
        else: D.append(toks[i]);i+=1
        LINE.append(li)
print(len(D),len(W))
assert len(D)==len(W)
json.dump({'D':D,'LINE':LINE},open('tokens.json','w'),ensure_ascii=False)
# line end times
ends=[max(W[i][2] for i in range(len(W)) if LINE[i]==li) for li in range(len(lines))]
starts=[min(W[i][1] for i in range(len(W)) if LINE[i]==li) for li in range(len(lines))]
print([round(e,2) for e in ends])
# silences
out=subprocess.run(['ffmpeg','-i','in/voice.mp3','-af','silencedetect=noise=-35dB:d=0.18','-f','null','-'],capture_output=True,text=True).stderr
S=[];cur=None
for l in out.split('\n'):
    m=re.search(r'silence_start: ([\d.]+)',l)
    if m: cur=float(m.group(1))
    m=re.search(r'silence_end: ([\d.]+)',l)
    if m and cur is not None: S.append((cur,float(m.group(1))));cur=None
json.dump(S,open('sil.json','w'))
# insert points: for lines 0..14 (after intro + each step), the silence that contains/follows the line end
ins=[]
for li in range(len(lines)-1):
    nxt=starts[li+1]
    cand=[s for s in S if s[1]>ends[li]-0.3 and s[0]<nxt+0.3]
    s=max(cand,key=lambda s:s[1]-s[0])
    dur=0.6 if li==0 else 1.0
    ins.append(((s[0]+s[1])/2,dur,s))
print([(round(a,2),d,round(s[1]-s[0],2)) for a,d,s in ins])
sr=44100
A=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','in/voice.mp3','-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
parts=[];prev=0;fade=int(0.015*sr)
for t,d,_ in ins:
    k=int(t*sr); seg=A[prev:k].copy()
    seg[-fade:]*=np.linspace(1,0,fade)
    if prev>0: seg[:fade]*=np.linspace(0,1,fade)
    parts+= [seg,np.zeros(int(d*sr),np.float32)]; prev=k
seg=A[prev:].copy(); seg[:fade]*=np.linspace(0,1,fade); parts.append(seg)
B=np.concatenate(parts)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(sr),'-ac','1','-i','-','-c:a','pcm_s16le','voice_edu.wav'],input=B.tobytes())
print('new dur',len(B)/sr)
json.dump(ins,open('ins.json','w'))
