// وظائف عامة تستخدم في جميع الصفحات

// تنسيق التاريخ
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('ar-SA', options);
}

// إظهار رسالة تنبيه
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // إخفاء التنبيه تلقائ<|im_start|> بعد 5 ثوانٍ
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
}

// التحقق من صحة النموذج
function validateTaskForm() {
    const title = document.getElementById('title').value.trim();
    const dueDate = document.getElementById('due_date').value;
    
    if (!title) {
        showAlert('يرجى إدخال عنوان للمهمة', 'danger');
        return false;
    }
    
    if (!dueDate) {
        showAlert('يرجى تحديد تاريخ التسليم', 'danger');
        return false;
    }
    
    return true;
}

// تهيئة عناصر Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // تفعيل popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});