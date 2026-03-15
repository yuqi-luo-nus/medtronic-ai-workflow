import json
import os

cases = [
    {
        "case_id": "case_01",
        "image_name": "pump_alarm.jpg",
        "device_type_hint": "insulin pump",
        "observed_problem": "screen displays warning icon and device casing slightly open",
        "source": "email attachment"
    },
    {
        "case_id": "case_02",
        "image_name": "monitor_connection_error.jpg",
        "device_type_hint": "patient monitor",
        "observed_problem": "screen shows connection error message",
        "source": "email attachment"
    },
    {
        "case_id": "case_03",
        "image_name": "battery_issue.jpg",
        "device_type_hint": "portable medical device",
        "observed_problem": "battery compartment not fully closed",
        "source": "email attachment"
    }
]

output_dir = "data/sample_inputs"

os.makedirs(output_dir, exist_ok=True)

for case in cases:
    filename = os.path.join(output_dir, case["case_id"] + ".json")
    with open(filename, "w") as f:
        json.dump(case, f, indent=4)

print("✅ Sample cases created successfully!")