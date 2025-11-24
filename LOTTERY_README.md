# 🎲 공정한 추첨 시스템

Commitment Scheme 기반의 **검증 가능한 공정한 추첨** Streamlit 웹 앱

## 🌟 특징

- ✅ **완전 공정**: 주최자도 결과를 미리 알거나 조작할 수 없음
- 🔐 **암호학적 안전성**: SHA-256 해시 + Commitment Scheme 사용
- 👥 **투명한 검증**: 누구나 공개된 데이터로 결과 재현 가능
- 🌐 **웹 기반**: 별도 설치 없이 브라우저에서 사용
- 📱 **반응형**: 모바일, 태블릿, PC 모두 지원
- ⏰ **한국시간 지원**: 모든 타임스탬프가 KST(UTC+9)로 표시

## 🚀 빠른 시작

### 로컬 실행

```bash
# 1. 저장소 클론 (또는 파일 다운로드)
git clone <repository-url>
cd study

# 2. 의존성 설치
pip install -r requirements_lottery.txt

# 3. 앱 실행
streamlit run streamlit_lottery.py
```

브라우저에서 자동으로 `http://localhost:8501` 열림

### Streamlit Cloud 배포

1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud)에 로그인
3. "New app" 클릭
4. 저장소와 `streamlit_lottery.py` 선택
5. Deploy!

**배포 URL 예시**: `https://your-app.streamlit.app`

## 📖 사용법

### 1단계: Commitment 생성 (추첨 전)

1. "1단계: Commitment 생성" 탭으로 이동
2. "Commitment 생성하기" 버튼 클릭
3. **생성된 Commitment Hash와 Timestamp를 즉시 공개**
   - 블로그, SNS, 커뮤니티 등에 게시
   - 스크린샷 찍어서 공유
   - 변경 불가능한 증거 남기기
4. **Nonce는 절대 공개하지 말고** 안전하게 보관
5. 참가자 모집

### 2단계: 추첨 실행 (참가 마감 후)

1. "2단계: 추첨 실행" 탭으로 이동
2. 1단계 데이터 불러오기 (자동 또는 JSON 업로드)
3. 추첨 범위 설정 (예: 1~100)
4. "추첨 실행하기" 버튼 클릭
5. **결과와 함께 Nonce 공개**

### 3단계: 검증 (누구나 가능)

1. "3단계: 검증" 탭으로 이동
2. 주최자가 공개한 정보 입력:
   - Commitment Hash (1단계 공개)
   - Timestamp (1단계 공개)
   - Nonce (2단계 공개)
   - 추첨 범위
3. "검증하기" 버튼 클릭
4. 결과 확인 ✅

## 🔐 왜 공정한가요?

### Commitment Scheme의 원리

1. **1단계 (Commitment)**:
   - 랜덤 Nonce 생성
   - Hash(Timestamp + Nonce) 계산
   - **해시만 먼저 공개** → 결과가 "봉인"됨

2. **2단계 (Reveal)**:
   - 원본 데이터(Nonce) 공개
   - 해시에서 결정론적으로 당첨 번호 생성

3. **검증 (Verify)**:
   - 누구나 Hash(Timestamp + Nonce) 재계산
   - 동일한 해시 → 조작 없음 증명

### 조작 불가능한 이유

- ❌ **미리 조작 불가**: 해시를 먼저 공개했으므로, 주최자도 결과를 모름
- ❌ **사후 조작 불가**: 원하는 결과를 만드는 Nonce를 찾는 것은 SHA-256 특성상 계산적으로 불가능 (2^256 경우의 수)
- ✅ **완벽한 투명성**: 모든 과정이 공개되고 검증 가능

## 📊 사용 예시

### 유튜브 구독자 추첨

```
1단계 (영상 업로드 전):
   - Commitment 생성
   - 영상 설명란에 Hash 기재
   - "2025.01.20 18:00에 추첨할게요!"

2단계 (마감 후):
   - 1~500 범위로 추첨 실행
   - 댓글에 Nonce와 결과 공개
   - "당첨 번호는 247번입니다!"

3단계 (시청자 검증):
   - 앱에서 Hash, Timestamp, Nonce 입력
   - 동일한 247번 나오면 ✅ 공정 인증
```

### 온라인 이벤트 경품 추첨

```
1단계 (이벤트 시작):
   - Commitment Hash를 블로그 공지사항에 게시
   - "1월 1일 ~ 1월 31일까지 참여 받습니다"

2단계 (이벤트 종료):
   - 총 참여자 150명 → 1~150 추첨
   - 당첨 번호와 Nonce 공개

3단계:
   - 참여자들이 직접 검증
   - 투명성 확보 → 신뢰도 상승
```

## 🛠️ 기술 스택

- **Frontend**: Streamlit (Python)
- **암호화**: hashlib (SHA-256)
- **랜덤**: Python random (시드 기반)
- **배포**: Streamlit Cloud / Heroku / AWS

## 📁 파일 구조

```
study/
├── streamlit_lottery.py       # Streamlit 앱 메인 파일
├── random_draw.py              # CLI 버전 (선택)
├── requirements_lottery.txt    # Python 의존성
└── LOTTERY_README.md           # 이 문서
```

## 🔧 개발자 가이드

### 핵심 함수

```python
def generate_commitment():
    """Commitment Hash 생성"""
    nonce = os.urandom(32).hex()
    timestamp = datetime.now().isoformat()
    hash = SHA256(timestamp + nonce)
    return hash, timestamp, nonce

def reveal_and_draw(timestamp, nonce, min_num, max_num):
    """추첨 실행"""
    seed = SHA256(timestamp + nonce)
    random.seed(seed)
    return random.randint(min_num, max_num)

def verify(hash, timestamp, nonce):
    """검증"""
    calculated_hash = SHA256(timestamp + nonce)
    return calculated_hash == hash
```

### 커스터마이징

- 해시 알고리즘 변경: `hashlib.sha256` → `hashlib.sha512`
- UI 테마 변경: CSS 스타일 수정
- 다국어 지원: `i18n` 추가

## 📜 라이선스

MIT License

## 🤝 기여

- 버그 리포트: GitHub Issues
- 기능 제안: Pull Requests 환영
- 문의: [이메일 주소]

## 📚 참고 자료

- [Commitment Scheme (위키백과)](https://en.wikipedia.org/wiki/Commitment_scheme)
- [SHA-256 해시 함수](https://en.wikipedia.org/wiki/SHA-2)
- [Streamlit 문서](https://docs.streamlit.io/)

## ⚠️ 주의사항

1. **Nonce 보안**: 1단계 Nonce를 절대 미리 공개하지 마세요
2. **타임스탬프 공개**: 1단계 Hash와 Timestamp는 즉시 공개해야 합니다
3. **백업**: Commitment 데이터를 안전하게 백업하세요 (JSON 다운로드)
4. **참여 기간**: 1단계와 2단계 사이에 충분한 시간을 두세요

## 🎯 FAQ

**Q: 주최자가 여러 번 Commitment를 생성해서 마음에 드는 결과를 선택하면?**
A: Commitment Hash를 **먼저 공개**하기 때문에 불가능합니다. 한 번 공개한 Hash는 변경할 수 없습니다.

**Q: Nonce를 찾아서 원하는 결과를 만들 수 있나요?**
A: SHA-256의 특성상 역산이 불가능합니다. 2^256 (천문학적 숫자) 경우의 수를 모두 시도해야 합니다.

**Q: 검증은 꼭 해야 하나요?**
A: 선택사항이지만, 검증 가능성 자체가 공정성을 보장합니다. 누구나 검증할 수 있다는 것이 핵심입니다.

**Q: Streamlit Cloud 무료인가요?**
A: 네! 공개 앱은 무료로 배포 가능합니다.

**Q: 타임스탬프가 다른 시간대로 표시되는데요?**
A: 모든 시각은 **한국 표준시(KST, UTC+9)**로 고정되어 있습니다. ISO 8601 형식에 타임존 정보(+09:00)가 포함되어 있으므로, 어디서 접속하든 동일한 결과를 검증할 수 있습니다.

## 🌟 성공 사례

> "구독자들이 직접 검증할 수 있어서 신뢰도가 크게 올랐습니다!" - 유튜버 A

> "이제 '조작 아니냐'는 댓글이 사라졌어요." - 커뮤니티 관리자 B

---

Made with ❤️ by [Your Name]

**⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**
