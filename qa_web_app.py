# 📋 게시판 상담 QA 평가 웹앱 (안정형: 평가 항목 축소 + 건수 제한 + timeout 설정)

import streamlit as st
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import io

# 🔐 환경 변수 불러오기
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🧾 웹앱 설정
st.set_page_config(page_title="게시판 QA 자동 평가기", page_icon="📝")
st.title("📋 게시판 QA 자동 평가기")

st.markdown("""
이 웹앱은 고객 질문과 상담사 답변을 기반으로 GPT 모델을 활용해 QA 평가를 자동으로 수행합니다.
- 단건 입력 또는 다건 업로드(CSV) 후 평가할 수 있습니다.
- ⚠ 다건 평가는 최대 10건까지만 평가됩니다.
""")

# 🔹 단건 입력 영역
st.subheader("✍ 단건 QA 평가")
customer = st.text_area("고객 질문을 입력하세요:", height=120)
agent = st.text_area("상담사 답변을 입력하세요:", height=150)

if st.button("🧠 단건 QA 평가 실행"):
    if not customer or not agent:
        st.warning("고객 질문과 상담사 답변을 모두 입력해주세요.")
    else:
        with st.spinner("GPT가 단건 평가 중입니다..."):
            prompt = f"""
너는 고객센터 QA 평가 전문가야.

[고객 질문]
{customer}

[상담사 답변]
{agent}

[평가 항목]
1. 문제 파악 – 고객 의도를 정확히 이해했는가?
2. 응답 정확도 – 정보 기준에 맞는 정확한 답변인가?
3. 공감 표현 – 정중하고 공감 어린 표현이 있었는가?
4. 해결책 제시 – 고객 문제 해결 방향을 제시했는가?
5. 전반적 인상 – 성의와 안정감이 느껴졌는가?

**각 항목에 대해 점수(10점 만점)와 간단한 코멘트를 테이블로 마크다운 형식으로 출력해줘.**
            """
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=800,
                    timeout=60
                )
                result = response.choices[0].message.content.strip()
                st.markdown("### 📝 단건 평가 결과")
                st.markdown(result)
            except Exception as e:
                st.error(f"❌ 평가 중 오류 발생: {e}")

# 🔹 다건 평가 영역 복원
st.subheader("📁 다건 QA 평가 (CSV 업로드, 최대 10건)")
uploaded_file = st.file_uploader("고객 질문/상담사 답변 CSV 파일 업로드", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if '고객질문' not in df.columns or '상담사답변' not in df.columns:
        st.error("CSV에는 반드시 '고객질문', '상담사답변' 컬럼이 있어야 합니다.")
    elif st.button("🧠 다건 평가 실행"):
        df = df.head(10)
        results = []
        from time import sleep
        progress_bar = st.progress(0, text="🔄 GPT 다건 평가 진행 중...")
        total = len(df)

        for i, (idx, row) in enumerate(df.iterrows()):
            prompt = f"""
너는 고객센터 QA 평가 전문가야.

아래 고객 질문과 상담사 답변을 바탕으로 아래 5가지 항목에 대해 점수(10점 만점)와 짧은 코멘트를 작성하고,
다음과 같은 **테이블 형식**으로 출력해줘:

형식:
| 항목 | 점수 | 결과 요약 |
|------|------|-------------|
| 1. 문제 파악 | 8점 | 고객의 요청은 이해했지만 회수 확인 방식은 빠졌음 |
...

마지막에는 총점도 따로 출력해줘.

[고객 질문]
{row['고객질문']}

[상담사 답변]
{row['상담사답변']}

[평가 항목]
1. 문제 파악 – 고객 의도를 정확히 이해했는가?
2. 응답 정확도 – 정보 기준에 맞는 정확한 답변인가?
3. 공감 표현 – 정중하고 공감 어린 표현이 있었는가?
4. 해결책 제시 – 고객 문제 해결 방향을 제시했는가?
5. 전반적 인상 – 성의와 안정감이 느껴졌는가?

**꼭 마크다운 테이블 형식으로 출력해줘.**
"""
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=800,
                    timeout=60
                )
                results.append(response.choices[0].message.content.strip())
                progress_bar.progress((i + 1) / total, text=f"✅ {i + 1}/{total} 건 완료")
            except Exception as e:
                results.append(f"❌ 에러 발생: {e}")
                progress_bar.progress((i + 1) / total, text=f"⚠ {i + 1}/{total} 건 오류")

        df["GPT평가결과"] = results
        st.success(f"총 {len(df)}건 평가 완료!")

        # 📊 통계 및 결과 구조화
        parsed_rows = []
        avg_scores = []
        for idx, result in enumerate(results):
            try:
                lines = result.split("\n")
                current_question = df.loc[idx, "고객질문"]
                current_answer = df.loc[idx, "상담사답변"]

                for line in lines:
                    if line.strip().startswith("|") and line.count("|") >= 4:
                        parts = [cell.strip() for cell in line.strip().split("|")[1:-1]]
                        if len(parts) == 3:
                            항목, 점수, 요약 = parts
                            parsed_rows.append({
                                "고객질문": current_question,
                                "상담사답변": current_answer,
                                "항목": 항목,
                                "점수": 점수,
                                "결과 요약": 요약
                            })
                    elif "총점" in line:
                        total = ''.join([c for c in line if c.isdigit()])
                        avg_scores.append(int(total))
                        parsed_rows.append({
                            "고객질문": current_question,
                            "상담사답변": current_answer,
                            "항목": "총점",
                            "점수": total + "점",
                            "결과 요약": ""
                        })
            except Exception as e:
                st.warning(f"⚠ 결과 파싱 오류: {e}")

        result_df = pd.DataFrame(parsed_rows)

        if avg_scores:
            avg = sum(avg_scores) / len(avg_scores)
            st.metric("📈 평균 총점", f"{avg:.1f}점")

        st.caption("⏱ 각 건 평가에는 약 5~10초 소요됩니다.")

        # 👉 전체 결과 테이블 시각화 제거됨

        csv_structured = result_df.to_csv(index=False).encode('utf-8-sig')
        csv_raw = df.to_csv(index=False).encode('utf-8-sig')

        st.download_button(
            label="⬇ 구조화된 평가 결과 다운로드 (테이블형)",
            data=csv_structured,
            file_name="qa_evaluation_structured.csv",
            mime="text/csv",
            key="structured_download"
        )
        st.download_button(
            label="⬇ GPT 전체 응답 포함 원본 다운로드",
            data=csv_raw,
            file_name="qa_evaluation_raw.csv",
            mime="text/csv",
            key="raw_download"
        )
        
