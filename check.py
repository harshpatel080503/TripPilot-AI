import sqlite3
conn = sqlite3.connect('travel_runs.db')
c = conn.cursor()
c.execute('''
SELECT t.tool_name, t.input_json, t.output_text, a.started_at
FROM tool_calls t 
JOIN agent_calls a ON t.agent_call_id = a.id 
WHERE a.phase = 'pricer' 
ORDER BY a.started_at DESC LIMIT 5
''')
for r in c.fetchall():
    print(f'{r[3]} | {r[0]}: {r[1]}\n{str(r[2])[:300]}\n---')
