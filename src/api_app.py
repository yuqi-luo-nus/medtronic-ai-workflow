import json
import os
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


app = FastAPI(
    title="Medical Device After-sales Workflow API",
    description="API for AI-assisted medical device support workflow",
    version="1.0.0"
)

# -----------------------------
# 路径设置
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_DIR = os.path.join(BASE_DIR, "data", "sample_inputs")
JSON_DIR = os.path.join(BASE_DIR, "outputs", "json")
EXCEL_DIR = os.path.join(BASE_DIR, "outputs", "excel")
PDF_DIR = os.path.join(BASE_DIR, "outputs", "pdf")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


# -----------------------------
# 请求数据模型
# -----------------------------
class CaseInput(BaseModel):
    case_id: str
    image_name: str
    device_type_hint: str
    observed_problem: str
    source: Optional[str] = "manual input"


# -----------------------------
# 模拟 AI 诊断
# -----------------------------
def ai_diagnose(case: dict) -> dict:
    observed_problem = case.get("observed_problem", "").lower()
    device_type = case.get("device_type_hint", "unknown")

    suspected_cause = "possible device enclosure issue"
    action_level = "medium"
    immediate_steps = [
        "Inspect device casing",
        "Check battery compartment",
        "Restart device and monitor warning"
    ]
    safety_warning = "For technician review only. Do not provide direct medical advice to patients."

    if "connection error" in observed_problem:
        suspected_cause = "possible cable disconnection or sensor interface issue"
        action_level = "medium"
        immediate_steps = [
            "Check all cable and sensor connections",
            "Verify interface ports are securely attached",
            "Restart monitor and re-check error message"
        ]
    elif "battery" in observed_problem:
        suspected_cause = "possible battery compartment closure issue"
        action_level = "low"
        immediate_steps = [
            "Inspect battery compartment closure",
            "Check battery installation",
            "Restart device after securing compartment"
        ]
    elif "warning icon" in observed_problem or "alarm" in observed_problem:
        suspected_cause = "possible device hardware warning"
        action_level = "high"
        immediate_steps = [
            "Stop device use until inspected",
            "Check visible damage or loose enclosure",
            "Escalate to technician if warning persists"
        ]

    result = {
        "case_id": case["case_id"],
        "device_info": {
            "device_type": device_type,
            "model": "unknown"
        },
        "issue_analysis": {
            "visible_issue": case.get("observed_problem", "unknown"),
            "error_indicator": case.get("image_name", "unknown"),
            "suspected_cause": suspected_cause,
            "confidence": 0.78
        },
        "recommended_action_level": action_level,
        "recommended_actions": immediate_steps,
        "compliance_check": {
            "requires_human_review": True,
            "safety_warning": safety_warning
        },
        "source": case.get("source", "manual input"),
        "timestamp": str(datetime.now())
    }

    return result


# -----------------------------
# 保存 JSON
# -----------------------------
def save_json(result: dict) -> str:
    path = os.path.join(JSON_DIR, result["case_id"] + "_diagnosis.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    return path


# -----------------------------
# 保存 Excel
# -----------------------------
def save_excel(result: dict) -> str:
    excel_path = os.path.join(EXCEL_DIR, "service_records.xlsx")

    row = {
        "case_id": result["case_id"],
        "device_type": result["device_info"]["device_type"],
        "model": result["device_info"]["model"],
        "visible_issue": result["issue_analysis"]["visible_issue"],
        "suspected_cause": result["issue_analysis"]["suspected_cause"],
        "confidence": result["issue_analysis"]["confidence"],
        "recommended_action_level": result["recommended_action_level"],
        "recommended_actions": " | ".join(result["recommended_actions"]),
        "requires_human_review": result["compliance_check"]["requires_human_review"],
        "safety_warning": result["compliance_check"]["safety_warning"],
        "source": result["source"],
        "timestamp": result["timestamp"]
    }

    df = pd.DataFrame([row])

    if os.path.exists(excel_path):
        old_df = pd.read_excel(excel_path)
        df = pd.concat([old_df, df], ignore_index=True)

    df.to_excel(excel_path, index=False)
    return excel_path


# -----------------------------
# 生成 PDF
# -----------------------------
def generate_pdf(result: dict) -> str:
    pdf_path = os.path.join(PDF_DIR, result["case_id"] + "_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)

    y = 750
    c.drawString(70, y, "Medical Device Support Case Report")
    y -= 35

    lines = [
        f"Case ID: {result['case_id']}",
        f"Device Type: {result['device_info']['device_type']}",
        f"Model: {result['device_info']['model']}",
        f"Visible Issue: {result['issue_analysis']['visible_issue']}",
        f"Error Indicator: {result['issue_analysis']['error_indicator']}",
        f"Suspected Cause: {result['issue_analysis']['suspected_cause']}",
        f"Confidence: {result['issue_analysis']['confidence']}",
        f"Action Level: {result['recommended_action_level']}",
        "Recommended Actions:"
    ]

    for line in lines:
        c.drawString(70, y, line)
        y -= 22

    for idx, action in enumerate(result["recommended_actions"], start=1):
        c.drawString(90, y, f"{idx}. {action}")
        y -= 22

    y -= 10
    c.drawString(70, y, "Compliance Check:")
    y -= 22
    c.drawString(90, y, f"Requires Human Review: {result['compliance_check']['requires_human_review']}")
    y -= 22
    c.drawString(90, y, f"Safety Warning: {result['compliance_check']['safety_warning']}")
    y -= 30

    c.drawString(70, y, "For technician review only.")
    c.save()

    return pdf_path


# -----------------------------
# 健康检查接口
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Medical Device After-sales Workflow API is running"
    }


# -----------------------------
# 单个案例诊断接口
# -----------------------------
@app.post("/diagnose")
def diagnose(case: CaseInput):
    case_dict = case.model_dump()

    diagnosis = ai_diagnose(case_dict)
    json_path = save_json(diagnosis)
    excel_path = save_excel(diagnosis)
    pdf_path = generate_pdf(diagnosis)

    return {
        "status": "success",
        "message": "Case processed successfully",
        "diagnosis": diagnosis,
        "files": {
            "json_path": json_path,
            "excel_path": excel_path,
            "pdf_path": pdf_path
        }
    }


# -----------------------------
# 读取某个 JSON 诊断结果
# -----------------------------
@app.get("/cases/{case_id}")
def get_case(case_id: str):
    json_path = os.path.join(JSON_DIR, case_id + "_diagnosis.json")

    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Case not found")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


# -----------------------------
# 批量处理 sample_inputs 里的案例
# -----------------------------
@app.post("/run-sample-workflow")
def run_sample_workflow():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]

    if not files:
        raise HTTPException(status_code=404, detail="No sample input files found")

    results = []

    for f in files:
        path = os.path.join(INPUT_DIR, f)

        with open(path, "r", encoding="utf-8") as file:
            case = json.load(file)

        diagnosis = ai_diagnose(case)
        json_path = save_json(diagnosis)
        excel_path = save_excel(diagnosis)
        pdf_path = generate_pdf(diagnosis)

        results.append({
            "case_id": case["case_id"],
            "json_path": json_path,
            "excel_path": excel_path,
            "pdf_path": pdf_path
        })

    return {
        "status": "success",
        "processed_cases": len(results),
        "results": results
    }