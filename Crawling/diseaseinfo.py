import asyncio
import nest_asyncio
import os
import re
from pyppeteer import launch

nest_asyncio.apply()

BASE_URL = "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoMain.do"
SAVE_DIR = "Database/diseaseinfo"

# PDF 저장 함수
async def save_pdf_from_page(page, path):
    await page.pdf({
        'path': path,
        'width': '1920px',
        'height': '1500px',
        'printBackground': True
    })

# 크롤링 함수
async def crawl():
    browser = await launch(headless=False, args=['--no-sandbox']) # 화면 보이기 조절
    page = await browser.newPage()
    await page.goto(BASE_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(1)

    # 신체계통 목록 가져오기
    system_selector = 'div.body-box > a'
    system_elems = await page.querySelectorAll(system_selector)
    system_names = []

    for elem in system_elems:
        name = await page.evaluate('(el) => el.getAttribute("alt") || ""', elem)
        system_names.append(name.strip())

    # 사용자 선택
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

        j = 0
        while True:
            # 🌀 메인 페이지로 이동
            await page.goto(BASE_URL, {'waitUntil': 'networkidle2'})
            await asyncio.sleep(1)

            # 🔁 계통 재클릭
            system_elems = await page.querySelectorAll(system_selector)
            await system_elems[i].click()
            await asyncio.sleep(1)

            # 질병 목록 로드
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
                disease_name = await page.evaluate('(el) => el.textContent.trim()', a_tag)

                # 파일명 안전하게
                safe_name = re.sub(r'[\\/*?:"<>|]', "_", disease_name)
                filename = f"{system_name}_{safe_name}.pdf"
                save_path = os.path.join(SAVE_DIR, filename)

                print(f"    🦠 질병 {j+1}: {disease_name}")

                # # 사용자 확인
                # user_input = input(f"    🦠 질병 {j+1}: {disease_name}\n    👉 이 질병을 저장하시겠습니까? (y/n): ").strip().lower()
                # if user_input != 'y':
                #     print("    ⏭️ 저장 생략")
                #     j += 1
                #     continue

                try:
                    try:
                        await a_tag.click()
                    except Exception as e:
                            print("    ⚠️ 상세페이지 입장 실패: 클릭 자체가 안 됨. 스킵합니다.")
                            j += 1
                            continue  # 클릭 실패한 경우 바로 다음으로 넘어감
                    # await page.waitForSelector("h2", {'timeout': 10000})
                    await asyncio.sleep(10)

                    # current_title = await page.evaluate('() => document.querySelector("h2")?.innerText || ""')

                    # if disease_name not in current_title:
                    #     print(f"    ⚠️ 제목 불일치: 상세페이지 제목이 '{current_title}' 이므로 '{disease_name}'과(와) 불일치합니다. 저장 생략.")
                    #     j += 1
                    #     continue

                    print("    ⏳ 상세 페이지 진입 완료. PDF 저장 중...")
                    os.makedirs(SAVE_DIR, exist_ok=True)
                    await save_pdf_from_page(page, save_path)
                    print(f"    ✅ 저장 완료: {save_path}")

                except Exception as e:
                    print(f"    ❌ 상세 페이지 진입 실패 또는 저장 실패: {e}")

                # # 사용자 계속 여부
                # cont = input("    🔁 다음 질병으로 진행할까요? (y/n): ").strip().lower()
                # if cont != 'y':
                #     print("    ⛔ 해당 계통 크롤링 중단")
                #     break

                j += 1

            except Exception as e:
                print(f"    ❌ 질병 {j+1} 처리 실패: {e}")
                j += 1
                continue

        # 계통별 완료 후 사용자 확인
        if len(selected_indices) > 1:
            cont_sys = input(f"\n📌 '{system_name}' 계통 저장 완료. 계속하시겠습니까? (y/n): ").strip().lower()
            if cont_sys != 'y':
                print("⛔ 전체 작업을 종료합니다.")
                break

    await browser.close()

# 실행
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(crawl())
    except KeyboardInterrupt:
        print("\n🛑 사용자가 작업을 중단했습니다.")