# 🌧️ RainBank

## Pay-When-It-Doesn't-Rain Insurance for African Smallholders

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://www.djangoproject.com/)
[![Africa's Talking](https://img.shields.io/badge/Africa's%20Talking-USSD-blue)](https://africastalking.com/)

---

## 🎯 The Problem

Every 3–5 years, drought destroys harvests across East Africa.

- **10 million** smallholder farmers affected
- **97%** have no insurance
- **$5 billion** lost annually

**Why no insurance?**
- ❌ Premiums too expensive (upfront cash needed for seeds)
- ❌ Claims take 3–6 months with paperwork
- ❌ No trust in traditional insurers

Meanwhile, farmers already practice regenerative farming (manure, mulching, minimal tillage) — without knowing it generates **carbon credits** worth $10–15 per ton.

---

## 💡 The Solution

RainBank turns soil carbon into drought protection.

```
Regenerative Farming → Carbon Credits → Insurance Fund → Automatic Payout
```

**Zero premium. Automatic. Instant.**

---

## ⚙️ How It Works

| Step | Action | Technology |
|------|--------|------------|
| **1** | Farmer dials `*384#` | USSD (any phone) |
| **2** | Register name + location + crop | 2 minutes |
| **3** | Satellite monitors rainfall daily | NASA POWER API |
| **4** | Drought detected (<70% rain for 10 days) | Python logic |
| **5** | Automatic M-Pesa payout | SMS + Daraja API |

**No claims. No paperwork. No waiting.**

---

## 🌍 Carbon Credit Engine

```
Farmer uses manure/mulch
↓
Soil traps 1.5 tons CO2/acre/year
↓
Carbon credit verified (Verra VM0042)
↓
Sold to companies ($10-15/ton)
↓
70% to payout pool | 20% to farmer | 10% operations
```

**The farmer pays nothing. The soil pays for itself.**

---

## 👩‍🌾 Inclusivity by Design

| Group | Feature |
|-------|---------|
| **Women** | Payouts to her own M-Pesa, not husband's |
| **Blind / low literacy** | Voice-based USSD prompts |
| **Deaf** | SMS alerts (visual) |
| **Mobility impaired** | No travel needed — fully remote |
| **Women's cooperatives** | Bonus carbon credits |

**No one is left behind.**

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Django 6.0 | API, USSD, business logic |
| **SMS/USSD** | Africa's Talking | USSD gateway (`*384#`) |
| **Satellite Data** | NASA POWER API | Daily rainfall (1km grid) |
| **Payouts** | M-Pesa Daraja API | STK push to farmers |
| **Dashboard** | Streamlit | Live map + analytics |
| **Carbon Verification** | Satellite + AI | Soil carbon estimation (industry standards ready) |hodology |
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
```

### Expose with ngrok (for USSD testing)

```bash
ngrok http 8000
```

Then set Africa's Talking USSD callback to:

```
https://your-ngrok-url/notifications/ussd/
```

> **Note:** Your ngrok URL changes each time you restart. Update the callback URL in Africa's Talking dashboard.

---

## 📱 Demo

### Live Demo Flow (3 minutes)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Dial `*384*12345#` | Welcome to RainBank |
| 2 | Press 1 | Enter your name |
| 3 | Type "Jane" | Enter location |
| 4 | Type "Machakos" | Registration complete |
| 5 | Press 2 | Check drought status |
| 6 | Trigger drought (dashboard) | SMS payout received |

### SMS Example

```
RainBank Alert!
Drought detected in Machakos.
2,500 KES sent to your M-Pesa.
No claim needed.
```

---

## 📊 Impact (2-Year Scale)

| Metric | Target |
|--------|--------|
| Farmers protected | 5,000,000 |
| CO₂ removed | 250,000 tons/year |
| Carbon revenue | $2.5M/year |
| Payout pool | $1.75M/year |
| Jobs created | 1,000+ |

---

##  SDGs Addressed

✅ **SDG 1** - No Poverty

✅ **SDG 2** - Zero Hunger

✅ **SDG 5** - Gender Equality

✅ **SDG 13** - Climate Action

---

## 👥 Team

| Role | Name | Responsibility |
|------|------|-----------------|



##  Hackathon Submission

**Event:** Climate Hackathon 2026

**Theme:** Carbon & Data + Finance & Resilience

**Track:** Climate & Green Economy

---

## 📄 License

MIT License - free for non-commercial and humanitarian use.

---

## 📬 Contact & Links

**GitHub:** [github.com/Wendy-Okoth/RainBank](https://github.com/Wendy-Okoth/RainBank)

**Live Demo:** [Insert URL here]

**Pitch Deck:** [Insert link here]

**Demo Video:** [Insert link here]

---

## 🙏 Acknowledgments

- **Africa's Talking** - USSD/SMS infrastructure
- **NASA POWER** - Free satellite rainfall data
- **Safaricom** - M-Pesa Daraja API
- **Verra** - Carbon credit methodology (VM0042)

---

**Made with ❤️ for climate resilience and farmer prosperity.**
