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
const likedSet = new Set(); // track liked submissions in session

async function likeSubmission(id) {
    const buttons = document.querySelectorAll(`.like-btn[data-id="${id}"]`);

    // Optimistic UI update
    const isLiked = likedSet.has(id);
    buttons.forEach(btn => {
        const countEl = btn.querySelector('.like-count');
        const current = parseInt(countEl.textContent) || 0;

        if (isLiked) {
            countEl.textContent = Math.max(0, current - 1);
            btn.classList.remove('liked');
            likedSet.delete(id);
        } else {
            countEl.textContent = current + 1;
            btn.classList.add('liked');
            likedSet.add(id);
        }
    });

    try {
        const res = await fetch(`/like/${id}`, { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            // Sync with server count
            buttons.forEach(btn => {
                btn.querySelector('.like-count').textContent = data.likes;
                if (data.action === 'liked') {
                    btn.classList.add('liked');
                    likedSet.add(id);
                } else {
                    btn.classList.remove('liked');
                    likedSet.delete(id);
                }
            });
        }
    } catch (err) {
        // Revert optimistic update on error
        buttons.forEach(btn => {
            const countEl = btn.querySelector('.like-count');
            const current = parseInt(countEl.textContent) || 0;
            countEl.textContent = isLiked ? current + 1 : Math.max(0, current - 1);
            if (isLiked) {
                btn.classList.add('liked');
                likedSet.add(id);
            } else {
                btn.classList.remove('liked');
                likedSet.delete(id);
            }
        });
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
            body: JSON.stringify({ code: code, format: format })
        });

        if (!res.ok) {
            throw new Error(`HTTP error: ${res.status}`);
        }

        const data = await res.json();

        if (data.explanation) {
            document.getElementById('modalBody').innerHTML = `
                <p style="line-height:1.8">${data.explanation.replace(/\n/g, '<br>')}</p>
            `;
        } else if (data.error) {
            document.getElementById('modalBody').innerHTML = `<p style="color:var(--text-muted)">${data.error}</p>`;
        } else {
            document.getElementById('modalBody').innerHTML = '<p style="color:var(--text-muted)">Could not generate explanation. Try again!</p>';
        }
    } catch (err) {
        console.error('Learn concept error:', err);
        document.getElementById('modalBody').innerHTML = '<p style="color:var(--text-muted)">Something went wrong. Try again!</p>';
    }
}

function openModal() {
    const modal = document.getElementById('learnModal');
    const overlay = document.getElementById('modalOverlay');
    if (modal) modal.classList.add('open');
    if (overlay) overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('learnModal');
    const overlay = document.getElementById('modalOverlay');
    if (modal) modal.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
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
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
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
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
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
