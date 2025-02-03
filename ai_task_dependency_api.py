from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE,
            task_name TEXT,
            phase TEXT,
            status TEXT,
            dependency TEXT,
            issue_flagged TEXT,
            resolution TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to check dependencies
def check_dependencies(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT dependency FROM tasks WHERE task_id = ?", (task_id,))
    dependencies = cursor.fetchone()
    conn.close()
    
    if dependencies and dependencies[0]:
        dep_list = dependencies[0].split(', ')
        
        for dep in dep_list:
            conn = sqlite3.connect("tasks.db")
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM tasks WHERE task_id = ?", (dep,))
            dep_status = cursor.fetchone()
            conn.close()
            
            if dep_status and dep_status[0] != "Complete":
                return False, f"Dependency {dep} is incomplete. Complete it before proceeding."
    return True, "All dependencies met."

# API Endpoint: Add a new task
@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.json
    task_id = data["task_id"]
    task_name = data["task_name"]
    phase = data["phase"]
    status = data["status"]
    dependency = data.get("dependency", "None")
    issue_flagged, resolution = check_dependencies(task_id)
    issue_flagged = "Yes" if not issue_flagged else "No"
    
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO tasks (task_id, task_name, phase, status, dependency, issue_flagged, resolution)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task_id, task_name, phase, status, dependency, issue_flagged, resolution))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task added successfully", "task_id": task_id})

# API Endpoint: Get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    
    task_list = [{"task_id": t[1], "task_name": t[2], "phase": t[3], "status": t[4],
                  "dependency": t[5], "issue_flagged": t[6], "resolution": t[7]} for t in tasks]
    return jsonify(task_list)

# API Endpoint: Update task status
@app.route("/update_task", methods=["POST"])
def update_task():
    data = request.json
    task_id = data["task_id"]
    status = data["status"]
    
    issue_flagged, resolution = check_dependencies(task_id)
    issue_flagged = "Yes" if not issue_flagged else "No"
    
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks SET status = ?, issue_flagged = ?, resolution = ? WHERE task_id = ?
    """, (status, issue_flagged, resolution, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Task updated successfully", "task_id": task_id})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
