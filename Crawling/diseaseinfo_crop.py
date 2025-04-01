import asyncio
import nest_asyncio
import os
import re
from pyppeteer import launch

nest_asyncio.apply()

BASE_URL = "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoMain.do"
SAVE_DIR = "Database/diseaseinfo"

# PDF 저장 함수 (영역 크롭 추가)
async def save_pdf_from_page(page, path):
    # 페이지에서 크롭할 영역 지정 (좌측 200px, 상단 150px 제거, 나머지 영역 크기 지정)
    clip_area = {
    'x': 500,            # 왼쪽 목차 제거
    'y': 360,            # 위쪽 헤더 제거
    'width': 1670,       # 1920px (기존) - 250px
    'height': 1320       # 1500px (기존) - 180px
    }

    await page.pdf({
        'path': path,
        'width': f'{clip_area["width"]}px',
        'height': f'{clip_area["height"]}px',
        'printBackground': True,
        'pageRanges': '1',  # 첫 페이지만 저장 (선택적)
        'clip': clip_area
    })

# 크롤링 함수
async def crawl():
    browser = await launch(headless=False, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(BASE_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(10)

    # 신체계통 목록
    system_selector = 'div.body-box > a'
    system_elems = await page.querySelectorAll(system_selector)
    system_names = []

    for elem in system_elems:
        name = await page.evaluate('(el) => el.getAttribute("alt") || ""', elem)
        system_names.append(name.strip())

    print("\n🧠 전체 신체계통 목록:")
    for idx, name in enumerate(system_names):
        print(f"  {idx + 1}. {name}")

    choice = input("\n원하는 계통 번호를 입력하세요 (전체는 all): ").strip().lower()

    if choice == 'all':
        selected_indices = list(range(len(system_names)))
    elif choice.isdigit() and 1 <= int(choice) <= len(system_names):
        selected_indices = [int(choice) - 1]
    else:
        print("❌ 잘못된 입력입니다.")
        await browser.close()
        return

    for i in selected_indices:
        system_name = system_names[i]
        print(f"\n🧠 신체계통: {system_name}")

        # 사용자 확인
        cont1 = input(f"    🧠 신체계통: {system_name}\n    👉 이 계통을 저장하시겠습니까? (y/n): ").strip().lower()
        if cont1 != 'y':
            print("    ⏭️ 저장 생략")
            # i += a1
            continue
        else:
            j = 0
            while True:
                # 🔁 메인 페이지로 이동 후 계통 클릭
                await page.goto(BASE_URL, {'waitUntil': 'networkidle2'})
                await asyncio.sleep(1)

                system_elems = await page.querySelectorAll(system_selector)

                # ⏬ 먼저 화면에 보이게 스크롤
                await page.evaluate('(el) => el.scrollIntoView()', system_elems[i])
                await asyncio.sleep(0.5)

                await system_elems[i].click()
                await asyncio.sleep(1)

                # 질병 리스트 로딩
                try:
                    await page.waitForSelector("div.hd-indexbox > ul > li", {'timeout': 10000})
                    disease_items = await page.querySelectorAll("div.hd-indexbox > ul > li")
                except:
                    print(f"⚠️ {system_name}의 질병 목록 로딩 실패")
                    break

                if j >= len(disease_items):
                    print("⚠️ 질병 인덱스를 초과했습니다. 해당 계통 종료.")
                    break

                try:
                    disease_items = await page.querySelectorAll("div.hd-indexbox > ul > li")
                    disease_elem = disease_items[j]
                    a_tag = await disease_elem.querySelector("a")
                    

                    # ⏬ 스크롤해서 보이도록
                    await page.evaluate('(el) => el.scrollIntoView()', a_tag)
                    await asyncio.sleep(0.5)

                    disease_name = await page.evaluate('(el) => el.textContent.trim()', a_tag)

                    # 파일명 안전화
                    safe_name = re.sub(r'[\\/*?:"<>|]', "_", disease_name)
                    filename = f"{system_name}_{safe_name}.pdf"
                    save_path = os.path.join(SAVE_DIR, filename)

                    print(f"    🦠 질병 {j+1}: {disease_name}")

                    try:
                        # await a_tag.click()
                        # ⛔ a_tag.click() 대신 JavaScript 함수 직접 실행
                        onclick_js = await page.evaluate('(el) => el.getAttribute("href")', a_tag)
                        if "fn_goView" in onclick_js:
                            await page.evaluate(onclick_js)
                    except Exception:
                        print("    ⚠️ 상세페이지 입장 실패: 클릭 자체가 안 됨. 스킵합니다.")
                        j += 1
                        continue

                    await asyncio.sleep(10)

                    # # 제목 일치 여부 확인
                    # current_title = await page.evaluate('() => document.querySelector("h2")?.innerText || ""')
                    # if disease_name not in current_title:
                    #     print(f"    ⚠️ 제목 불일치: '{current_title}' ≠ '{disease_name}' → 저장 생략")
                    #     j += 1
                    #     continue

                    print("    ⏳ 상세 페이지 진입 완료. PDF 저장 중...")
                    os.makedirs(SAVE_DIR, exist_ok=True)
                    await save_pdf_from_page(page, save_path)
                    print(f"    ✅ 저장 완료: {save_path}")

                    j += 1

                except Exception as e:
                    print(f"    ❌ 질병 {j+1} 처리 실패: {e}")
                    j += 1
                    continue

    await browser.close()

# 실행
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(crawl())
    except KeyboardInterrupt:
        print("\n🛑 사용자가 작업을 중단했습니다.")