from pathlib import Path
root = Path(__file__).resolve().parents[1]
required = ['SKILL.md','README.md','references/requirements.md','references/architecture.md','references/data-contracts.md','references/ml-routing.md','references/security-operations.md','assets/templates/backend/app/main.py','assets/templates/frontend/app/page.tsx','assets/templates/sql/bigquery_daily_demand.sql']
for name in required:
    assert (root/name).is_file(), f'Missing {name}'
text = (root/'SKILL.md').read_text(encoding='utf-8')
assert text.startswith('---\n') and 'name: logistics-demand-ai' in text
assert root.name == 'logistics-demand-ai'
print('Skill structure OK')
