import sys,asyncio,json,base64
from playwright.async_api import async_playwright
async def main(times,prefix):
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--allow-file-access-from-files'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file:///home/claude/ep10/scene.html')
        await pg.evaluate('document.fonts.ready')
        await pg.evaluate("Promise.all([document.fonts.load('900 60px Taj'),document.fonts.load('700 60px Taj'),document.fonts.load('900 60px Kufi'),document.fonts.load('700 60px Amiri')])")
        info=await pg.evaluate('window.INFO');print(json.dumps(info))
        for t in times:
            await pg.evaluate(f'render({t})')
            d=await pg.evaluate("document.getElementById('c').toDataURL('image/jpeg',0.9)")
            open(f'{prefix}_{t:07.2f}.jpg','wb').write(base64.b64decode(d.split(',')[1]))
        await b.close()
asyncio.run(main([float(x) for x in sys.argv[2:]],sys.argv[1]))
