# utils/functions.py
import re
import tempfile

import json
from typing import Any, List
from PIL import Image, ExifTags


def get_args(**kwargs) -> List[Any]:
    return [item for sublist in kwargs.values() for item in sublist]


def is_streamlit_running() -> bool:
    """
    Check if the code is being executed in a Streamlit environment.

    Returns:
        bool: True if Streamlit is running, False otherwise.
    """
    try:
        import streamlit.runtime.scriptrunner
        return True
    except ImportError:
        return False


def extract_caption(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()  # Get EXIF metadata
        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                if tag_name == "ImageDescription":  # Look for ImageDescription tag
                    return value
        return None
    except Exception as e:
        return None


def parse_data(text: str):
    # 숫자. 으로 시작하는 항목 구분, **제목**: 내용을 구조적으로 파싱
    pattern = r"(?P<number>\d+)\.\s+\*\*(?P<section>.+?)\*\*:\s+(?P<content>.+?)(?=\n\d+\.\s+\*\*|$)"
    matches = re.finditer(pattern, text, re.DOTALL)

    results = []
    current_entry = {"번호": None, "위험 요소": None, "위험 등급": None, "위험 감소 조치": []}

    for match in matches:
        section = match.group("section").strip()
        content = match.group("content").strip()

        if section.isdigit():  # 새 항목 시작
            if current_entry["번호"]:  # 기존 항목 저장
                results.append(current_entry)
            # 새 항목 초기화
            current_entry = {"번호": int(section), "위험 요소": None, "위험 등급": None, "위험 감소 조치": []}
        elif section == "위험 요소":
            current_entry["위험 요소"] = content
        elif section == "위험 등급":
            current_entry["위험 등급"] = int(content)
        elif section == "위험 감소 조치":
            # 리스트로 추가
            measures = re.split(r"\n\s*-\s*", content)
            current_entry["위험 감소 조치"] = [measure.strip() for measure in measures if measure.strip()]

    if current_entry["번호"]:  # 마지막 항목 저장
        results.append(current_entry)

    return results


def json_to_md_table(data):
    table = "| 번호 | 위험 요소 | 위험 등급 | 위험 감소 조치 |\n"
    table += "|------|-----------|------------|----------------|\n"

    for item in data:
        measures = "<br>".join(item.get("위험 감소 조치", []))
        table += f"| {item.get('번호', '')} | {item.get('위험 요소', '')} | {item.get('위험 등급', '')} | {measures} |\n"

    return table


def parse2chart(text):
    # CrewOutput을 문자열로 변환
    if not isinstance(text, (str, bytes)):
        try:
            text = json.dumps(text, ensure_ascii=False)  # JSON으로 변환
        except TypeError:
            text = str(text)  # 일반 문자열로 변환
    
    # 데이터를 파싱하여 리스트 형태로 변환
    parsed_data = parse_data(text)
    
    # Markdown 표로 변환
    return json_to_md_table(parsed_data)


def get_image_path(uploaded_file):
    if uploaded_file is None:
        return None
    # Save the uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name
