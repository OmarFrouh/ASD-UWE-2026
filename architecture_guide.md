# The "Backbone" Strategy
**For the Technical Lead**

You are right. If you trust your coding skills more than the others, you should build the **Skeleton** and let them fill in the **Flesh**.

## The 4 "Crown Jewels" You Must Own
If you control these, you control the quality of the entire project.

### 1. The `DatabaseManager` (The Brain)
*   **What it is**: A single class that handles connecting to SQLite, creating tables, and running queries.
*   **Why you own it**: You don't want Member 3 randomly deleting tables or Member 2 forgetting to close connections. You write the `execute_query(sql)` function; they just call it.

### 2. The `SessionManager` & Auth (The Gatekeeper)
*   **What it is**: The code that stores "Who is logged in?".
*   **Why you own it**: If this breaks, security fails (and you lose marks). usage: `if Session.current_user.role == 'Admin': ...`

### 3. The `MainView` (The Shell)
*   **What it is**: The main window with the Sidebar/Navigation buttons.
*   **Why you own it**: You build the "Frame". You create an empty function `show_tenant_screen()`. You tell Sarah: *"Write the code inside this function."*

### 4. The `BaseView` Class (The Template)
*   **What it is**: A Python class that defines what a "Screen" looks like (e.g., standard background color, standard title font).
*   **Why you own it**: This forces consistency. If Sarah inherits from your `BaseView`, her screen automatically looks correct.

---

## How to distribute work (The "Plug-in" Model)

You tell your team: **"I will give you an empty file. You just make the buttons work inside it."**

### Example:
**You write `views/tenant_view.py`:**
```python
# You write this scaffolding
class TenantView(BaseView):
    def __init__(self):
        super().__init__()
        self.title("Tenant Management")
        # SARAH: ADD YOUR CODE HERE
        # 1. Create label
        # 2. Create entry fields
```

**Sarah's Job:**
She pulls the code, sees the file, and just fills in the blank space. She doesn't need to worry about the database connection or the window size because **you handled that in the Core**.

## Recommended Action
For **Sprint 1**, your job is to build this "Backbone":
1.  `db.py` (Database manager)
2.  `auth.py` (Login logic)
3.  `main.py` (The main shell)
4.  `views/base_view.py` (The UI template)

Once you push that, the others can start working without breaking the app.
