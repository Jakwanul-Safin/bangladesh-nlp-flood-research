from datetime import datetime

#bengaliTextChars = set(' ৫এঊ্টধহ‘৯ি১ঠূ০’আ৮ডইতঞণঐশ৭২ঙ৬।াড়ছলঢ়যঃরৌোংউষদগবঢঈসচঝঅীথজখও )়;,কঘেয়ঋমঔুভফনপঁ৩ৎ৪ৈ–ৃ-')

__bengali_unicode_exeptions__ = set((2436, 2445, 2446, 2449, 2450, 2473, 2481, 2483, 2484, 2485, 2490, 2491, 2501, 2502, 2505, 2506, 2526, 2532, 2533)) | set(range(2511, 2519)) | set(range(2520, 2524))
bengaliTextChars = set(chr(x) for x in range(2432, 2559) if x not in __bengali_unicode_exeptions__)
punctuations = set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~।ঃ‘’–')
digits = set('০১২৩৪৫৬৭৮৯')
whitespaces = set(" \t\r\n\f")
bengaliChars = bengaliTextChars | punctuations | whitespaces

numbersBengaliEnglish = {b:e for b, e in zip('০১২৩৪৫৬৭৮৯', '0123456789')}
monthsBengaliEnglish = {b:e for b, e in zip(
    ['জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর', "জানু", "ফেব"], 
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 
     "January", 'February'])}
timeWordsBegnaliEnglish = {b:e for b, e in zip(["আগে", "দিন", "ঘন্টা", "আগে"], ["ago", "days", "hours", "before"])}

def translateBengaliDate(date):
    splitOn = punctuations | whitespaces

    translated = "".join(c if c not in splitOn else " " for c in date)
    translated = "".join(c if c not in numbersBengaliEnglish else numbersBengaliEnglish[c] for c in translated)
    translated = translated.split(" ")
    translated = (w if w not in monthsBengaliEnglish else monthsBengaliEnglish[w] for w in translated)
    translated = (w if w not in timeWordsBegnaliEnglish else timeWordsBegnaliEnglish[w] for w in translated)
    translated = " ".join(translated)

    splits = (c for c in date if c in splitOn)
    translated = (c if c not in splitOn else splits.__next__() for c in translated)

    return translated

keywords = {"জলমগ্ন": "submerged",
    "জোয়ারের":"tidal", 
    "প্লাবিত": "flooded", 
    "বন্যা": "flood", 
    "জলাবদ্ধ": "waterlogged", 
    "উজান": "upstream", 
    "ঘূর্ণিঝড়": "cyclone",
    "নদী": "river", 
    "ভাঙ্গন": "erosion",
    "বাঁধ": "embankment",
    "বেড়িবাঁধ": "embankment",
    "পোল্ডার": "polder"
    }

updatedKeywords = {
    "বাঁধ": "embankment",
    "বেড়িবাঁধ": "embankment",
    "পোল্ডার": "polder",
    "বেড়িবাঁধ ক্ষতিগ্রস্ত": "embankment damaged",
    "বেড়িবাঁধ উপচে": "water overflew the embankment",
    "পানিবন্দী": "waterlogged",
    "মানুষ পানিবন্দী": "people are waterlogged",
    "নিমজ্জিত হয়েছে": "are submerged",
    "পানিবন্দি হয়ে পড়েছে": "have become waterlogged",
    "প্রবল বর্ষণ": "heavy rain",
    "টানা বৃষ্টি": "continuous rain",
    "পাহাড়ি ঢলে": "steam coming down the hill"
}

def keywordCount(content, keywords = keywords):
    #words = tokenizer.tokenize(content)
    return {keyword: content.count(keyword) for keyword in keywords.keys()}