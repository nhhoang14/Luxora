# Luxora 🛋️
 • Elegant lighting decor store — discover, customize, and shop modern lamps with Luxora.  
 • A modern furniture e-commerce web app built with **Django + TailwindCSS + daisyUI**.

## 🚀 Setup Guide

### 1️⃣ Clone the repository
```bash
git clone https://github.com/nhhoang14/Luxora.git
cd Luxora
```

### 2️⃣ Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Install Node.js dependencies (Tailwind + daisyUI)
```bash
cd theme/static_src
npm install
cd ../../
```
### 5️⃣ Database setup
```bash
python manage.py migrate
python manage.py loaddata users.json categorys.json colors.json products.json
```
### 6️⃣ Build TailwindCSS
```bash
python manage.py tailwind build
```
### 7️⃣ Run the project
Mở 2 terminal song song:

Terminal 1 (Tailwind watcher):
```bash
venv\Scripts\activate
python manage.py tailwind start
```
Terminal 2 (Django server):
```bash
venv\Scripts\activate
python manage.py runserver
```
## ⚙️ Development Notes

### 🔄 1. When updating static files
If you add, edit, or delete files in static/ (like images, JS, or CSS):
```bash
python manage.py collectstatic
```
> This command collects all static assets into /staticfiles/ for deployment.

### 🧩 2. When modifying Django models
After changing any model (e.g. adding new fields or tables):
```bash
python manage.py makemigrations
python manage.py migrate
```
### 🎨 3. When editing Tailwind or theme styles
If you update Tailwind config, component classes, or theme/static_src/src/style.css:
```bash
python manage.py tailwind build
```
Or during active development, run the watcher:
```bash
python manage.py tailwind start
```
> Changes in Tailwind or daisyUI classes will rebuild your CSS in real-time.

### 🧰 4. If Tailwind or Node dependencies change
```bash
cd theme/static_src
npm install
cd ../../
python manage.py tailwind build
```
