import sqlite3
import json
conn = sqlite3.connect('travel_runs.db')
c = conn.cursor()
c.execute("SELECT id FROM agent_calls WHERE phase='pricer' ORDER BY started_at DESC LIMIT 1")
agent_call_id = c.fetchone()[0]

c.execute("SELECT tool_name, input_json, success FROM tool_calls WHERE agent_call_id=? ORDER BY id", (agent_call_id,))
for row in c.fetchall():
    print(row)
