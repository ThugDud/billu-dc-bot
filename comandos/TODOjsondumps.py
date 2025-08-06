import subprocess
import re
import json

def get_sensors_output():
    result = subprocess.run(['sensors'], capture_output=True, text=True)
    return result.stdout

def parse_sensors(output):
    data = {}
    current_chip = None

    for line in output.splitlines():
        line = line.strip()
        if not line:
            current_chip = None
            continue

        # Detecção de cabeçalho de chip
        if not ':' in line and not line.startswith('Adapter'):
            current_chip = line
            data[current_chip] = {}
        elif line.startswith('Adapter'):
            continue
        elif current_chip:
            match = re.match(r'([\w\s\d\.\-+]+):\s+([\+\-]?[0-9\.]+)(°C|V|A|RPM|%)?', line)
            if match:
                label = match.group(1).strip()
                value = float(match.group(2))
                unit = match.group(3) if match.group(3) else ''
                data[current_chip][label] = {"value": value, "unit": unit}

    return data

if __name__ == "__main__":
    raw_output = get_sensors_output()
    parsed_data = parse_sensors(raw_output)
    
    # Só exibir de forma bonitinha
    print(json.dumps(parsed_data, indent=4))
