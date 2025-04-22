# 📋 게시판 QA 자동 평가기

이 앱은 고객 질문과 상담사 답변을 기반으로 GPT 모델을 사용해 상담 품질을 평가하는 웹앱입니다.  
단건 입력 및 CSV 파일 업로드로 다건 평가도 가능합니다.

## 🚀 실행 방법

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run qa_web_app.py
```

### 배포 (Streamlit Cloud)

1. 이 저장소를 [Streamlit Cloud](https://streamlit.io/cloud)에 연결
2. App file path: `qa_web_app.py`
3. 환경 변수 설정 (`OPENAI_API_KEY`)

## 📁 CSV 파일 예시

| 고객질문         | 상담사답변                         |
|------------------|------------------------------------|
| 배송이 안 왔어요 | 금일 중 도착 예정입니다            |
