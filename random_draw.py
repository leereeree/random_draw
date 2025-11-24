# %%
import random
import hashlib
import json
import os
from datetime import datetime, timezone, timedelta

# 한국 타임존 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

#%%
def generate_commitment():
    """1단계: Commitment 생성 (추첨 전)"""

    # 한국 시간으로 현재 시간 생성
    draw_time = datetime.now(KST)
    nonce = os.urandom(32).hex()  # 256비트 랜덤 값

    # Commitment 데이터
    commitment_data = {
        "timestamp": draw_time.isoformat(),
        "nonce": nonce
    }

    # 해시 계산 (SHA-256)
    data_string = json.dumps(commitment_data, sort_keys=True)
    commitment_hash = hashlib.sha256(data_string.encode()).hexdigest()
    timestamp_str = commitment_data["timestamp"]

    # Commitment 저장
    with open('commitment.json', 'w') as f:
        json.dump(commitment_data, f, indent=2)

    print("=" * 70)
    print("🔒 1단계: COMMITMENT 생성 완료")
    print("=" * 70)
    print(f"\n생성 시간 (KST 한국시간): {draw_time.strftime('%Y년 %m월 %d일 %H:%M:%S')}")
    print(f"\n📌 Commitment Hash (먼저 공개할 값):")
    print(f"{commitment_hash}")
    print(f"\nTimestamp (먼저 공개할 값, KST 포함): {timestamp_str}")
    print("\n" + "=" * 70)
    print("⚠️  이 해시값과 타임스탬프를 먼저 공개하세요!")
    print("⚠️  추첨 후 원본 데이터를 공개하면 검증이 가능합니다.")
    print("💡 모든 시각은 한국 표준시(KST, UTC+9)입니다.")
    print("=" * 70)

    return commitment_hash

def reveal_and_draw(min_num=1, max_num=10):
    """2단계: 추첨 및 검증 (추첨 시)"""

    # Commitment 데이터 읽기
    try:
        with open('commitment.json', 'r') as f:
            commitment_data = json.load(f)
    except FileNotFoundError:
        print("❌ 에러: commitment.json 파일을 찾을 수 없습니다.")
        print("먼저 1단계(commitment 생성)를 실행하세요.")
        return

    # 해시 재계산으로 검증
    data_string = json.dumps(commitment_data, sort_keys=True)
    commitment_hash = hashlib.sha256(data_string.encode()).hexdigest()

    # 시드 생성 (timestamp + nonce)
    timestamp_str = commitment_data["timestamp"]
    nonce = commitment_data["nonce"]
    seed_string = timestamp_str + nonce
    seed_value = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16) % (2**32)

    # 랜덤 추첨
    random.seed(seed_value)
    result = random.randint(min_num, max_num)

    # 결과 출력
    print("=" * 70)
    print("🎲 2단계: 추첨 실행 및 공개")
    print("=" * 70)
    # print(f"\n추첨 일시: {timestamp_str}")
    print(f"\n✅ Commitment Hash (검증용):")
    print(f"  {commitment_hash}")
    print(f"✅ Timestamp (KST 한국시간): {timestamp_str}")
    print(f"\n🔓 원본 데이터 공개:")
    print(f"  - Nonce: {nonce}")
    print(f"\n📌 추첨 범위: {min_num} ~ {max_num}")
    print(f"\n🎯 당첨 번호: {result}")
    print("\n" + "=" * 70)
    print("✅ 누구나 위 원본 데이터로 동일한 해시값과 추첨 결과를 재현할 수 있습니다!")
    print("💡 모든 시각은 한국 표준시(KST, UTC+9)입니다.")
    print("=" * 70)

    # 검증용 정보 저장
    reveal_data = {
        "commitment_hash": commitment_hash,
        "timestamp": timestamp_str,
        "nonce": nonce,
        "seed_value": seed_value,
        "min_num": min_num,
        "max_num": max_num,
        "result": result
    }

    with open('reveal.json', 'w') as f:
        json.dump(reveal_data, f, indent=2)

    return result

def verify(commitment_hash, timestamp, nonce):
    """검증 함수: 제3자가 결과를 검증할 수 있음"""

    # 해시 재계산
    commitment_data = {
        "timestamp": timestamp,
        "nonce": nonce
    }
    data_string = json.dumps(commitment_data, sort_keys=True)
    calculated_hash = hashlib.sha256(data_string.encode()).hexdigest()

    # 해시 검증
    if calculated_hash != commitment_hash:
        print("❌ 검증 실패: 해시값이 일치하지 않습니다!")
        return False

    # reveal.json에서 추첨 범위 읽기 (있으면)
    min_num, max_num = 1, 10  # 기본값
    try:
        with open('reveal.json', 'r') as f:
            reveal_data = json.load(f)
            min_num = reveal_data.get('min_num', 1)
            max_num = reveal_data.get('max_num', 10)
    except FileNotFoundError:
        pass  # reveal.json 없으면 기본값 사용

    # 추첨 결과 재현
    seed_string = timestamp + nonce
    seed_value = int(hashlib.sha256(seed_string.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed_value)
    result = random.randint(min_num, max_num)

    print("=" * 70)
    print("✅ 검증 성공!")
    print("=" * 70)
    print(f"Commitment Hash: {commitment_hash}")
    print(f"계산된 Hash: {calculated_hash}")
    print(f"Timestamp (KST): {timestamp}")
    print(f"seed: {seed_value}")
    print(f"추첨 범위: {min_num} ~ {max_num}")
    print(f"추첨 결과: {result}")
    print("\n💡 타임스탬프는 한국 표준시(KST, UTC+9)입니다.")
    print("=" * 70)

    return True

# %%
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "commit":
            generate_commitment()
        elif sys.argv[1] == "reveal":
            # python random_draw.py reveal [min_num] [max_num]
            if len(sys.argv) >= 4:
                min_num = int(sys.argv[2])
                max_num = int(sys.argv[3])
                reveal_and_draw(min_num, max_num)
            elif len(sys.argv) == 2:
                # 기본값 사용
                reveal_and_draw()
            else:
                print("사용법: python random_draw.py reveal [min_num] [max_num]")
                print("예시: python random_draw.py reveal 1 9")
        elif sys.argv[1] == "verify":
            if len(sys.argv) != 5:
                print("사용법: python random_draw.py verify <commitment_hash> <timestamp> <nonce>")
            else:
                verify(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("사용법:")
        print("  1단계 (추첨 전): python random_draw.py commit")
        print("  2단계 (추첨): python random_draw.py reveal [min_num] [max_num]")
        print("  예시: python random_draw.py reveal 1 9")
        print("  검증: python random_draw.py verify <hash> <timestamp> <nonce>")
