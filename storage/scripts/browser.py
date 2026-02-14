import playwright
with playwright.async_launch() as p:
    browser = await p.chromium()
    page = await browser.new_page()
    await page.goto('https://news.ycombinator.com')
    await page.screenshot()
    await browser.close()