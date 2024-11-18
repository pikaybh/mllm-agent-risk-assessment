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

"""
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

"""
def json_to_md_table(data):
    num = "번호"
    precursor = "위험 요인"
    matrix = "위험 등급"
    todo = "위험 저감 대책"
    table = f"| {num} | {precursor} | {matrix} | {todo} |\n"
    table += "|------|-----------|------------|----------------|\n"

    for item in data:
        measures = item.get(todo, '').replace(" -", "<br/>•").replace("- ", "• ")
        if measures.startswith("<br/>"):
            measures = measures[5:]
        table += f"| {item.get(num, '')} | {item.get(precursor, '')} | {item.get(matrix, '')} | {measures} |\n"

    return table

"""
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
"""


'''
def raw_to_md_table_fixed(raw_text):
    """
    Parses risk data and ensures all multi-line sections are properly processed.
    Includes detailed debugging to verify the correctness of the process.

    Args:
        raw_text (str): Input raw text containing risk factors.

    Returns:
        tuple: Markdown table of the parsed data and debug log.
    """
    lines = raw_text.strip().splitlines()
    entries = []
    current_entry = {}
    measures_buffer = []  # Buffer for "위험 저감 대책"
    debug_log = []  # Debug log

    for line in lines:
        line = line.strip()
        debug_log.append(f"Processing line: {line}")

        if re.match(r"^\d+\.\s\*\*위험 요인\*\*:", line):
            # Finalize the current entry if exists
            if current_entry:
                if measures_buffer:
                    current_entry["risk_measures"] = " ".join(measures_buffer).strip()
                    debug_log.append(f"Merged measures into entry: {current_entry['risk_measures']}")
                    measures_buffer = []
                entries.append(current_entry)
                debug_log.append(f"Finalized entry: {current_entry}")
                current_entry = {}

            # Start a new entry
            match = re.match(r"^(?P<index>\d+)\.\s\*\*위험 요인\*\*:\s(?P<risk_factor>.*)", line)
            if match:
                current_entry["index"] = match.group("index")
                current_entry["risk_factor"] = match.group("risk_factor")
                debug_log.append(f"Started new entry: {current_entry}")

        elif "**위험 등급**:" in line:
            match = re.match(r"^\*\*위험 등급\*\*:\s(?P<risk_rating>\d+)", line)
            if match:
                current_entry["risk_rating"] = match.group("risk_rating")
                debug_log.append(f"Added 위험 등급: {current_entry['risk_rating']}")

        elif "**위험 저감 대책**:" in line:
            match = re.match(r"^\*\*위험 저감 대책\*\*:\s(?P<risk_measures>.*)", line)
            if match:
                measures_buffer = [match.group("risk_measures").strip()]
                debug_log.append(f"Started 위험 저감 대책 buffer: {measures_buffer}")

        elif measures_buffer:
            # Continuation of "위험 저감 대책"
            measures_buffer.append(line)
            debug_log.append(f"Appended to buffer: {measures_buffer}")

    # Finalize the last entry
    if current_entry:
        if measures_buffer:
            current_entry["risk_measures"] = " ".join(measures_buffer).strip()
            debug_log.append(f"Merged measures into last entry: {current_entry['risk_measures']}")
        entries.append(current_entry)
        debug_log.append(f"Finalized last entry: {current_entry}")

    # Markdown table header
    md_table = "| **순번** | **위험 요인** | **위험 등급** | **위험 저감 대책** |\n"
    md_table += "|----------|---------------|---------------|--------------------|\n"

    for entry in entries:
        risk_measures = entry.get("risk_measures", "").replace("\n", "<br>").strip()
        debug_log.append(f"Adding to table: Risk Measures - {risk_measures}")
        md_table += f"| {entry['index']} | {entry['risk_factor']} | {entry['risk_rating']} | {risk_measures} |\n"

    return md_table, debug_log
'''


def get_image_path(uploaded_file):
    if uploaded_file is None:
        return None
    # Save the uploaded file to a temporary path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(uploaded_file.read())
        return temp_file.name


def transform_to_json_format_debug_fixed(raw_text):
    """
    Transforms the raw text into a JSON format with consistent parsing.

    Args:
        raw_text (str): Input raw text in the given format.

    Returns:
        list: JSON-formatted data.
    """
    lines = raw_text.strip().splitlines()
    json_output = []
    current_entry = {}
    
    for line in lines:
        line = line.strip()
        
        # New entry for "위험 요인"
        if re.match(r"^\d+\.\s\*\*위험 요인\*\*:", line):
            if current_entry:
                json_output.append(current_entry)
                current_entry = {}
            match = re.match(r"^\d+\.\s\*\*위험 요인\*\*:\s(?P<factor>.+)", line)
            if match:
                current_entry["번호"] = len(json_output) + 1
                current_entry["위험 요인"] = match.group("factor").strip()

        # Parse "위험 등급"
        elif re.match(r"^\s*-?\s*\*\*위험 등급\*\*:", line):
            match = re.match(r"^\s*-?\s*\*\*위험 등급\*\*:\s*(?P<grade>\d+)", line)
            if match:
                current_entry["위험 등급"] = match.group("grade").strip()
        
        # Parse "위험 저감 대책"
        elif re.match(r"^\s*-?\s*\*\*위험 저감 대책\*\*:", line):
            match = re.match(r"^\s*-?\s*\*\*위험 저감 대책\*\*:\s*(?P<measures>.+)", line)
            if match:
                current_entry["위험 저감 대책"] = match.group("measures").strip()
            else:
                # If no new key, append to existing measures
                if "위험 저감 대책" in current_entry:
                    current_entry["위험 저감 대책"] += f" {line.strip()}"
                else:
                    current_entry["위험 저감 대책"] = line.strip()

    # Add the last entry
    if current_entry:
        json_output.append(current_entry)

    return json_output
    
    
    """
    Transforms the A-format risk data to JSON format with debugging.

    Args:
        raw_text (str): Input raw text in A format.

    Returns:
        list: JSON-formatted risk data with all values as strings.
    """
    lines = raw_text.strip().splitlines()
    json_output = []
    current_entry = {}
    index = None

    for line in lines:
        line = line.strip()

        # Detect a new risk factor entry
        if re.match(r"^\d+\.\s\*\*위험 요인\*\*:", line):
            if current_entry:
                # Add completed entry to the output
                json_output.append(current_entry)
                current_entry = {}

            # Extract risk factor and start a new entry
            match = re.match(r"^(?P<index>\d+)\.\s\*\*위험 요인\*\*:\s(?P<risk_factor>.*)", line)
            if match:
                index = match.group("index")
                current_entry = {
                    "번호": index,
                    "위험 요인": match.group("risk_factor").strip(),
                    "위험 저감 대책": ""
                }

        # Extract the risk level
        elif re.match(r"^\*\*위험 등급\*\*:", line):
            match = re.match(r"^\*\*위험 등급\*\*:\s(?P<risk_rating>\d+)", line)
            if match:
                current_entry["위험 등급"] = match.group("risk_rating").strip()

        # Extract or append the risk mitigation measures
        elif re.match(r"^\*\*위험 저감 대책\*\*:", line) or "위험 저감 대책" in current_entry:
            if re.match(r"^\*\*위험 저감 대책\*\*:", line):
                # Start a new risk mitigation section
                current_entry["위험 저감 대책"] = line.split("**위험 저감 대책**:")[1].strip()
            else:
                # Append to an existing mitigation section
                current_entry["위험 저감 대책"] += f" {line.strip()}"

    # Finalize the last entry
    if current_entry:
        json_output.append(current_entry)

    return json_output
