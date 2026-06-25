"""
DeepDive AI — Translation and Localization Management
"""

from __future__ import annotations

import streamlit as st

# Supported Languages configuration
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "mr": "मराठी",
    "te": "తెలుగు",
}

TRANSLATIONS = {
    "en": {
        "app_title": "🔬 DeepDive AI",
        "app_tagline": "AI-Powered Research Report Generator",
        "how_to_use": "How to use:",
        "step_1": "1. Go to **🔬 Research** page",
        "step_2": "2. Enter any research topic",
        "step_3": "3. Click **Generate Report**",
        "step_4": "4. Download **PDF** or **PPT**",
        "built_with": "Built with",
        "hero_title": "🔬 DeepDive AI",
        "hero_subtitle": (
            "Enter any research topic and receive a comprehensive, AI-generated "
            "report — complete with executive summary, key insights, statistics, "
            "and downloadable exports."
        ),
        "feat_summary_title": "Executive Summary",
        "feat_summary_desc": "A concise, professional overview of your research topic.",
        "feat_insights_title": "Key Insights",
        "feat_insights_desc": "The most important findings and takeaways, distilled.",
        "feat_stats_title": "Statistics & Data",
        "feat_stats_desc": (
            "Relevant numbers, metrics, and data points supporting research."
        ),
        "feat_ref_title": "References & Citations",
        "feat_ref_desc": "Credible sources with descriptions and URLs.",
        "feat_pdf_title": "PDF Report",
        "feat_pdf_desc": "Download a professionally formatted PDF report.",
        "feat_ppt_title": "PowerPoint Deck",
        "feat_ppt_desc": "Get a ready-to-present slide deck for meetings.",
        "cta_text": (
            "👉 Select <strong>🔬 Research</strong> from the sidebar to get started."
        ),
        "ui_language": "UI Language",
        "report_language": "Report Language",
        "research_topic": "Research Topic",
        "input_placeholder": "e.g. Impact of climate change on agriculture",
        "btn_generate": "🚀 Generate Report",
        "warning_empty_topic": "⚠️ Please enter a research topic.",
        "spinner_msg": "🔍 Researching **{topic}**… This may take up to 30 seconds.",
        "success_msg": "✅ Report generated successfully!",
        "err_api_key": (
            "🔑 API key not configured. Please configure `GEMINI_API_KEY` in "
            "Streamlit Secrets, environment variables, or your .env file."
        ),
        "err_generation": "❌ Research generation failed. Please try again.",
        "err_schema": (
            "⚠️ The AI returned an unexpected response format. Please try again."
        ),
        "err_unexpected": "❌ An unexpected error occurred. Please try again.",
        "sec_summary": "📝 Executive Summary",
        "sec_background": "🌍 Background & Context",
        "sec_concepts": "🔑 Core Concepts & Terminology",
        "sec_insights": "💡 Key Insights",
        "sec_stats": "📊 Statistics & Data",
        "sec_benefits": "⚖️ Benefits, Challenges & Risks",
        "sec_apps": "🚀 Real-World Applications",
        "sec_outlook": "🔮 Future Outlook & Recommendations",
        "sec_references": "📚 References & Citations",
        "download_section_title": "⬇️ Download Your Report",
        "btn_download_pdf": "⬇️ Download PDF",
        "btn_download_ppt": "⬇️ Download PPT",
        "pdf_err": "Failed to generate PDF. Please try again.",
        "ppt_err": "Failed to generate PowerPoint. Please try again.",
        "welcome_back": "Welcome back! Ready to explore?",
        "nav_home": "Home",
        "nav_research": "🔬 Research",
        "limited_data_warn": "⚠️ Limited data available for this topic.",
        "limited_stats_warn": "⚠️ Limited statistical data available for this topic.",
        "concept_label": "CONCEPT",
        "usecase_label": "USE CASE",
        "benefit_label": "🟢 Benefits",
        "challenge_label": "🟡 Challenges",
        "risk_label": "🔴 Risks & Trade-offs",
        "sec_future_roadmap": "FUTURE STRATEGIC ROADMAP",
        "primary_metrics_label": "PRIMARY METRICS",
        "landscape_importance_label": "LANDSCAPE IMPORTANCE",
        "why_it_matters_text": (
            "Understanding this landscape enables leaders to identify key trends, "
            "address operational limits, and deploy strategic frameworks to gain "
            "early market advantage."
        ),
        "key_analysis_insights": "KEY ANALYSIS INSIGHTS",
        "supporting_data": "SUPPORTING DATA",
        "sources_references": "SOURCES & REFERENCES",
        "strategic_overview_heading": "Strategic Overview & High-Level Insights",
        "why_this_matters_heading": "Why This Matters & Industry Relevance",
        "foundational_principles_heading": "Foundational Principles & Key Terminology",
        "findings_analysis_heading": "Major Discoveries & Supporting Evidence",
        "advantages_constraints_heading": "Advantages, Constraints & Risks Analysis",
        "practical_adoption_heading": "Practical Adoption & Case Studies",
        "strategic_predictions_heading": "Strategic Predictions & Citations",
        "benefit_col_title": "BENEFITS & ADVANTAGES",
        "challenge_col_title": "CHALLENGES & LIMITS",
        "risk_col_title": "RISKS & THREATS",
    },
    "hi": {
        "app_title": "🔬 डीपडाइव एआई",
        "app_tagline": "एआई-संचालित अनुसंधान रिपोर्ट जनरेटर",
        "how_to_use": "उपयोग कैसे करें:",
        "step_1": "1. **🔬 अनुसंधान** पृष्ठ पर जाएं",
        "step_2": "2. कोई भी अनुसंधान विषय दर्ज करें",
        "step_3": "3. **रिपोर्ट उत्पन्न करें** पर क्लिक करें",
        "step_4": "4. **PDF** या **PPT** डाउनलोड करें",
        "built_with": "द्वारा निर्मित",
        "hero_title": "🔬 डीपडाइव एआई",
        "hero_subtitle": (
            "कोई भी अनुसंधान विषय दर्ज करें और एक व्यापक, एआई-जनित रिपोर्ट प्राप्त करें "
            "— कार्यकारी सारांश, महत्वपूर्ण अंतर्दृष्टि, आंकड़ों और डाउनलोड योग्य निर्यात के साथ।"
        ),
        "feat_summary_title": "कार्यकारी सारांश",
        "feat_summary_desc": "एआई द्वारा तैयार आपके शोध विषय का एक संक्षिप्त, पेशेवर अवलोकन।",
        "feat_insights_title": "महत्वपूर्ण अंतर्दृष्टि",
        "feat_insights_desc": "त्वरित समझ के लिए सबसे महत्वपूर्ण निष्कर्ष और सीख।",
        "feat_stats_title": "आंकड़े और डेटा",
        "feat_stats_desc": "अनुसंधान का समर्थन करने वाले प्रासंगिक आंकड़े, मेट्रिक्स और डेटा बिंदु।",
        "feat_ref_title": "संदर्भ और उद्धरण",
        "feat_ref_desc": "विवरण और URL के साथ विश्वसनीय स्रोत।",
        "feat_pdf_title": "PDF रिपोर्ट",
        "feat_pdf_desc": "एक पेशेवर रूप से स्वरूपित PDF रिपोर्ट डाउनलोड करें।",
        "feat_ppt_title": "PowerPoint डेक",
        "feat_ppt_desc": "बैठकों के लिए प्रस्तुति-तैयार स्लाइड डेक प्राप्त करें।",
        "cta_text": "👉 शुरू करने के लिए साइडबार से <strong>🔬 अनुसंधान</strong> चुनें।",
        "ui_language": "इंटरफ़ेस भाषा",
        "report_language": "रिपोर्ट की भाषा",
        "research_topic": "अनुसंधान विषय",
        "input_placeholder": "जैसे: कृषि पर जलवायु परिवर्तन का प्रभाव",
        "btn_generate": "🚀 रिपोर्ट उत्पन्न करें",
        "warning_empty_topic": "⚠️ कृपया एक शोध विषय दर्ज करें।",
        "spinner_msg": (
            "🔍 **{topic}** पर शोध किया जा रहा है… इसमें 30 सेकंड तक का समय लग सकता है।"
        ),
        "success_msg": "✅ रिपोर्ट सफलतापूर्वक उत्पन्न हुई!",
        "err_api_key": (
            "🔑 API कुंजी कॉन्फ़िगर नहीं है। कृपया Streamlit Secrets, पर्यावरण "
            "चर, या अपनी .env फ़ाइल में `GEMINI_API_KEY` कॉन्फ़िगर करें।"
        ),
        "err_generation": "❌ अनुसंधान निर्माण विफल रहा। कृपया पुनः प्रयास करें।",
        "err_schema": "⚠️ एआई ने अप्रत्याशित प्रतिक्रिया प्रारूप लौटाया। कृपया पुनः प्रयास करें।",
        "err_unexpected": "❌ एक अप्रत्याशित त्रुटि हुई। कृपया पुनः प्रयास करें।",
        "sec_summary": "📝 कार्यकारी सारांश",
        "sec_background": "🌍 पृष्ठभूमि और संदर्भ",
        "sec_concepts": "🔑 मुख्य अवधारणाएँ और शब्दावली",
        "sec_insights": "💡 महत्वपूर्ण अंतर्दृष्टि",
        "sec_stats": "📊 आंकड़े और डेटा",
        "sec_benefits": "⚖️ लाभ, चुनौतियाँ और जोखिम",
        "sec_apps": "🚀 वास्तविक दुनिया के अनुप्रयोग",
        "sec_outlook": "🔮 भविष्य का दृष्टिकोण और सिफारिशें",
        "sec_references": "📚 संदर्भ और उद्धरण",
        "download_section_title": "⬇️ अपनी रिपोर्ट डाउनलोड करें",
        "btn_download_pdf": "⬇️ PDF डाउनलोड करें",
        "btn_download_ppt": "⬇️ PPT डाउनलोड करें",
        "pdf_err": "PDF उत्पन्न करने में विफल। कृपया पुनः प्रयास करें।",
        "ppt_err": "PowerPoint उत्पन्न करने में विफल। कृपया पुनः प्रयास करें।",
        "welcome_back": "वापसी पर आपका स्वागत है! शोध के लिए तैयार हैं?",
        "nav_home": "मुख्य पृष्ठ",
        "nav_research": "🔬 अनुसंधान",
        "limited_data_warn": "⚠️ इस विषय के लिए सीमित डेटा उपलब्ध है।",
        "limited_stats_warn": "⚠️ इस विषय के लिए सीमित सांख्यिकीय डेटा उपलब्ध है।",
        "concept_label": "अवधारणा",
        "usecase_label": "उपयोग मामला",
        "benefit_label": "🟢 लाभ",
        "challenge_label": "🟡 चुनौतियाँ",
        "risk_label": "🔴 जोखिम और व्यापार-नाप",
        "sec_future_roadmap": "भविष्य का रणनीतिक रोडमैप",
        "primary_metrics_label": "प्राथमिक मेट्रिक्स",
        "landscape_importance_label": "परिदृश्य महत्व",
        "why_it_matters_text": (
            "इस परिदृश्य को समझने से नेताओं को प्रमुख प्रवृत्तियों की पहचान करने, "
            "परिचालन सीमाओं को संबोधित करने और रणनीतिक लाभ प्राप्त करने में मदद मिलती है।"
        ),
        "key_analysis_insights": "प्रमुख विश्लेषण अंतर्दृष्टि",
        "supporting_data": "सहायक डेटा",
        "sources_references": "स्रोत और संदर्भ",
        "strategic_overview_heading": "रणनीतिक अवलोकन और उच्च-स्तरीय अंतर्दृष्टि",
        "why_this_matters_heading": "यह क्यों महत्वपूर्ण है और उद्योग प्रासंगिकता",
        "foundational_principles_heading": "संस्थागत सिद्धांत और प्रमुख शब्दावली",
        "findings_analysis_heading": "प्रमुख खोजें और सहायक साक्ष्य",
        "advantages_constraints_heading": "लाभ, सीमाएं और जोखिम विश्लेषण",
        "practical_adoption_heading": "व्यावहारिक अनुप्रयोग और केस स्टडीज",
        "strategic_predictions_heading": "रणनीतिक भविष्यवाणियां और उद्धरण",
        "benefit_col_title": "लाभ और फायदे",
        "challenge_col_title": "चुनौतियां और सीमाएं",
        "risk_col_title": "जोखिम और खतरे",
    },
    "mr": {
        "app_title": "🔬 डीपडाइव एआय",
        "app_tagline": "एआय-चालित संशोधन अहवाल जनरेटर",
        "how_to_use": "कसे वापरावे:",
        "step_1": "1. **🔬 संशोधन** पृष्ठावर जा",
        "step_2": "2. कोणताही संशोधन विषय प्रविष्ट करा",
        "step_3": "3. **अहवाल तयार करा** वर क्लिक करा",
        "step_4": "4. **PDF** किंवा **PPT** डाउनलोड करा",
        "built_with": "द्वारे निर्मित",
        "hero_title": "🔬 डीपडाइव एआय",
        "hero_subtitle": (
            "कोणताही संशोधन विषय प्रविष्ट करा आणि एक विस्तृत, "
            "एआय-जनरेट केलेला अहवाल मिळवा — कार्यकारी सारांश, "
            "महत्त्वपूर्ण अंतर्दृष्टी, आकडेवारी आणि डाउनलोड करण्यायोग्य निर्यातीसह।"
        ),
        "feat_summary_title": "कार्यकारी सारांश",
        "feat_summary_desc": (
            "एआय द्वारे तयार केलेल्या तुमच्या संशोधन विषयाचे संक्षिप्त, व्यावसायिक विहंगावलोकन।"
        ),
        "feat_insights_title": "महत्त्वपूर्ण अंतर्दृष्टी",
        "feat_insights_desc": "द्रुत आकलनासाठी सर्वात महत्त्वाचे निष्कर्ष आणि शिकवण।",
        "feat_stats_title": "आकडेवारी आणि डेटा",
        "feat_stats_desc": "संशोधनाला समर्थन देणारे संबंधित आकडे, मेट्रिक्स आणि डेटा पॉइंट्स।",
        "feat_ref_title": "संदर्भ आणि उद्धरण",
        "feat_ref_desc": "तपशील आणि URL सह विश्वसनीय स्रोत।",
        "feat_pdf_title": "PDF अहवाल",
        "feat_pdf_desc": "व्यावसायिकरित्या स्वरूपित केलेला PDF अहवाल डाउनलोड करा।",
        "feat_ppt_title": "PowerPoint डेक",
        "feat_ppt_desc": "बैठकांसाठी सादरीकरण-तयार स्लाइड डेक मिळवा।",
        "cta_text": "👉 सुरू करण्यासाठी साइडबारमधून <strong>🔬 संशोधन</strong> निवडा।",
        "ui_language": "इंटरफेस भाषा",
        "report_language": "अहवालाची भाषा",
        "research_topic": "संशोधन विषय",
        "input_placeholder": "उदा: शेतीवर हवामान बदलाचा प्रभाव",
        "btn_generate": "🚀 अहवाल तयार करा",
        "warning_empty_topic": "⚠️ कृपया शोध विषय प्रविष्ट करा।",
        "spinner_msg": "🔍 **{topic}** वर संशोधन सुरू आहे… याला ३० सेकंदांपर्यंत वेळ लागू शकतो।",
        "success_msg": "✅ अहवाल यशस्वीरित्या तयार झाला!",
        "err_api_key": (
            "🔑 API की कॉन्फिगर केलेली नाही. कृपया Streamlit Secrets, पर्यावरण "
            "व्हेरिएबल्स किंवा तुमच्या .env फाईलमध्ये `GEMINI_API_KEY` कॉन्फिगर करा।"
        ),
        "err_generation": "❌ संशोधन निर्मिती अयशस्वी. कृपया पुन्हा प्रयत्न करा।",
        "err_schema": "⚠️ एआयने अनपेक्षित प्रतिसाद स्वरूप परत केले. कृपया पुन्हा प्रयत्न करा।",
        "err_unexpected": "❌ एक अनपेक्षित त्रुटी आली. कृपया पुन्हा प्रयत्न करा।",
        "sec_summary": "📝 कार्यकारी सारांश",
        "sec_background": "🌍 पार्श्वभूमी आणि संदर्भ",
        "sec_concepts": "🔑 मुख्य संकल्पना आणि शब्दावली",
        "sec_insights": "💡 महत्त्वपूर्ण अंतर्दृष्टी",
        "sec_stats": "📊 आकडेवारी आणि डेटा",
        "sec_benefits": "⚖️ लाभ, आव्हाने आणि जोखीम",
        "sec_apps": "🚀 वास्तविक जगातील अनुप्रयोग",
        "sec_outlook": "🔮 भविष्यातील दृष्टिकोन आणि शिफारसी",
        "sec_references": "📚 संदर्भ आणि उद्धरण",
        "download_section_title": "⬇️ तुमचा अहवाल डाउनलोड करा",
        "btn_download_pdf": "⬇️ PDF डाउनलोड करा",
        "btn_download_ppt": "⬇️ PPT डाउनलोड करा",
        "pdf_err": "PDF तयार करण्यात अयशस्वी. कृपया पुन्हा प्रयत्न करा।",
        "ppt_err": "PowerPoint तयार करण्यात अयशस्वी. कृपया पुन्हा प्रयत्न करा।",
        "welcome_back": "परत आल्याबद्दल आपले स्वागत आहे! संशोधनासाठी तयार आहात?",
        "nav_home": "मुख्य पृष्ठ",
        "nav_research": "🔬 संशोधन",
        "limited_data_warn": "⚠️ या विषयासाठी मर्यादित डेटा उपलब्ध आहे।",
        "limited_stats_warn": "⚠️ या विषयासाठी मर्यादित सांख्यिकीय डेटा उपलब्ध आहे।",
        "concept_label": "संकल्पना",
        "usecase_label": "वापराचे उदाहरण",
        "benefit_label": "🟢 फायदे",
        "challenge_label": "🟡 आव्हाने",
        "risk_label": "🔴 जोखीम आणि व्यापार-नाप",
        "sec_future_roadmap": "भविष्यातील धोरणात्मक रोडमॅप",
        "primary_metrics_label": "प्राथमिक मेट्रिक्स",
        "landscape_importance_label": "लँडस्केप महत्त्व",
        "why_it_matters_text": (
            "हा लँडस्केप समजून घेतल्याने नेत्यांना मुख्य प्रवृत्ती ओळखण्यास, "
            "ऑपरेशनल मर्यादांचे निराकरण करण्यास आणि रणनीतिक लाभ मिळवण्यास मदत होते।"
        ),
        "key_analysis_insights": "प्रमुख विश्लेषण अंतर्दृष्टी",
        "supporting_data": "सहाय्यक डेटा",
        "sources_references": "स्रोत आणि संदर्भ",
        "strategic_overview_heading": "धोरणात्मक विहंगावलोकन आणि उच्च-स्तरीय अंतर्दृष्टी",
        "why_this_matters_heading": "हे का महत्त्वाचे आहे आणि उद्योग प्रासंगिकता",
        "foundational_principles_heading": "संस्थात्मक सिद्धांत आणि प्रमुख शब्दावली",
        "findings_analysis_heading": "प्रमुख शोध आणि सहाय्यक पुरावे",
        "advantages_constraints_heading": "फायदे, मर्यादा आणि जोखीम विश्लेषण",
        "practical_adoption_heading": "व्यावहारिक अवलंब आणि केस स्टडीज",
        "strategic_predictions_heading": "धोरणात्मक अंदाज आणि उद्धरण",
        "benefit_col_title": "फायदे आणि नफा",
        "challenge_col_title": "आव्हाने आणि मर्यादा",
        "risk_col_title": "जोखीम आणि धोके",
    },
    "te": {
        "app_title": "🔬 డీప్‌డైవ్ AI",
        "app_tagline": "AI-ఆధారిత పరిశోధనా నివేదిక జనరేటర్",
        "how_to_use": "ఎలా ఉపయోగించాలి:",
        "step_1": "1. **🔬 పరిశోధన** పేజీకి వెళ్లండి",
        "step_2": "2. ఏదైనా పరిశోధన అంశాన్ని నమోదు చేయండి",
        "step_3": "3. **నివేదికను సృష్టించండి** క్లిక్ చేయండి",
        "step_4": "4. **PDF** లేదా **PPT** డౌన్‌లోడ్ చేయండి",
        "built_with": "తో నిర్మించబడింది",
        "hero_title": "🔬 డీప్‌డైవ్ AI",
        "hero_subtitle": (
            "ఏదైనా పరిశోధన అంశాన్ని నమోదు చేయండి మరియు సమగ్రమైన, AI-సృష్టించిన నివేదికను "
            "పొందండి — ఎగ్జిక్యూటివ్ సారాంశం, ముఖ్యమైన అంతర్దృష్టులు, గణాంకాలు మరియు డౌన్‌లోడ్లతో."
        ),
        "feat_summary_title": "ఎగ్జిక్యూటివ్ సారాంశం",
        "feat_summary_desc": (
            "AI చేత రూపొందించబడిన మీ పరిశోధనా అంశం యొక్క సంక్షిప్త, వృత్తిపరమైన అవలోకనం."
        ),
        "feat_insights_title": "ముఖ్యమైన అంతర్దృష్టులు",
        "feat_insights_desc": "త్వరిత అవగాహన కోసం అత్యంత ముఖ్యమైన అన్వేషణలు మరియు ముఖ్యాంశాలు.",
        "feat_stats_title": "గణాంకాలు & డేటా",
        "feat_stats_desc": "పరిశోధనకు మద్దతు ఇచ్చే సంబంధిత సంఖ్యలు, కొలమానాలు మరియు డేటా పాయింట్లు.",
        "feat_ref_title": "ఆధారాలు & ఉల్లేఖనాలు",
        "feat_ref_desc": "వివరణలు మరియు URLలతో కూడిన విశ్వసనీయ వనరులు.",
        "feat_pdf_title": "PDF నివేదిక",
        "feat_pdf_desc": "వృత్తిపరంగా ఫార్మాట్ చేయబడిన PDF నివేదికను డౌన్‌లోడ్ చేసుకోండి.",
        "feat_ppt_title": "PowerPoint డెక్",
        "feat_ppt_desc": "సమావేశాల కోసం ప్రదర్శన-సిద్ధంగా ఉన్న స్లైడ్ డెక్‌ను పొందండి.",
        "cta_text": "👉 ప్రారంభించడానికి సైడ్‌బార్ నుండి <strong>🔬 పరిశోధన</strong> ఎంచుకోండి.",
        "ui_language": "ఇంటర్‌ఫేస్ భాష",
        "report_language": "నివేదిక భాష",
        "research_topic": "పరిశోధనా అంశం",
        "input_placeholder": "ఉదా: వ్యవసాయంపై వాతావరణ మార్పుల ప్రభావం",
        "btn_generate": "🚀 నిвеదికను సృష్టించండి",
        "warning_empty_topic": "⚠️ దయచేసి పరిశోధనా అంశాన్ని నమోదు చేయండి.",
        "spinner_msg": "🔍 **{topic}** పై పరిశోధన జరుగుతోంది… దీనికి 30 సెకన్లు పట్టవచ్చు.",
        "success_msg": "✅ నివేదిక విజయవంతంగా సృష్టించబడింది!",
        "err_api_key": (
            "🔑 API కీ కాన్ఫిగర్ చేయబడలేదు. దయచేసి Streamlit Secrets, పర్యావరణ "
            "వేరియబుల్స్ లేదా మీ .env ఫైల్‌లో `GEMINI_API_KEY`ని కాన్ఫిగర్ చేయండి."
        ),
        "err_generation": "❌ పరిశోధన సృష్టి విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "err_schema": "⚠️ AI ఊహించని ప్రతిస్పందన ఆకృతిని అందించింది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "err_unexpected": "❌ ఊహించని లోపం సంభవించింది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "sec_summary": "📝 ఎగ్జిక్యూటివ్ సారాంశం",
        "sec_background": "🌍 నేపథ్యం & సందర్భం",
        "sec_concepts": "🔑 ముఖ్య భావనలు & పరిభాష",
        "sec_insights": "💡 ముఖ్యమైన అంతర్దృష్టులు",
        "sec_stats": "📊 గణాంకాలు & డేటా",
        "sec_benefits": "⚖️ ప్రయోజనాలు, సవాళ్లు & నష్టాలు",
        "sec_apps": "🚀 నిజ-ప్రపంచ అనువర్తనాలు",
        "sec_outlook": "🔮 భవిష్యత్తు దృక్పథం & సిఫార్సులు",
        "sec_references": "📚 ఆధారాలు & ఉльలేఖనాలు",
        "download_section_title": "⬇️ మీ నివేదికను డౌన్‌లోడ్ చేసుకోండి",
        "btn_download_pdf": "⬇️ PDF డౌన్‌లోడ్",
        "btn_download_ppt": "⬇️ PPT డౌన్‌లోడ్",
        "pdf_err": "PDF సృష్టించడంలో విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "ppt_err": "PowerPoint సృష్టించడంలో విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.",
        "welcome_back": "మళ్లీ స్వాగతం! పరిశోధనకు సిద్ధంగా ఉన్నారా?",
        "nav_home": "హోమ్",
        "nav_research": "🔬 పరిశోధన",
        "limited_data_warn": "⚠️ ఈ అంశం కోసం పరిమిత డేటా అందుబాటులో ఉంది.",
        "limited_stats_warn": "⚠️ ఈ అంశం కోసం పరిమిత గణాంక డేటా అందుబాటులో ఉంది.",
        "concept_label": "భావన",
        "usecase_label": "ఉపయోగ సందర్భం",
        "benefit_label": "🟢 ప్రయోజనాలు",
        "challenge_label": "🟡 సవాళ్లు",
        "risk_label": "🔴 నష్టాలు & ట్రేడ్-ఆఫ్‌లు",
        "sec_future_roadmap": "భవిష్యత్తు వ్యూహాత్మక ప్రణాళిక",
        "primary_metrics_label": "ప్రాథమిక కొలమానాలు",
        "landscape_importance_label": "సందర్భ ప్రాముఖ్యత",
        "why_it_matters_text": (
            "ఈ సందర్భాన్ని అర్థం చేసుకోవడం ద్వారా నాయకులు ముఖ్యమైన పోకడలను గుర్తించవచ్చు, "
            "పరిమితులను పరిష్కరించవచ్చు మరియు వ్యూహాత్మక ప్రయోజనాన్ని పొందవచ్చు."
        ),
        "key_analysis_insights": "కీలక విశ్లేషణ అంతర్దృష్టులు",
        "supporting_data": "మద్దతు ఇచ్చే డేటా",
        "sources_references": "మూలాధారాలు & ఆధారాలు",
        "strategic_overview_heading": "వ్యూహాత్మక అవలోకనం & కీలక అంతర్దృష్టులు",
        "why_this_matters_heading": "ఇది ఎందుకు ముఖ్యం & పరిశ్రమ ప్రాముఖ్యత",
        "foundational_principles_heading": "ప్రాథమిక సూత్రాలు & కీలక పరిభాష",
        "findings_analysis_heading": "కీలక ఆవిష్కరణలు & సహాయక ఆధారాలు",
        "advantages_constraints_heading": "ప్రయోజనాలు, పరిమితులు & నష్టాల విశ్లేషణ",
        "practical_adoption_heading": "ప్రయోగాత్మక అనువర్తనం & కేస్ స్టడీస్",
        "strategic_predictions_heading": "వ్యూహాత్మక అంచనాలు & ఆధారాలు",
        "benefit_col_title": "ప్రయోజనాలు & లాభాలు",
        "challenge_col_title": "సవాళ్లు & పరిమితులు",
        "risk_col_title": "నష్టాలు & ముప్పులు",
    },
}


def get_text(key: str, lang: str = "en") -> str:
    """Get localized text with English fallback."""
    if not lang or lang not in TRANSLATIONS:
        lang = "en"
    return TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))


def detect_browser_language() -> str:
    """Detect browser language from request headers, fallback to English."""
    detected = "en"
    try:
        accept_lang = st.context.headers.get("Accept-Language", "")
        if accept_lang:
            first_lang = accept_lang.split(",")[0].split("-")[0].strip().lower()
            if first_lang in LANGUAGES:
                detected = first_lang
    except Exception:  # nosec B110
        pass
    return detected
