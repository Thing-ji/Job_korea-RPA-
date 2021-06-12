## tkinter 관련
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import webbrowser

## 데이터 pandas 관련
import requests
from bs4 import BeautifulSoup
import pandas as pd

## sqlite
import sqlite3 # sql에 저장

#### 웹 스크레핑
data = pd.DataFrame(columns=['회사이름', '공고제목', '직무', '경력', '학력', '모집기간', '상세보기'])
page = 1
while page <= 20:
    url = 'https://www.jobkorea.co.kr/Starter/?JoinPossible_Stat=0&schOrderBy=0&LinkGubun=0&LinkNo=0&schType=0&schGid=0&Page={}'.format(
        page)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, 'lxml')
    print('{} 번째 페이지'.format(page))
    corporates = soup.find("div", attrs={"class": "filterListArea"}).find_all("li")

    # 회사이름, 공고제목, 직무, 경력, 모집기간 추출
    for i in range(len(corporates)):
        try:
            a = ','.join(corporates[i].find("a", attrs={"class": "coLink"}).get_text().split())
            b = ','.join(corporates[i].find("a", attrs={"class": "link"}).get_text().split())
            c = ','.join(corporates[i].find("div", attrs={"class": "sTit"}).get_text().split())
            d = ','.join(corporates[i].find("div", attrs={"class": "sDesc"}).find('strong').get_text().split())
            e = ','.join(corporates[i].find("div", attrs={"class": "sDesc"}).find('span').get_text().split())
            f = ','.join(corporates[i].find("span", attrs={"class": "day"}).get_text().split())
            g = "https://www.jobkorea.co.kr" + corporates[i].find("div", attrs={"class":"tit"}).a['href']

            alphas = [a, b, c, d, e, f, g]
            data = data.append(pd.Series(alphas, index=data.columns), ignore_index=True)

        except:
            pass

    page += 1


####################
# 전체 연결 불러오기
con = sqlite3.connect('Job_korea2.db')  # DB 연결
data.to_sql('Recruitment', con, index=False)  # 'Recruitment' 라는 이름의 table 생성
cur = con.cursor()  # DB에 위치시키기

sql = '''SELECT * FROM Recruitment'''

data = pd.read_sql(sql, con)
con.commit()
con.close()
#####################



#### 변수정의
favorite_list = [] ## 마이페이지에 트리뷰에 들어갈 즐겨찾기 리스트
temp3 = [] ## 마이페이지 삭제기능에 임시로 들어가는 리스트



#### 함수설정
### 메인 트리뷰에 남아있는 데이터 클리어/삭제
def clear_data():
    global data
    for i in range(len(data)):
        try:
            result.delete(i)
        except:
            pass


### result에 페이지 보여주는 함수
def show_data():
    if data.shape[0] >= 40:  # 회사수가 40이상
        for i in range(40):
            result.insert(parent='', index=i, iid=i, text='', values=(
                i + 1, data.loc[i, '회사이름'], data.loc[i, '공고제목'], data.loc[i, '직무'], data.loc[i, '경력'],
                data.loc[i, '학력'],
                data.loc[i, '모집기간']))

    else:  # 회사수가 40이상이 되지 않으면
        for i in range(data.shape[0]):
            result.insert(parent='', index=i, iid=i, text='', values=(
                i + 1, data.loc[i, '회사이름'], data.loc[i, '공고제목'], data.loc[i, '직무'], data.loc[i, '경력'],
                data.loc[i, '학력'],
                data.loc[i, '모집기간']))


### 경력 체크박스 함수 구현
def job_fitter(job_var) :
    global data
    global cur
    global sql

    if job_var[0] == 1 and job_var[1] == 0:
        sql = '''SELECT * FROM Recruitment
                 WHERE 경력 LIKE "%신입%"'''

    elif job_var[0] == 0 and job_var[1] == 1:
        sql = '''SELECT * FROM Recruitment
                 WHERE 경력 LIKE "%경력%"'''

    elif job_var[0] == 1 and job_var[1] == 1 :
        sql = '''SELECT * FROM Recruitment
                 WHERE (경력 LIKE "%신입%") OR (경력 LIKE "%경력%")'''

    else :
        sql = '''SELECT * FROM Recruitment'''

    return sql


### 학력 체크박스 함수 구현
def school_fitter(school_var) :
    global data
    global cur
    global sql

    sql = '''SELECT * FROM Recruitment '''

    if school_var[0] == 1:
        if "WHERE" in sql:
            sql += '''OR (학력 LIKE "%고졸%") '''
        else:
            sql += '''WHERE (학력 LIKE "%고졸%") '''

    if school_var[1] == 1 :
        if "WHERE" in sql:
            sql += '''OR (학력 LIKE "%초대졸%") '''
        else:
            sql += '''WHERE (학력 LIKE "%초대졸%") '''

    if school_var[2] == 1 :
        if "WHERE" in sql:
            sql += '''OR (학력 LIKE "%대졸%") '''
        else:
            sql += '''WHERE (학력 LIKE "대졸%") '''

    if school_var[3] == 1 :
        if "WHERE" in sql:
            sql += '''OR (학력 LIKE "%석사%") OR (학력 LIKE "%박사%") '''
        else:
            sql += '''WHERE (학력 LIKE "%석사%") OR (학력 LIKE "%박사%") '''

    if school_var[4] == 1 :
        if "WHERE" in sql:
            sql += '''OR (학력 LIKE "%학력무관%") '''
        else:
            sql += '''WHERE (학력 LIKE "%학력무관%") '''

    return sql


### 키워드 검색 함수 구현
def search_keyword(word):
    global data
    global cur

    sql = '''
    SELECT * FROM Recruitment
    WHERE (회사이름 LIKE "%{}%" OR 공고제목 LIKE "%{}%" OR 직무 LIKE "%{}%")'''.format(word, word, word)

    return sql


### 등록일순, 마감임박 날짜 Sorting 함수
def date_sorting(value):
    global data
    global cur

    sql = '''SELECT * FROM Recruitment '''

    if value == 1 :  # 등록일 순 (초기상태와 동일)
        sql

    elif value == 2 :  # 마감임박 순 (날짜기준 오름차순)
        sql += 'ORDER BY 모집기간 '

    elif value == 3 :  # 마감여유 순 (날짜기준 내림차순)
        sql += 'ORDER BY 모집기간 DESC '

    return sql


### 각 함수 테이블 통합 교집합, 합집합 함수 (경력, 학력, 키워드, 날짜 Sorting의 sql문을 불러온뒤 교집합 형태로 구현)
def final_fitter(job, school, keyword, sort) :
    global data
    global cur

    con = sqlite3.connect('Job_korea2.db')  # DB 연결
    cur = con.cursor()  # DB에 위치시키기
    sql = '{} intersect {} intersect {} intersect {}'.format(job,school,keyword,sort)
    data = pd.read_sql(sql, con)
    con.commit()
    con.close()

    return data


### 검색 버튼 함수
def search_new_data():
    global data
    global cur
    global page

    page = 1
    now_page.configure(text='- ' + str(page) + ' 페이지 -')

    ## 경력 체크박스 변수 리스트 형태로 불러들이기
    ## Ex)[1,0] -> 신입 체크, 경력 체크 안한 것
    job_var_list = []
    job_var_list.append(job_check_var1.get())
    job_var_list.append(job_check_var2.get())

    ## 학력 체크박스 변수 리스트 형태로 불러들이기
    ## Ex)[1,0,0,0,0] -> 고졸체크, 나머지 체크 안한 것
    school_var_list = []
    school_var_list.append(school_check_var1.get())
    school_var_list.append(school_check_var2.get())
    school_var_list.append(school_check_var3.get())
    school_var_list.append(school_check_var4.get())
    school_var_list.append(school_check_var5.get())


    ## 등록일순, 마감일순, 마감여유순 변수 지정 (date를 1 2 3으로 지정해줘서 날짜 Sorting 함수에서 처리하기 위함)
    date_temp = combo_chosen.get()
    if date_temp == '등록일순' :
        date = 1
    elif date_temp == '마감임박순' :
        date = 2
    elif date_temp == '마감여유순' :
        date = 3

    con = sqlite3.connect('Job_korea2.db')  # DB 연결
    cur = con.cursor()  # DB에 위치시키기

    clear_data() # 메인 트리뷰에 남아있는 데이터 클리어/삭제

    ## 각 필터 함수 실행하여 a,b,c,d 라는 변수에 저장
    a = job_fitter(job_var_list) # 경력 필터 함수
    b = school_fitter(school_var_list) # 학력 필터 함수
    c = search_keyword(search_entry.get()) # 입력 검색 함수
    d = date_sorting(date) # 등록일순 Date Sorting 함수

    ## a,b,c,d 변수값을 최종적으로 필터하여 데이터프레임 형태로 저장
    final_fitter(a, b, c, d)

    show_data() # 메인 트리뷰에 저장된 데이터프레임 출력


### 다음 페이지 버튼 함수
def nxt_page():
    global page
    global error
    error = 0
    page += 1

    clear_data() # 메인 트리뷰에 남아있는 데이터 클리어/삭제

    if data.shape[0]/40 == data.shape[0]//40 : # 정수일떄만
        try :
            for i in range(40):
                result.insert(parent='', index=i, iid=i, text='', values=(
                (page - 1) * 40 + (i + 1), data.loc[(page - 1) * 40 + i, '회사이름'], data.loc[(page - 1) * 40 + i, '공고제목'],
                data.loc[(page - 1) * 40 + i, '직무'], data.loc[(page - 1) * 40 + i, '경력'], data.loc[(page - 1) * 40 + i, '학력'],
                data.loc[(page - 1) * 40 + i, '모집기간']))
        except :
            error = 1
            pass

    elif data.shape[0]/40 > data.shape[0]//40 : # 정수가 아닌 실수일떄
        try :
            for i in range(40):
                result.insert(parent='', index=i, iid=i, text='', values=(
                (page - 1) * 40 + (i + 1), data.loc[(page - 1) * 40 + i, '회사이름'], data.loc[(page - 1) * 40 + i, '공고제목'],
                data.loc[(page - 1) * 40 + i, '직무'], data.loc[(page - 1) * 40 + i, '경력'], data.loc[(page - 1) * 40 + i, '학력'],
                data.loc[(page - 1) * 40 + i, '모집기간']))

        except :
            for i in range(data.shape[0]-((40*page)-1)):
                result.insert(parent='', index=i, iid=i, text='', values=(
                (page - 1) * 40 + (i + 1), data.loc[(page - 1) * 40 + i, '회사이름'], data.loc[(page - 1) * 40 + i, '공고제목'],
                data.loc[(page - 1) * 40 + i, '직무'], data.loc[(page - 1) * 40 + i, '경력'], data.loc[(page - 1) * 40 + i, '학력'],
                data.loc[(page - 1) * 40 + i, '모집기간']))

            if (data.shape[0]//40 + 2) == page :
                error = 1
                pass
    now_page.configure(text='- ' + str(page) + ' 페이지 -') # 현재 페이지 연동 실시간 갱신

    ## 마지막 페이지일시에 안내문 출력
    if error == 1:
        error -= 1
        messagebox.showwarning("안내", "마지막 페이지입니다.") # 마지막 페이지 안내문 출력
        clear_data()
        if data.shape[0] / 40 == data.shape[0] // 40 : # 정수일때, 이전 페이지로 이동 및 메인 트리뷰 갱신
            for i in range(40):
                result.insert(parent='', index=i, iid=i, values=(
                    (page - 2) * 40 + (i + 1), data.loc[(page - 2) * 40 + i, '회사이름'],
                    data.loc[(page - 2) * 40 + i, '공고제목'],
                    data.loc[(page - 2) * 40 + i, '직무'],
                    data.loc[(page - 2) * 40 + i, '경력'], data.loc[(page - 2) * 40 + i, '학력'],
                    data.loc[(page - 2) * 40 + i, '모집기간']))
            page = len(data) // 40  # 페이지 수에 맞게 지정

        elif data.shape[0]/40 > data.shape[0]//40 :  # 실수일떄, 이전 페이지로 이동 및 메인 트리뷰 갱신
            try :
                for i in range(data.shape[0]):
                    result.insert(parent='', index=i, iid=i, values=(
                        (page - 2) * 40 + (i + 1), data.loc[(page - 2) * 40 + i, '회사이름'],
                        data.loc[(page - 2) * 40 + i, '공고제목'],
                        data.loc[(page - 2) * 40 + i, '직무'],
                        data.loc[(page - 2) * 40 + i, '경력'], data.loc[(page - 2) * 40 + i, '학력'],
                        data.loc[(page - 2) * 40 + i, '모집기간']))
                page = 1
            except :
                page = (len(data)//40)+1
                pass

        now_page.configure(text='- ' + str(page) + ' 페이지 -') # 현재 페이지 연동 실시간 갱신


### 이전 페이지 버튼 함수
def pre_page():
    global page
    global error
    page -= 1
    for i in range(len(data)): # 메인 트리뷰에 남은 데이터 삭제
        try:
            result.delete(i)
        except:
            pass

    for i in range(40):
        try:
            result.insert(parent='', index=i, iid=i, values=(
            (page - 1) * 40 + (i + 1), data.loc[(page - 1) * 40 + i, '회사이름'], data.loc[(page - 1) * 40 + i, '공고제목'],
            data.loc[(page - 1) * 40 + i, '직무'],
            data.loc[(page - 1) * 40 + i, '경력'], data.loc[(page - 1) * 40 + i, '학력'],
            data.loc[(page - 1) * 40 + i, '모집기간']))
        except:
            error = 1
            pass

    ## 첫번째 페이지일시에 안내문 출력
    if error == 1:
        error -= 1
        messagebox.showwarning("안내", "첫번째 페이지입니다.")
        for i in range(len(data)):
            try:
                result.delete(i)
            except:
                pass

        for i in range(40):
            try:
                result.insert(parent='', index=i, iid=i, values=(
                    (page) * 40 + (i + 1), data.loc[(page) * 40 + i, '회사이름'], data.loc[(page) * 40 + i, '공고제목'],
                    data.loc[(page) * 40 + i, '직무'],
                    data.loc[(page) * 40 + i, '경력'], data.loc[(page) * 40 + i, '학력'],
                    data.loc[(page) * 40 + i, '모집기간']))
            except:
                page = 1
                pass
        page = 1
    now_page.configure(text='- ' + str(page) + ' 페이지 -') # 현재 페이지 연동 실시간 갱신


### 마이페이지에 추가하는 함수
def add_my_favorite():
    global cur
    global favorite_list
    global my_favorite
    selectedItem = result.focus()
    getValue = result.item(selectedItem).get('values')  # 딕셔너리의 값만 가져오기

    con = sqlite3.connect('Job_korea2.db')
    cur = con.cursor()
    sql = '''
    SELECT 회사이름, 공고제목, 상세보기
    FROM Recruitment
    WHERE (회사이름 == "{}") AND (공고제목 == "{}")
    '''.format(getValue[1], getValue[2])
    cur.execute(sql)
    rows = cur.fetchall()
    favorite_list.append(rows[0])
    con.commit()
    con.close()

    my_favorite = pd.DataFrame(favorite_list)

    return my_favorite


### 마이페이지 화면 출력 함수
def createNewWindow():
    global my_page
    global my_favorite
    global my_page_result
    global my_page_selectedItem
    global my_page_getValue
    global my_page_homepage
    my_page = Toplevel(window)
    my_page.geometry("1100x300+100+100")
    my_page.title("마이페이지")

    ## 마이페이지 안내 레이블
    my_page_title_1 = Label(my_page, text="※ 즐겨찾기한 기업 리스트 ※", font=("맑은 고딕", 15, 'bold'))
    my_page_title_1.place(x=30, y=0)

    ## 마이페이지 트리뷰
    my_page_result = Treeview(my_page)
    my_page_result['columns'] = ['number', 'com_name', 'title', 'com_page']
    my_page_result.column('#0', width=0, stretch=FALSE)
    my_page_result.column('number', anchor=CENTER, width=60, stretch=FALSE)
    my_page_result.column('com_name', anchor=W, width=160, stretch=FALSE)
    my_page_result.column('title', anchor=W, width=450, stretch=FALSE)
    my_page_result.column('com_page', anchor=W, width=350, stretch=FALSE)

    my_page_result.heading('#0', text='', anchor=CENTER)
    my_page_result.heading('number', text='번호', anchor=CENTER)
    my_page_result.heading('com_name', text='회사이름', anchor=CENTER)
    my_page_result.heading('title', text='공고제목', anchor=CENTER)
    my_page_result.heading('com_page', text='홈페이지', anchor=CENTER)
    my_page_result.place(x=30, y=40, height=200)
    try : # 마이페이지 트리뷰에 데이터 입력
        for i in range(len(my_favorite)) :
            my_page_result.insert(parent='', index=i, iid=i, text='', values=(
            i + 1, my_favorite.loc[i, 0], my_favorite.loc[i, 1], my_favorite.loc[i, 2]))
    except : # 마이페이지 아무것도 없을시에 안내문 출력
        messagebox.showwarning("안내", "마이페이지에 저장된 기업이 없습니다.")

    ## 마에피이지 트리뷰 스크롤바
    my_page_scrollbar = Scrollbar(my_page, orient="vertical", command=my_page_result.yview)
    my_page_scrollbar.place(x=1055, y=40, height=180 + 20)
    my_page_result.configure(yscrollcommand=my_page_scrollbar.set)

    ## 홈페이지 바로가기 버튼
    my_page_homepage = Button(my_page, width=11, text='홈페이지 연결하기', command = open_website)
    my_page_homepage.place(x=970, y=250)


### 마이페이지 웹사이트 오픈 함수
def open_website () :
    global my_page_selectedItem
    global my_page_getValue
    global my_page_homepage
    my_page_selectedItem = my_page_result.focus()
    my_page_getValue = my_page_result.item(my_page_selectedItem).get('values')
    webbrowser.open('{}'.format(my_page_getValue[3]))

### 메뉴얼 안내 창 함수
def help_manual():
    filewin = Toplevel(window)
    filewin.geometry("1000x450+500+250")

    labelframe = Label(filewin, text="본 프로그램은 정보시스템분석 팀프로젝트를 위해 만들어졌습니다.")
    labelframe.config(font=('맑은 고딕', 9, 'bold'))
    labelframe.place(x=0, y=0)

    help0 = Label(filewin, text="<프로그램 사용설명서>\n")
    help0.place(x=0, y=50)
    help0.config(font=('맑은 고딕', 12, 'bold'))
    help1 = Label(filewin, text="1. 이 프로그램은 1920*1080 모니터 크기에 최적화 되어 있어 화면 일부가 안 보일 수 있습니다.")
    help1.place(x=0, y=90)
    help1.config(font=('현대하모니 L', 10))
    help2 = Label(filewin, text="2. 궁금한 키워드를 입력하여 검색하면 관련된 기업공채정보를 얻을 수 있습니다. 단, 회사이름, 공고제목, 직무에 관련된 키워드에 한함.")
    help2.place(x=0, y=130)
    help2.config(font=('현대하모니 L', 10))
    help3 = Label(filewin, text="3. 본인의 경력, 학력을 선택하여 이에 해당하는 기업공채정보를 얻을 수 있습니다.")
    help3.place(x=0, y=170)
    help3.config(font=('현대하모니 L', 10))
    help4 = Label(filewin, text="4. 등록일순, 마감임박순, 마감여유순 중 하나를 선택하여 원하는 정보를 해당 시간 순서대로 볼 수 있습니다.")
    help4.place(x=0, y=210)
    help4.config(font=('현대하모니 L', 10))
    help5 = Label(filewin, text="5. 기타 기업 공채 정보 관련 사이트에 들어가고 싶은 경우 우측에 기타 홈페이지들을 클릭하면 바로 이동할 수 있습니다.  ")
    help5.place(x=0, y=250)
    help5.config(font=('현대하모니 L', 10))
    help6 = Label(filewin, text="<프로그램 주의사항>\n")
    help6.place(x=0, y=290)
    help6.config(font=('맑은 고딕', 12, 'bold'))
    help7 = Label(filewin, text="1. '담아두기' 사용 시 한 번에 여러 기업을 담을 경우, 오류가 발생합니다. ")
    help7.place(x=0, y=330)
    help7.config(font=('현대하모니 L', 10))
    help8 = Label(filewin, text="2. 원하는 기업 정보를 하나 선택 후, '담아두기'를 해야 마이페이지에서 오류 없이 확인 가능하다.")
    help8.place(x=0, y=370)
    help8.config(font=('현대하모니 L', 10))



#### Main 함수
window = Tk()
window.geometry("1500x550+200+200")
window.title("기업공채 정보 검색 시스템")


### Main 상단바 메뉴
menubar = Menu(window)
helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Help Index", command=help_manual)
window.config(menu=menubar)



### 각종 레이블 생성
## 첫 칸 안내 레이블
title_1 = Label(window, text="※ 기업 공채 검색 시스템 ※", font=("맑은 고딕", 15, 'bold'))
title_1.place(x=50, y=0)


## 두번째 칸 레이블들
# 경력여부 레이블
job_lb1 = Label(window, text="▶ 경력", font=("맑은 고딕", 10, 'bold'))
job_lb1.place(x=50, y=80)

# 학력여부 레이블
school_lb1 = Label(window, text="▶ 학력", font=("맑은 고딕", 10, 'bold'))
school_lb1.place(x=50, y=105)


### 등록일순, 마감임박 콤보 박스
select_combovar = StringVar()
combo_chosen = Combobox(window, width=10, textvariable=select_combovar)
combo_chosen['values'] = ('등록일순', '마감임박순', '마감여유순')
combo_chosen.place(x=50, y=50)
combo_chosen.current(0)


### 경력 체크 박스
job_check_var1 = IntVar()  # IntVar() 타입의 변수를 생성 # Checkbutton 인자로 IntVar() 타입의 변수를 전달
job_check1 = Checkbutton(window, text="신입", variable=job_check_var1, state='normal', onvalue = 1, offvalue=0)
job_check1.place(x=110, y=80)

job_check_var2 = IntVar()
job_check2 = Checkbutton(window, text="경력", variable=job_check_var2, state='normal', onvalue = 1, offvalue=0)
job_check2.place(x=160, y=80)


### 학력 체크박스
school_check_var1 = IntVar()  # 고졸
school_check1 = Checkbutton(window, text="고졸", variable=school_check_var1, onvalue = 1, offvalue=0, state='normal')
school_check1.place(x=110, y=105)

school_check_var2 = IntVar()  # 대학 2년제
school_check2 = Checkbutton(window, text="대학졸업(2,3년)", variable=school_check_var2, state='normal', onvalue = 1, offvalue=0)
school_check2.place(x=160, y=105)

school_check_var3 = IntVar()  # 대학 4년제
school_check3 = Checkbutton(window, text="대학졸업(4년)", variable=school_check_var3, state='normal', onvalue = 1, offvalue=0)
school_check3.place(x=270, y=105)

school_check_var4 = IntVar()  # 석박사
school_check4 = Checkbutton(window, text="석/박사 졸업", variable=school_check_var4, state='normal', onvalue = 1, offvalue=0)
school_check4.place(x=370, y=105)

school_check_var5 = IntVar()  # 무관
school_check5 = Checkbutton(window, text="학력무관", variable=school_check_var5, state='normal', onvalue = 1, offvalue=0)
school_check5.place(x=460, y=105)


### 검색 텍스트 엔트리
search_entry = Entry(window, width=20)
search_entry.place(x=150, y=50)


### 데이터 검색 버튼
search_b1 = Button(window, width=9, text="검색", command=search_new_data)
search_b1.place(x=300, y=48)


### 메인 트리뷰 데이터 구현
result = Treeview(window)
result['columns'] = ['number', 'com_name', 'title', 'job', 'years', 'school', 'date']
result.column('#0', width=0, stretch=FALSE)
result.column('number', anchor=CENTER, width=60, stretch=FALSE)
result.column('com_name', anchor=W, width=160, stretch=FALSE)
result.column('title', anchor=W, width=450, stretch=FALSE)
result.column('job', anchor=W, width=350, stretch=FALSE)
result.column('years', anchor=W, width=100, stretch=FALSE)
result.column('school', anchor=W, width=100, stretch=FALSE)
result.column('date', anchor=W, width=120, stretch=FALSE)

result.heading('#0', text='', anchor=CENTER)
result.heading('number', text='번호', anchor=CENTER)
result.heading('com_name', text='회사이름', anchor=CENTER)
result.heading('title', text='공고제목', anchor=CENTER)
result.heading('job', text='직무', anchor=CENTER)
result.heading('years', text='경력', anchor=CENTER)
result.heading('school', text='학력', anchor=CENTER)
result.heading('date', text='모집기간', anchor=CENTER)

result.place(x=50, y=150, height = 328)


### 메인 트리뷰 스크롤바
scrollbar = Scrollbar(window, orient="vertical", command=result.yview)
scrollbar.place(x=1395, y=150, height=310 + 20)
result.configure(yscrollcommand=scrollbar.set)


### pandas 데이터 가지고와서 메인 트리뷰에 집어넣기
show_data()

### 다음 페이지, 이전 페이지 버튼
page = 1
main_chart_nxt_page = Button(window, width=9, text="다음 페이지", command = nxt_page)  # 다음페이지 버튼
main_chart_nxt_page.place(x=800, y=490)
main_chart_pre_page = Button(window, width=9, text="이전 페이지", command = pre_page)  # 이전페이지 버튼
main_chart_pre_page.place(x=600, y=490)

now_page = Label(window, text="- 1 페이지 -", font=("맑은 고딕", 10)) # 현재 페이지 안내 레이블
now_page.place(x=700, y=492)


### 기타 홈페이지 안내 및 다이렉트 버튼
homepage_label = Label(window, text="▶ 기타 홈페이지 연결", font=("맑은 고딕", 10, 'bold'))
homepage_label.place(x=800, y=50)
button_facebook = Button(window, text='사람인', command = lambda: webbrowser.open('https://www.saramin.co.kr/'))
button_google = Button(window, text='잡코리아', command = lambda: webbrowser.open('https://www.jobkorea.co.kr/'))
button_yahoo = Button(window, text='잡플래닛', command = lambda: webbrowser.open('https://www.jobplanet.co.kr/'))
button_youtube = Button(window, text='인크루트', command = lambda: webbrowser.open('https://www.incruit.com/'))
button_facebook.place(x=800,y=80)
button_google.place(x=900,y=80)
button_yahoo.place(x=1000,y=80)
button_youtube.place(x=1100,y=80)


### 마이페이지 버튼
mypage_button = Button(window, text="마이페이지", command = createNewWindow)
mypage_button.place(x=1200,y=490)


### 마이페이지에 추가하기 버튼
mypage_addbutton = Button(window, text="담아두기", command=add_my_favorite)
mypage_addbutton.place(x=1300,y=490)


window.mainloop()