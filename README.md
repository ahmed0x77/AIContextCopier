# 🤖 AI Context Copier 📋

  

A simple and powerful desktop application designed to make your life easier when working with AI assistants like ChatGPT, Claude, and Gemini.

  

Tired of manually copying and pasting dozens of files, organizing them in a text editor, and adding file paths just to give an AI the context of your project? This app automates that entire process. With a few clicks, you can select any number of files and folders, and the app will generate a perfectly formatted, AI-friendly prompt with all your code, ready to be pasted directly into your chat.

  

_(Feel free to replace this with your own screenshot!)_

  

---

  

## ✨ Key Features

  

- **🗂️ Modern Tree View Browser:** Navigate your project directory with a clean, intuitive, and VS Code-style file browser. Folders are always sorted on top, followed by alphabetically sorted files.

  

- **🎨 Visually-Rich UI with Icons:** A sleek and modern UI powered by `customtkinter`. The app uses colorful emoji icons for different file types (🐍 for Python, 📜 for JS/TS, 🎨 for HTML/CSS, etc.), making it easy to identify files at a glance.

  

- **🖱️ Full Multi-Select Support:** Use **Ctrl+Click** and **Shift+Click** to select multiple files and folders in both the file browser and the "Selected Items" list, just like in a native file explorer.

  

- **🧠 Smart Folder & File Handling:**

  

  - Add entire folders to your selection, and the app will intelligently include all files within them.

  - The app automatically prevents duplicates and handles redundancy (e.g., if you add a file and then its parent folder, it will consolidate them).

  

- **🌟 Recents & Favorites Manager:**

  

  - The app remembers the last 5 project folders you've opened for one-click access.

  - You can "star" a project to add it to a persistent Favorites list.

  

- **⚙️ Persistent Settings:**

  

  - A dedicated settings window to manage your preferences.

  - All settings (including your Favorites list and options) are automatically saved to an `app_settings.json` file, so your setup is always remembered.

  

- **📋 AI-Optimized Markdown Output:**

  

  - The final output is copied to your clipboard as clean, structured Markdown.

  - It automatically detects file types and wraps code in language-specific blocks (e.g., ` ```python `) for perfect syntax highlighting and AI comprehension.

  

- **🌳 Automatic Project Structure Tree:**

  - (Optional, on by default) The app generates a text-based tree diagram of your _selected_ files and folders and places it at the very top of your clipboard content. This gives the AI an immediate high-level overview of your project's structure.

  

---

  

## 🚀 Setup and Usage

  

### 1. Prerequisites

  

- You must have **Python 3** installed on your system.

  

### 2. Installation

  

Open your terminal or command prompt and simply run:

  

```bash

pip install -r requirements.txt

```

  

### 3. Running the App

  

Save the application code as a Python file (e.g., `main_app.py`) and run it from your terminal:

  

```bash

python main_app.py

```

  

### 4. How to Use

  

1.  Click **"Select Project Directory"** to open the project selector. Choose a recent/favorite project or browse for a new one.

2.  Use the left-hand panel to navigate your project. Select files and folders using your mouse (**Ctrl+Click** and **Shift+Click** for multi-select).

3.  Click the **"Add >>"** button to move your selection to the "Selected Items" list on the right.

4.  Manage the "Selected Items" list by checking items and clicking **"<< Remove"** or by clicking the individual **[X]** buttons.

5.  Click the big green **"Copy All Selected Items to Clipboard"** button.

6.  **Paste** the perfectly formatted context into your AI chat!

  

---

  

## 📝 Example Output

  

If you select a folder `src` containing `main.py` and a `README.md` file, the content copied to your clipboard will look like this:

  

````markdown

**Selected Project Structure:**

  

```text

my-project/

└── 📁 src

    ├── 📝 README.md

    └── 🐍 main.py

```

  

# Project Context

  

### `src/README.md`

  

```markdown

This is the project's README file.

```

  

### `src/main.py`

  

```python

def hello_world():

    print("Hello, AI!")

  

if __name__ == "__main__":

    hello_world()

```

````