# backend/core/templatetags/translate.py
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Complete translation dictionary for the entire app
TRANSLATIONS = {
    # Navigation
    'Dashboard': 'Dashibodi',
    'Drought Status': 'Hali ya Ukame',
    'Carbon Credits': 'Hisa za Kaboni',
    'Payout History': 'Historia ya Malipo',
    'Farm Map': 'Ramani ya Shamba',
    'Profile': 'Wasifu',
    'Profile Settings': 'Mipangilio ya Wasifu',
    'Logout': 'Toka',
    'Settings': 'Mipangilio',
    
    # Buttons
    'Save Changes': 'Hifadhi Mabadiliko',
    'Cancel': 'Ghairi',
    'Register': 'Jisajili',
    'Login': 'Ingia',
    'Submit': 'Wasilisha',
    'Update': 'Sasisha',
    'Delete': 'Futa',
    'Edit': 'Hariri',
    'View All': 'Tazama Zote',
    'Filter': 'Chuja',
    
    # Profile Page
    'Personal Information': 'Taarifa Binafsi',
    'Full Name': 'Jina Kamili',
    'Phone Number': 'Nambari ya Simu',
    'Contact support to change phone number': 'Wasiliana na msaada kubadilisha nambari ya simu',
    'Gender': 'Jinsia',
    'Female': 'Mwanamke',
    'Male': 'Mwanamume',
    'Other': 'Nyingine',
    'Preferred Language': 'Lugha Unayopendelea',
    'English': 'Kiingereza',
    'Kiswahili': 'Kiswahili',
    
    # Location
    'Location': 'Mahali',
    'County': 'Kaunti',
    'Village/Town': 'Kijiji/Mji',
    
    # Farm Details
    'Farm Details': 'Maelezo ya Shamba',
    'Crop Type': 'Aina ya Mazao',
    'Farm Size (acres)': 'Ukubwa wa Shamba (ekari)',
    'Maize': 'Mahindi',
    'Beans': 'Maharage',
    'Mixed': 'Mchanganyiko',
    'Vegetables': 'Mboga',
    'acres': 'ekari',
    'acres covered': 'ekari zimefunikwa',
    'tons': 'tani',
    'days': 'siku',
    'km away': 'km mbali',
    'to': 'mpaka',
    
    # Regenerative Practices
    'Regenerative Practices': 'Mbinu za Kurejeshe Udongo',
    'Manure / Compost': 'Mbolea / Mboji',
    'Mulching': 'Kufunika Udongo',
    'Minimum Tillage': 'Kulima Kidogo',
    'Cover Crops': 'Mazao ya Kufunika',
    
    # Notifications
    'Notification Preferences': 'Mapendeleo ya Arifa',
    'SMS Alerts': 'Arifa za SMS',
    'Email Alerts': 'Arifa za Barua Pepe',
    'Drought Warnings': 'Onyo la Ukame',
    'Payout Confirmations': 'Uthibitisho wa Malipo',
    
    # Payment
    'Payment Settings': 'Mipangilio ya Malipo',
    'M-Pesa Phone Number': 'Nambari ya Simu ya M-Pesa',
    'All payouts will be sent to this number': 'Malipo yote yatatumwa kwa nambari hii',
    
    # Security
    'Security': 'Usalama',
    'Change PIN': 'Badilisha PIN',
    'Current PIN': 'PIN ya Sasa',
    'New PIN': 'PIN Mpya',
    'Confirm New PIN': 'Thibitisha PIN Mpya',
    'Login History': 'Historia ya Kuingia',
    'Today': 'Leo',
    'Yesterday': 'Jana',
    
    # Danger Zone
    'Danger Zone': 'Eneo la Hatari',
    'Once you deactivate your account, you will no longer receive drought insurance payouts.': 'Ukizima akaunti yako, hutapokea malipo ya bima ya ukame tena.',
    'Deactivate Account': 'Zima Akaunti',
    
    # Dashboard Overview
    'Insurance Status': 'Hali ya Bima',
    'Active': 'Inafanya Kazi',
    'Drought Risk': 'Hatari ya Ukame',
    'HIGH': 'KUBWA',
    'MEDIUM': 'WASTANI',
    'days dry': 'siku kavu',
    'Carbon Sequestered': 'Kaboni Iliyohifadhiwa',
    'Value': 'Thamani',
    'Total Payouts': 'Malipo Yote',
    'transactions': 'shughuli',
    'Recent Payouts': 'Malipo ya Hivi Karibuni',
    'View all': 'Tazama Zote',
    'Completed': 'Imekamilika',
    'No payouts yet': 'Hakuna malipo bado',
    'Your first drought alert will appear here': 'Onyo lako la kwanza la ukame litaonekana hapa',
    'Tip: Increase your carbon credits': 'Kidokezo: Ongeza hisa zako za kaboni',
    'Adding more regenerative practices like cover crops or agroforestry can double your carbon earnings.': 'Kuongeza mbinu za kurejeshe udongo kama vile mazao ya kufunika au kilimo cha miti kunaweza kuongeza mara mbili mapato yako ya kaboni.',
    'Need help?': 'Unahitaji msaada?',
    'Dial': 'Piga',
    'for USSD support or call': 'kwa msaada wa USSD au piga',
    
    # Drought Status
    'Drought Status Monitor': 'Kifuatiliaji Hali ya Ukame',
    'Current Drought Status': 'Hali ya Sasa ya Ukame',
    'Drought threshold': 'Kiwango cha ukame',
    'consecutive dry days': 'siku kavu mfululizo',
    'Actual Rainfall (10 days)': 'Mvua Halisi (siku 10)',
    'Expected Rainfall (10 days)': 'Mvua Inayotarajiwa (siku 10)',
    'mm': 'mm',
    'Payout Triggered!': 'Malipo Yameanzishwa!',
    'has been sent to your M-Pesa': 'yame tumwa kwa M-Pesa yako',
    'Warning': 'Onyo',
    'day(s) to trigger': 'siku (za) kuanzisha',
    'If no rain in': 'Kama hakuna mvua ndani ya',
    'day(s), you will receive': 'siku, utapokea',
    'Daily Rainfall (Last 30 Days)': 'Mvua ya Kila Siku (Siku 30 zilizopita)',
    'Date': 'Tarehe',
    'Rainfall (mm)': 'Mvua (mm)',
    'Normal (mm)': 'Kawaida (mm)',
    'Status': 'Hali',
    'Dry Day': 'Siku Kavu',
    'Wet Day': 'Siku ya Mvua',
    'Drought History': 'Historia ya Ukame',
    'days without rain': 'siku bila mvua',
    'No drought events recorded': 'Hakuna matukio ya ukame yaliyorekodiwa',
    'Your farm has been drought-free since registration': 'Shamba lako limekuwa bila ukame tangu usajili',
    'KES': 'KES',
    
    # Carbon Credits
    'Tons CO₂ Sequestered': 'Tani za CO₂ Zilizohifadhiwa',
    'Carbon Value (USD)': 'Thamani ya Kaboni (USD)',
    'Carbon Value (KES)': 'Thamani ya Kaboni (KES)',
    'How Your Carbon Credits Work': 'Jinsi Hisa Zako za Kaboni Zinavyofanya Kazi',
    'Your soil captures CO₂': 'Udongo wako unachukua CO₂',
    'Regenerative practices sequester carbon': 'Mbinu za kurejeshe udongo huhifadhi kaboni',
    'Companies buy credits': 'Makampuni hununua hisa',
    'Airlines, tech companies offset emissions': 'Mashirika ya ndege, makampuni ya teknolojia hulipa fidia uzalishaji',
    'You get free insurance + bonus': 'Unapata bima ya bure + bonasi',
    'How Your Credits Are Calculated': 'Jinsi Hisa Zako Zinavyohesabiwa',
    'Base sequestration (conventional farming)': 'Uhifadhi wa kawaida (kilimo cha kawaida)',
    'Total Annual Credits': 'Jumla ya Hisa za Mwaka',
    'Revenue Distribution (70-20-10 Split)': 'Ugawaji wa Mapato (70-20-10)',
    'Insurance Pool': 'Bwawa la Bima',
    'Your Bonus': 'Bonasi Yako',
    'Operations': 'Uendeshaji',
    'Companies Buying Your Carbon Credits': 'Makampuni Yanayonunua Hisa Zako za Kaboni',
    'Your credits are verified by Verra (VM0042 methodology)': 'Hisa zako zimethibitishwa na Verra (Mbinu ya VM0042)',
    'Annual Bonus History': 'Historia ya Bonasi ya Mwaka',
    'Year': 'Mwaka',
    'Credits (tons)': 'Hisa (tani)',
    'Bonus (KES)': 'Bonasi (KES)',
    'Paid': 'Imelipwa',
    'Pending': 'Inasubiri',
    'No bonus history yet': 'Hakuna historia ya bonasi bado',
    'Your first annual bonus will be calculated after 12 months': 'Bonasi yako ya kwanza ya mwaka itahesabiwa baada ya miezi 12',
    
    # Payout History
    'Number of Events': 'Idadi ya Matukio',
    'Average Payout': 'Malipo ya Wastani',
    'Last Payout': 'Malipo ya Mwisho',
    'Date Range': 'Kipindi cha Tarehe',
    'Last 30 days': 'Siku 30 zilizopita',
    'Last 6 months': 'Miezi 6 iliyopita',
    'Last year': 'Mwaka uliopita',
    'All time': 'Muda wote',
    'Payout Type': 'Aina ya Malipo',
    'All types': 'Aina zote',
    'Drought Insurance': 'Bima ya Ukame',
    'Carbon Bonus': 'Bonasi ya Kaboni',
    'Women Empowerment': 'Uwezeshaji Wanawake',
    'Payout Transactions': 'Shughuli za Malipo',
    'Drought Duration': 'Muda wa Ukame',
    'Amount (KES)': 'Kiasi (KES)',
    'Type': 'Aina',
    'Transaction ID': 'Kitambulisho cha Shughuli',
    'No payout transactions yet': 'Hakuna shughuli za malipo bado',
    'When drought triggers a payout, it will appear here': 'Ukame ukianza malipo, utaonekana hapa',
    'Payouts Over Time': 'Malipo kwa Muda',
    'Payout Amount (KES)': 'Kiasi cha Malipo (KES)',
    "Didn't receive a payout?": 'Hukupokea malipo?',
    'Contact our support team at': 'Wasiliana na timu yetu ya msaada kwa',
    'or dial': 'au piga',
    
    # Farm Map
    'Farm Name': 'Jina la Shamba',
    'GPS Coordinates': 'Kuratibu za GPS',
    'Size': 'Ukubwa',
    'Soil Type': 'Aina ya Udongo',
    'Satellite Layers': 'Tabaka za Setilaiti',
    'Rainfall (Last 7 days)': 'Mvua (Siku 7 zilizopita)',
    'Vegetation Health (NDVI)': 'Afya ya Mimea (NDVI)',
    'Soil Moisture': 'Unyevu wa Udongo',
    'Share Your Location': 'Shiriki Mahali Pako',
    'Share with Cooperative': 'Shiriki na Ushirika',
    'Download Map': 'Pakua Ramani',
    'Nearby RainBank Farms': 'Shamba za RainBank Zilizo Karibu',
    'No nearby farms found': 'Hakuna shamba za karibu zilizopatikana',
    'Protected by RainBank': 'Inalindwa na RainBank',
    'acres of': 'ekari za',
    'Location sharing link generated! Share with your cooperative.': 'Kiungo cha kushiriki mahali kimezalishwa! Shiriki na ushirika wako.',
    'Map download started. Check your downloads folder.': 'Upakuaji wa ramani umeanza. Angalia folda yako ya kupakua.',
    
    # Alerts & Messages
    'Profile updated successfully!': 'Wasifu umesasishwa kikamilifu!',
    'Please login to access your dashboard.': 'Tafadhali ingia kufikia dashibodi yako.',
    'Registration successful!': 'Usajili umefanikiwa!',
    'Welcome back!': 'Karibu tena!',
    'Invalid PIN. Please try again.': 'PIN si sahihi. Tafadhali jaribu tena.',
    'Phone number not found. Please register first.': 'Nambari ya simu haikupatikana. Tadhali jisajili kwanza.',
    'You have been logged out successfully.': 'Umetoka kikamilifu.',
    'Reset instructions sent to your phone.': 'Maagizo ya kuweka upya yametumwa kwa simu yako.',
    
    # Dashboard Navbar
    'My Profile': 'Wasifu Wangu',
    'Help & Support': 'Msaada & Usaidizi',
    
    # Rainfall Chart
    'Actual Rainfall (mm)': 'Mvua Halisi (mm)',
    'Drought Threshold': 'Kiwango cha Ukame',
    'Dashed line shows drought threshold (70% of normal)': 'Mstari wa vitone unaonyesha kiwango cha ukame (70% ya kawaida)',
    
    # Carbon Chart
    'Carbon Sequestered': 'Kaboni Iliyohifadhiwa',
    'Annual Target Remaining': 'Lengo la Mwaka Lililobaki',
    'Your annual carbon value': 'Thamani yako ya kaboni ya mwaka',
    'You earn 20% bonus annually': 'Unapata bonasi ya 20% kila mwaka',
    
    # Drought Alert
    'Drought Alert': 'Onyo la Ukame',
    'Your farm has gone': 'Shamba lako limepita',
    'without adequate rainfall.': 'bila mvua ya kutosha.',
    'Payout triggered! Check your M-Pesa.': 'Malipo yameanzishwa! Angalia M-Pesa yako.',
    'If this continues for': 'Kama hii itaendelea kwa',
    'more day(s), you will receive an automatic payout of': 'siku zaidi, utapokea malipo ya kiotomatiki ya',
    'days without rain': 'siku bila mvua',
    
    # Rain Alert Banner
    'Rainfall Trend (Last 7 Days)': 'Mwelekeo wa Mvua (Siku 7 zilizopita)',
    'Carbon Credits Breakdown': 'Uchambuzi wa Hisa za Kaboni',
}

@register.simple_tag(takes_context=True)
def translate(context, text):
    """Translate text based on current language"""
    request = context.get('request')
    if request:
        language = getattr(request, 'LANGUAGE', 'en')
        if language == 'sw':
            # Check if we have a translation
            if text in TRANSLATIONS:
                return TRANSLATIONS[text]
            # If not found, return original text
            return text
    return text

@register.filter
def translate_filter(text, request):
    """Filter to translate text"""
    if not text:
        return text
    language = getattr(request, 'LANGUAGE', 'en')
    if language == 'sw' and text in TRANSLATIONS:
        return TRANSLATIONS[text]
    return text