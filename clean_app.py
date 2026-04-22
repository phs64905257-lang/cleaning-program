import streamlit as st
import pandas as pd
import random
import time

# 페이지 설정
st.set_page_config(page_title="중1-2반 청소 배정기", page_icon="🧹")

st.info("🧹 **2026 스마트 학급 경영: 청소 배정 시스템**")

# 설명 문구 (사이드바 혹은 메인에 배치)
st.markdown("""
### ⚙️ 사용 가이드
1. **인원 설정**: 왼쪽 메뉴에서 현재 우리 반 총 인원을 입력하세요.
2. **구역 관리**: 구역명과 배정 인원을 자유롭게 **추가, 수정, 삭제**할 수 있습니다.
3. **무결성 확인**: 설정된 구역 인원의 합이 전체 학생 수와 일치해야 배정이 시작됩니다.
""")

# 1. 사이드바 - 설정 영역
with st.sidebar:
    st.header("⚙️ 설정")
    student_count = st.number_input("학급 전체 인원 수", min_value=1, value=25)
    
    st.subheader("📍 구역 및 인원 관리")
    # 기본 구역 설정
    default_sections = {
        "쓸기": 3, "닦기": 2, "나르기": 5, "쓰레기통": 2, 
        "복도쓸기": 1, "복도닦기": 1, "칠판 및 교탁": 1, 
        "컴퓨터/진로실": 4, "중앙현관": 6
    }
    
    # 구역 편집을 위한 데이터프레임
    section_df = pd.DataFrame(list(default_sections.items()), columns=["구역명", "인원"])
    edited_sections = st.data_editor(section_df, num_rows="dynamic")
    
    total_needed = edited_sections["인원"].sum()

# 2. 메인 화면 - 명단 업로드
st.subheader("1. 학생 명단 준비")
uploaded_file = st.file_uploader("1열 [이름] 컬럼이 포함된 엑셀/CSV 파일을 업로드하세요.", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    student_list = df["이름"].tolist()
    st.success(f"✅ {len(student_list)}명의 명단을 확인했습니다.")
else:
    student_list = [f"학생 {i+1}" for i in range(student_count)]
    st.warning("⚠️ 파일이 없어 임시 명단(학생 1, 2...)을 사용합니다.")

# 3. 배정 로직 및 애니메이션
st.subheader("2. 배정 실행")

# 무결성 체크
if total_needed != len(student_list):
    st.error(f"🚨 무결성 오류: 구역 인원 합({total_needed})과 학생 수({len(student_list)})가 일치해야 합니다!")
else:
    if st.button("🎰 슬롯머신 배정 시작!", type="primary"):
        with st.status("🎲 무작위 추첨 중...", expanded=True) as status:
            time.sleep(1)
            st.write("학생 명단 셔플 중...")
            random.shuffle(student_list)
            time.sleep(1)
            st.write("구역별 인원 배치 중...")
            
            # 배정 계산
            results = {}
            current_idx = 0
            for _, row in edited_sections.iterrows():
                sec_name = row["구역명"]
                sec_count = row["인원"]
                results[sec_name] = student_list[current_idx : current_idx + sec_count]
                current_idx += sec_count
            
            status.update(label="배정 완료!", state="complete", expanded=False)
        
        # 슬롯머신 효과(풍선)
        st.balloons()
        
        # 결과 표시
        st.success("🎉 배정이 완료되었습니다!")
        res_df_list = []
        for sec, names in results.items():
            st.markdown(f"**[{sec}]**: {', '.join(names)}")
            res_df_list.append({"구역": sec, "배정인원": ", ".join(names)})
        
        # 4. 저장 기능 (웹에서는 다운로드 방식)
        res_df = pd.DataFrame(res_df_list)
        
        st.divider()
        st.subheader("3. 결과 내보내기")
        
        # 엑셀 다운로드
        csv = res_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 엑셀(CSV) 다운로드", csv, "cleaning_result.csv", "text/csv")
        
        # 팁: 웹 브라우저의 '인쇄(Ctrl+P) -> PDF 저장'을 이용하면 가장 깔끔하게 PDF를 얻을 수 있습니다.
