import re
from typing import List, Dict

OPERATIONS = ['+', '-', '*', '/', '%', '//', '^', '&', '|', '<<', '>>', '·', 'xor', 'mod']

BINS = [
    ('bin_≤26', 26),
    ('bin_27_500', 500),
    ('bin_501_5000', 5000),
    ('bin_5001_1e6', 1_000_000),
    ('bin_large', float('inf'))
]

# Helper functions
def parse_number(num_str: str) -> int:
    # converts number formats into integers
    num_str = num_str.replace(' ', '').replace(',', '')
    num_str = num_str.replace('·', '*').replace('⋅', '*')
    
    if 'e' in num_str.lower():
        return int(float(num_str))
    
    match = re.match(r'([-+]?[0-9]*\.?[0-9]+)\s*\*\s*10\^(\d+)', num_str)
    if match:
        base, exp = match.groups()
        return int(float(base) * (10 ** int(exp)))
    
    match = re.match(r'([-+]?)10\^(\d+)', num_str)
    if match:
        sign, exp = match.groups()
        val = 10 ** int(exp)
        return -val if sign == '-' else val
    
    return int(float(num_str))

def extract_variable_ranges(problem_text: str, variable_names: list) -> Dict[str, tuple]:
    ranges = {}

    #  (lower ≤ vars ≤ upper), vars = "n", "n,m", "a, b, c", etc.
    pattern = re.compile(
        r'(-?\s*[\d.,eE^*·⋅]+)\s*[≤<=]\s*([a-z](?:\s*,?\s*[a-z])*)\s*[≤<=]\s*(-?\s*[\d.,eE^*·⋅]+)',
        re.I
    )

    for match in pattern.finditer(problem_text):
        low_raw, vars_str, high_raw = match.groups()

        try:
            low = parse_number(low_raw)
            high = parse_number(high_raw)
            rng = high - low + 1
        except Exception:
            continue

        vars_list = [v.strip() for v in vars_str.split(',')]

        for var in vars_list:
            if var in variable_names:
                ranges[var] = (low, high, rng)

    return ranges

def extract_time_limit(text: str) -> int:
    match = re.search(r'time limit per test\s*(\d+)', text)
    return int(match.group(1)) if match else None

def extract_memory_limit(text: str) -> int:
    match = re.search(r'memory limit per test\s*(\d+)', text)
    return int(match.group(1)) if match else None

def compute_bin(range_val: int) -> str:
    lower = 0
    for name, upper in BINS:
        if range_val <= upper and range_val > lower:
            return name
        lower = upper
    return 'bin_large'

def extract_variables(text: str) -> list[str]:
    if not text:
        return []

    text = re.sub(r'^[A-Za-z]\.', '', text, count=1).lstrip()

    vars_found = re.findall(r'(?:^|[\s\(\.,;:])([a-zA-Z])(?:[\s\)\.,;:]|$)', text)
    return list(set(vars_found))

def count_operations(text: str, operations: list[str]) -> int:
    total = 0
    for op in operations:
        op_escaped = re.escape(op)
        if op.isalpha():
            total += len(re.findall(rf'\b{op_escaped}\b', text))
        else:
            total += len(re.findall(rf'{op_escaped}', text))

    return total


# main function
def extract_features(problem_id: str, cleaned_text: str, tags: List[str], complexity_counts: dict) -> Dict:
    features = {}
    features['problem_id'] = problem_id
    features['problem_url'] = f"https://codeforces.com/contest/{problem_id.split('_')[0]}/problem/{problem_id.split('_')[1]}"
    features['time_limit'] = extract_time_limit(cleaned_text)
    features['memory_limit'] = extract_memory_limit(cleaned_text)
    features['word_count'] = len(cleaned_text.split())
    features['num_numbers'] = len(re.findall(r'\d+', cleaned_text))
    features['num_operations'] = count_operations(cleaned_text, OPERATIONS)

    unique_vars = extract_variables(cleaned_text)
    features['num_unique_variables'] = len(unique_vars)

    ranges = extract_variable_ranges(cleaned_text, list(unique_vars))

    for name, _ in BINS:
        features[name] = 0
    for _, _, r in ranges.values():
        bin_name = compute_bin(r)
        if bin_name in features:
            features[bin_name] += 1
            
    features['tags'] = tags
    features['complexity_counts'] = complexity_counts

    return features
