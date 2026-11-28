import numpy as np,json,subprocess
from scipy.signal import butter,sosfilt
sr=48000;OFF=1.0
T=json.load(open('timing.json'));ST=[x+OFF for x in T['st']]
info=json.loads(open('info.json').read())
TOT=info['TOTAL'];N=int(TOT*sr)+sr
out=np.zeros(N,np.float32);rng=np.random.default_rng(3)
def put(x,t,g):
    i=int(t*sr);n=min(len(x),N-i);out[i:i+n]+=x[:n]*g
def whoosh(d=0.6):
    n=int(d*sr);x=rng.standard_normal(n).astype(np.float32);y=np.zeros(n,np.float32);blk=512
    for k in range(0,n,blk):
        f=250*(5000/250)**(k/n);sos=butter(2,[max(f*0.6,60),min(f*1.6,20000)],btype='band',fs=sr,output='sos');y[k:k+blk]=sosfilt(sos,x[k:k+blk])
    env=np.sin(np.linspace(0,np.pi,n))**1.5;return y*env/ (np.abs(y).max()+1e-9)
def tap(f=520):
    n=int(0.12*sr);t=np.arange(n)/sr;x=rng.standard_normal(n)*np.exp(-t*60);sos=butter(2,[f*0.7,f*1.4],btype='band',fs=sr,output='sos');y=sosfilt(sos,x);return (y/np.abs(y).max()).astype(np.float32)
def thump():
    n=int(0.5*sr);t=np.arange(n)/sr;b=lambda t0:np.where(t>t0,np.sin(2*np.pi*55*(t-t0))*np.exp(-(t-t0)*18),0)
    y=b(0)+0.7*b(0.22);sos=butter(2,180,fs=sr,output='sos');y=sosfilt(sos,y);return (y/np.abs(y).max()).astype(np.float32)
W=whoosh()
for s in info['STEPSTART'][1:]: put(W,s-0.45,0.10)
put(W,info['QUESTION']-0.3,0.08);put(W,info['CLOSE0']-0.45,0.09);put(W,info['CARD0']-0.3,0.10);put(W,OFF-0.2,0.08)
for i,ti in enumerate([147,150,150,151,151,152,152]): put(tap(480+40*i),ST[ti]+(i%2)*0.15,0.12)
put(thump(),ST[41],0.22);put(thump(),ST[289],0.18)
for k in range(20): put(tap(900),ST[18]+k*0.06,0.035)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(sr),'-ac','1','-i','-','-c:a','pcm_s16le','sfx.wav'],input=out.tobytes())
