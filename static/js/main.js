// Main JavaScript functionality for University LMS

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.classList.contains('alert-dismissible')) {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.click();
                }
            }
        }, 5000);
    });

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = width;
            bar.style.transition = 'width 1s ease-in-out';
        }, 100);
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                
                // Re-enable button after 3 seconds in case of errors
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
    });

    // Store original button text
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(btn) {
        btn.setAttribute('data-original-text', btn.innerHTML);
    });

    // Quiz timer functionality
    if (window.location.pathname.includes('/quiz/')) {
        startQuizTimer();
    }

    // Lesson progress tracking
    if (window.location.pathname.includes('/lesson/')) {
        trackLessonProgress();
    }
});

// Quiz timer function
function startQuizTimer() {
    const timerElement = document.getElementById('quiz-timer');
    if (!timerElement) return;

    const timeLimit = parseInt(timerElement.getAttribute('data-time-limit')) * 60; // Convert to seconds
    let timeRemaining = timeLimit;

    const timer = setInterval(function() {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        
        timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Change color when less than 5 minutes remaining
        if (timeRemaining <= 300) {
            timerElement.classList.add('text-warning');
        }
        
        // Change color when less than 1 minute remaining
        if (timeRemaining <= 60) {
            timerElement.classList.remove('text-warning');
            timerElement.classList.add('text-danger');
        }
        
        timeRemaining--;
        
        // Auto-submit when time is up
        if (timeRemaining < 0) {
            clearInterval(timer);
            alert('Time is up! Submitting quiz automatically.');
            document.getElementById('quiz-form').submit();
        }
    }, 1000);
}

// Lesson progress tracking
function trackLessonProgress() {
    let timeSpent = 0;
    const startTime = Date.now();
    
    // Track time spent on page
    setInterval(function() {
        timeSpent = Math.floor((Date.now() - startTime) / 1000);
    }, 1000);
    
    // Send progress update when user leaves page
    window.addEventListener('beforeunload', function() {
        if (timeSpent > 30) { // Only track if user spent more than 30 seconds
            navigator.sendBeacon('/api/track-progress', JSON.stringify({
                lessonId: getLessonId(),
                timeSpent: timeSpent
            }));
        }
    });
}

// Get lesson ID from URL
function getLessonId() {
    const pathParts = window.location.pathname.split('/');
    const lessonIndex = pathParts.indexOf('lesson');
    return lessonIndex !== -1 ? pathParts[lessonIndex + 1] : null;
}

// File upload preview
function previewFile(input) {
    const file = input.files[0];
    const preview = document.getElementById('file-preview');
    
    if (file && preview) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (file.type.startsWith('image/')) {
                preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px;">`;
            } else {
                preview.innerHTML = `<p class="text-muted">File selected: ${file.name}</p>`;
            }
        };
        reader.readAsDataURL(file);
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Copied to clipboard!', 'success');
    }).catch(function() {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(function() {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// AJAX form submission
function submitFormAjax(formId, successCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
        
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message, 'success');
                if (successCallback) successCallback(data);
            } else {
                showToast(data.message, 'danger');
            }
        })
        .catch(error => {
            showToast('An error occurred. Please try again.', 'danger');
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
            }
        });
    });
}