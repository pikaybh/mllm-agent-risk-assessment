# utils/functions.py
import re
import tempfile
from deprecated import deprecated

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


@deprecated(version='1.1.1', reason="Error prune.")
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


@deprecated(version='1.1.1', reason="No need MD. Need HTML for style.")
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


def json_to_html_table(data):
    """
    Converts a JSON-like list of dictionaries into an HTML table.

    Args:
        data (list): A list of dictionaries containing keys like "번호", "위험 요인", "위험 등급", and "위험 저감 대책".

    Returns:
        str: A string containing the HTML table.
    """
    num = "번호"
    precursor = "위험 요인"
    matrix = "위험 등급"
    todo = "위험 저감 대책"

    # Start the table
    html_table = """
    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
        <thead>
            <tr>
                <th style="border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #d8e4fc; color: #244180; width: 60px">번호</th>
                <th style="border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #d8e4fc; color: #244180; width: 120px"">위험 요인</th>
                <th style="border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #d8e4fc; color: #244180; width: 100px"">위험 등급</th>
                <th style="border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #d8e4fc; color: #244180;">위험 저감 대책</th>
            </tr>
        </thead>
        <tbody>
    """

    # Add table rows
    for item in data:
        measures = item.get(todo, '').replace(" -", "<br>•").replace("- ", "• ")
        if measures.startswith("<br>"):
            measures = measures[4:]  # Remove leading <br> if present
        html_table += f"""
            <tr>
                <td style="border: 1px solid #ccc; padding: 10px; text-align: center; background-color: #f5f5f5"><b>{item.get(num, '')}</b></td>
                <td style="border: 1px solid #ccc; padding: 10px; text-align: center;">{item.get(precursor, '')}</td>
                <td style="border: 1px solid #ccc; padding: 10px; text-align: center;">{item.get(matrix, '')}</td>
                <td style="border: 1px solid #ccc; padding: 10px; text-align: center;">{measures}</td>
            </tr>
        """

    # Close the table
    html_table += """
        </tbody>
    </table>
    """

    return html_table


@deprecated(version='1.1.1', reason="Error prune.")
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


@deprecated(version='1.1.1', reason="Error prune.")
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
    capturing_measures = False  # Flag to handle multi-line "위험 저감 대책"

    for line in lines:
        line = line.strip()

        # New entry for "위험 요인"
        if re.match(r"^\d+\.\s\*\*위험 요인\*\*:", line):
            if current_entry:
                json_output.append(current_entry)
                current_entry = {}
            capturing_measures = False
            match = re.match(r"^\d+\.\s\*\*위험 요인\*\*:\s(?P<factor>.+)", line)
            if match:
                current_entry["번호"] = len(json_output) + 1
                current_entry["위험 요인"] = match.group("factor").strip()

        # Parse "위험 등급"
        elif re.match(r"^\s*-?\s*\*\*위험 등급\*\*:", line):
            capturing_measures = False
            match = re.match(r"^\s*-?\s*\*\*위험 등급\*\*:\s*(?P<grade>\d+)", line)
            if match:
                current_entry["위험 등급"] = match.group("grade").strip()

        # Parse "위험 저감 대책"
        elif re.match(r"^\s*-?\s*\*\*위험 저감 대책\*\*:", line):
            capturing_measures = True
            match = re.match(r"^\s*-?\s*\*\*위험 저감 대책\*\*:\s*(?P<measures>.+)", line)
            if match:
                current_entry["위험 저감 대책"] = match.group("measures").strip()
            else:
                current_entry["위험 저감 대책"] = ""

        # Handle additional lines for "위험 저감 대책"
        elif capturing_measures:
            # Continue capturing measures for multi-line entries
            if "위험 저감 대책" in current_entry:
                current_entry["위험 저감 대책"] += f" {line.strip()}"
            else:
                current_entry["위험 저감 대책"] = line.strip()

    # Add the last entry
    if current_entry:
        json_output.append(current_entry)

    return json_output


def dict_to_markdown_table(data_dict: dict) -> str:
    # Markdown 표 형식으로 변환
    keys = list(data_dict.keys())
    values = list(data_dict.values())
    
    # Markdown 표 생성
    markdown = (
        f"\n| {' | '.join(keys)} |\n"
        f"|{'--|' * len(keys)}\n"
        f"| {' | '.join(values)} |\n"
    )

    return markdown


def get_tasks_into_chart(data: str) -> str:
    if ':' in data:
            # 콜론을 기준으로 키-값 쌍 생성
        key_value_pairs = [pair.strip() for pair in data.split(",")]
        result_dict = {}

        for pair in key_value_pairs:
            if ":" in pair:
                key, value = map(str.strip, pair.split(":", 1))
                result_dict[key] = value

        return dict_to_markdown_table(result_dict)

    else:
        return data