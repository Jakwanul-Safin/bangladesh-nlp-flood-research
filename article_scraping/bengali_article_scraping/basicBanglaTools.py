from google_trans_new import google_translator  
translator = google_translator()  


numbersBengaliEnglish = {b:e for b, e in zip('০১২৩৪৫৬৭৮৯', '0123456789')}
monthsBengaliEnglish = {b:e for b, e in zip(
    ['জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর', "জানু", "ফেব"], 
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 
     "January", 'February'])}
timeWordBegnaliEnglish = {b:e for b, e in zip(["আগে", "দিন"], ["ago", "days"])}


def translate(phrase):
    """Convenience function for translating Begali to English"""
    return translator.translate(phrase)

def translateBengaliDate(date):
    for k, v in numbersBengaliEnglish.items():
        date = date.replace(k, v)
                            
    for k, v in monthsBengaliEnglish.items():
        date = date.replace(k, v)
        
    for k, v in timeWordBegnaliEnglish.items():
        date = date.replace(k, v)
    
    return date