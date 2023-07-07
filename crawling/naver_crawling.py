import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 

import time
import re
import json
from bs4 import BeautifulSoup 
from tqdm import tqdm
import numpy as np

#driver = webdriver.Chrome(service= Service(ChromeDriverManager().install()))
#driver2 = webdriver.Chrome(service= Service(ChromeDriverManager().install()))
ser = Service('../chromedriver/chromedriver.exe')
driver = webdriver.Chrome(service=ser)
driver2 = webdriver.Chrome(service=ser)
url = 'https://map.naver.com/v5/search'
driver.get(url)
key_word='경희대 국제캠퍼스 근처 식당'


###################################################################
# css 찾을때 까지 10초대기
def time_wait(num, code):
    try:
        wait = WebDriverWait(driver, num).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, code)))
    except:
        print(code, '태그를 찾지 못하였습니다.')
        driver.quit()
    return wait

time_wait(30, 'input.input_search')

# 검색창 찾기
search = driver.find_element(By.CSS_SELECTOR,'input.input_search')
search.send_keys(key_word)  # 검색어 입력
search.send_keys(Keys.ENTER)  # 엔터버튼 누르기

res = driver.page_source  # 페이지 소스 가져오기
soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

time.sleep(1)


# frame 변경 메소드
def switch_frame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경
    res
    soup


# 페이지 다운
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR,'body')
    body.click()
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)


# frame 변경
switch_frame('searchIframe')
page_down(100)
time.sleep(5)

# 매장 리스트
store_list = driver.find_elements(By.CSS_SELECTOR,'li.UEzoS.rTjJo')
print("매장 리스트 길이 : ",len(store_list))
# 페이지 리스트
next_btn = driver.find_elements(By.CSS_SELECTOR,'a.mBN2s')

# dictionary 생성
store_dict = {'매장정보': []}
# 시작시간
start = time.time()
print('[크롤링 시작...]')

# 크롤링 - 1페이지부터 6페이지까지
for btn in range(6):
    # 페이지 리스트
    next_btn = driver.find_elements(By.CSS_SELECTOR,'a.mBN2s')
    page_down(150) 
    store_list
    print("이 페이지에 있는 가게 개수 : ",len(store_list))
    if btn != 4 :
        try : 
            next_btn[btn+1].click()
        except :
            break
        continue
    for data in range(len(store_list)):  # 매장 리스트 만큼
        page = driver.find_elements(By.CSS_SELECTOR,'span.place_bluelink.TYaxT')
        print(len(page))
        page[data].click()
        time.sleep(2)
        try:
            # 상세 페이지로 이동
            switch_frame('entryIframe')

            # 매장명 가져오기
            store_name = driver.find_element(By.CSS_SELECTOR,'span.Fc1rA').text
            print(store_name)

            # 매장 판매 음식 종류(중식당, 요리주점, 등) 가져요기
            theme=driver.find_element(By.CSS_SELECTOR,'span.DJJvD').text
            print(theme)

            # 평점
            try:
                store_rating_list = driver.find_element(By.CSS_SELECTOR,'span.PXMot.LXIwF').text
                store_rating = re.sub('별점', '', store_rating_list).replace('\n', '')  # 별점이라는 단어 제거
                store_rating=store_rating.split('/')[0]
            except:
                store_rating=np.NaN
                pass # 평점 데이터가 존재하지 않는 경우를 고려
            print(store_rating)

            # -----주소(위치)-----
            try:
                store_addr=driver.find_element(By.CSS_SELECTOR,'span.LDgIH').text
            except:
                pass
            print(store_addr)

            # -----키워드 리뷰 가져오기-----
            try:
                cu = driver.current_url # 검색이 성공된 플레이스에 대한 개별 페이지 
                res_code = re.findall(r"place/(\d+)", cu)
                final_url = 'https://pcmap.place.naver.com/restaurant/'+res_code[0]+'/review/visitor?shouldKeywordUnfold=true'
                driver2.get(final_url)
                time.sleep(1)

            except:  # 키워드리뷰 없으면 다음 음식점으로
                print('키워드리뷰 없음 >>> 다음으로',)
                switch_frame('searchIframe')
                continue
            
            # 키워드 리뷰 총 수
            try :
                total_kwd_review=driver2.find_element(By.CSS_SELECTOR,'._Wmab').text
                total_kwd_review=total_kwd_review.split('회')[0]
            except :
                total_kwd_review=np.NaN
                print("못 찾음") 

            try:
                keyword_review_list = driver2.find_elements(By.CSS_SELECTOR,'.nbD78')  # 리뷰 리스트
                kwd_title = []
                kwd_count = []
                time.sleep(2)

                for i in keyword_review_list:
                    review = i.find_element(By.CSS_SELECTOR,'.CsBE9').text  # 키워드리뷰
                    kwd_name=review.split('\n')[0].replace('\"','')
                    kwd_title.append(kwd_name)
                    kwd_count.append(review.split('\n')[-1])

            except:
                kwd_title=np.NaN
                kwd_count=np.NaN
                pass

            try :
                kwd_count = list(map(int, kwd_count))  # int 형변환
            except :
                pass

            # ---- dict에 데이터 집어넣기----
            dict_temp = {
                'name': store_name,
                'theme' : theme,
                'star': store_rating,
                'addr': store_addr,
                'total_kwd_review' : total_kwd_review,
                'kwd': kwd_title,
                'kwd_count': kwd_count,
            }

            store_dict['매장정보'].append(dict_temp)

            print(f'{store_name} ...완료')
            switch_frame('searchIframe')
            time.sleep(1)

        except:
            print('ERROR!' * 3)
    
    if page[-1]:  # 마지막 매장일 경우 다음버튼 클릭
        try : 
            next_btn[btn+1].click()
        except :
            break
        time.sleep(2)
    else:
        print('페이지 인식 못함')
        break
    

print('[데이터 수집 완료]\n소요 시간 :', time.time() - start)
driver.quit()  # 작업이 끝나면 창을닫는다.
driver2.quit()

# json 파일로 저장
with open('data/store_data.json', 'w', encoding='utf-8') as f:
    json.dump(store_dict, f, indent=4, ensure_ascii=False)

# csv 파일로 저장
df=pd.DataFrame.from_dict(data=store_dict,orient='columns')
print(df)
data_csv=df.to_csv('data/naver2.csv')