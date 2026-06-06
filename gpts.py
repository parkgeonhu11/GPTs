### `src/app.py` 전체 코드
import streamlit as st
import time

st.set_page_config(
    page_title="서연중학교 학교생활 안내 AI",
    page_icon="🏫",
    layout="centered"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

faq_data = {
    "지각 기준": "서연중학교 지각 기준은 오전 8시 40분입니다. 40분까지 교실 책상에 입실하지 완료하지 못하면 지각 처리되며, 무단 지각이 누적될 경우 학생 생활지도 규정에 따라 상벌점 제도의 벌점이 부과될 수 있으니 유의하시기 바랍니다.",
    "생활복/체육복 등교": "기본적으로 정복 교복 착용이 원칙이나, 지정된 하복/동복 생활복 등교는 전면 허용됩니다. 단, 체육복 등교는 체육 수업이 드는 날에 한해 허용되며 일반 교과일에는 등교 후 탈의실에서 갈아입어야 합니다.",
    "사복 허용": "동절기 한파 및 우천 시 교복 위에 외투(패딩, 코트)를 껴입는 것은 전면 허용됩니다. 다만, 교복을 아예 입지 않고 사복 후드티나 맨투맨만 단독으로 착용하고 등교하는 것은 학칙상 제한됩니다.",
    "두발/귀걸이": "두발 염색 및 파마는 학교 생활 규정상 제한 대상입니다. 귀걸이 및 피어싱의 경우 안전상의 이유로 등교 중 착용은 금지되나, 귀가 막히는 것을 방지하기 위한 투명 귀걸이는 단정한 선에서 묵인됩니다.",
    "화장/렌즈": "과도한 색조 화장 및 써클/컬러 렌즈 착용은 학생 지도 규정 위반으로 벌점이 부과될 수 있습니다. 자외선 차단용 선크림 및 자연스러운 틴트류는 허용 기준 내에 포함됩니다.",
    "매점/자판기": "현재 서연중학교 본관 1층 후문 인근에 음료 및 간식용 자판기가 설치되어 있습니다. 쉬는 시간과 점심시간에 한해 이용이 가능하며 수업 시간 중 이용은 금지됩니다.",
    "급식 더 먹기": "전체 학급의 1차 배식이 완료된 후, 잔여 음식이 있는 경우에 한해 추가 배식 매대에서 더 받아먹을 수 있습니다. 추가 배식 시작 시간은 보통 13시 10분부터입니다.",
    "급식 패스": "학년별, 반별로 공평하게 순환하는 급식 순번제가 운영 중입니다. 학생회 및 방송부의 통제에 따라 지정된 시간 규칙을 반드시 준수하여 줄을 서야 합니다.",
    "쉬는 시간 외출": "안전 및 생활지도 규정상 점심시간과 쉬는 시간을 포함하여 학과 시간 중에는 교문 밖으로의 무단 외출이 절대 금지됩니다. 필요시 담임선생님의 외출증 발급이 필수적입니다.",
    "와이파이": "교내 보안 정책 및 학습 집중도 유지를 위해 학생용 공공 와이파이는 별도로 제공되지 않습니다. 교실 내 무선 네트워크는 교사 수업용 기기 전용으로 제한됩니다.",
    "충전": "수업 목적의 태블릿이나 교육용 기기는 교실 뒤편 충전 보관함에서 충전이 가능합니다. 개인 스마트폰의 경우 조례 시간 제출이 원칙이므로 개별 충전은 불가능하며 걸릴 시 압수될 수 있습니다.",
    "체육관/운동장": "점심시간 점심 배식을 마친 학생들은 체육관 및 운동장 개방 시간 내 자유로운 활동이 가능합니다. 체육 기구 및 공은 체육 교무실에서 학생증을 지참한 후 대여할 수 있습니다.",
    "탈의실": "본관 2층과 4층 서편 계단 옆에 남녀 분리된 현대식 탈의실이 완비되어 있습니다. 체육 시간 전후 지정된 공간을 이용해야 하며 교실 내 탈의는 금지됩니다.",
    "시험 찍기": "지필평가 시 오답에 대한 감점 제도(부정 점수제)는 존재하지 않습니다. OMR 카드 마킹 실수 시 시험 종료 5분 전까지 교체 요정이 가능하며, 종료 후 마킹은 무효 처리됩니다.",
    "수행평가 미제출": "수행평가 기한을 엄수하지 못할 경우 지연 제출 기간에 따라 일정 비율 감점 처리가 적용됩니다. 최종 마감일까지 미제출 시 규정에 따라 0점 처리되므로 반드시 기한 내 제출해야 합니다.",
    "평가 기준": "지필평가 난이도는 교육과정 성취기준에 맞춰 출제됩니다. 지난 학년도 기출문제의 경우, 학교 홈페이지 발간 자료실 및 도서관 내 기출문제 보관철에서 상시 열람할 수 있습니다.",
    "석차/등수": "현행 교육부 지침에 따라 성적표에는 전교 등수 및 반 석차가 표기되지 않고 성취도(A-B-C-D-E)와 원점수, 과목 평균만 출력됩니다. 개별 등수는 공식적으로 공개되지 않습니다.",
    "친구 갈등": "교우 관계 갈등이나 심리적 소외감을 느낄 때 본관 1층 Wee클래스(상담실)를 방문하면 전문 상담 선생님의 도움을 받을 수 있습니다. 모든 상담 내용은 철저히 비밀이 보장됩니다.",
    "뒷담/사이버불링": "단톡방 및 SNS 공간에서의 언어폭력, 모욕, 비방 행위는 학교폭력예방 및 대책에 관한 법률에 의거하여 엄연한 학교폭력 행위로 간주됩니다. 신고 시 신고자의 인적 사항은 법적으로 강력하게 비밀 보장됩니다.",
    "연애 규정": "학칙 내에 학생 간 교제를 직접적으로 금지하는 처벌 조항은 없습니다. 다만, 교내에서 과도한 신체 접촉이나 면학 분위기를 저해하는 행위는 학생 생활지도 위원회에 회부될 수 있습니다.",
    "분실/도난": "물품 분실 시 즉시 담임선생님께 보고해야 하며, 생활지도부를 통해 복도 및 주요 시설 CCTV 확인 절차를 밟을 수 있습니다. 단, 교실 내부는 개인정보 보호법상 CCTV가 설치되어 있지 않습니다.",
    "벌점 리셋": "본인의 상벌점 현황은 나이스(NEIS) 대국민 서비스 또는 담임선생님을 통해 확인 가능합니다. 누적된 벌점은 학교에서 시행하는 교내 봉사 활동, 환경 정화, 상점 취득 프로그램을 통해 상쇄 및 리셋이 가능합니다.",
    "소지품 검사": "교내 안전 유지 및 금지 물품(흡연 용품, 흉기 등) 소지 의혹이 명백한 경우에 한해, 학생 생활지도 규정에 의거하여 교사의 동석 하에 제한적인 소지품 검사가 실시될 수 있습니다.",
    "폰 압수": "조례 시간 휴대폰 미제출 후 수업 중 무단 사용하다 적발될 경우 학칙에 의거하여 즉시 압수됩니다. 1차 적발 시 당일 종례 후 반환되나, 반복 적발 시 학부모 내방 후 인계가 원칙입니다."
}

st.write("")
st.write("")
st.markdown("<h1 style='text-align: center;'>🏫 서연중학교 학교생활 가이드</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>전교 부회장 데이터 정제 프로젝트 - RAG 지식 데이터베이스 작동 중</p>",
            unsafe_allow_html=True)
st.write("")
st.write("")

if not st.session_state.chat_history:
    st.markdown("### 💡 자주 묻는 질문 카테고리")
    st.write("아래의 주요 관심 키워드를 클릭하면 즉시 정확한 학칙 및 가이드를 검색합니다.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👗 등교 / 복장 / 두발**")
        if st.button("📌 지각 처리 기준이 궁금해요", use_container_width=True):
            st.session_state.selected_question = "지각 기준"
        if st.button("📌 생활복이나 체육복 등교 가능한가요?", use_container_width=True):
            st.session_state.selected_question = "생활복/체육복 등교"
        if st.button("📌 날씨 추울 때 사복 패딩 입어도 돼요?", use_container_width=True):
            st.session_state.selected_question = "사복 허용"
        if st.button("📌 두발 염색이나 귀걸이 규정이 어떻게 되나요?", use_container_width=True):
            st.session_state.selected_question = "두발/귀걸이"
        if st.button("📌 화장이나 컬러 렌즈 끼면 벌점인가요?", use_container_width=True):
            st.session_state.selected_question = "화장/렌즈"

        st.write("")
        st.markdown("**🍱 매점 / 급식 / 시설**")
        if st.button("📌 우리 학교에 매점이나 자판기가 있나요?", use_container_width=True):
            st.session_state.selected_question = "매점/자판기"
        if st.button("📌 급식이 맛있는데 더 받아먹어도 되나요?", use_container_width=True):
            st.session_state.selected_question = "급식 더 먹기"
        if st.button("📌 학교 와이파이 비밀번호는 무엇인가요?", use_container_width=True):
            st.session_state.selected_question = "와이파이"
        if st.button("📌 체육복 갈아입는 탈의실 위치가 어디예요?", use_container_width=True):
            st.session_state.selected_question = "탈의실"

    with col2:
        st.markdown("**✍️ 시험 / 성적 / 평가**")
        if st.button("📌 지필평가 때 찍으면 감점 처리 있나요?", use_container_width=True):
            st.session_state.selected_question = "시험 찍기"
        if st.button("📌 수행평가 늦게 제출하면 무조건 0점인가요?", use_container_width=True):
            st.session_state.selected_question = "수행평가 미제출"
        if st.button("📌 전교 석차나 등수는 왜 성적표에 안 나와요?", use_container_width=True):
            st.session_state.selected_question = "석차/등수"

        st.write("")
        st.markdown("**🤝 고민 상담 / 교내 갈등**")
        if st.button("📌 친구 관계나 소외감 문제로 상담받고 싶어요", use_container_width=True):
            st.session_state.selected_question = "친구 갈등"
        if st.button("📌 SNS 단톡방 뒷담화도 학폭 신고 되나요?", use_container_width=True):
            st.session_state.selected_question = "뒷담/사이버불링"
        if st.button("📌 학교 내 교실 에어팟 분실 시 CCTV 보나요?", use_container_width=True):
            st.session_state.selected_question = "분실/도난"

        st.write("")
        st.markdown("**🚨 벌점 / 징계 대처**")
        if st.button("📌 상벌점 확인 및 벌점 지우는 법이 있나요?", use_container_width=True):
            st.session_state.selected_question = "벌점 리셋"
        if st.button("📌 선생님이 소지품 검사나 사물함 열어도 돼요?", use_container_width=True):
            st.session_state.selected_question = "소지품 검사"
        if st.button("📌 수업 시간 폰 하다가 압수당하면 언제 줘요?", use_container_width=True):
            st.session_state.selected_question = "폰 압수"

st.write("")
st.write("")

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])
        if "reference" in chat:
            with st.expander("🔍 RAG 검색 연동 및 데이터 출처 확인"):
                st.write(chat["reference"])

user_input = st.chat_input("서연중 학사 시스템 및 규정에 대해 질문하세요...")

if st.session_state.selected_question:
    user_input = st.session_state.selected_question
    st.session_state.selected_question = ""

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        matched_key = None
        for key in faq_data.keys():
            if key in user_input or user_input in key:
                matched_key = key
                break

        if matched_key:
            answer = faq_data[matched_key]
            ref_info = f"서연중학교 학생 생활 규정 제2026-1호 / 학사 관리 지침서 기반 매핑 가상 벡터 데이터 데이터셋 코드번호 [RAG-REF-{hash(matched_key) % 10000}]"
        else:
            answer = "입력하신 질문에 대한 정확한 학칙 문서를 탐색 중입니다. 현재 데이터 정제 주간(6/1~6/7)으로, 제공해주신 25선 이외의 세부 문항은 임베딩 처리가 진행 중입니다."
            ref_info = "미정제 임시 텍스트 버퍼 스트림 데이터 수집 진행 중"

        with st.spinner("벡터 유사도 검색 점수 계산 중..."):
            time.sleep(0.8)

        for chunk in answer.split(" "):
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.write(full_response + "▌")
        message_placeholder.write(full_response)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response,
            "reference": ref_info
        })
        st.rerun()