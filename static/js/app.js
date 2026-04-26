// ─── SERVICE WORKER REGISTRATION ───
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('SW registered:', reg.scope))
            .catch(err => console.log('SW registration failed:', err));
    });
}

// ─── FORMAT SELECT ───
const formatSelect = document.getElementById('formatSelect');
const languageGroup = document.getElementById('languageGroup');

if (formatSelect && languageGroup) {
    formatSelect.addEventListener('change', () => {
        languageGroup.style.display = formatSelect.value === 'pseudocode' ? 'none' : 'flex';
    });
}

// ─── LIKE / UNLIKE TOGGLE ───
async function likeSubmission(id) {
    try {
        const res = await fetch(`/like/${id}`, { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            // Update like count on all matching buttons
            document.querySelectorAll(`.like-btn[data-id="${id}"] .like-count`)
                .forEach(el => el.textContent = data.likes);

            // Toggle button style
            document.querySelectorAll(`.like-btn[data-id="${id}"]`)
                .forEach(btn => {
                    if (data.action === 'liked') {
                        btn.style.color = '#c0392b';
                        btn.style.borderColor = '#c0392b';
                        btn.style.background = 'rgba(192,57,43,0.08)';
                    } else {
                        btn.style.color = '';
                        btn.style.borderColor = '';
                        btn.style.background = '';
                    }
                });
        }
    } catch (err) {
        console.error('Like error:', err);
    }
}

// ─── LEARN CONCEPT MODAL ───
async function learnConcept(code, format) {
    openModal();
    document.getElementById('modalBody').innerHTML = '<div class="loading">Asking Groq... 🤔</div>';

    try {
        const res = await fetch('/explain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, format })
        });
        const data = await res.json();

        if (data.explanation) {
            document.getElementById('modalBody').innerHTML = `
                <p>${data.explanation.replace(/\n/g, '<br>')}</p>
            `;
        } else {
            document.getElementById('modalBody').innerHTML = '<p>Could not generate explanation. Try again!</p>';
        }
    } catch (err) {
        document.getElementById('modalBody').innerHTML = '<p>Something went wrong. Try again!</p>';
    }
}

function openModal() {
    document.getElementById('learnModal').classList.add('open');
    document.getElementById('modalOverlay').classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('learnModal').classList.remove('open');
    document.getElementById('modalOverlay').classList.remove('open');
    document.body.style.overflow = '';
}

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});

// ─── PUSH NOTIFICATIONS ───
const notifyBtn = document.getElementById('notifyBtn');

if (notifyBtn) {
    notifyBtn.addEventListener('click', async () => {
        if (!('Notification' in window)) {
            showToast('Notifications not supported in this browser.');
            return;
        }

        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            showToast('Notification permission denied.');
            return;
        }

        try {
            const reg = await navigator.serviceWorker.ready;
            const vapidPublicKey = notifyBtn.dataset.vapidKey || '';

            if (!vapidPublicKey) {
                showToast('Notifications configured! 🔔');
                return;
            }

            const subscription = await reg.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
            });

            await fetch('/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ subscription })
            });

            notifyBtn.textContent = '✓ Subscribed';
            notifyBtn.style.color = 'var(--green)';
            showToast("You'll be notified daily! 🔔");
        } catch (err) {
            console.error('Subscription error:', err);
            showToast('Could not subscribe. Try again.');
        }
    });
}

// ─── TOAST ───
function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        color: var(--text);
        font-family: 'Fira Code', monospace;
        font-size: 0.8rem;
        padding: 10px 20px;
        border-radius: 8px;
        z-index: 9999;
        animation: fadeUp 0.3s ease;
        white-space: nowrap;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ─── VAPID KEY HELPER ───
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}
