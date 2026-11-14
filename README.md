# 📋 assihelper

**assihelper** is a smart, color-coded Command Line Interface (CLI) assignment and task prioritizer built with Python. It features a dynamic priority scoring algorithm that evaluates tasks based on deadline urgency, importance, and estimated effort, rendering a gorgeous terminal interface powered by the `rich` library. It doesn't require network once installed. (Keep in mind assignments.json and completed.json are formed within in the same folder so do not move or delete it.)
💡 Core Idea
assihelper was created to solve a common developer and student problem: task list paralysis. Traditional to-do apps treat every task with equal weight, making it hard to decide what to tackle next.

The core idea behind assihelper is a smart CLI task prioritizer that acts like an automated triage system. Instead of manual sorting, it continuously recalculates what matters most using a mathematical priority formula, presenting your queue in a stunning, color-coded terminal dashboard.The mathematical formula it uses to calculate is 
$$\text{Score} = (\text{Importance} \times 3.0) + (\text{Urgency} \times 15.0) + (\text{Effort Hours} \times 0.2)$$

---

## 🚀 Features

* **Dynamic Priority Scoring:** Automatically calculates task priority weights based on deadline proximity, importance ratings (1–5 stars), and estimated effort hours.
* **Smart Urgency & Color Coding:** Instantly categorizes tasks into **Overdue**, **Urgent**, **Upcoming**, or **On Track** with distinct visual color badges and ASCII progress bars.
* **Persistent Storage:** Keeps active tasks saved in `assignments.json` and archives completed items separately into `completed.json`.
* **Automatic Importance Boosting:** When marking tasks as complete, they are automatically archived with a 100% importance rating (`★★★★★`) in your history log.
* **Flexible Deadlines:** Supports both simple dates (`YYYY-MM-DD`) and precise timestamps (`YYYY-MM-DD HH:MM`).

---

## 📦 Prerequisites & Installation

Make sure you have Python 3.x installed along with the `rich` UI library.

1. Install the required dependency:
   ```bash
   pip install rich

## Commands
```bash
python assihelper.py add "Title" -due "YYYY-MM-DD HH:MM" -hrs <hours> -imp <1-5>
```

-d command is optional but can be used here.



```bash
python assihelper.py
```
OR
```bash
python assihelper.py list
```

Lists the assignments to be completed.



```bash
python assihelper.py delete -id ID
```
Deletes assignment wrt to the id.



```bash
python assihelper.py history
```
Shows completed assignments history.



```bash
python assihelper.py done -id ID
```
Here -due command is optional, if not given then uses the system time.


