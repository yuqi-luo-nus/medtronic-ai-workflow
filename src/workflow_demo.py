import json
import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# 输入路径
INPUT_DIR = "../data/sample_inputs"

# 输出路径
JSON_DIR = "../outputs/json"
EXCEL_DIR = "../outputs/excel"
PDF_DIR = "../outputs/pdf"

os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)


# 模拟 AI 诊断函数
def ai_diagnose(case):

    result = {
        "case_id": case["case_id"],
        "device_type": case["device_type_hint"],
        "visible_issue": case["observed_problem"],
        "suspected_cause": "possible device enclosure issue",
        "recommended_action_level": "medium",
        "immediate_steps": [
            "Inspect device casing",
            "Check battery compartment",
            "Restart device and monitor warning"
        ],
        "requires_human_review": True,
        "timestamp": str(datetime.now())
    }

    return result


# 保存 JSON
def save_json(result):

    path = os.path.join(JSON_DIR, result["case_id"] + "_diagnosis.json")

    with open(path, "w") as f:
        json.dump(result, f, indent=4)

    return path


# 写入 Excel
def save_excel(result):

    excel_path = os.path.join(EXCEL_DIR, "service_records.xlsx")

    df = pd.DataFrame([result])

    if os.path.exists(excel_path):
        old = pd.read_excel(excel_path)
        df = pd.concat([old, df], ignore_index=True)

    df.to_excel(excel_path, index=False)

    return excel_path


# 生成 PDF 报告
def generate_pdf(result):

    pdf_path = os.path.join(PDF_DIR, result["case_id"] + "_report.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)

    y = 750

    c.drawString(100, y, "Medical Device Support Case Report")
    y -= 40

    for k, v in result.items():

        text = f"{k}: {v}"

        c.drawString(100, y, text)

        y -= 25

    y -= 20

    c.drawString(100, y, "For technician review only")

    c.save()

    return pdf_path


# 主流程
def run_workflow():

    files = os.listdir(INPUT_DIR)

    for f in files:

        path = os.path.join(INPUT_DIR, f)

        with open(path) as file:

            case = json.load(file)

        diagnosis = ai_diagnose(case)

        json_path = save_json(diagnosis)

        excel_path = save_excel(diagnosis)

        pdf_path = generate_pdf(diagnosis)

        print("Processed:", case["case_id"])
        print("JSON:", json_path)
        print("Excel:", excel_path)
        print("PDF:", pdf_path)
        print("---------")


if __name__ == "__main__":

    run_workflow()