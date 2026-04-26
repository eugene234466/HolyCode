# ✦ HolyCode

> Scripture written as code. Daily devotionals and coding challenges for developers of faith.

HolyCode is a community platform where Bible verses are interpreted as actual code or pseudocode. Every day, a new devotional drops automatically and a new challenge invites developers (and non-developers) to write their own interpretation.

---

## 🌐 Live Demo

[holycode.onrender.com](https://holycode.onrender.com)

---

## ✨ Features

- **Daily Devotional** — OurManna API fetches the verse of the day, Groq writes a code snippet interpretation in any programming language
- **Daily Challenge** — Groq picks a separate scripture and writes a challenge prompt for the community
- **Anonymous Submissions** — No account needed. Submit code or pseudocode interpretations
- **Community Feed** — Like and vote on submissions by other developers
- **Learn This Concept** — Click any submission to get a plain English explanation of the programming concept used, powered by Groq
- **Code Card** — Generate a downloadable styled image of any submission
- **AI Image** — Generate an AI image inspired by the scripture using Pollinations.ai
- **PWA** — Installable on mobile and desktop, works offline
- **Push Notifications** — Subscribe to get notified when the daily devotional and challenge drop
- **Archive** — Browse all past devotionals and challenges

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | PostgreSQL (Supabase) |
| AI | Groq (llama-3.3-70b-versatile) |
| Scripture API | OurManna API |
| Image Generation | Pillow + Pollinations.ai |
| Scheduler | APScheduler |
| Push Notifications | pywebpush (VAPID) |
| Deployment | Render |

---

## 📁 Project Structure

```
holycode/
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── images/
│   └── manifest.json
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── archive.html
│   └── submission.html
├── services/
│   ├── bible.py
│   ├── groq_ai.py
│   ├── image_gen.py
│   └── scheduler.py
├── database/
│   └── db.py
├── sw.js
├── app.py
├── config.py
├── requirements.txt
└── .env
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/holycode.git
cd holycode
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the root:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@host:5432/postgres
BIBLE_API_URL=https://beta.ourmanna.com/api/v1/get/?format=json&order=verse
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_EMAIL=mailto:your@email.com
```

### 4. Generate VAPID keys (for push notifications)

```bash
python -m py_webpush generate_vapid_keys
```

### 5. Run the app

```bash
python app.py
```

Visit `http://localhost:5000`

---

## ☁️ Deploying to Render

1. Push your project to GitHub
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repo
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Add all environment variables from your `.env` in the Render dashboard
6. Deploy!

---

## 📖 How It Works

```
Every day at midnight:
  1. OurManna API → fetches verse of the day
  2. Groq → writes a code snippet devotional from the verse
  3. Groq → independently picks a challenge verse + writes prompt
  4. Both are saved to the database
  5. Push notifications sent to subscribers

Users:
  1. Visit the site → see today's devotional + challenge
  2. Submit their own code or pseudocode interpretation
  3. Like other submissions
  4. Click "Learn This Concept" → Groq explains the programming concept
  5. Download code card or generate AI image
```

---

## 🤝 Contributing

This project is open to contributions! Feel free to:
- Add more programming languages to the submission form
- Improve the code card design
- Add syntax highlighting
- Suggest new features

---

## 📜 License

MIT License — free to use, modify and distribute.

---

## 🙏 Built With Faith

> *"Whatever you do, work at it with all your heart, as working for the Lord."*
> — Colossians 3:23

Built by [Eugene](https://github.com/yourusername) • Powered by Groq & Flask
