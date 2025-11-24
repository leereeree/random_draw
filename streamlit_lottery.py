"""
공정한 추첨 시스템 (Commitment Scheme)
- Streamlit 웹 앱
"""

import streamlit as st
import random
import hashlib
import json
from datetime import datetime, timezone, timedelta

# 페이지 설정
st.set_page_config(
    page_title="공정한 추첨 시스템",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #667eea;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1em;
        margin: 1em 0;
        border-radius: 5px;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1em;
        margin: 1em 0;
        border-radius: 5px;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1em;
        margin: 1em 0;
        border-radius: 5px;
    }
    .hash-display {
        background: #f1f3f5;
        padding: 1em;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        word-break: break-all;
        margin: 1em 0;
    }
    .result-number {
        text-align: center;
        font-size: 5em;
        font-weight: bold;
        color: #667eea;
        margin: 0.5em 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 한국 타임존 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

# 세션 상태 초기화
if 'commitment_data' not in st.session_state:
    st.session_state.commitment_data = None
if 'reveal_data' not in st.session_state:
    st.session_state.reveal_data = None


def generate_commitment():
    """Commitment 생성"""
    import os

    # 한국 시간으로 현재 시간 생성
    draw_time = datetime.now(KST)
    nonce = os.urandom(32).hex()

    # Commitment 데이터
    commitment_data = {
        "timestamp": draw_time.isoformat(),
        "nonce": nonce
    }

    # 해시 계산
    data_string = json.dumps(commitment_data, sort_keys=True)
    commitment_hash = hashlib.sha256(data_string.encode()).hexdigest()

    return commitment_hash, commitment_data


def reveal_and_draw(commitment_data, min_num, max_num):
    """추첨 실행"""
    # 해시 재계산
    data_string = json.dumps(commitment_data, sort_keys=True)
    commitment_hash = hashlib.sha256(data_string.encode()).hexdigest()

    # 시드 생성
    timestamp_str = commitment_data["timestamp"]
    nonce = commitment_data["nonce"]
    seed_string = timestamp_str + nonce
    seed_value = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16) % (2**32)

    # 랜덤 추첨
    random.seed(seed_value)
    result = random.randint(min_num, max_num)

    reveal_data = {
        "commitment_hash": commitment_hash,
        "timestamp": timestamp_str,
        "nonce": nonce,
        "seed_value": seed_value,
        "min_num": min_num,
        "max_num": max_num,
        "result": result
    }

    return reveal_data


def verify_drawing(commitment_hash, timestamp, nonce, min_num, max_num):
    """검증"""
    # 해시 재계산
    commitment_data = {
        "timestamp": timestamp,
        "nonce": nonce
    }
    data_string = json.dumps(commitment_data, sort_keys=True)
    calculated_hash = hashlib.sha256(data_string.encode()).hexdigest()

    # 해시 검증
    if calculated_hash != commitment_hash:
        return False, None, calculated_hash

    # 추첨 결과 재현
    seed_string = timestamp + nonce
    seed_value = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed_value)
    result = random.randint(min_num, max_num)

    return True, result, calculated_hash


# ========== 메인 앱 ==========

st.markdown('<div class="main-header">🎲 공정한 추첨 시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Commitment Scheme 기반 검증 가능한 추첨</div>', unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["📖 사용법", "🔒 1단계: Commitment 생성", "🎲 2단계: 추첨 실행", "✅ 3단계: 검증"])

# ========== Tab 1: 사용법 ==========
with tab1:
    st.markdown("""
    <div class="info-box">
        <h3>🎯 이 시스템의 목적</h3>
        <p>
        추첨 주최자가 미리 결과를 조작할 수 없도록 보장하는 <strong>공정한 추첨 시스템</strong>입니다.
        <br>Commitment Scheme을 사용하여 추첨 전에 결과를 "봉인"하고, 추첨 후 검증할 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 추첨 진행 순서")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 1️⃣ Commitment 생성
        - 추첨 **전**에 실행
        - Commitment Hash를 생성
        - **이 해시를 먼저 공개**
        - 원본 데이터는 **비밀로 보관**
        """)

    with col2:
        st.markdown("""
        #### 2️⃣ 추첨 실행
        - 참가자 모집 완료 후 실행
        - 추첨 범위 설정 (예: 1~100)
        - 당첨 번호 추첨
        - **원본 데이터(Nonce) 공개**
        """)

    with col3:
        st.markdown("""
        #### 3️⃣ 검증
        - **누구나** 검증 가능
        - 공개된 Hash, Timestamp, Nonce 입력
        - 동일한 결과가 나오는지 확인
        - ✅ 조작 불가능 증명
        """)

    st.markdown("---")

    st.markdown("""
    <div class="warning-box">
        <h3>⚠️ 중요 주의사항</h3>
        <ul>
            <li><strong>1단계에서 생성된 Commitment Hash와 Timestamp를 반드시 먼저 공개하세요!</strong></li>
            <li>Nonce는 2단계(추첨 실행) 전까지 절대 공개하면 안됩니다.</li>
            <li>공개 방법: 블로그, SNS, 스크린샷 등 변경 불가능한 증거 남기기</li>
            <li>1단계와 2단계 사이에는 충분한 시간을 두고 참가자를 모집하세요.</li>
            <li><strong>⏰ 모든 시각은 한국 표준시(KST, UTC+9)로 표시됩니다.</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔐 왜 공정한가요?")

    st.markdown("""
    1. **미리 결과 조작 불가**: Commitment Hash를 먼저 공개하므로, 주최자는 이미 결과가 "봉인"됨
    2. **사후 조작 불가**: Hash는 일방향 함수이므로, 원하는 결과를 만드는 Nonce를 찾는 것은 거의 불가능
    3. **투명한 검증**: 누구나 공개된 데이터로 동일한 결과를 재현할 수 있음
    4. **암호학적 안전성**: SHA-256 해시 알고리즘 사용
    """)


# ========== Tab 2: Commitment 생성 ==========
with tab2:
    st.markdown("## 🔒 1단계: Commitment 생성")

    st.markdown("""
    <div class="info-box">
        <h3>📌 이 단계에서 할 일</h3>
        <p>
        1. 아래 버튼을 클릭하여 Commitment Hash를 생성합니다.<br>
        2. 생성된 <strong>Commitment Hash와 Timestamp를 즉시 공개</strong>합니다 (블로그, SNS 등).<br>
        3. Nonce는 <strong>절대 공개하지 말고</strong> 안전하게 보관합니다.<br>
        4. 참가자를 모집합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🎲 Commitment 생성하기", key="gen_commit", use_container_width=True):
            commitment_hash, commitment_data = generate_commitment()
            st.session_state.commitment_data = commitment_data
            st.session_state.commitment_hash = commitment_hash
            st.rerun()

    if st.session_state.commitment_data:
        st.markdown("---")
        st.markdown("### ✅ Commitment 생성 완료!")

        st.markdown("""
        <div class="success-box">
            <h3>🔓 먼저 공개할 정보 (지금 바로 공개하세요!)</h3>
        </div>
        """, unsafe_allow_html=True)

        # Commitment Hash
        st.markdown("**📌 Commitment Hash:**")
        st.code(st.session_state.commitment_hash, language=None)

        # Timestamp
        timestamp = st.session_state.commitment_data['timestamp']
        draw_time = datetime.fromisoformat(timestamp)
        st.markdown("**⏰ 생성 시각 (한국시간 KST):**")
        st.code(f"{draw_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')} KST (한국시간)", language=None)
        st.code(f"ISO 8601 (타임존 포함): {timestamp}", language=None)

        # 타임존 정보 추가 설명
        st.info("💡 생성된 시각은 한국 표준시(KST, UTC+9)입니다. ISO 8601 형식에 타임존(+09:00)이 포함되어 있습니다.")

        st.markdown("---")

        st.markdown("""
        <div class="warning-box">
            <h3>🔒 비밀로 보관할 정보 (지금은 공개하지 마세요!)</h3>
            <p>이 정보는 2단계(추첨 실행) 때까지 <strong>절대 공개하면 안됩니다</strong>.</p>
        </div>
        """, unsafe_allow_html=True)

        # Nonce (접기)
        with st.expander("⚠️ Nonce 보기 (주의: 아직 공개하지 마세요!)"):
            st.code(st.session_state.commitment_data['nonce'], language=None)
            st.markdown("**📝 이 값을 안전하게 복사해두세요. 추첨 실행 시 필요합니다.**")

        # 다운로드 버튼
        commitment_json = json.dumps(st.session_state.commitment_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="💾 Commitment 데이터 다운로드 (JSON)",
            data=commitment_json,
            file_name=f"commitment_{draw_time.strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


# ========== Tab 3: 추첨 실행 ==========
with tab3:
    st.markdown("## 🎲 2단계: 추첨 실행")

    st.markdown("""
    <div class="info-box">
        <h3>📌 이 단계에서 할 일</h3>
        <p>
        1. 1단계에서 생성한 Commitment 데이터를 불러옵니다.<br>
        2. 추첨 범위를 설정합니다 (예: 1 ~ 100).<br>
        3. 추첨을 실행합니다.<br>
        4. <strong>결과와 함께 Nonce를 공개</strong>합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Commitment 데이터 입력 방법 선택
    input_method = st.radio(
        "Commitment 데이터 입력 방법:",
        ["1단계에서 생성한 데이터 사용", "JSON 파일 업로드", "수동 입력"],
        horizontal=True
    )

    commitment_data_to_use = None

    if input_method == "1단계에서 생성한 데이터 사용":
        if st.session_state.commitment_data:
            commitment_data_to_use = st.session_state.commitment_data
            st.success("✅ 1단계에서 생성한 Commitment 데이터를 사용합니다.")
        else:
            st.warning("⚠️ 1단계에서 먼저 Commitment를 생성해주세요.")

    elif input_method == "JSON 파일 업로드":
        uploaded_file = st.file_uploader("Commitment JSON 파일 선택", type=['json'])
        if uploaded_file:
            commitment_data_to_use = json.load(uploaded_file)
            st.success("✅ JSON 파일을 불러왔습니다.")

    else:  # 수동 입력
        st.markdown("**Timestamp 입력:**")
        manual_timestamp = st.text_input("ISO 8601 형식 (예: 2025-01-15T10:30:00.123456)")
        st.markdown("**Nonce 입력:**")
        manual_nonce = st.text_area("64자리 Hex 문자열", height=100)

        if manual_timestamp and manual_nonce:
            commitment_data_to_use = {
                "timestamp": manual_timestamp,
                "nonce": manual_nonce.strip()
            }
            st.success("✅ 수동 입력 완료.")

    if commitment_data_to_use:
        st.markdown("---")
        st.markdown("### 🎯 추첨 범위 설정")

        col1, col2 = st.columns(2)
        with col1:
            min_num = st.number_input("최소값", min_value=1, value=1, step=1)
        with col2:
            max_num = st.number_input("최대값", min_value=min_num, value=100, step=1)

        st.info(f"📌 추첨 범위: **{min_num}** ~ **{max_num}** ({max_num - min_num + 1}명)")

        # 추첨 실행 버튼
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎲 추첨 실행하기", key="do_draw", use_container_width=True, type="primary"):
                reveal_data = reveal_and_draw(commitment_data_to_use, min_num, max_num)
                st.session_state.reveal_data = reveal_data
                st.rerun()

        if st.session_state.reveal_data:
            st.markdown("---")
            st.balloons()

            st.markdown("## 🎊 추첨 결과")

            # 당첨 번호 크게 표시
            st.markdown(f'<div class="result-number">{st.session_state.reveal_data["result"]}</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 1.5em; color: #666;'>추첨 범위: {st.session_state.reveal_data['min_num']} ~ {st.session_state.reveal_data['max_num']}</p>", unsafe_allow_html=True)

            st.markdown("---")

            st.markdown("""
            <div class="success-box">
                <h3>🔓 검증용 정보 공개</h3>
                <p>아래 정보를 모두 공개하여 누구나 검증할 수 있도록 하세요!</p>
            </div>
            """, unsafe_allow_html=True)

            # 검증용 정보
            st.markdown("**✅ Commitment Hash (1단계에서 공개한 값):**")
            st.code(st.session_state.reveal_data["commitment_hash"], language=None)

            st.markdown("**⏰ Timestamp (1단계에서 공개한 값, KST 한국시간):**")
            # 시간을 한국시간으로 파싱해서 보기 좋게 표시
            reveal_time = datetime.fromisoformat(st.session_state.reveal_data["timestamp"])
            st.code(f"{reveal_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')} KST", language=None)
            st.code(f"ISO 8601: {st.session_state.reveal_data['timestamp']}", language=None)

            st.markdown("**🔓 Nonce (지금 공개하는 값):**")
            st.code(st.session_state.reveal_data["nonce"], language=None)

            st.markdown("**📊 추첨 정보:**")
            st.json({
                "추첨 범위": f"{st.session_state.reveal_data['min_num']} ~ {st.session_state.reveal_data['max_num']}",
                "당첨 번호": st.session_state.reveal_data['result'],
                "시드 값": st.session_state.reveal_data['seed_value']
            })

            # 다운로드
            reveal_json = json.dumps(st.session_state.reveal_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 검증 데이터 다운로드 (JSON)",
                data=reveal_json,
                file_name=f"reveal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


# ========== Tab 4: 검증 ==========
with tab4:
    st.markdown("## ✅ 3단계: 검증")

    st.markdown("""
    <div class="info-box">
        <h3>📌 검증 방법</h3>
        <p>
        주최자가 공개한 정보를 입력하여 추첨 결과를 검증할 수 있습니다.<br>
        동일한 결과가 나온다면, 추첨이 공정하게 진행되었음을 증명합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 검증 데이터 입력 방법
    verify_method = st.radio(
        "검증 데이터 입력 방법:",
        ["2단계 결과 사용", "JSON 파일 업로드", "수동 입력"],
        horizontal=True,
        key="verify_method"
    )

    verify_data = None

    if verify_method == "2단계 결과 사용":
        if st.session_state.reveal_data:
            verify_data = st.session_state.reveal_data
            st.success("✅ 2단계 추첨 결과를 사용합니다.")
        else:
            st.warning("⚠️ 2단계에서 먼저 추첨을 실행해주세요.")

    elif verify_method == "JSON 파일 업로드":
        uploaded_verify = st.file_uploader("검증 JSON 파일 선택", type=['json'], key="verify_upload")
        if uploaded_verify:
            verify_data = json.load(uploaded_verify)
            st.success("✅ JSON 파일을 불러왔습니다.")

    else:  # 수동 입력
        st.markdown("**주최자가 공개한 정보를 입력하세요:**")

        verify_hash = st.text_input("Commitment Hash (1단계에서 먼저 공개된 값)")
        verify_timestamp = st.text_input("Timestamp (1단계에서 먼저 공개된 값)")
        verify_nonce = st.text_area("Nonce (2단계에서 공개된 값)", height=100, key="verify_nonce")

        col1, col2 = st.columns(2)
        with col1:
            verify_min = st.number_input("최소값", min_value=1, value=1, step=1, key="verify_min")
        with col2:
            verify_max = st.number_input("최대값", min_value=verify_min, value=100, step=1, key="verify_max")

        if verify_hash and verify_timestamp and verify_nonce:
            verify_data = {
                "commitment_hash": verify_hash.strip(),
                "timestamp": verify_timestamp.strip(),
                "nonce": verify_nonce.strip(),
                "min_num": verify_min,
                "max_num": verify_max
            }

    if verify_data:
        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ 검증하기", key="do_verify", use_container_width=True, type="primary"):
                success, result, calculated_hash = verify_drawing(
                    verify_data["commitment_hash"],
                    verify_data["timestamp"],
                    verify_data["nonce"],
                    verify_data["min_num"],
                    verify_data["max_num"]
                )

                st.markdown("---")

                if success:
                    st.success("### ✅ 검증 성공! 추첨이 공정하게 진행되었습니다.")
                    st.balloons()

                    st.markdown(f'<div class="result-number">{result}</div>', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 1.5em; color: #666;'>재현된 당첨 번호</p>", unsafe_allow_html=True)

                    st.markdown("---")

                    st.markdown("**🔍 검증 세부사항:**")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("공개된 Hash", "일치 ✅")
                        st.code(verify_data["commitment_hash"][:32] + "...", language=None)

                    with col2:
                        st.metric("계산된 Hash", "일치 ✅")
                        st.code(calculated_hash[:32] + "...", language=None)

                    st.markdown("**결론:**")
                    st.markdown("""
                    - 1단계에서 먼저 공개된 Commitment Hash가 원본 데이터와 일치합니다.
                    - 동일한 알고리즘으로 동일한 당첨 번호가 재현되었습니다.
                    - 주최자가 결과를 조작하지 않았음이 증명되었습니다.
                    """)

                else:
                    st.error("### ❌ 검증 실패! 해시값이 일치하지 않습니다.")

                    st.markdown("**🔍 검증 세부사항:**")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("공개된 Hash", "불일치 ❌", delta_color="off")
                        st.code(verify_data["commitment_hash"][:32] + "...", language=None)

                    with col2:
                        st.metric("계산된 Hash", "불일치 ❌", delta_color="off")
                        st.code(calculated_hash[:32] + "...", language=None)

                    st.markdown("**가능한 원인:**")
                    st.markdown("""
                    - 입력한 Timestamp 또는 Nonce가 잘못되었습니다.
                    - 주최자가 원본 데이터를 변조했을 가능성이 있습니다.
                    - 입력 값을 다시 확인해주세요.
                    """)


# 사이드바
with st.sidebar:
    st.markdown("### 📚 추가 정보")

    st.markdown("""
    **🔐 암호학 기술:**
    - SHA-256 해시 함수
    - Commitment Scheme
    - 암호학적 난수 생성

    **📖 참고 자료:**
    - [Commitment Scheme (위키백과)](https://en.wikipedia.org/wiki/Commitment_scheme)
    - [SHA-256 해시](https://en.wikipedia.org/wiki/SHA-2)

    **💡 사용 예시:**
    - 온라인 경품 추첨
    - 이벤트 당첨자 선정
    - 공정한 무작위 선택
    """)

    st.markdown("---")

    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        Made with ❤️ using Streamlit<br>
        © 2025 공정한 추첨 시스템
    </div>
    """, unsafe_allow_html=True)
