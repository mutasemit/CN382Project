from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from config import Config
from models import db, User, Task
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# إنشاء قاعدة البيانات باستخدام سياق التطبيق
with app.app_context():
    db.create_all()

# التحقق من تسجيل الدخول
def login_required(view):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view

# صفحة الرئيسية
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            app.logger.info(f'{username} تم تسجيل الدخول بنجاح')
            return redirect(url_for('dashboard'))
        
        flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render_template('login.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح')
    return redirect(url_for('login'))

# لوحة المهام
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.due_date).all()
    return render_template('dashboard.html', tasks=tasks)

# إضافة مهمة جديدة
@app.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        status = request.form['status']
        
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            user_id=session['user_id']
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('تمت إضافة المهمة بنجاح')
        return redirect(url_for('dashboard'))
    
    return render_template('task_form.html')

# تعديل مهمة
@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # التحقق من ملكية المهمة
    if task.user_id != session['user_id']:
        flash('ليس لديك صلاحية تعديل هذه المهمة')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        task.status = request.form['status']
        
        db.session.commit()
        
        flash('تم تحديث المهمة بنجاح')
        return redirect(url_for('dashboard'))
    
    return render_template('task_form.html', task=task)

# حذف مهمة
@app.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # التحقق من ملكية المهمة
    if task.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية حذف هذه المهمة'})
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'success': True})

# تحديث حالة المهمة
@app.route('/task/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_status(task_id):
    task = Task.query.get_or_404(task_id)
    
    # التحقق من ملكية المهمة
    if task.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'ليس لديك صلاحية تعديل هذه المهمة'})
    
    status = request.form.get('status')
    if status in ['جاري', 'مكتمل', 'متأخر']:
        task.status = status
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'حالة غير صالحة'})

# إنشاء مستخدم (للاختبار فقط)
@app.route('/setup')
def setup():
    if User.query.count() == 0:
        user = User(username='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return 'تم إنشاء المستخدم بنجاح!'
    return 'المستخدم موجود بالفعل!'

# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # التحقق من تطابق كلمات المرور
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة')
            return render_template('register.html')
        
        # التحقق من عدم وجود المستخدم مسبق
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('اسم المستخدم موجود بالفعل')
            return render_template('register.html')
        
        # إنشاء مستخدم جديد
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول')
        return redirect(url_for('login'))
    
    return render_template('register.html')


# عرض قائمة المستخدمين (لجميع المستخدمين المسجلين)
@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
