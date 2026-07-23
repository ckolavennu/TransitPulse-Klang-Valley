# TransitPulse Klang Valley — GitHub Push Guide

Use these steps after the local dashboard is working.

---

## 1. Open the project folder

```bash
cd path/to/transitpulse_klang_valley
```

---

## 2. Check Git status

```bash
git status
```

---

## 3. Initialise Git if needed

If the folder is not already a Git repository:

```bash
git init
```

---

## 4. Add files

```bash
git add .
```

---

## 5. Commit files

```bash
git commit -m "Initial TransitPulse dashboard MVP"
```

---

## 6. Create a GitHub repository

Create a new GitHub repository named:

```text
transitpulse-klang-valley
```

Do not initialise it with a README if your local project already has one.

---

## 7. Connect local repo to GitHub

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/transitpulse-klang-valley.git
```

---

## 8. Push to GitHub

```bash
git branch -M main
git push -u origin main
```

---

## 9. If GitHub rejects the push

If GitHub says the remote has files that your local repo does not have, run:

```bash
git pull origin main --allow-unrelated-histories
```

Resolve any conflicts, then:

```bash
git add .
git commit -m "Resolve initial repository merge"
git push -u origin main
```

---

## 10. Streamlit Deployment

After pushing to GitHub:

1. Go to Streamlit Community Cloud
2. Select the GitHub repository
3. Set the main file path:

```text
dashboard/app.py
```

4. Deploy
5. Add the deployed dashboard link to README.md
