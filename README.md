# 🌧️ RainBank
### Pay-When-It-Doesn't-Rain Insurance for African Smallholders

[![Carbon Credits](https://img.shields.io/badge/Funded%20By-Soil%20Carbon%20Credits-2E7D32)](https://github.com)
[![Data Source](https://img.shields.io/badge/Weather%20Data-NASA%20POWER-0288D1)](https://power.larc.nasa.gov)
[![Platform](https://img.shields.io/badge/Payments-M--Pesa-00A650)](https://www.safaricom.co.ke)

> **The first zero-premium parametric insurance protocol that turns regenerative farming practices into drought resilience.**



## 🎯 The Problem

Smallholder farmers in Kenya lose **$5B annually** to drought, yet **97% have no insurance** because:
- ❌ Premiums are upfront (3,000 KES) when cash is needed for seeds
- ❌ Claims take 3-6 months with paperwork and adjusters
- ❌ Mistrust of traditional insurers

Meanwhile, their soil traps **0.5 tonnes CO2e/acre/year** through mulching and minimal tillage—worth $15/tonne on carbon markets they cannot access.



## 💡 The Solution

**RainBank** bridges carbon finance and climate resilience:

Regenerative Farming ───► Carbon Credits ───► Insurance Premium ───► Instant Payouts (Farmer) (Sold to buyers) (Zero cost) (M-Pesa)


### How It Works (2-Minute Flow)

1. **Dial `*384#`** → 2-minute registration via USSD (works on $15 feature phones)
2. **Carbon Qualification** → Answer 3 questions about mulch/manure/tillage
3. **Satellite Monitoring** → NASA POWER API tracks rainfall daily (1km grids)
4. **Automatic Trigger** → <70% average rainfall for 10 days = instant payout
5. **M-Pesa Deposit** → 2,500 KES hits phone within 2 hours, no claim forms

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Django 6.0 | API, USSD, business logic |
| **SMS/USSD** | Africa's Talking | USSD gateway (`*384#`) |
| **Satellite Data** | NASA POWER API | Daily rainfall (1km grid) |
| **Payouts** | M-Pesa Daraja API | STK push to farmers |
| **Dashboard** | Streamlit | Live map + analytics |
| **Carbon Verification** | Verra VM0042 | Soil carbon methodology |
| **Database** | SQLite / PostgreSQL | Farmer records |


---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Africa's Talking sandbox account (free)
- M-Pesa Daraja sandbox credentials (free)

### Installation

```bash
# Clone the repo
git clone https://github.com/Wendy-Okoth/RainBank.git
cd RainBank

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver

### Expose with ngrok (for USSD testing)

```bash
ngrok http 8000
```

Then set Africa's Talking USSD callback to:

`https://your-ngrok-url/notifications/ussd/`

> **Note:** Your ngrok URL changes each time you restart. Update the callback URL in Africa's Talking dashboard.
