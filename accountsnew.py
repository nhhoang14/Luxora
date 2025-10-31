
# accountsnew.py
# Single-file Flask app: accounts (register/login/logout/change password/profile)
# + Avatar upload persisted, + simple shipping addresses CRUD
import os
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# -------------------- Config --------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "accountsnew.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# -------------------- Models --------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_filename = db.Column(db.String(255), nullable=True)  # e.g. 'u3_1700000000.jpg'

    # optional profile fields
    phone = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    addresses = db.relationship("Address", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    @property
    def avatar_url(self):
        if self.avatar_filename:
            return url_for("static", filename=f"avatars/{self.avatar_filename}")
        # default placeholder (public domain icon)
        return "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    recipient = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    line1 = db.Column(db.String(255), nullable=False)
    line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(120), nullable=False, default="Vietnam")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------- Helpers --------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------- Routes: Auth --------------------
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            flash("Vui lòng nhập đủ tên, email và mật khẩu.", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email đã tồn tại.", "error")
        else:
            u = User(name=name, email=email)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash("Tạo tài khoản thành công. Đăng nhập nhé!", "success")
            return redirect(url_for("login"))
    return render_template_string(TPL_REGISTER)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        u = User.query.filter_by(email=email).first()
        if not u or not u.check_password(password):
            flash("Email hoặc mật khẩu không đúng.", "error")
        else:
            login_user(u, remember=True)
            return redirect(url_for("profile"))
    return render_template_string(TPL_LOGIN)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "success")
    return redirect(url_for("login"))


@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    old = request.form.get("old_password", "")
    new = request.form.get("new_password", "")
    if not current_user.check_password(old):
        flash("Mật khẩu cũ không đúng.", "error")
    elif len(new) < 6:
        flash("Mật khẩu mới tối thiểu 6 ký tự.", "error")
    else:
        current_user.set_password(new)
        db.session.commit()
        flash("Đổi mật khẩu thành công.", "success")
    return redirect(url_for("profile"))


# -------------------- Routes: Profile + Avatar --------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Update profile basic
    if request.method == "POST" and "update_profile" in request.form:
        current_user.name = request.form.get("name", current_user.name).strip()
        current_user.phone = request.form.get("phone", current_user.phone).strip() or None
        db.session.commit()
        flash("Cập nhật thông tin thành công.", "success")
        return redirect(url_for("profile"))

    addrs = Address.query.filter_by(user_id=current_user.id).order_by(Address.created_at.desc()).all()
    return render_template_string(TPL_PROFILE, user=current_user, addresses=addrs)


@app.route("/upload-avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if not file or file.filename == "":
        flash("Chưa chọn ảnh.", "error")
        return redirect(url_for("profile"))
    if not allowed_file(file.filename):
        flash("Định dạng ảnh không hợp lệ. Chấp nhận: png, jpg, jpeg, gif, webp.", "error")
        return redirect(url_for("profile"))

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"u{current_user.id}_{int(datetime.utcnow().timestamp())}.{ext}")
    path = os.path.join(AVATAR_DIR, filename)

    # delete old avatar
    try:
        if current_user.avatar_filename:
            old_path = os.path.join(AVATAR_DIR, current_user.avatar_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
    except Exception:
        pass

    file.save(path)
    current_user.avatar_filename = filename
    db.session.commit()
    flash("Đã cập nhật ảnh đại diện.", "success")
    return redirect(url_for("profile"))


# -------------------- Routes: Addresses CRUD --------------------
@app.route("/addresses/add", methods=["POST"])
@login_required
def add_address():
    f = request.form
    addr = Address(
        user_id=current_user.id,
        recipient=f.get("recipient", "").strip(),
        phone=f.get("addr_phone", "").strip(),
        line1=f.get("line1", "").strip(),
        line2=f.get("line2", "").strip() or None,
        city=f.get("city", "").strip(),
        state=f.get("state", "").strip() or None,
        postal_code=f.get("postal_code", "").strip() or None,
        country=f.get("country", "Vietnam").strip() or "Vietnam",
    )
    if not (addr.recipient and addr.phone and addr.line1 and addr.city):
        flash("Vui lòng nhập đủ người nhận, điện thoại, địa chỉ, thành phố.", "error")
    else:
        db.session.add(addr)
        db.session.commit()
        flash("Đã thêm địa chỉ giao hàng.", "success")
    return redirect(url_for("profile"))


@app.route("/addresses/<int:addr_id>/delete", methods=["POST"])
@login_required
def delete_address(addr_id):
    addr = Address.query.filter_by(id=addr_id, user_id=current_user.id).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash("Đã xóa địa chỉ.", "success")
    return redirect(url_for("profile"))


# -------------------- Templates (inline) --------------------
TPL_BASE = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title or 'Accounts' }}</title>
  <style>
    body { font-family: system-ui, Arial, sans-serif; background:#f7f7f8; margin:0; }
    .container { max-width: 980px; margin: 40px auto; padding: 24px; background:#fff; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,.06); }
    h1 { font-size: 22px; margin: 0 0 16px; }
    form { margin: 0; }
    input, button, textarea, select { font-size: 14px; }
    .row { display:flex; gap:12px; margin-bottom:12px; }
    .row > * { flex:1; }
    .btn { padding:10px 14px; border:1px solid #ddd; border-radius:8px; background:#fff; cursor:pointer; }
    .btn.primary { background:#111827; color:white; border-color:#111827; }
    .btn.danger { background:#ef4444; color:white; border-color:#ef4444; }
    .field { display:flex; flex-direction:column; gap:6px; }
    .input { padding:10px 12px; border:1px solid #ddd; border-radius:8px; }
    .card { border:1px solid #e5e7eb; border-radius:12px; padding:16px; background:#fafafa; }
    .flash { padding:10px 12px; border-radius:8px; margin-bottom:12px; }
    .flash.error { background:#fee2e2; color:#991b1b; }
    .flash.success { background:#dcfce7; color:#166534; }
    .center { text-align:center; }
    .avatar-wrap { display:flex; flex-direction:column; align-items:center; gap:12px; padding:16px; }
    .avatar {
      width: 128px; height:128px; border-radius:50%;
      object-fit:cover; border:3px solid #e5e7eb; background:#fff;
    }
    a { color:#2563eb; text-decoration:none; }
    .topnav { padding:16px; background:#111827; color:white; }
    .topnav a { color:#93c5fd; margin-right:12px; }
    table { width:100%; border-collapse:collapse; }
    th, td { padding:8px 10px; border-bottom:1px solid #eee; text-align:left; }
  </style>
</head>
<body>
  <div class="topnav">
    <a href="{{ url_for('profile') }}">Trang cá nhân</a>
    {% if current_user.is_authenticated %}
      <a href="{{ url_for('logout') }}">Đăng xuất</a>
    {% else %}
      <a href="{{ url_for('login') }}">Đăng nhập</a>
      <a href="{{ url_for('register') }}">Đăng ký</a>
    {% endif %}
  </div>

  <div class="container">
    {% for m, c in get_flashed_messages(with_categories=True) %}
      <div class="flash {{ c }}">{{ m }}</div>
    {% endfor %}
    {{ body|safe }}
  </div>
</body>
</html>
"""

TPL_LOGIN = """
{% set title = "Đăng nhập" %}
{% set body %}
<h1>Đăng nhập</h1>
<form method="post" class="card">
  <div class="field"><label>Email</label><input class="input" type="email" name="email" required></div>
  <div class="field"><label>Mật khẩu</label><input class="input" type="password" name="password" required></div>
  <div class="row">
    <button class="btn primary" type="submit">Đăng nhập</button>
    <a class="btn" href="{{ url_for('register') }}">Tạo tài khoản</a>
  </div>
</form>
{% endset %}
{{ TPL_BASE | replace("{{ body|safe }}", body) }}
"""

TPL_REGISTER = """
{% set title = "Đăng ký" %}
{% set body %}
<h1>Tạo tài khoản</h1>
<form method="post" class="card">
  <div class="field"><label>Họ tên</label><input class="input" type="text" name="name" required></div>
  <div class="field"><label>Email</label><input class="input" type="email" name="email" required></div>
  <div class="field"><label>Mật khẩu</label><input class="input" type="password" name="password" minlength="6" required></div>
  <button class="btn primary" type="submit">Đăng ký</button>
</form>
{% endset %}
{{ TPL_BASE | replace("{{ body|safe }}", body) }}
"""

TPL_PROFILE = """
{% set title = "Trang cá nhân" %}
{% set body %}
<h1>Hồ sơ người dùng</h1>

<div class="card">
  <div class="avatar-wrap">
    <img class="avatar" src="{{ user.avatar_url }}" alt="avatar">
    <div class="center"><strong>{{ user.name }}</strong><br>{{ user.email }}</div>

    <form action="{{ url_for('upload_avatar') }}" method="post" enctype="multipart/form-data" class="row" style="justify-content:center;">
      <input type="file" name="avatar" accept=".png,.jpg,.jpeg,.gif,.webp" required>
      <button class="btn primary" type="submit">Thay đổi ảnh đại diện</button>
    </form>
  </div>
</div>

<br>

<div class="card">
  <h3>Thông tin cơ bản</h3>
  <form method="post">
    <input type="hidden" name="update_profile" value="1">
    <div class="row">
      <div class="field"><label>Họ tên</label><input class="input" name="name" value="{{ user.name }}"></div>
      <div class="field"><label>Số điện thoại</label><input class="input" name="phone" value="{{ user.phone or '' }}"></div>
    </div>
    <div class="row"><button class="btn primary" type="submit">Lưu thay đổi</button></div>
  </form>
</div>

<br>

<div class="card">
  <h3>Đổi mật khẩu</h3>
  <form action="{{ url_for('change_password') }}" method="post">
    <div class="row">
      <div class="field"><label>Mật khẩu cũ</label><input class="input" type="password" name="old_password" required></div>
      <div class="field"><label>Mật khẩu mới</label><input class="input" type="password" name="new_password" minlength="6" required></div>
    </div>
    <button class="btn" type="submit">Đổi mật khẩu</button>
  </form>
</div>

<br>

<div class="card">
  <h3>Địa chỉ giao hàng</h3>
  <form action="{{ url_for('add_address') }}" method="post">
    <div class="row">
      <div class="field"><label>Người nhận</label><input class="input" name="recipient" required></div>
      <div class="field"><label>Điện thoại</label><input class="input" name="addr_phone" required></div>
    </div>
    <div class="row">
      <div class="field"><label>Địa chỉ (line 1)</label><input class="input" name="line1" required></div>
      <div class="field"><label>Địa chỉ (line 2)</label><input class="input" name="line2"></div>
    </div>
    <div class="row">
      <div class="field"><label>Thành phố</label><input class="input" name="city" required></div>
      <div class="field"><label>Tỉnh/Bang</label><input class="input" name="state"></div>
    </div>
    <div class="row">
      <div class="field"><label>Mã bưu chính</label><input class="input" name="postal_code"></div>
      <div class="field"><label>Quốc gia</label><input class="input" name="country" value="Vietnam"></div>
    </div>
    <button class="btn primary" type="submit">Thêm địa chỉ</button>
  </form>

  {% if addresses %}
  <br>
  <table>
    <thead><tr><th>Người nhận</th><th>Điện thoại</th><th>Địa chỉ</th><th>Hành động</th></tr></thead>
    <tbody>
      {% for a in addresses %}
        <tr>
          <td>{{ a.recipient }}</td>
          <td>{{ a.phone }}</td>
          <td>{{ a.line1 }}{% if a.line2 %}, {{ a.line2 }}{% endif %}, {{ a.city }}{% if a.state %}, {{ a.state }}{% endif %}{% if a.postal_code %} {{ a.postal_code }}{% endif %}, {{ a.country }}</td>
          <td>
            <form action="{{ url_for('delete_address', addr_id=a.id) }}" method="post" onsubmit="return confirm('Xóa địa chỉ này?');">
              <button class="btn danger" type="submit">Xóa</button>
            </form>
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endif %}
</div>

{% endset %}
{{ TPL_BASE | replace("{{ body|safe }}", body) }}
"""

# Make base available to children templates
app.jinja_env.globals["TPL_BASE"] = TPL_BASE


# -------------------- Bootstrap DB --------------------
with app.app_context():
    db.create_all()


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=True)
