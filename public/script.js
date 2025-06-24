document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const statusArea = document.getElementById('statusArea');
    const progressBar = document.getElementById('progress');
    const statusText = document.getElementById('statusText');
    const downloadArea = document.getElementById('downloadArea');
    const downloadBtn = document.getElementById('downloadBtn');
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const guiType = document.getElementById('guiType').value;
        const pythonFile = document.getElementById('pythonFile').files[0];
        const resourceFiles = document.getElementById('resourceFiles').files;
        const extraDeps = document.getElementById('extraDeps').value;
        const permissions = document.getElementById('permissions').value;
        
        // Show status area
        statusArea.classList.remove('hidden');
        updateStatus('准备上传文件...', 10);
        
        // Prepare form data
        const formData = new FormData();
        formData.append('gui_type', guiType);
        formData.append('python_file', pythonFile);
        
        // Add resource files if any
        if (resourceFiles.length > 0) {
            for (let i = 0; i < resourceFiles.length; i++) {
                formData.append('resource_files', resourceFiles[i]);
            }
        }
        
        // Add extra dependencies if any
        if (extraDeps.trim() !== '') {
            formData.append('extra_deps', extraDeps);
        }
        
        // Add permissions if any
        if (permissions.trim() !== '') {
            formData.append('permissions', permissions);
        }
        
        try {
            updateStatus('上传文件中...', 20);
            
            // Submit to backend
            const response = await fetch('/api/build', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('服务器响应错误');
            }
            
            const data = await response.json();
            
            if (!data.task_id) {
                throw new Error('未收到任务ID');
            }
            
            updateStatus('文件上传成功，开始构建APK...', 30);
            
            // Start polling for build status
            await pollBuildStatus(data.task_id);
            
        } catch (error) {
            console.error('Error:', error);
            updateStatus(`错误: ${error.message}`, 0, true);
        }
    });
    
    async function pollBuildStatus(taskId) {
        let attempts = 0;
        const maxAttempts = 60; // 1 minute timeout (poll every second)
        
        const poll = async () => {
            attempts++;
            
            try {
                const response = await fetch(`/api/status/${taskId}`);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || '状态检查失败');
                }
                
                updateStatus(data.status, 30 + Math.floor(attempts / maxAttempts * 70));
                
                if (data.completed) {
                    if (data.success) {
                        updateStatus('APK构建完成!', 100);
                        showDownloadLink(data.download_url);
                        startCountdown();
                    } else {
                        updateStatus(`构建失败: ${data.error}`, 100, true);
                    }
                    return;
                }
                
                if (attempts >= maxAttempts) {
                    throw new Error('构建超时');
                }
                
                // Continue polling
                setTimeout(poll, 1000);
                
            } catch (error) {
                console.error('Polling error:', error);
                updateStatus(`错误: ${error.message}`, 0, true);
            }
        };
        
        await poll();
    }
    
    function updateStatus(text, progress, isError = false) {
        statusText.textContent = text;
        progressBar.style.width = `${progress}%`;
        
        if (isError) {
            statusText.style.color = 'var(--error-color)';
            progressBar.style.backgroundColor = 'var(--error-color)';
        } else {
            statusText.style.color = 'var(--text-color)';
            progressBar.style.backgroundColor = 'var(--primary-color)';
        }
    }
    
    function showDownloadLink(url) {
        downloadBtn.href = url;
        downloadArea.classList.remove('hidden');
    }
    
    function startCountdown() {
        let secondsLeft = 60;
        const countdownInterval = setInterval(() => {
            secondsLeft--;
            
            if (secondsLeft <= 0) {
                clearInterval(countdownInterval);
                downloadArea.innerHTML = '<p class="warning">下载链接已过期</p>';
                downloadBtn.classList.add('hidden');
            } else {
                document.querySelector('#downloadArea .warning').textContent = 
                    `注意: APK文件将在${secondsLeft}秒后自动删除，请及时下载！`;
            }
        }, 1000);
    }
});
