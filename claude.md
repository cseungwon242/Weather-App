# 프로젝트 개요
공공데이터 CSV를 표, 그래프, 지도로 보여주는 Streamlit 웹앱. 기획서는 PLAN.md 참고.

## 파일 구조
- .env : ANTHROPIC_API_KEY 보관
- ai_helper.py : Claude API를 사용하는 ask_ai() 함수 정의
- datalog.csv : 공공데이터 파일
- project10.py : 매인 앱 (UI + 로직)

## 규칙
- 항상 plan.md 기획서를 기준으로 구현할 것
- API 호출은 반드시 ask_ai() 함수를 거칠 것
- API Key는 .env에서 읽고 코드에 직접 쓰지 말 것
- 주석은 한국어로 작성
- datalog.csv를 utf-8로 먼저, 안 되면 cp949로 읽는다.