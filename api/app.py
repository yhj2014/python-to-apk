import os
import uuid
import shutil
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = '/tmp/uploads'
BUILD_FOLDER = '/tmp/builds'
ALLOWED_EXTENSIONS = {'py', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'kv', 'json'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BUILD_FOLDER'] = BUILD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传和构建目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BUILD_FOLDER, exist_ok=True)

# 内存中的任务存储（在实际应用中应使用数据库）
tasks = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/build', methods=['POST'])
def build_apk():
    # 检查GUI类型
    gui_type = request.form.get('gui_type')
    if gui_type not in ['kivy', 'tkinter', 'pyside6']:
        return jsonify({'error': '无效的GUI类型'}), 400
    
    # 检查Python文件
    if 'python_file' not in request.files:
        return jsonify({'error': '未提供Python文件'}), 400
    
    python_file = request.files['python_file']
    if python_file.filename == '':
        return jsonify({'error': '未选择Python文件'}), 400
    
    if not allowed_file(python_file.filename):
        return jsonify({'error': '文件类型不允许'}), 400
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    # 保存Python文件
    python_filename = secure_filename(python_file.filename)
    python_path = os.path.join(task_dir, python_filename)
    python_file.save(python_path)
    
    # 保存资源文件
    resource_files = request.files.getlist('resource_files')
    resource_paths = []
    for file in resource_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(task_dir, filename)
            file.save(file_path)
            resource_paths.append(filename)
    
    # 保存额外依赖和权限
    extra_deps = request.form.get('extra_deps', '')
    permissions = request.form.get('permissions', '')
    
    # 创建任务
    tasks[task_id] = {
        'status': '上传完成，等待构建',
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(minutes=5),
        'gui_type': gui_type,
        'python_file': python_filename,
        'resource_files': resource_paths,
        'extra_deps': extra_deps.split('\n') if extra_deps else [],
        'permissions': permissions.split('\n') if permissions else [],
        'completed': False,
        'success': False,
        'output_file': None
    }
    
    # 在实际应用中，这里应该将任务加入队列
    # 这里我们模拟立即开始构建
    simulate_build(task_id)
    
    return jsonify({'task_id': task_id})

@app.route('/api/status/<task_id>')
def build_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    # 清理过期任务
    if datetime.now() > task['expires_at']:
        cleanup_task(task_id)
        return jsonify({'error': '任务已过期'}), 404
    
    return jsonify({
        'status': task['status'],
        'completed': task['completed'],
        'success': task['success'],
        'download_url': f'/api/download/{task_id}' if task['success'] and task['output_file'] else None,
        'error': task.get('error')
    })

@app.route('/api/download/<task_id>')
def download_apk(task_id):
    task = tasks.get(task_id)
    if not task or not task['success'] or not task['output_file']:
        return jsonify({'error': 'APK不可用'}), 404
    
    build_dir = os.path.join(app.config['BUILD_FOLDER'], task_id)
    return send_from_directory(build_dir, task['output_file'], as_attachment=True)

def simulate_build(task_id):
    """模拟构建过程，实际应用中应调用GitHub Actions"""
    task = tasks[task_id]
    
    # 模拟构建步骤
    steps = [
        '准备构建环境',
        '安装依赖',
        '打包资源文件',
        '编译Python代码',
        '构建APK',
        '签名APK',
        '完成'
    ]
    
    for i, step in enumerate(steps):
        time.sleep(2)
        progress = int((i + 1) / len(steps) * 100)
        task['status'] = f'{step} ({progress}%)'
    
    # 模拟构建完成
    task['completed'] = True
    task['success'] = True
    task['status'] = '构建成功'
    task['output_file'] = f'app-{task_id[:8]}.apk'
    
    # 设置1分钟后过期
    task['expires_at'] = datetime.now() + timedelta(minutes=1)

def cleanup_task(task_id):
    """清理任务文件和记录"""
    if task_id in tasks:
        # 删除上传的文件
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], task_id)
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        
        # 删除构建的文件
        build_dir = os.path.join(app.config['BUILD_FOLDER'], task_id)
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        
        # 删除任务记录
        del tasks[task_id]

if __name__ == '__main__':
    app.run(debug=True)
