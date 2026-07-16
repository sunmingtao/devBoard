import yaml

with open('test.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

for key in data['paths']:
    print(key)
