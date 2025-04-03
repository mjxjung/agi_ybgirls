# crop_parsing/loader.py
import json

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n✅ 총 {len(data)}개 항목 로드 완료!")
    return data