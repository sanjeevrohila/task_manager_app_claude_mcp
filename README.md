# Smart Task Manager MCP Server

A lightweight task management system powered by Flask, SQLite, and FastMCP that works both as a web app and as an MCP server for Claude AI.

## Features

**Web Application**
- Create, update, and delete tasks
- Toggle task completion status
- Priority-based ranking with dynamic scoring
- Due-date tracking and urgency indicators
- Beautiful responsive UI

**MCP Tools for Claude**
- `list_tasks` - Get all tasks sorted by priority
- `add_task` - Create new tasks
- `complete_task` - Toggle task completion
- `delete_task` - Remove tasks

---

## Quick Start

### Prerequisites
- Python 3.12+
- pip (comes with Python)

### Installation (5 minutes)

```bash
# 1. Clone repo
git clone https://github.com/sanjeevrohila/task_manager_app_claude_mcp.git
cd task_manager_app_claude_mcp

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run web app
python app.py

# Visit http://127.0.0.1:5000
```

---

## Running the Application

### Web Interface

```bash
source .venv/bin/activate
python app.py
```

Open: `http://127.0.0.1:5000`

You can:
- Add tasks with due dates and importance levels (1-5)
- Toggle task completion
- Delete tasks
- See priority scores calculated automatically

### MCP Server (for Claude)

```bash
source .venv/bin/activate
python mcp_server.py
```

This starts the MCP server that Claude Desktop can connect to.

---

## Claude Desktop Integration

### Step 1: Find Your Configuration File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 2: Get Your Paths

Run these commands in your terminal:

```bash
# Get Python executable path
which python
# Output: /Users/mac/task_manager_app_claude_mcp/.venv/bin/python

# Get full path to mcp_server.py
pwd
# Output: /Users/mac/task_manager_app_claude_mcp
```

### Step 3: Add to Claude Config

Edit your `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "/Users/mac/task_manager_app_claude_mcp/.venv/bin/python",
      "args": ["/Users/mac/task_manager_app_claude_mcp/mcp_server.py"]
    }
  }
}
```

**Replace the paths with your actual paths from Step 2**

### Step 4: Restart Claude

1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. Look for the 🔨 hammer icon in the message box - this shows MCP tools are connected

### Step 5: Start Using It!

Ask Claude things like:

```
"Show me all my tasks"
"Add a task 'Prepare presentation' due on 2026-05-25 with importance 4"
"Mark task 1 as complete"
"Delete task 2"
```

Claude will use the MCP tools to manage your tasks!

---

## Priority Score Formula

Tasks are ranked using this formula:

```
priority_score = urgency_weight + (importance × 2)

Where:
- urgency_weight = 10 if overdue, else 10 / days_until_due
- importance = 1-5 (your input)
```

**Example:**
- Task due in 2 days, importance 5: Score = (10/2) + (5×2) = 15
- Task due in 5 days, importance 3: Score = (10/5) + (3×2) = 8

---

## Project Structure

```
task_manager_app_claude_mcp/
├── app.py              # Flask web application
├── mcp_server.py       # MCP server for Claude
├── models.py           # Database models
├── templates/
│   └── index.html      # Web UI
├── instance/
│   └── tasks.db        # SQLite database (auto-created)
├── requirements.txt    # Dependencies
├── pyproject.toml      # Project metadata
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## Database

Uses SQLite with one table:

```
tasks
├── id (primary key)
├── title (string)
├── due_date (date)
├── importance (1-5)
└── completed (boolean)
```

Database is at: `instance/tasks.db`

---

## Troubleshooting

### Claude says "Tool not found"

```bash
# Check your config file syntax (must be valid JSON)
# Verify paths exist:
ls -la /path/to/.venv/bin/python
ls -la /path/to/mcp_server.py

# Fully restart Claude (not just close, but Quit completely)
```

### "Command not found" Error

- Use **absolute paths** in config, not relative paths (`~` won't work)
- Don't use `~/` - use full path like `/Users/mac/...`

### Database Issues

```bash
# Delete old database and restart
rm instance/tasks.db
python app.py  # Will create fresh database
```

### Port 5000 Already in Use

```bash
python app.py --port 5001
```

---

## Technology Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| Flask | 3.0.0 | Web framework |
| SQLAlchemy | 2.0.23 | Database ORM |
| Flask-SQLAlchemy | 3.1.1 | Flask + SQLAlchemy |
| FastMCP | 0.1.0 | MCP protocol |

---

## Deployment

### Production Web Server

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t task-manager .
docker run -p 5000:5000 task-manager
```

### Heroku

```bash
# Create Procfile
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

---

## File Descriptions

### `app.py`
Flask web application. Handles:
- HTTP routing for web UI
- Form submissions
- HTML rendering

### `mcp_server.py`
MCP protocol server. Handles:
- JSON-RPC communication
- Tool definitions for Claude
- No HTTP - pure stdio interface

### `models.py`
SQLAlchemy database models:
- `Task` class
- Priority score calculation
- Status tag logic

### `templates/index.html`
Web UI template with:
- Task creation form
- Task list display
- Priority sorting visualization

---

## API Reference (MCP Tools)

### `list_tasks()`
Returns all tasks sorted by priority.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Fix bug",
    "due_date": "2026-05-20",
    "importance": 5,
    "completed": false,
    "priority_score": 12.5,
    "status": "Urgent"
  }
]
```

### `add_task(title, due_date, importance)`
Add a new task.

**Parameters:**
- `title` (str): Task name
- `due_date` (str): YYYY-MM-DD format
- `importance` (int): 1-5 scale

### `complete_task(task_id)`
Toggle task completion.

**Parameters:**
- `task_id` (int): Task ID

### `delete_task(task_id)`
Delete a task.

**Parameters:**
- `task_id` (int): Task ID

---

## Contributing

```bash
# Fork and clone
git clone your-fork
cd task_manager_app_claude_mcp

# Create branch
git checkout -b feature/my-feature

# Make changes, commit, push
git commit -m "Add my feature"
git push origin feature/my-feature

# Open pull request
```

---

## Future Ideas

- [ ] Task tags/categories
- [ ] Recurring tasks
- [ ] Email reminders
- [ ] REST API
- [ ] Multi-user support
- [ ] Task notes
- [ ] Subtasks
- [ ] Time tracking
- [ ] Export to CSV/PDF

---

## License

MIT License - Use freely!

---

## Support

Issues? Questions? 
- Open a GitHub issue
- Check the troubleshooting section above

---

## Quick Commands

```bash
# Setup (one-time)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run web app
python app.py

# Run MCP server
python mcp_server.py

# Deactivate virtualenv
deactivate
```