import base64
import json
from openai import OpenAI
from api.info_extract.schema_extract import generate_upstage_response_format
import os
import json
from dotenv import load_dotenv
load_dotenv()

UPSTAGE_API_KEY=os.getenv("API_KEY")
FILE_PATH="../../pdf_samples/구강_구강건조증.pdf"
MIME_TYPE="application/pdf"

SCHEMA1 = generate_upstage_response_format(FILE_PATH) # 일부 schema 말고 전부 못 쓰나?

client = OpenAI(
    base_url="https://api.upstage.ai/v1/information-extraction",
    api_key=UPSTAGE_API_KEY
)

# Read file
def encode_to_base64(file_path):
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
        base64_encoded = base64.b64encode(file_bytes).decode('utf-8')
        return base64_encoded

base64_encoded = encode_to_base64(FILE_PATH)

# Information Extraction
extraction_response = client.chat.completions.create(
    model="information-extract",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{MIME_TYPE};base64,{base64_encoded}"},
                },
            ],
        }
    ],
    response_format=SCHEMA1
)

# print(json.loads(extraction_response.choices[0].message.content))

if __name__=="__main__":
  # print(json.loads(extraction_response.choices[0].message.content))

  # 예시: extraction_response.choices[0].message.content가 JSON 문자열이라고 가정
  json_content = extraction_response.choices[0].message.content

  # JSON 문자열을 파싱
  parsed_json = json.loads(json_content)

  # 보기 좋게 정렬된 문자열로 변환 (indent를 통해 예쁘게 저장)
  formatted_json = json.dumps(parsed_json, indent=4, ensure_ascii=False)

  # .txt 파일로 저장
  with open("information_extract_test.txt", "w", encoding="utf-8") as f:
      f.write(formatted_json)

  print("information_extract_test.txt에 저장되었습니다.")
      


# ... 위와 동일한 코드 ...

    
