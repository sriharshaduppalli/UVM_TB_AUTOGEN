import re
from typing import List, Dict

PORT_RE = re.compile(r'\b(input|output|inout)\b\s*(?:reg|wire)?\s*(?:\[(.*?)\])?\s*(\w+)', re.IGNORECASE)
MODULE_RE = re.compile(r'\bmodule\s+(\w+)\s*\((.*?)\)\s*;', re.S)

def parse_dut(file_path: str) -> Dict:
    text = open(file_path, 'r', errors='ignore').read()
    m = MODULE_RE.search(text)
    if not m:
        raise ValueError("No module declaration found")
    module_name = m.group(1)
    port_block = m.group(2)
    ports = []
    # split by commas but keep balanced parentheses (simple approach)
    tokens = re.split(r',\s*(?![^()]*\))', port_block)
    for t in tokens:
        t = t.strip()
        pm = PORT_RE.search(t)
        if pm:
            direction = pm.group(1)
            width = pm.group(2) or ''
            name = pm.group(3)
            ports.append({'name': name, 'dir': direction, 'width': width})
    return {'module': module_name, 'ports': ports}