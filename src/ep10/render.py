import sys,asyncio,base64,subprocess
from playwright.async_api import async_playwright
a,b,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(args=['--allow-file-access-from-files'])
        pg=await br.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file:///home/claude/ep10/scene.html')
        await pg.evaluate("Promise.all([document.fonts.load('900 60px Taj'),document.fonts.load('700 60px Taj'),document.fonts.load('900 60px Kufi'),document.fonts.load('700 60px Amiri')])")
        ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for f in range(a,b):
            d=await pg.evaluate(f"(render({f/30}),document.getElementById('c').toDataURL('image/jpeg',0.93))")
            ff.stdin.write(base64.b64decode(d.split(',')[1]))
            if f%300==0: print(out,f,flush=True)
        ff.stdin.close();ff.wait();await br.close()
asyncio.run(main())
