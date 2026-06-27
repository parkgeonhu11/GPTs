import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
import os
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv  # 💡 환경 변수 로드 라이브러리 추가

# .env 파일이 폴더에 있을 경우 환경 변수를 읽어옵니다.
load_dotenv()

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="Seoyeon Middle School AI Guide",
    page_icon="🤖",
    layout="wide"
)

# 📂 데이터 생성 및 RAG용 리스트 분할 관리 함수
def DATA_INIT_AND_LOAD():
    rule_file_path = "seoyeon_chatbot_data.csv"
    lunch_file_path = "seoyeon_lunch_data.csv"

    # ① 학칙 및 대규모 FAQ 규정 CSV 자동 생성 (32개 명세 완벽 내장)
    if not os.path.exists(rule_file_path):
        default_rules = [
            ["카테고리", "학칙 및 규정 내용"],
            ["등교 시간", "아침 오전 8시 50분까지 교실에 입실 완료해야 합니다. 8시 50분이 지나면 지각 처리됩니다."],
            ["지각 처리 기준", "오전 8시 50분 이후에 교실에 들어오면 지각으로 기록됩니다. 단, 버스 지연 등 불가피한 사유는 증빙 서류 제출 시 인정될 수 있습니다."],
            ["무단 지각 결석", "무단 지각, 무단 결과, 무단 조퇴를 합산하여 3회가 되면 무단 결석 1회로 처리되므로 생활기록부 관리를 위해 유의해야 합니다."],
            ["질병 결석 신청", "질병으로 인해 결석할 경우, 등교 후 3일 이내에 질병결석계와 함께 의사 진단서, 소견서 또는 처방전 등 증빙 서류를 담임선생님께 제출해야 합니다."],
            ["조퇴 및 외출", "일과 중 아프거나 부득이한 사정으로 조퇴·외출을 하려면 반드시 담임선생님의 승인을 받아 '외출증/조퇴증'을 발급받은 후 경비실에 제출하고 하교해야 합니다."],
            ["복장 규정", "사복(평상복) 착용은 절대 금지됩니다. 등교 시 교복 또는 학교 생활복, 체육복 중에서 본인이 원하는 옷을 자율적으로 선택해서 편하게 입고 오면 됩니다."],
            ["체육복 등교", "체육 수업이 없는 날을 포함하여 평일 언제든 학교 지정 체육복을 입고 등하교하는 것이 전면 허용됩니다."],
            ["교복 사복 혼용", "교복이나 체육복 위에 사복 아우터(패딩, 코트 등)를 입는 것은 허용되지만, 아우터 안에는 반드시 교복, 생활복, 체육복 중 하나를 착용해야 합니다."],
            ["두발 규정", "학생의 개성을 존중하여 파마, 단발, 롱헤어 등 커트 및 펌 스타일은 자율적으로 허용됩니다. 단, 탈색이나 화려한 원색 염색은 제한됩니다."],
            ["교내 화장", "타인에게 혐오감을 주지 않는 기초화장이나 가벼운 립밤 등은 허용되지만, 과도한 색조 화장이나 아이라인 등은 용모 규정에 따라 제한될 수 있습니다."],
            ["피어싱 및 귀걸이", "귀걸이나 피어싱은 착용 가능하나, 체육 활동 시 부상 위험이 있거나 타인에게 위해를 가할 수 있는 날카롭고 과도하게 큰 장신구는 착용을 금지합니다."],
            ["전자기기 반납", "아침 조례 시간에 개인 스마트폰을 의무적으로 반납해야 하며, 종례 시간 하교 시에 돌려받습니다. 공계기 적발 시 규정에 따라 조치됩니다."],
            ["쉬는시간 스마트폰", "조례 때 스마트폰을 일괄 수거하므로 쉬는 시간이나 점심시간에도 개인 휴대폰 사용은 원칙적으로 불가능합니다."],
            ["아이패드 노트북", "개인 태블릿PC나 노트북은 원칙적으로 수거하지 않으나, 수업 시간 중 교과 선생님의 허락을 받은 학습 목적 외에 게임이나 동영상 시청 등으로 사용 시 압수될 수 있습니다."],
            ["무선 이어폰 에어팟", "일과 시간 중(쉬는 시간 포함) 에어팟, 갤럭시 버즈 등 무선 이어폰 착용은 금지됩니다. 단, 수업 중 선생님이 허가한 시청각 학습 시에는 사용 가능합니다."],
            ["전동 킥보드 자전거", "학생의 안전을 위해 전동 킥보드를 이용한 등하교는 절대 금지됩니다. 자전거 등교는 가능하나 반드시 교내 자전거 보관소를 이용하고 헬멧을 착용해야 합니다."],
            ["상벌점 제도", "우리 학교는 그린마일리지(상벌점) 제도 자체가 존재하지 않습니다. 벌점 누적에 대한 걱정 없이 자율적이고 즐겁게 학교생활을 하면 됩니다."],
            ["교내 흡연 금지", "교내 공공장소 및 학교 주변에서의 흡연은 학생 생활 규정에 따라 엄격히 금지되며, 적발 시 즉시 학생생활지도위원회에 회부되어 징계 및 금연 교육을 받게 됩니다."],
            ["무단 외출 금지", "점심시간이나 쉬는 시간에 교사 승인 없이 학교 정문 밖으로 나가는 것은 무단 외출로 간주되며, 안전사고 예방을 위해 엄격히 통제됩니다."],
            ["학교 폭력 예방", "언어폭력, 사이버 따돌림, 신체 폭력 등 모든 형태의 학교폭력은 무관용 원칙으로 대응하며, 인성인권부와 학교폭력대책심의위원회를 통해 엄중 처벌됩니다."],
            ["Wee클래스 상담", "본관 2층 서편에 위치해 있으며, 친구 관계, 학업 스트레스 등으로 상담이 필요할 때 쉬는 시간, 점심시간, 방과 후에 언제든 편하게 방문할 수 있습니다."],
            ["보건실 이용", "일과 중 몸이 아프면 교과 선생님이나 담임선생님께 말씀드리고 '보건실 이용증'을 받아 본관 1층 보건실로 가면 됩니다. 최대 1시간 동안 안정을 취할 수 있습니다."],
            ["도서관 이용 시간", "본관 3층에 위치한 도서관은 점심시간(오후 12시 40분 ~ 1시 30분)과 방과 후 오후 4시 30분까지 자유롭게 도서 대출 및 열람이 가능합니다."],
            ["체육관 강당 개방", "체육관(강당)은 안전 관리를 위해 체육 수업 및 학교 공식 행사 시간 외에는 임의로 출입할 수 없으며, 점심시간 자율 개방 여부는 학생회 공지에 따릅니다."],
            ["학생회실 위치", "전교 학생회실은 본관 2층 동편 끝에 위치해 있으며, 학교 발전을 위한 건의사항이나 아이디어가 있는 학생은 언제든 방문하거나 건의함을 이용할 수 있습니다."],
            ["급식 배식 순서", "안전하고 질서 있는 급식을 위해 3학년 -> 2학년 -> 1학년 순서로 배식합니다. 반별 세부 순서는 매달 공평하게 로테이션됩니다."],
            ["주말 급식 운영", "토요일, 일요일 등 주말과 법정공휴일, 재량휴업일에는 학교 급식이 제공되지 않으며 평일 학사 일정에 맞춰서만 운영됩니다."],
            ["급식실 새치기", "급식실 내에서 줄을 서는 중 새치기를 하거나 일행을 끼워주는 행위는 금지되며, 적발 시 배식 순서가 가장 뒤로 밀리는 등의 불이익을 받을 수 있습니다."],
            ["지방선거 휴무", "지방선거일 등 법정공휴일은 학교가 쉬는 날이므로 등교하지 않으며, 당연히 학교 급식도 운영되지 않습니다."],
            ["동아리 활동", "창의적 체험활동 동아리는 격주 금요일 5~6교시에 운영되며, 학기 초 부서별 희망 조사를 통해 선발 및 배정됩니다."],
            ["지필평가 시험", "중간고사 및 기말고사 지필평가 기간에는 점심 급식을 먹지 않고 시험 일정이 끝나는 대로 즉시 하교 조치됩니다."],
            ["방과후 학교", "방과 후 학교 수업은 정규 수업이 끝난 오후 3시 40분부터 시작되며, 분기별로 가정통신문을 통해 신청한 학생에 한해 참여합니다."]
        ]
        with open(rule_file_path, mode="w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(default_rules)

    # ② 6월 급식 식단표 CSV 자동 생성
    if not os.path.exists(lunch_file_path):
        default_lunch = [
            ["날짜", "요일", "특이사항", "메뉴"],
            ["6월 1일", "월요일", "생일축하의 날", "차수수밥, 감자미역국, 등푸른막(10), 마라교자만두, 무말랭이김치, 수박롤케이크"],
            ["6월 2일", "화요일", "저탄소식단", "칼슘강화쌀밥, 생배추된장국, 오징어야채볶음, 츄러스고구마맛탕, 열무김치, 큐브치즈"],
            ["6월 3일", "수요일", "지방선거 (휴무)", "지방선거로 인한 휴업일 (급식 없음)"],
            ["6월 4일", "목요일", "일반식단", "보리밥, 맑은콩나물국, 치즈불닭, 김구이, 애호박새우젓볶음, 백김치, 자두슬러시"],
            ["6월 5일", "금요일", "환경의 날", "종합잡곡밥, 도토리들깨수제비&또띠아쌈, 치플레콤보치킨&오리훈제, 삼색겨자냉채, 배추김치, 망고수박"],
            ["6월 8일", "월요일", "뺨데이", "칼슘강화쌀밥, 우렁된장찌개, 삼겹살구이, 상추쌈&쌈장, 콩나물파채무침, 열무김치, 체리"],
            ["6월 9일", "화요일", "일반식단", "찰옥수수밥, 쇠고기무국, 카레닭살볶음, 감자채볶음, 쑥갓두부무침, 배추김치"],
            ["6월 10일", "수요일", "수다날", "냉메밀국수, 우리카레밥(작은밥), 카츠산도, 토마토황도샐러드, 깍두기, 미숫가루라떼"],
            ["6월 11일", "목요일", "국없는날", "계란볶음밥&짜장소스, 유린기&소스, 꼬들오이지무침, 배추김치, 마시는요구르트(샤인머스캣)"],
            ["6월 12일", "금요일", "일반식단", "강황쌀밥, 순대국, 삼치데리야끼구이, 영양부추겉절이, 석박지, (로컬)생블루베리&생크림"],
            ["6월 15일", "월요일", "일반식단", "차조밥, 목살김치찌개, 목화솜탕수육&소스, 오징어기계맛살볶음, 총각김치, 우베요거트"],
            ["6월 16일", "화요일", "일반식단", "칼슘강화쌀밥, 어묵국, 까르보나라떡볶이, 오징어링&소스, 숙주미나리무침, 배추김치, (로컬)블루베리"],
            ["6월 17일", "수요일", "분식의 날", "김치볶음밥, 팽이미소된장국, 계란후라이, 또띠아치즈소시지롤, 잔멸치유자올리브볶음, 오이지무침, 미니초코우유"],
            ["6월 18일", "목요일", "일반식단", "홍국쌀밥, 나가사끼짬뽕국, 불고기우동볶음, 야채비빔만두, 배추김치, (로컬)멜론"],
            ["6월 19일", "금요일", "단오", "곤드레밥&양념장, 도토리묵채국, 치킨치즈카츠&감자튀김, 총각김치, 초코슈리쉬락"],
            ["6월 22일", "월요일", "일반식단", "현미밥, 아욱된장국, 돈육메추리알장조림, 메밀전병, 상추겉절이, 총각김치, 구슬똑똑아이스크림"],
            ["6월 23일", "화요일", "일반식단", "기장밥, 동태매운탕, 훈제오리&야채, 만두탕수, 백김치, (로컬)블루베리"],
            ["6월 24일", "수요일", "수다날", "투움바파스타, 바베큐폭립, 망고요거트샐러드, 모듬피클, 백김치, 부시맨빵&초코"],
            ["6월 25일", "목요일", "일반식단", "칼슘강화쌀밥, 오징어국, 안동찜닭, 로제치즈볼, 오이사과초무침, 배추김치, 나박김치"],
            ["6월 26일", "금요일", "일반식단", "흑미밥, 닭곰탕, 코코넛새우튀김&칠리소스, 잡채, 오이김치, 파인애플"],
            ["6월 29일", "월요일", "일반식단", "칼슘강화쌀밥, 조랭이떡국, 뿌링클치자치킨, 검은깨두부&김치볶음, 열무김치, (로컬)수박"],
            ["6월 30일", "화요일", "일반식단", "귀리밥, 열무된장국, 대패삼겹살숙주볶음, 계란찜, 노각무침, 배추김치"]
        ]
        with open(lunch_file_path, mode="w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(default_lunch)

    # 🔍 RAG 인덱싱용 고품질 Chunk 크롤러 구성
    raw_documents = []
    with open(rule_file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                raw_documents.append(f"[학칙/규정] 카테고리: {row[0]} -> 내용: {row[1]}")

    with open(lunch_file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                raw_documents.append(f"[급식식단] 날짜: {row[0]} ({row[1]}) [{row[2]}] -> 오늘의 메뉴 반찬 구성: {row[3]}")

    return raw_documents

# 시스템 실행 시 문서 풀 초기 인덱싱
ALL_CHUNKS = DATA_INIT_AND_LOAD()

# 🎯 [RAG 핵심 검색 알고리즘 함수]
def retrieve_relevant_context(query, documents, top_n=3):
    if not documents:
        return ""
    
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
    tfidf_matrix = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform([query])
    
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    retrieved_context = "\n".join([documents[i] for i in top_indices if similarities[i] > 0.03])
    return retrieved_context

# 💡 [보안 최적화 코드] 
# OpenAI API 키를 소스 코드 내에서 완전히 제거하고 환경 변수에서 안전하게 가져옵니다.
# 만약 환경 변수가 등록되지 않았다면 Streamlit의 secrets 기능을 시도합니다.
MY_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# 2. 🎨 디자인 테마 고정 CSS (PC 유지 + 모바일 미디어 쿼리 완벽 대응)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght=400;500;700;900&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Noto Sans KR', sans-serif;
        }

        /* 🖥️ [PC 기본 스타일 정의] */
        .title-section-container {
            background-color: #FFFFFF !important;
            padding: 35px 50px;
            border-radius: 24px;
            border: 1px solid #E9ECEF;
            box-shadow: 0 8px 24px rgba(0,0,0,0.02);
            margin-bottom: 35px;
            text-align: center;
        }
        .title-text {
            background: linear-gradient(135deg, #FF6B6B, #FFBB5C);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem !important;
            font-weight: 900 !important;
            margin: 0;
            letter-spacing: -1px;
        }
        .subtitle-text {
            color: #495057 !important;
            font-size: 1.25rem !important;
            font-weight: 500 !important;
            margin-top: 12px;
            margin-bottom: 0;
        }

        .premium-card {
            background-color: #FFFFFF !important;
            padding: 24px 28px;
            border-radius: 20px;
            border: 1px solid #E9ECEF;
            box-shadow: 0 8px 20px rgba(0,0,0,0.01);
            margin-bottom: 30px;
        }
        .card-title {
            color: #212529 !important;
            font-size: 1.35rem;
            font-weight: 700;
            margin-top: 0;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-content {
            color: #495057 !important;
            font-size: 1.05rem;
            line-height: 1.7;
            margin: 0;
        }
        .card-highlight {
            color: #FF6B6B !important;
            font-weight: 700;
        }

        /* 📱 [모바일 전용 최적화 반응형 레이아웃] 화면 가로 크기가 768px 이하일 때 활성화 */
        @media screen and (max-width: 768px) {
            .title-section-container {
                padding: 20px 15px !important;
                margin-bottom: 20px !important;
                border-radius: 16px !important;
            }
            .title-text {
                font-size: 1.8rem !important; /* 모바일 화면 크기에 맞춰 가변 축소 */
            }
            .subtitle-text {
                font-size: 1rem !important;
                margin-top: 8px !important;
            }
            .premium-card {
                padding: 16px 18px !important;
                margin-bottom: 20px !important;
                border-radius: 14px !important;
            }
            .card-title {
                font-size: 1.15rem !important;
            }
            .card-content {
                font-size: 0.95rem !important;
                line-height: 1.5 !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 💾 미분류 질문 기록 함수
def save_unknown_question(question):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{current_time}] 검토 필요 질문: {question}\n"
    with open("unknown_questions.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

# 4. 사이드바 UI 디자인
with st.sidebar:
    st.markdown("<h2 style='font-weight:800; margin-bottom:0;'>🏫 Seoyeon AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #86868B; margin-top:0;'>전교 부회장 기획 · 운영</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # API 키 상태 체크를 통한 경고/성공 메시지 출력
    if MY_OPENAI_API_KEY:
        st.success("🔒 OpenAI API 보안 상시 연동 완료")
    else:
        st.error("🔑 OpenAI API Key가 감지되지 않았습니다. 환경 변수 설정을 확인해 주세요.")
        
    st.markdown("---")
    st.markdown("<h4 style='font-weight:700; margin-bottom:15px;'>📱 오늘의 퀵 포커스</h4>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #FFF0F0; border-radius: 12px; padding: 15px; border: 1px solid #FFD9D9; margin-bottom: 15px;">
            <p style="color: #FF6B6B; margin: 0; font-weight: 600; font-size: 0.95rem;">
                💡 복장 팁: 사복만 아니면 <b>교복·생활복·체육복 자율 혼용 오케이!</b>
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
        <div style="font-size: 1rem; line-height: 1.9;">
            <p style="margin: 0;">🏃‍♂️ <span style="font-weight:600;">등교 마감</span>: <span style="color: #FF6B6B; font-weight:700;">08:50</span></p>
            <p style="margin: 0;">🍱 <span style="font-weight:600;">급식 순서</span>: 3학년 ➔ 2학년 ➔ 1학년</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("🤖 Seoyeon Guide v12.0")

# 5. 메인 화면 상단 레이아웃
st.markdown("""
    <div class="title-section-container">
        <h1 class="title-text">서연중학교 챗봇 AI</h1>
        <p class="subtitle-text">📌 전교 부회장 기획 · 실시간 날짜 연동 및 스마트 RAG 엔진 안내 시스템</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="premium-card">
        <div class="card-title">
            <img src="https://img.icons8.com/fluency/48/light-it-up.png" width="26" height="26"/>
            어떻게 시작할까요?
        </div>
        <p class="card-content">
            우리 학교생활 규칙이나 급식에 대해 무엇이든 물어보세요!<br>
            <span class="card-highlight">👉 "체육복 입고 등교해도 돼요?"</span>, <span class="card-highlight">👉 "에어팟 쉬는 시간에 끼면 압수인가요?"</span>, <span class="card-highlight">👉 "오늘 급식 뭐야?"</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# 6. 세션 상태 대화 기록방 유지
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "반가워요! 서연중학교 AI 가이드입니다. 32가지 이상의 상세 학칙 데이터베이스와 6월 급식 정보가 RAG 검색 엔진으로 최적화되었습니다. 무엇이든 편하게 물어보세요! 🍱"}
    ]

# 기존 대화창 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 7. 챗봇 추론 및 스마트 로그 로직
if user_input := st.chat_input("Seoyeon AI에게 물어보세요..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # API 키 유효성 빠른 검사
        if not MY_OPENAI_API_KEY:
            raise ValueError("OpenAI API Key가 설정되지 않았습니다. .env 파일 혹은 Streamlit Secrets를 확인하세요.")
            
        # 📅 실시간 날짜 동기화 및 타겟 날짜 유추
        now = datetime.now()
        realtime_today = now.strftime("%Y년 %m월 %d일")
        
        is_asking_lunch = any(keyword in user_input for keyword in ["급식", "식단", "메뉴", "밥", "먹어"])
        target_date = now
        is_asking_specific_day = False

        if "오늘" in user_input:
            target_date = now
            is_asking_specific_day = True
        elif "내일" in user_input:
            target_date = now + timedelta(days=1)
            is_asking_specific_day = True
        elif "모레" in user_input:
            target_date = now + timedelta(days=2)
            is_asking_specific_day = True
        elif "어제" in user_input:
            target_date = now - timedelta(days=1)
            is_asking_specific_day = True

        # 🛑 주말 완전 차단 필터
        if is_asking_lunch and is_asking_specific_day and target_date.weekday() in [5, 6]:
            with st.chat_message("assistant"):
                if "오늘" in user_input:
                    full_response = f"오늘은 {target_date.strftime('%m월 %d일')} 주말이므로 급식이 제공되지 않습니다! 주말 잘 보내세요. ☀️"
                elif "내일" in user_input:
                    full_response = f"내일은 {target_date.strftime('%m월 %d일')} 주말이므로 급식이 제공되지 않습니다! 편안한 주말 되세요. ☀️"
                else:
                    full_response = "해당 날짜는 주말이므로 급식이 제공되지 않습니다."
                st.write(full_response)
        else:
            # 🔍 [RAG 엔진 구동] 개선된 형태소 단위 검색 진행
            DYNAMIC_CONTEXT = retrieve_relevant_context(user_input, ALL_CHUNKS, top_n=3)

            # 🧠 고성능 시스템 프롬프트
            SYSTEM_PROMPT = f"""
            당신은 서연중학교 학생들을 위한 친절하고 똑똑한 '학교생활 및 급식 안내 AI 챗봇'입니다. 이 시스템은 전교 부회장이 기획 및 운영합니다.

            [중요: 실시간 오늘 날짜 기준 정보]
            - 오늘은 {realtime_today} 입니다. 사용자가 '오늘', '내일', '어제' 급식을 물어보면 이 날짜를 기준으로 급식 식단 데이터에서 요일과 날짜를 맵핑 및 유추하여 답변하세요.

            [RAG 검색 기반 추출 데이터베이스 - 최우선 참조]
            {DYNAMIC_CONTEXT if DYNAMIC_CONTEXT else "사용자의 질문과 정확히 일치하는 학칙이나 식단 컨텍스트가 검색되지 않았습니다."}

            [답변 가이드라인 및 예외 처리 규칙 - 필수 준수]
            1. 사용자가 물어본 질문이 '상벌점', '벌점' 등 학칙에 관한 내용이라면, 식단 정보와 혼동하지 말고 제공된 [학칙/규정] 데이터를 기반으로 정확하게 안내하세요. (예: 우리 학교는 그린마일리지 상벌점 제도가 없음)
            2. 사용자가 물어본 날짜가 토요일이나 일요일(주말)일 경우, 무조건 "주말에는 급식이 제공되지 않습니다."라고 명확하게 출력하세요. 절대 메뉴를 지어내거나 유추하지 마세요.
            3. 식단표 정보에 '일반식단'이라는 명칭이 들어있더라도, 절대로 답변에 "일반식단입니다"라고 요약하여 답하지 마세요. 반드시 데이터에 포함되어 있는 구체적인 반찬 이름 전체를 단 한 단어명도 빠짐없이 그대로 출력해야 합니다.
            4. 검색 데이터에 정보가 없는 일반적인 질문도 최대한 친절하게 답변하되, 학교 고유 규칙을 유추해야 하는 경우 끝에 "[확인 필요]"를 붙이세요.
            5. 모든 답변은 핵심 요약형으로 최대 3~4줄 이내로 간결하게 출력하세요. 다정하고 든든한 선배 톤을 유지하세요.
            """

            client = OpenAI(api_key=MY_OPENAI_API_KEY)
            
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages[:-1]:
                api_messages.append({"role": msg["role"], "content": msg["content"]})
            
            if not api_messages or api_messages[-1]["content"] != user_input:
                api_messages.append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                response_stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=api_messages,
                    stream=True
                )

                def make_stream_generator(stream):
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content

                full_response = st.write_stream(make_stream_generator(response_stream))

        # 분석 완료 라벨 추가 출력
        st.markdown("""
            <div style="text-align: right; margin-top: 5px;">
                <span style="background-color: #E9ECEF; color: #495057; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">
                    🎯 [Seoyeon AI] RAG 멀티 검색 완료
                </span>
            </div>
        """, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

        if "[확인 필요]" in full_response:
            save_unknown_question(user_input)
            st.toast("💡 새로운 질문이 감지되어 기록에 저장되었습니다.", icon="💾")

    except Exception as e:
        st.error(f"시스템 오류가 발생했습니다: {e}")
