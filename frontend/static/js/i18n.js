/**
 * AgriLeaf — i18n.js
 * Multi-language support: English, Telugu, Hindi, Tamil
 */

const TRANSLATIONS = {
    en: {
        nav_analyze: "Analyze", nav_how: "How It Works", nav_history: "History",
        nav_dashboard: "Dashboard", nav_logout: "Logout",
        hero_title: "Detect Leaf Disease with Deep Learning",
        hero_sub: "Upload a leaf photo → AI identifies the disease → Get instant treatment recommendations. Supports 8 crops with 40 disease classes.",
        hero_cta: "Analyze a Leaf",
        stat_classes: "Disease Classes", stat_crops: "Crops Supported", stat_modules: "AI Modules",
        section_core: "CORE FEATURE", analyzer_title: "Leaf Disease Analyzer",
        analyzer_sub: "Upload a clear photo of the affected leaf for instant AI diagnosis",
        crop_label: "Crop Type", crop_auto: "🔍 Auto Detect",
        soil_title: "Soil Data", soil_optional: "(optional — improves diagnosis)",
        nitrogen_label: "Nitrogen Level",
        soil_hint: "Get soil pH from your nearest Krishi Vigyan Kendra or use a soil test kit (₹50–200 at agri shops).",
        upload_title: "Drop your leaf image here", choose_file: "Choose File",
        tips_title: "Tips for better results",
        tip1: "Use natural daylight — avoid harsh shadows",
        tip2: "Fill at least 60% of frame with the leaf",
        tip3: "Capture the most affected area clearly",
        tip4: "Keep camera steady to avoid blur",
        analyze_btn: "Analyze Leaf",
        ready_title: "Ready to Analyze",
        ready_sub: "Upload a leaf image and click Analyze Leaf to get disease detection, severity assessment, and treatment recommendations.",
        analyzing: "Analyzing Leaf...",
        ls1: "Preprocessing image", ls2: "Extracting CNN features",
        ls3: "Running disease classifier", ls4: "Generating treatment plan",
        confidence: "confidence", cnn_pred: "CNN Top Predictions",
        severity: "Severity Assessment", about_disease: "About This Disease",
        treatment: "Treatment Recommendations",
        chemical: "Chemical", organic: "Organic", prevention: "Prevention",
        yield_loss: "Estimated Yield Loss (if untreated)",
        download_report: "Download Report", share_whatsapp: "Share on WhatsApp", new_analysis: "New Analysis",
        analysis_failed: "Analysis Failed", try_again: "Try Again",
        how_title: "How It Works", how_sub: "3 modules working together — from image to diagnosis",
        mod1_title: "User Interaction", mod1_desc: "Farmer logs in, captures leaf photo, selects crop type.",
        mod2_title: "Disease Detection & Analysis", mod2_desc: "MobileNetV2 CNN processes the 224×224 image. Outputs disease class + severity.",
        mod3_title: "Recommendation & Storage", mod3_desc: "Chemical + organic treatments generated. Result saved to farmer's history.",
        history_title: "My Analysis History", history_sub: "Every analysis is automatically saved to your account,",
        refresh: "Refresh", clear_history: "Clear History", full_dashboard: "Full Dashboard",
        total: "Total", healthy: "Healthy", diseased: "Diseased",
        loading_history: "Loading your history..."
    },
    te: {
        nav_analyze: "విశ్లేషించు", nav_how: "ఎలా పని చేస్తుంది", nav_history: "చరిత్ర",
        nav_dashboard: "డాష్‌బోర్డ్", nav_logout: "లాగ్అవుట్",
        hero_title: "ఆకు వ్యాధిని గుర్తించండి - డీప్ లెర్నింగ్ తో",
        hero_sub: "ఆకు ఫోటో అప్‌లోడ్ చేయండి → AI వ్యాధిని గుర్తిస్తుంది → వెంటనే చికిత్స సిఫార్సులు పొందండి. 8 పంటలు, 40 వ్యాధి తరగతులు.",
        hero_cta: "ఆకును విశ్లేషించండి",
        stat_classes: "వ్యాధి తరగతులు", stat_crops: "పంటలు", stat_modules: "AI మాడ్యూల్స్",
        section_core: "ప్రధాన లక్షణం", analyzer_title: "ఆకు వ్యాధి విశ్లేషకుడు",
        analyzer_sub: "తక్షణ AI నిర్ధారణ కోసం ప్రభావిత ఆకు యొక్క స్పష్టమైన ఫోటో అప్‌లోడ్ చేయండి",
        crop_label: "పంట రకం", crop_auto: "🔍 స్వయంచాలకంగా గుర్తించు",
        soil_title: "నేల డేటా", soil_optional: "(ఐచ్ఛికం — నిర్ధారణను మెరుగుపరుస్తుంది)",
        nitrogen_label: "నైట్రోజన్ స్థాయి",
        soil_hint: "మీ సమీప కృషి విజ్ఞాన కేంద్రం నుండి నేల pH పొందండి లేదా నేల పరీక్ష కిట్ ఉపయోగించండి.",
        upload_title: "మీ ఆకు చిత్రాన్ని ఇక్కడ వదలండి", choose_file: "ఫైల్ ఎంచుకోండి",
        tips_title: "మెరుగైన ఫలితాల కోసం చిట్కాలు",
        tip1: "సహజ పగటి వెలుతురు ఉపయోగించండి", tip2: "ఆకుతో కనీసం 60% ఫ్రేమ్ నింపండి",
        tip3: "అత్యంత ప్రభావిత ప్రాంతాన్ని స్పష్టంగా తీయండి", tip4: "మసకబారకుండా కెమెరా స్థిరంగా ఉంచండి",
        analyze_btn: "ఆకును విశ్లేషించు",
        ready_title: "విశ్లేషణకు సిద్ధం", ready_sub: "ఆకు చిత్రాన్ని అప్‌లోడ్ చేసి విశ్లేషించు క్లిక్ చేయండి.",
        analyzing: "ఆకును విశ్లేషిస్తోంది...",
        ls1: "చిత్రాన్ని ప్రాసెస్ చేస్తోంది", ls2: "CNN లక్షణాలు సేకరిస్తోంది",
        ls3: "వ్యాధి గుర్తించడం జరుగుతోంది", ls4: "చికిత్స ప్రణాళిక రూపొందిస్తోంది",
        confidence: "విశ్వాసం", cnn_pred: "CNN అగ్ర అంచనాలు",
        severity: "తీవ్రత అంచనా", about_disease: "ఈ వ్యాధి గురించి",
        treatment: "చికిత్స సిఫార్సులు",
        chemical: "రసాయనిక", organic: "సేంద్రీయ", prevention: "నివారణ",
        yield_loss: "అంచనా దిగుబడి నష్టం (చికిత్స చేయకపోతే)",
        download_report: "నివేదిక డౌన్‌లోడ్ చేయండి", share_whatsapp: "వాట్సాప్‌లో షేర్ చేయండి", new_analysis: "కొత్త విశ్లేషణ",
        analysis_failed: "విశ్లేషణ విఫలమైంది", try_again: "మళ్ళీ ప్రయత్నించండి",
        how_title: "ఎలా పని చేస్తుంది", how_sub: "3 మాడ్యూల్స్ కలిసి పనిచేస్తాయి",
        mod1_title: "వినియోగదారు పరస్పర చర్య", mod1_desc: "రైతు లాగిన్ అవుతారు, ఆకు ఫోటో తీస్తారు.",
        mod2_title: "వ్యాధి గుర్తింపు", mod2_desc: "MobileNetV2 CNN చిత్రాన్ని ప్రాసెస్ చేస్తుంది.",
        mod3_title: "సిఫార్సు & నిల్వ", mod3_desc: "చికిత్స ఉత్పత్తి చేయబడుతుంది. ఫలితం సేవ్ చేయబడుతుంది.",
        history_title: "నా విశ్లేషణ చరిత్ర", history_sub: "ప్రతి విశ్లేషణ మీ ఖాతాకు స్వయంచాలకంగా సేవ్ చేయబడుతుంది,",
        refresh: "రిఫ్రెష్", clear_history: "చరిత్ర క్లియర్ చేయి", full_dashboard: "పూర్తి డాష్‌బోర్డ్",
        total: "మొత్తం", healthy: "ఆరోగ్యకరమైన", diseased: "వ్యాధిగ్రస్తమైన",
        loading_history: "మీ చరిత్రను లోడ్ చేస్తోంది..."
    },
    hi: {
        nav_analyze: "विश्लेषण", nav_how: "यह कैसे काम करता है", nav_history: "इतिहास",
        nav_dashboard: "डैशबोर्ड", nav_logout: "लॉगआउट",
        hero_title: "पत्ती की बीमारी का पता लगाएं - डीप लर्निंग के साथ",
        hero_sub: "पत्ती की फोटो अपलोड करें → AI बीमारी की पहचान करेगा → तुरंत उपचार की सिफारिशें पाएं। 8 फसलें, 40 रोग वर्ग।",
        hero_cta: "पत्ती का विश्लेषण करें",
        stat_classes: "रोग वर्ग", stat_crops: "फसलें", stat_modules: "AI मॉड्यूल",
        section_core: "मुख्य सुविधा", analyzer_title: "पत्ती रोग विश्लेषक",
        analyzer_sub: "तत्काल AI निदान के लिए प्रभावित पत्ती की स्पष्ट फोटो अपलोड करें",
        crop_label: "फसल का प्रकार", crop_auto: "🔍 स्वचालित पहचान",
        soil_title: "मिट्टी डेटा", soil_optional: "(वैकल्पिक — निदान में सुधार करता है)",
        nitrogen_label: "नाइट्रोजन स्तर",
        soil_hint: "अपने निकटतम कृषि विज्ञान केंद्र से मिट्टी pH प्राप्त करें या मिट्टी परीक्षण किट का उपयोग करें।",
        upload_title: "यहाँ अपनी पत्ती की छवि छोड़ें", choose_file: "फ़ाइल चुनें",
        tips_title: "बेहतर परिणाम के लिए सुझाव",
        tip1: "प्राकृतिक दिन के उजाले का उपयोग करें", tip2: "पत्ती से कम से कम 60% फ्रेम भरें",
        tip3: "सबसे प्रभावित क्षेत्र को स्पष्ट रूप से कैप्चर करें", tip4: "धुंध से बचने के लिए कैमरा स्थिर रखें",
        analyze_btn: "पत्ती का विश्लेषण करें",
        ready_title: "विश्लेषण के लिए तैयार", ready_sub: "पत्ती की छवि अपलोड करें और विश्लेषण पर क्लिक करें।",
        analyzing: "पत्ती का विश्लेषण हो रहा है...",
        ls1: "छवि प्रसंस्करण", ls2: "CNN विशेषताएँ निकाल रहा है",
        ls3: "रोग वर्गीकरण चल रहा है", ls4: "उपचार योजना बना रहा है",
        confidence: "विश्वास", cnn_pred: "CNN शीर्ष भविष्यवाणियाँ",
        severity: "गंभीरता मूल्यांकन", about_disease: "इस बीमारी के बारे में",
        treatment: "उपचार की सिफारिशें",
        chemical: "रासायनिक", organic: "जैविक", prevention: "रोकथाम",
        yield_loss: "अनुमानित उपज हानि (यदि उपचार न किया जाए)",
        download_report: "रिपोर्ट डाउनलोड करें", share_whatsapp: "WhatsApp पर शेयर करें", new_analysis: "नया विश्लेषण",
        analysis_failed: "विश्लेषण विफल रहा", try_again: "पुनः प्रयास करें",
        how_title: "यह कैसे काम करता है", how_sub: "3 मॉड्यूल मिलकर काम करते हैं",
        mod1_title: "उपयोगकर्ता इंटरफ़ेस", mod1_desc: "किसान लॉगिन करते हैं, पत्ती की फोटो लेते हैं।",
        mod2_title: "रोग पहचान", mod2_desc: "MobileNetV2 CNN छवि को प्रोसेस करता है।",
        mod3_title: "सिफारिश और भंडारण", mod3_desc: "उपचार उत्पन्न होता है। परिणाम सहेजा जाता है।",
        history_title: "मेरा विश्लेषण इतिहास", history_sub: "प्रत्येक विश्लेषण आपके खाते में स्वचालित रूप से सहेजा जाता है,",
        refresh: "रीफ्रेश", clear_history: "इतिहास साफ़ करें", full_dashboard: "पूर्ण डैशबोर्ड",
        total: "कुल", healthy: "स्वस्थ", diseased: "रोगग्रस्त",
        loading_history: "आपका इतिहास लोड हो रहा है..."
    },
    ta: {
        nav_analyze: "பகுப்பாய்வு", nav_how: "எப்படி செயல்படுகிறது", nav_history: "வரலாறு",
        nav_dashboard: "டாஷ்போர்டு", nav_logout: "வெளியேறு",
        hero_title: "இலை நோயை கண்டறியுங்கள் - டீப் லேர்னிங் மூலம்",
        hero_sub: "இலை புகைப்படம் பதிவேற்றவும் → AI நோயை கண்டறியும் → உடனடியாக சிகிச்சை பரிந்துரைகள் பெறவும். 8 பயிர்கள், 40 நோய் வகுப்புகள்.",
        hero_cta: "இலையை பகுப்பாய்வு செய்யுங்கள்",
        stat_classes: "நோய் வகுப்புகள்", stat_crops: "பயிர்கள்", stat_modules: "AI தொகுதிகள்",
        section_core: "முக்கிய அம்சம்", analyzer_title: "இலை நோய் பகுப்பாய்வி",
        analyzer_sub: "உடனடி AI கண்டறிதலுக்கு பாதிக்கப்பட்ட இலையின் தெளிவான புகைப்படம் பதிவேற்றவும்",
        crop_label: "பயிர் வகை", crop_auto: "🔍 தானாக கண்டறி",
        soil_title: "மண் தரவு", soil_optional: "(விருப்பமான — கண்டறிதலை மேம்படுத்துகிறது)",
        nitrogen_label: "நைட்ரஜன் அளவு",
        soil_hint: "உங்கள் அருகிலுள்ள கிருஷி விஞ்ஞான கேந்திரத்திலிருந்து மண் pH பெறுங்கள்.",
        upload_title: "உங்கள் இலை படத்தை இங்கே போடுங்கள்", choose_file: "கோப்பு தேர்ந்தெடு",
        tips_title: "சிறந்த முடிவுகளுக்கான குறிப்புகள்",
        tip1: "இயற்கை பகல் வெளிச்சம் பயன்படுத்துங்கள்", tip2: "இலையுடன் குறைந்தது 60% சட்டகம் நிரப்புங்கள்",
        tip3: "மிகவும் பாதிக்கப்பட்ட பகுதியை தெளிவாக பிடிக்கவும்", tip4: "மங்கலைத் தவிர்க்க கேமராவை நிலையாக வைக்கவும்",
        analyze_btn: "இலையை பகுப்பாய்வு செய்",
        ready_title: "பகுப்பாய்வுக்கு தயார்", ready_sub: "இலை படத்தை பதிவேற்றி பகுப்பாய்வு செய்யவும் என்பதை கிளிக் செய்யவும்.",
        analyzing: "இலையை பகுப்பாய்வு செய்கிறது...",
        ls1: "படத்தை செயலாக்குகிறது", ls2: "CNN அம்சங்களை பிரித்தெடுக்கிறது",
        ls3: "நோய் வகைப்படுத்தி இயங்குகிறது", ls4: "சிகிச்சை திட்டம் உருவாக்குகிறது",
        confidence: "நம்பிக்கை", cnn_pred: "CNN சிறந்த கணிப்புகள்",
        severity: "தீவிரம் மதிப்பீடு", about_disease: "இந்த நோயைப் பற்றி",
        treatment: "சிகிச்சை பரிந்துரைகள்",
        chemical: "இரசாயன", organic: "இயற்கை", prevention: "தடுப்பு",
        yield_loss: "மதிப்பிடப்பட்ட விளைச்சல் இழப்பு (சிகிச்சையளிக்காவிட்டால்)",
        download_report: "அறிக்கை பதிவிறக்கம்", share_whatsapp: "WhatsApp-ல் பகிர்", new_analysis: "புதிய பகுப்பாய்வு",
        analysis_failed: "பகுப்பாய்வு தோல்வியுற்றது", try_again: "மீண்டும் முயற்சிக்கவும்",
        how_title: "எப்படி செயல்படுகிறது", how_sub: "3 தொகுதிகள் ஒன்றாக செயல்படுகின்றன",
        mod1_title: "பயனர் தொடர்பு", mod1_desc: "விவசாயி உள்நுழைகிறார், இலை புகைப்படம் எடுக்கிறார்.",
        mod2_title: "நோய் கண்டறிதல்", mod2_desc: "MobileNetV2 CNN படத்தை செயலாக்குகிறது.",
        mod3_title: "பரிந்துரை & சேமிப்பு", mod3_desc: "சிகிச்சை உருவாக்கப்படுகிறது. முடிவு சேமிக்கப்படுகிறது.",
        history_title: "என் பகுப்பாய்வு வரலாறு", history_sub: "ஒவ்வொரு பகுப்பாய்வும் உங்கள் கணக்கில் தானாக சேமிக்கப்படுகிறது,",
        refresh: "புதுப்பி", clear_history: "வரலாற்றை அழி", full_dashboard: "முழு டாஷ்போர்டு",
        total: "மொத்தம்", healthy: "ஆரோக்கியமான", diseased: "நோயுற்ற",
        loading_history: "உங்கள் வரலாற்றை ஏற்றுகிறது..."
    }
};

let currentLang = 'en';

function setLang(lang) {
    currentLang = lang;
    // Update buttons
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    const btns = document.querySelectorAll('.lang-btn');
    const langMap = { en: 0, te: 1, hi: 2, ta: 3 };
    if (btns[langMap[lang]]) btns[langMap[lang]].classList.add('active');

    // Translate all elements
    const t = TRANSLATIONS[lang] || TRANSLATIONS['en'];
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) el.textContent = t[key];
    });

    // Save preference
    try { localStorage.setItem('agrileaf_lang', lang); } catch(e) {}
}

// Load saved language
(function() {
    try {
        const saved = localStorage.getItem('agrileaf_lang');
        if (saved && TRANSLATIONS[saved]) setLang(saved);
    } catch(e) {}
})();