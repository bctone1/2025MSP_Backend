from __future__ import annotations
import json, os
from pathlib import Path
from typing import Union
import requests
from dotenv import load_dotenv
load_dotenv(override=True)

class LayoutAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _upstage_layout_analysis(self, input_file: Union[str, Path]) -> str:
        """
        레이아웃 분석 API 호출
        input_file: 분석할 PDF 파일 경로
        생성된 JSON 파일 경로 문자열
        """
        input_path = Path(input_file)

        url = "https://api.upstage.ai/v1/document-ai/layout-analysis"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        data = {"ocr": "false"}  # 필요 시 "true" 로 변경

        with input_path.open("rb") as f:
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    data=data,
                    files={"document": f},
                    timeout=120,
                )
            except requests.RequestException as e:
                raise ValueError(f"Upstage layout API 요청 실패: {e}") from e

        if response.status_code != 200:
            snippet = (response.text or "")[:200]
            raise ValueError(f"예상치 못한 상태 코드: {response.status_code} | {snippet}")

        output_path = input_path.with_suffix(".json")
        with output_path.open("w", encoding="utf-8") as out:
            json.dump(response.json(), out, ensure_ascii=False, indent=2)

        return str(output_path)

    def analyze(self, input_file: Union[str, Path]) -> str:
        """Run Upstage layout analysis and return resulting JSON path."""
        return self._upstage_layout_analysis(input_file)

    def execute(self, input_file: Union[str, Path]) -> str:
        """Backward compatible wrapper around :meth:`analyze`."""
        return self.analyze(input_file)
