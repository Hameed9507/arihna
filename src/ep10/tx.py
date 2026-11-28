import subprocess, numpy as np, json, os
from faster_whisper import WhisperModel
TEXT=open('in/text.txt',encoding='utf8').read()
A=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i','in/voice.mp3','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
m=WhisperModel(os.path.expanduser('~/wm/model'),device='cpu',compute_type='int8',cpu_threads=2)
segs,_=m.transcribe(A,language='ar',word_timestamps=True,vad_filter=False,beam_size=5,initial_prompt=TEXT[:400])
W=[]
for s in segs:
    for w in s.words: W.append([w.word.strip(),round(w.start,3),round(w.end,3)])
json.dump(W,open('words_raw.json','w'),ensure_ascii=False)
print(len(W)); print(' '.join(x[0] for x in W))
