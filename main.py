
import json
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

# 페이지 기본 설정
st.set_page_config(
    page_title="문학 작품 AI 분석기", page_icon="📚", layout="wide"
)

st.title("📚 AI 기반 문학 작품 분석 & 시각화 도구")
st.caption(
    "소설의 제목과 작가 이름을 입력하면 AI가 키워드, 인물 관계, 감정 선을 분석해 드립니다."
)

# 사이드바: API 키 입력
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.markdown(
        "[Google AI Studio](https://aistudio.google.com/)에서 무료 API 키를 발급받을 수 있습니다."
    )

# 메인 입력 폼
col1, col2 = st.columns(2)
with col1:
    title = st.text_input("소설 제목", placeholder="예: 날개")
with col2:
    author = st.text_input("작가 이름", placeholder="예: 이상")

btn_analyze = st.button("🚀 작품 분석 시작하기", use_container_width=True)

if btn_analyze:
    if not api_key:
        st.error("좌측 사이드바에 Gemini API Key를 입력해 주세요!")
    elif not title or not author:
        st.warning("소설 제목과 작가 이름을 모두 입력해 주세요.")
    else:
        with st.spinner("AI가 소설을 읽고 분석하는 중입니다... 🔍"):
            try:
                # Client 생성
                client = genai.Client(api_key=api_key)

                # 프롬프트 구성 (JSON 형태로 응답받기 위해 규격 지정)
                prompt = f"""
                다음 소설 작품을 깊이 있게 분석해서 반드시 지정된 JSON 형식으로만 응답해줘.
                
                작품 제목: {title}
                작가: {author}
                
                응답할 JSON 구조:
                {{
                    "summary": "작품의 핵심 주제 및 한 줄 요약",
                    "top_words": [
                        {{"word": "단어1", "count": 100}},
                        {{"word": "단어2", "count": 80}},
                        {{"word": "단어3", "count": 65}},
                        {{"word": "단어4", "count": 50}},
                        {{"word": "단어5", "count": 40}}
                    ],
                    "relationships": [
                        {{"person1": "인물A", "person2": "인물B", "relation": "갈등/조력 등 관계 설명"}}
                    ],
                    "emotions": [
                        {{"character": "인물A", "main_emotion": "주요 감정(예: 무기력, 불안)", "description": "감정 변화 및 배경 설명"}}
                    ]
                }}
                """

                # API 호출 (Gemini 2.5 Flash 모델 활용)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )

                # JSON 파싱
                data = json.loads(response.text)

                st.success("분석이 완료되었습니다! 🎉")
                st.divider()

                # 📌 0. 작품 요약
                st.subheader("📌 작품 한 줄 요약 및 핵심 주제")
                st.info(data.get("summary", "요약 정보가 없습니다."))

                # 📊 1. 가장 많이 등장한 단어 상위 5개
                st.subheader("📊 기능 1: 주요 핵심 키워드 Top 5")
                df_words = pd.DataFrame(data.get("top_words", []))
                if not df_words.empty:
                    col_chart, col_table = st.columns([2, 1])
                    with col_chart:
                        # 막대 그래프 시각화
                        st.bar_chart(
                            df_words.set_index("word")["count"],
                            color="#3182CE",
                        )
                    with col_table:
                        st.dataframe(df_words, use_container_width=True)

                st.divider()

                # 🤝 2. 등장인물들의 관계성
                st.subheader("🤝 기능 2: 등장인물 간 관계성")
                rel_list = data.get("relationships", [])
                if rel_list:
                    for rel in rel_list:
                        st.markdown(
                            f"- **{rel['person1']}** ↔ **{rel['person2']}**: {rel['relation']}"
                        )

                st.divider()

                # 🎭 3. 등장인물들의 감정 분석
                st.subheader("🎭 기능 3: 주요 등장인물 감정 분석")
                emo_list = data.get("emotions", [])
                if emo_list:
                    cols = st.columns(len(emo_list))
                    for idx, emo in enumerate(emo_list):
                        with cols[idx % len(cols)]:
                            st.metric(
                                label=emo["character"],
                                value=emo["main_emotion"],
                            )
                            st.caption(emo["description"])

            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
