# 📋 Simple Deployment Checklist - Print This!

## Before You Start
- [ ] Your GitHub repository is ready
- [ ] You have a computer with internet
- [ ] You have a credit/debit card for payments
- [ ] Budget: $15-30 for first month

---

## Step 1: Domain (15 minutes)
- [ ] Go to namecheap.com
- [ ] Search for domain name (try `jossiefancies.com`)
- [ ] Buy domain (~$12/year)
- [ ] Save login details somewhere safe
- [ ] **Don't configure anything yet**

---

## Step 2: Railway Setup (10 minutes)
- [ ] Go to railway.app
- [ ] Sign up with GitHub
- [ ] Connect your jossie2 repository
- [ ] Add payment method
- [ ] Create new project

---

## Step 3: Get Secret Key (5 minutes)
- [ ] Open terminal in your project folder
- [ ] Run: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- [ ] Copy the long key that appears
- [ ] Keep it safe - you'll paste it in Railway

---

## Step 4: Railway Deployment (20 minutes)
- [ ] In Railway: New Project → Deploy from GitHub
- [ ] Select your jossie2 repository
- [ ] Go to "Variables" tab
- [ ] Add these variables:
  - [ ] `SECRET_KEY` = (paste your generated key)
  - [ ] `DEBUG` = `False`
  - [ ] `ALLOWED_HOSTS` = `yourdomain.com,www.yourdomain.com,*.railway.app`
  - [ ] `DJANGO_SETTINGS_MODULE` = `jossie_fancies.settings_production`
- [ ] Add PostgreSQL database (New → Database → PostgreSQL)
- [ ] Wait for green checkmark

---

## Step 5: Connect Domain (15 minutes)
- [ ] In Railway: Settings → Domains → Custom Domain
- [ ] Enter your domain name
- [ ] Copy the DNS settings Railway shows
- [ ] Go to Namecheap → Domain List → Manage → Advanced DNS
- [ ] Add the DNS records Railway provided
- [ ] Wait 30 minutes

---

## Step 6: Test Website (10 minutes)
- [ ] Visit your domain: https://yourdomain.com
- [ ] Check if it loads (green lock = secure)
- [ ] Test product pages
- [ ] Test cart functionality
- [ ] Access admin: yourdomain.com/admin-login/

---

## 🎉 Success Indicators
- [ ] Website loads at your domain
- [ ] Green lock icon (HTTPS working)
- [ ] Products display correctly
- [ ] WhatsApp button works
- [ ] Admin panel accessible
- [ ] No error messages

---

## If Stuck - Check These:
1. **Website won't load**: Wait longer (DNS takes time)
2. **Application Error**: Check Railway logs
3. **Admin won't work**: Create superuser in Railway
4. **Database errors**: Make sure PostgreSQL is added

---

## Monthly Costs After Setup:
- Domain: ~$1/month
- Railway: $5-15/month
- **Total: $6-16/month**

## 🆘 Emergency Help:
- Railway Discord: railway.app/discord
- Check Railway deployment logs
- Google the error message

**You got this! 💪**