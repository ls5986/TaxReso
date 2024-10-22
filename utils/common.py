# utils/common.py

def extract_float(value: str) -> float:
    try:
        return float(value.replace(',', '').replace('$', ''))
    except ValueError:
        return 0.0
def get_last_four_ssn(ssn: str) -> str:
    return ssn[-4:] if len(ssn) >= 4 else "Unknown"