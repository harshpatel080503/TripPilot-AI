import sqlite3
import json
conn = sqlite3.connect('travel_runs.db')
c = conn.cursor()
c.execute("SELECT output_text FROM agent_calls WHERE phase='pricer' ORDER BY started_at DESC LIMIT 1")
res = c.fetchone()[0]
with open('pricer_out.txt', 'w', encoding='utf-8') as f:
    f.write(res)
