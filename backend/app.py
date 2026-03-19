import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import json
import numpy as np
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
import io
import base64

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, '..', 'frontend', 'templates'), static_folder=os.path.join(BASE_DIR, '..', 'frontend', 'static'))
app.secret_key = 'agrileaf_secret_key_2024_production_fixed'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agrileaf.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MODEL_PATH'] = os.path.join(BASE_DIR, '..', 'model', 'agrileaf_model.h5')
app.config['CLASS_NAMES_PATH'] = os.path.join(BASE_DIR, '..', 'model', 'class_names.json')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

# ── MODELS ────────────────────────────────────────────────────
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('Analysis', backref='user', lazy=True)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crop = db.Column(db.String(50))
    disease = db.Column(db.String(100))
    severity = db.Column(db.String(20))
    confidence = db.Column(db.Float)
    image_data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ── DISEASE DATABASE ──────────────────────────────────────────
DISEASE_DATABASE = {
    # BANANA
    "Banana___Cordana": {
        "crop": "Banana", "disease": "Cordana Leaf Spot",
        "description": "Fungal disease causing oval brown spots with yellow halos on banana leaves.",
        "severity_indicators": {"mild": "Few small spots", "moderate": "Multiple spots merging", "severe": "Large necrotic areas"},
        "chemical_treatment": "Apply Mancozeb 75% WP @ 2.5g/L or Carbendazim 50% WP @ 1g/L every 10-14 days.",
        "organic_treatment": "Spray Neem oil 3ml/L or Trichoderma viride 5g/L. Remove infected leaves immediately.",
        "prevention": "Ensure good drainage, avoid overhead irrigation, maintain proper plant spacing.",
        "yield_loss": "10-30% if untreated",
        "best_time_to_spray": "Early morning or evening. Avoid spraying in rain.",
        "indian_context": "Common in Kerala, Tamil Nadu, Andhra Pradesh banana plantations."
    },
    "Banana___Panama_Disease": {
        "crop": "Banana", "disease": "Panama Wilt (Fusarium Wilt)",
        "description": "Soil-borne fungal disease causing yellowing, wilting and internal browning of vascular tissue.",
        "severity_indicators": {"mild": "Lower leaf yellowing", "moderate": "Most leaves yellowing, plant wilting", "severe": "Complete plant collapse"},
        "chemical_treatment": "No effective chemical cure. Apply Carbendazim 1g/L as preventive soil drench.",
        "organic_treatment": "Apply Trichoderma harzianum 10g/plant to soil. Use resistant varieties like Grand Naine.",
        "prevention": "Use disease-free planting material, avoid waterlogging, maintain soil pH 6-6.5.",
        "yield_loss": "Up to 100% — plant may die",
        "best_time_to_spray": "Apply soil treatments during planting and early growth.",
        "indian_context": "Major threat to Cavendish bananas in Karnataka, Tamil Nadu, Telangana."
    },
    "Banana___Sigatoka": {
        "crop": "Banana", "disease": "Black/Yellow Sigatoka",
        "description": "Fungal disease causing streaks and spots on leaves, severely reducing photosynthesis.",
        "severity_indicators": {"mild": "Light yellow streaks", "moderate": "Dark brown spots with yellow margins", "severe": "Leaves turning black, premature ripening"},
        "chemical_treatment": "Apply Propiconazole 25% EC @ 1ml/L or Mancozeb 2.5g/L alternately every 14 days.",
        "organic_treatment": "Spray Bordeaux mixture (1%) or Neem oil 5ml/L. Defoliate severely infected leaves.",
        "prevention": "Improve air circulation, avoid dense planting, use resistant varieties.",
        "yield_loss": "20-50%",
        "best_time_to_spray": "Start spraying at first sign of infection.",
        "indian_context": "Widespread across all banana growing states in India."
    },
    "Banana___healthy": {
        "crop": "Banana", "disease": "Healthy",
        "description": "Your banana plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue regular care — proper irrigation, balanced fertilization.",
        "prevention": "Maintain field hygiene, monitor regularly for early signs of disease.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Keep monitoring every 7-10 days."
    },

    # COTTON
    "Cotton___Bacterial_Blight": {
        "crop": "Cotton", "disease": "Bacterial Blight (Angular Leaf Spot)",
        "description": "Water-soaked angular spots on leaves that turn brown. Caused by Xanthomonas citri.",
        "severity_indicators": {"mild": "Few angular spots", "moderate": "Spots merging, leaf yellowing", "severe": "Boll infection, stem cankers"},
        "chemical_treatment": "Spray Streptomycin Sulphate 500ppm + Copper Oxychloride 0.3% or Bactericidal copper compounds.",
        "organic_treatment": "Apply Pseudomonas fluorescens 5g/L. Use disease-free certified seeds.",
        "prevention": "Treat seeds with HCl (sulfuric acid delinting), use resistant varieties, avoid overhead irrigation.",
        "yield_loss": "10-40%",
        "best_time_to_spray": "At first symptom appearance. Repeat every 10-12 days.",
        "indian_context": "Major problem in Gujarat, Maharashtra, Andhra Pradesh cotton belts."
    },
    "Cotton___Curl_Virus": {
        "crop": "Cotton", "disease": "Cotton Leaf Curl Virus (CLCuV)",
        "description": "Viral disease spread by whitefly causing upward/downward curling of leaves, vein thickening.",
        "severity_indicators": {"mild": "Slight leaf curling", "moderate": "Severe curling, vein darkening", "severe": "Complete stunting, no boll formation"},
        "chemical_treatment": "Control whitefly vector: spray Imidacloprid 17.8% SL @ 0.3ml/L or Thiamethoxam 25% WG @ 0.3g/L.",
        "organic_treatment": "Apply Neem oil 5ml/L to control whitefly. Remove and destroy infected plants.",
        "prevention": "Use CLCuV resistant varieties, control whitefly population, avoid late sowing.",
        "yield_loss": "30-80% if early infection",
        "best_time_to_spray": "Start whitefly control at seedling stage.",
        "indian_context": "Devastating disease in Punjab, Haryana, Rajasthan cotton areas."
    },
    "Cotton___Fusarium_Wilt": {
        "crop": "Cotton", "disease": "Fusarium Wilt",
        "description": "Soil-borne fungal disease causing yellowing, wilting and internal vascular browning.",
        "severity_indicators": {"mild": "Lower leaves yellowing", "moderate": "Wilting of branches", "severe": "Complete plant death"},
        "chemical_treatment": "Soil drench with Carbendazim 50% WP @ 1g/L. Seed treatment with Thiram + Carbendazim.",
        "organic_treatment": "Apply Trichoderma viride 4g/kg seed treatment. Add organic matter to improve soil.",
        "prevention": "Use wilt-resistant varieties, practice crop rotation, avoid waterlogging.",
        "yield_loss": "20-60%",
        "best_time_to_spray": "Preventive soil treatment before sowing.",
        "indian_context": "Common in light sandy soils of Rajasthan, Gujarat, Madhya Pradesh."
    },
    "Cotton___healthy": {
        "crop": "Cotton", "disease": "Healthy",
        "description": "Your cotton plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue balanced NPK fertilization and proper irrigation.",
        "prevention": "Regular scouting every 7 days for early pest and disease detection.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Keep monitoring regularly during boll development stage."
    },

    # MANGO
    "Mango___Anthracnose": {
        "crop": "Mango", "disease": "Anthracnose",
        "description": "Fungal disease causing dark spots on leaves, flowers and fruits. Major post-harvest disease.",
        "severity_indicators": {"mild": "Small dark spots on leaves", "moderate": "Spots on flowers causing blossom blight", "severe": "Fruit infection, black rot"},
        "chemical_treatment": "Spray Carbendazim 50% WP @ 1g/L or Copper Oxychloride 3g/L. Start at flowering.",
        "organic_treatment": "Apply Neem oil 3ml/L or Trichoderma 5g/L. Prune dense canopy for air circulation.",
        "prevention": "Prune dead branches, avoid overhead irrigation, apply lime paste on pruning wounds.",
        "yield_loss": "20-80% in severe cases",
        "best_time_to_spray": "Start spraying at panicle emergence. Spray 3-4 times during flowering.",
        "indian_context": "Most serious mango disease in India — affects Alphonso, Dasheri, Langra varieties."
    },
    "Mango___Bacterial_Canker": {
        "crop": "Mango", "disease": "Bacterial Canker",
        "description": "Water-soaked lesions on leaves, stems and fruits that become raised cankers.",
        "severity_indicators": {"mild": "Small water-soaked spots", "moderate": "Raised cankers on leaves/stem", "severe": "Twig dieback, fruit cracking"},
        "chemical_treatment": "Spray Streptomycin 500ppm + Copper Oxychloride 0.3% or Bordeaux mixture 1%.",
        "organic_treatment": "Apply Copper-based bactericides. Prune and destroy infected parts.",
        "prevention": "Avoid mechanical injury, prune during dry weather, use certified planting material.",
        "yield_loss": "15-40%",
        "best_time_to_spray": "Spray after pruning and at new flush emergence.",
        "indian_context": "Common in Uttar Pradesh, Bihar, West Bengal mango orchards."
    },
    "Mango___Cutting_Weevil": {
        "crop": "Mango", "disease": "Mango Cutting Weevil",
        "description": "Insect pest causing characteristic cutting of leaf petioles and shoots.",
        "severity_indicators": {"mild": "Few cut petioles", "moderate": "Multiple shoots cut", "severe": "Heavy defoliation"},
        "chemical_treatment": "Spray Chlorpyrifos 20% EC @ 2ml/L or Quinalphos 25% EC @ 2ml/L.",
        "organic_treatment": "Collect and destroy fallen shoots. Apply Neem oil 5ml/L.",
        "prevention": "Regular orchard hygiene, remove weeds, apply sticky bands on tree trunks.",
        "yield_loss": "10-25%",
        "best_time_to_spray": "At new flush emergence stage.",
        "indian_context": "Common pest in South Indian mango orchards."
    },
    "Mango___Die_Back": {
        "crop": "Mango", "disease": "Die Back",
        "description": "Fungal disease causing drying and dying back of twigs from tip downward.",
        "severity_indicators": {"mild": "Tips of young shoots drying", "moderate": "Branches drying back", "severe": "Complete branch death, tree decline"},
        "chemical_treatment": "Prune affected parts, apply Copper Oxychloride paste on cut ends. Spray Carbendazim 1g/L.",
        "organic_treatment": "Apply Trichoderma paste on pruned areas. Improve drainage and soil health.",
        "prevention": "Avoid mechanical damage, proper pruning, maintain tree vigor with balanced nutrition.",
        "yield_loss": "20-50%",
        "best_time_to_spray": "After pruning infected branches.",
        "indian_context": "Affects old mango trees in all major mango growing states."
    },
    "Mango___Gall_Midge": {
        "crop": "Mango", "disease": "Mango Gall Midge",
        "description": "Insect pest causing gall formation on leaves and shoots due to larval feeding.",
        "severity_indicators": {"mild": "Few galls on leaves", "moderate": "Heavy galling on new flush", "severe": "Complete new flush destruction"},
        "chemical_treatment": "Spray Dimethoate 30% EC @ 1.5ml/L or Imidacloprid 0.3ml/L at new flush stage.",
        "organic_treatment": "Apply Neem oil 5ml/L. Collect and destroy galled leaves.",
        "prevention": "Synchronize new flush emergence, regular monitoring from January onwards.",
        "yield_loss": "15-35%",
        "best_time_to_spray": "At bud burst/new flush emergence.",
        "indian_context": "Major pest of mango in Andhra Pradesh, Telangana, Tamil Nadu."
    },
    "Mango___Powdery_Mildew": {
        "crop": "Mango", "disease": "Powdery Mildew",
        "description": "White powdery fungal growth on leaves, flowers and young fruits.",
        "severity_indicators": {"mild": "White powder on few leaves", "moderate": "Heavy powdery coating on panicles", "severe": "Flower and fruitlet drop"},
        "chemical_treatment": "Spray Wettable Sulphur 80% WP @ 3g/L or Hexaconazole 5% EC @ 1ml/L or Dinocap 48% EC @ 1ml/L.",
        "organic_treatment": "Apply Neem oil 3ml/L. Spray potassium bicarbonate 5g/L.",
        "prevention": "Avoid dense planting, prune for air circulation, avoid excess nitrogen.",
        "yield_loss": "20-70% during flowering",
        "best_time_to_spray": "Start spraying at panicle emergence. Critical to protect flowers.",
        "indian_context": "Serious problem during flowering season (Jan-March) across all mango regions."
    },
    "Mango___Sooty_Mould": {
        "crop": "Mango", "disease": "Sooty Mould",
        "description": "Black sooty coating on leaves due to fungal growth on honeydew secreted by sucking insects.",
        "severity_indicators": {"mild": "Light black coating", "moderate": "Heavy black coating reducing photosynthesis", "severe": "Complete leaf blackening"},
        "chemical_treatment": "Control sucking pests first: spray Imidacloprid 0.3ml/L. Then wash with starch solution.",
        "organic_treatment": "Spray Neem oil 5ml/L to control pest. Wash leaves with mild soap solution.",
        "prevention": "Control mealybug, scale insects and hoppers which produce honeydew.",
        "yield_loss": "10-30%",
        "best_time_to_spray": "Control insects causing honeydew — mealybug, scale.",
        "indian_context": "Associated with mango hoppers — common across all mango states."
    },
    "Mango___healthy": {
        "crop": "Mango", "disease": "Healthy",
        "description": "Your mango plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue regular care, balanced fertilization with micronutrients.",
        "prevention": "Regular pruning after harvest, orchard hygiene, monitoring for pests.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Apply preventive fungicide spray at panicle emergence as good practice."
    },

    # PEPPER
    "Pepper___Bacterial_spot": {
        "crop": "Pepper (Bell Pepper)", "disease": "Bacterial Spot",
        "description": "Water-soaked spots on leaves and fruits that turn dark brown with yellow margins.",
        "severity_indicators": {"mild": "Few spots on lower leaves", "moderate": "Multiple spots, leaf drop", "severe": "Heavy defoliation, fruit spots"},
        "chemical_treatment": "Spray Copper Hydroxide 77% WP @ 2g/L or Streptomycin 500ppm + Copper Oxychloride 0.3%.",
        "organic_treatment": "Apply Pseudomonas fluorescens 5g/L. Remove and destroy infected plant debris.",
        "prevention": "Use disease-free seeds, avoid overhead irrigation, practice crop rotation.",
        "yield_loss": "15-40%",
        "best_time_to_spray": "At first symptom. Repeat every 7-10 days during wet weather.",
        "indian_context": "Common in capsicum/chilli growing areas of Karnataka, Himachal Pradesh."
    },
    "Pepper___healthy": {
        "crop": "Pepper (Bell Pepper)", "disease": "Healthy",
        "description": "Your pepper plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue regular care with balanced fertilization.",
        "prevention": "Monitor regularly, ensure proper drainage and air circulation.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Keep monitoring every 7 days."
    },

    # POTATO
    "Potato___Early_blight": {
        "crop": "Potato", "disease": "Early Blight",
        "description": "Brown spots with concentric rings like a target on older leaves. Caused by Alternaria solani.",
        "severity_indicators": {"mild": "Few spots on lower leaves", "moderate": "Spots on middle leaves, yellowing", "severe": "Heavy defoliation, tuber infection"},
        "chemical_treatment": "Spray Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 75% WP @ 2g/L every 7-10 days.",
        "organic_treatment": "Apply Copper Sulphate 3g/L or Neem oil 3ml/L. Remove infected leaves.",
        "prevention": "Use certified seed tubers, practice crop rotation (3 years), balanced potassium nutrition.",
        "yield_loss": "10-30%",
        "best_time_to_spray": "Start preventive sprays 30-40 days after planting.",
        "indian_context": "Common in UP, Punjab, West Bengal potato growing areas."
    },
    "Potato___Late_blight": {
        "crop": "Potato", "disease": "Late Blight",
        "description": "Water-soaked lesions on leaves that turn brown-black rapidly. White mold visible underneath. Caused by Phytophthora infestans.",
        "severity_indicators": {"mild": "Small water-soaked areas", "moderate": "Large brown lesions, white mold", "severe": "Complete plant collapse within days"},
        "chemical_treatment": "Spray Metalaxyl + Mancozeb (Ridomil) @ 2.5g/L or Cymoxanil + Mancozeb @ 2g/L. Act fast — spreads quickly.",
        "organic_treatment": "Spray Copper Oxychloride 3g/L. Remove infected plants immediately.",
        "prevention": "Plant resistant varieties, avoid overhead irrigation, ensure good drainage.",
        "yield_loss": "50-100% if untreated",
        "best_time_to_spray": "EMERGENCY — spray immediately at first sign. Repeat every 5-7 days.",
        "indian_context": "Most devastating potato disease in India — major outbreaks in hills of UP, HP, WB."
    },
    "Potato___healthy": {
        "crop": "Potato", "disease": "Healthy",
        "description": "Your potato plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue regular hilling, balanced fertilization.",
        "prevention": "Monitor regularly especially during cool humid weather — ideal for blight.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Apply preventive fungicide spray during monsoon as good practice."
    },

    # RICE
    "Rice___Brown_Spot": {
        "crop": "Rice", "disease": "Brown Spot",
        "description": "Oval brown spots with gray center on leaves. Associated with nutrient deficiency. Caused by Helminthosporium oryzae.",
        "severity_indicators": {"mild": "Few spots on lower leaves", "moderate": "Spots on multiple leaves", "severe": "Heavy spotting, grain infection"},
        "chemical_treatment": "Spray Mancozeb 75% WP @ 2.5g/L or Edifenphos 50% EC @ 1ml/L.",
        "organic_treatment": "Apply Pseudomonas fluorescens 5g/L. Ensure balanced potassium fertilization.",
        "prevention": "Treat seeds with Thiram 3g/kg, apply potassium fertilizer, avoid water stress.",
        "yield_loss": "5-45%",
        "best_time_to_spray": "At tillering and panicle initiation stages.",
        "indian_context": "Common in nutrient-deficient soils across all rice growing states."
    },
    "Rice___Hispa": {
        "crop": "Rice", "disease": "Rice Hispa (Leaf Miner)",
        "description": "Insect pest — larvae mine inside leaves creating white streaks; adults scrape leaf surface.",
        "severity_indicators": {"mild": "Few white streaks on leaves", "moderate": "Multiple mined leaves", "severe": "Heavy mining, plants look burned"},
        "chemical_treatment": "Spray Chlorpyrifos 20% EC @ 2ml/L or Quinalphos 25% EC @ 2ml/L or Cartap Hydrochloride 4G @ 18kg/ha.",
        "organic_treatment": "Cut and destroy affected tillers. Release natural enemies — Tetrastichus hisparum.",
        "prevention": "Avoid dense planting, reduce nitrogen application, remove weeds.",
        "yield_loss": "10-30%",
        "best_time_to_spray": "At active infestation — spray in evening.",
        "indian_context": "Common in West Bengal, Assam, Odisha, Tamil Nadu rice fields."
    },
    "Rice___Leaf_Blast": {
        "crop": "Rice", "disease": "Leaf Blast",
        "description": "Diamond-shaped gray lesions with brown borders on leaves. Caused by Magnaporthe oryzae.",
        "severity_indicators": {"mild": "Few small diamond lesions", "moderate": "Many lesions, leaf drying", "severe": "Complete leaf death, neck blast possible"},
        "chemical_treatment": "Spray Tricyclazole 75% WP @ 0.6g/L or Isoprothiolane 40% EC @ 1.5ml/L or Carbendazim 1g/L.",
        "organic_treatment": "Apply Silicon fertilizer — increases plant resistance. Spray Pseudomonas fluorescens 5g/L.",
        "prevention": "Use blast-resistant varieties, avoid excess nitrogen, maintain proper water level.",
        "yield_loss": "10-50% — neck blast can cause 100% loss",
        "best_time_to_spray": "At first sign. Critical to spray at panicle initiation to prevent neck blast.",
        "indian_context": "Most serious rice disease in India — common in hilly areas and Eastern India."
    },
    "Rice___healthy": {
        "crop": "Rice", "disease": "Healthy",
        "description": "Your rice plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue balanced NPK fertilization and proper water management.",
        "prevention": "Monitor regularly, maintain proper plant spacing for air circulation.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Apply preventive spray at tillering stage during humid conditions."
    },

    # TOMATO
    "Tomato___Bacterial_spot": {
        "crop": "Tomato", "disease": "Bacterial Spot",
        "description": "Small water-soaked spots on leaves and fruits turning dark brown with yellow halo.",
        "severity_indicators": {"mild": "Few spots on lower leaves", "moderate": "Multiple spots, leaf drop", "severe": "Heavy defoliation, fruit lesions"},
        "chemical_treatment": "Spray Copper Hydroxide 77% WP @ 2g/L or Streptomycin 500ppm + Copper Oxychloride 0.3%.",
        "organic_treatment": "Apply Pseudomonas fluorescens 5g/L. Avoid overhead irrigation.",
        "prevention": "Use disease-free seeds, crop rotation, avoid working in wet conditions.",
        "yield_loss": "15-40%",
        "best_time_to_spray": "At first symptom. Repeat every 7-10 days.",
        "indian_context": "Common in Karnataka, Andhra Pradesh, Maharashtra tomato growing areas."
    },
    "Tomato___Early_blight": {
        "crop": "Tomato", "disease": "Early Blight",
        "description": "Dark brown spots with concentric target rings on older leaves. Caused by Alternaria solani.",
        "severity_indicators": {"mild": "Few spots on older leaves", "moderate": "Multiple target spots, yellowing", "severe": "Heavy defoliation from bottom up"},
        "chemical_treatment": "Spray Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 75% WP @ 2g/L or Iprodione 50% WP @ 2g/L.",
        "organic_treatment": "Apply Copper Oxychloride 3g/L or Neem oil 3ml/L.",
        "prevention": "Stake plants for air circulation, mulch to prevent soil splash, crop rotation.",
        "yield_loss": "10-30%",
        "best_time_to_spray": "Start sprays at first sign of symptoms.",
        "indian_context": "Very common in all tomato growing regions of India."
    },
    "Tomato___Late_blight": {
        "crop": "Tomato", "disease": "Late Blight",
        "description": "Large irregular water-soaked lesions turning brown-black. White mold on leaf undersides. Caused by Phytophthora infestans.",
        "severity_indicators": {"mild": "Small water-soaked patches", "moderate": "Large brown lesions with white mold", "severe": "Plant collapse, complete fruit rot"},
        "chemical_treatment": "Spray Metalaxyl + Mancozeb @ 2.5g/L or Cymoxanil 8% + Mancozeb 64% @ 2g/L. Act immediately.",
        "organic_treatment": "Spray Copper Oxychloride 3g/L. Remove and destroy infected plants.",
        "prevention": "Avoid overhead irrigation, improve drainage, grow resistant varieties.",
        "yield_loss": "50-100%",
        "best_time_to_spray": "EMERGENCY — spray immediately. Repeat every 5-7 days.",
        "indian_context": "Major threat during cool humid weather in hills and during rains."
    },
    "Tomato___Leaf_Mold": {
        "crop": "Tomato", "disease": "Leaf Mold",
        "description": "Yellow patches on upper leaf surface with olive-green to gray mold on underside. Caused by Passalora fulva.",
        "severity_indicators": {"mild": "Few yellow patches", "moderate": "Multiple patches with visible mold", "severe": "Heavy mold, premature leaf drop"},
        "chemical_treatment": "Spray Chlorothalonil 75% WP @ 2g/L or Mancozeb 2.5g/L or Copper Fungicides.",
        "organic_treatment": "Improve ventilation in greenhouse. Apply Neem oil 3ml/L.",
        "prevention": "Reduce humidity, improve air circulation, avoid wetting foliage.",
        "yield_loss": "10-40%",
        "best_time_to_spray": "At first appearance of yellow patches.",
        "indian_context": "Mainly a problem in protected cultivation (polyhouse) tomatoes."
    },
    "Tomato___Mosaic_Virus": {
        "crop": "Tomato", "disease": "Tomato Mosaic Virus (ToMV)",
        "description": "Light and dark green mosaic pattern on leaves, leaf distortion, stunted growth.",
        "severity_indicators": {"mild": "Light mosaic on few leaves", "moderate": "Clear mosaic, some distortion", "severe": "Severe mosaic, stunting, poor fruit set"},
        "chemical_treatment": "No cure for viral disease. Control aphid vectors with Imidacloprid 0.3ml/L.",
        "organic_treatment": "Remove infected plants. Spray Neem oil 5ml/L to control aphid vectors.",
        "prevention": "Use virus-free seeds/transplants, control aphids, disinfect tools with bleach.",
        "yield_loss": "20-60%",
        "best_time_to_spray": "Control aphid vectors preventively.",
        "indian_context": "Spread through contaminated hands and tools — wash hands before handling plants."
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato", "disease": "Septoria Leaf Spot",
        "description": "Small circular spots with dark borders and gray/white centers with dark dots inside. Caused by Septoria lycopersici.",
        "severity_indicators": {"mild": "Few spots on lower leaves", "moderate": "Heavy spotting progressing upward", "severe": "Complete defoliation"},
        "chemical_treatment": "Spray Mancozeb 75% WP @ 2.5g/L or Chlorothalonil 2g/L or Copper Oxychloride 3g/L.",
        "organic_treatment": "Apply Copper-based fungicides. Remove infected lower leaves.",
        "prevention": "Avoid overhead watering, stake plants, mulch soil, practice crop rotation.",
        "yield_loss": "20-50%",
        "best_time_to_spray": "At first sign. Spray every 7-10 days.",
        "indian_context": "Common in humid regions during kharif tomato season."
    },
    "Tomato___Spider_mites": {
        "crop": "Tomato", "disease": "Spider Mite Infestation",
        "description": "Tiny mites causing yellow stippling on leaves, webbing on undersides. Leaves turn bronze.",
        "severity_indicators": {"mild": "Light stippling on few leaves", "moderate": "Yellow stippling with visible webbing", "severe": "Bronze/brown leaves, heavy webbing, plant stress"},
        "chemical_treatment": "Spray Abamectin 1.8% EC @ 0.5ml/L or Spiromesifen 22.9% SC @ 1ml/L or Dicofol 18.5% EC @ 2.5ml/L.",
        "organic_treatment": "Spray Neem oil 5ml/L or insecticidal soap. Release predatory mite Phytoseiulus persimilis.",
        "prevention": "Avoid dusty conditions, maintain proper irrigation, avoid excess nitrogen.",
        "yield_loss": "15-40%",
        "best_time_to_spray": "Spray under leaf surface. Repeat after 5-7 days.",
        "indian_context": "Severe problem during hot dry conditions — common in summer tomato crop."
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato", "disease": "Target Spot",
        "description": "Brown circular lesions with concentric rings on leaves and fruits. Caused by Corynespora cassiicola.",
        "severity_indicators": {"mild": "Few circular spots", "moderate": "Multiple target spots, leaf yellowing", "severe": "Heavy defoliation, fruit spots"},
        "chemical_treatment": "Spray Azoxystrobin 23% SC @ 1ml/L or Difenoconazole 25% EC @ 0.5ml/L or Mancozeb 2.5g/L.",
        "organic_treatment": "Apply Copper Oxychloride 3g/L. Remove infected plant debris.",
        "prevention": "Improve air circulation, avoid overhead irrigation, remove infected leaves.",
        "yield_loss": "10-30%",
        "best_time_to_spray": "At first appearance. Repeat every 10-14 days.",
        "indian_context": "Increasingly common in South Indian tomato growing areas."
    },
    "Tomato___Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato", "disease": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "description": "Severe upward curling and yellowing of leaves, stunted growth, flower drop. Spread by whitefly.",
        "severity_indicators": {"mild": "Slight yellowing of young leaves", "moderate": "Severe curling and yellowing", "severe": "Complete stunting, no fruit production"},
        "chemical_treatment": "No cure. Control whitefly: spray Imidacloprid 17.8% SL @ 0.3ml/L or Thiamethoxam 0.3g/L.",
        "organic_treatment": "Use yellow sticky traps, Neem oil 5ml/L spray, silver mulch to repel whitefly.",
        "prevention": "Use TYLCV-resistant varieties (like Naveen, Abhinav), use insect-proof nets in nursery.",
        "yield_loss": "50-100%",
        "best_time_to_spray": "Control whitefly from transplanting stage.",
        "indian_context": "Most serious tomato virus in India — widespread in Karnataka, AP, Tamil Nadu."
    },
    "Tomato___healthy": {
        "crop": "Tomato", "disease": "Healthy",
        "description": "Your tomato plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue regular care with balanced NPK + micronutrient fertilization.",
        "prevention": "Monitor every 3-4 days, stake plants, mulch to prevent soil splash.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Apply preventive fungicide once a month as good practice."
    },

    # WHEAT
    "Wheat___Brown_Rust": {
        "crop": "Wheat", "disease": "Brown Rust (Leaf Rust)",
        "description": "Orange-brown pustules scattered on leaf surface. Caused by Puccinia triticina.",
        "severity_indicators": {"mild": "Few pustules on lower leaves", "moderate": "Many pustules on multiple leaves", "severe": "Heavy pustule coverage, premature leaf death"},
        "chemical_treatment": "Spray Propiconazole 25% EC @ 1ml/L or Tebuconazole 25.9% EC @ 1ml/L at first sign.",
        "organic_treatment": "Apply Sulphur 80% WP @ 3g/L. Use resistant varieties.",
        "prevention": "Grow resistant varieties, timely sowing, avoid excess nitrogen.",
        "yield_loss": "10-40%",
        "best_time_to_spray": "At first pustule appearance — early action critical.",
        "indian_context": "Common in Punjab, Haryana, UP wheat belt during February-March."
    },
    "Wheat___Septoria": {
        "crop": "Wheat", "disease": "Septoria Leaf Blotch",
        "description": "Tan-brown irregular blotches with yellow margins on leaves. Caused by Zymoseptoria tritici.",
        "severity_indicators": {"mild": "Small blotches on lower leaves", "moderate": "Large blotches progressing up plant", "severe": "Flag leaf infection, severe yield loss"},
        "chemical_treatment": "Spray Propiconazole 25% EC @ 1ml/L or Azoxystrobin + Propiconazole @ 1ml/L.",
        "organic_treatment": "Apply Copper Oxychloride 3g/L. Improve air circulation.",
        "prevention": "Use resistant varieties, avoid dense sowing, crop rotation with non-cereal crops.",
        "yield_loss": "10-50%",
        "best_time_to_spray": "At flag leaf stage — most critical time.",
        "indian_context": "More common in North-East India and hilly wheat growing regions."
    },
    "Wheat___Smut": {
        "crop": "Wheat", "disease": "Loose Smut",
        "description": "Entire wheat head replaced by black powdery smut spore mass. Caused by Ustilago tritici.",
        "severity_indicators": {"mild": "Few smutted heads in field", "moderate": "10-20% heads affected", "severe": "Heavy smut incidence across field"},
        "chemical_treatment": "Seed treatment with Carboxin 75% WP @ 2g/kg seed or Tebuconazole 2% DS @ 1.5g/kg seed.",
        "organic_treatment": "Hot water seed treatment at 52°C for 10 minutes. Use certified smut-free seeds.",
        "prevention": "Seed treatment is the only effective control — must be done before sowing.",
        "yield_loss": "Up to 30% if widespread",
        "best_time_to_spray": "Seed treatment before sowing — cannot control after infection.",
        "indian_context": "Present wherever wheat is grown — Punjab, Haryana, UP, Rajasthan."
    },
    "Wheat___Yellow_Rust": {
        "crop": "Wheat", "disease": "Yellow Rust (Stripe Rust)",
        "description": "Yellow-orange pustules in stripes along leaf veins. Caused by Puccinia striiformis.",
        "severity_indicators": {"mild": "Few yellow stripes", "moderate": "Heavy striping on multiple leaves", "severe": "Complete yellowing, plant death possible"},
        "chemical_treatment": "Spray Propiconazole 25% EC @ 1ml/L or Tebuconazole 25.9% EC @ 1ml/L immediately.",
        "organic_treatment": "Apply Sulphur dust 20-25kg/ha. Use resistant varieties.",
        "prevention": "Grow resistant varieties (HD-2967, PBW-550), timely sowing, avoid late planting.",
        "yield_loss": "10-70% — can be catastrophic",
        "best_time_to_spray": "URGENT — spray within 48 hours of first sign. Spreads extremely fast.",
        "indian_context": "Highly destructive in North-West India (Punjab, HP, Uttarakhand) — major epidemic risk."
    },
    "Wheat___healthy": {
        "crop": "Wheat", "disease": "Healthy",
        "description": "Your wheat plant appears healthy with no visible disease symptoms.",
        "severity_indicators": {"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
        "chemical_treatment": "No treatment needed.",
        "organic_treatment": "Continue balanced fertilization — ensure adequate potassium for disease resistance.",
        "prevention": "Monitor weekly especially during Feb-March when rust risk is high.",
        "yield_loss": "None",
        "best_time_to_spray": "N/A",
        "indian_context": "Keep monitoring regularly during heading stage."
    },
}

CLASS_TO_DB = {
    "Banana___Cordana": "Banana___Cordana",
    "Banana___Panama_Disease": "Banana___Panama_Disease",
    "Banana___Sigatoka": "Banana___Sigatoka",
    "Banana___healthy": "Banana___healthy",
    "Cotton___Bacterial_Blight": "Cotton___Bacterial_Blight",
    "Cotton___Curl_Virus": "Cotton___Curl_Virus",
    "Cotton___Fusarium_Wilt": "Cotton___Fusarium_Wilt",
    "Cotton___healthy": "Cotton___healthy",
    "Mango___Anthracnose": "Mango___Anthracnose",
    "Mango___Bacterial_Canker": "Mango___Bacterial_Canker",
    "Mango___Cutting_Weevil": "Mango___Cutting_Weevil",
    "Mango___Die_Back": "Mango___Die_Back",
    "Mango___Gall_Midge": "Mango___Gall_Midge",
    "Mango___Powdery_Mildew": "Mango___Powdery_Mildew",
    "Mango___Sooty_Mould": "Mango___Sooty_Mould",
    "Mango___healthy": "Mango___healthy",
    "Pepper___Bacterial_spot": "Pepper___Bacterial_spot",
    "Pepper___healthy": "Pepper___healthy",
    "Potato___Early_blight": "Potato___Early_blight",
    "Potato___Late_blight": "Potato___Late_blight",
    "Potato___healthy": "Potato___healthy",
    "Rice___Brown_Spot": "Rice___Brown_Spot",
    "Rice___Hispa": "Rice___Hispa",
    "Rice___Leaf_Blast": "Rice___Leaf_Blast",
    "Rice___healthy": "Rice___healthy",
    "Tomato___Bacterial_spot": "Tomato___Bacterial_spot",
    "Tomato___Early_blight": "Tomato___Early_blight",
    "Tomato___Late_blight": "Tomato___Late_blight",
    "Tomato___Leaf_Mold": "Tomato___Leaf_Mold",
    "Tomato___Mosaic_Virus": "Tomato___Mosaic_Virus",
    "Tomato___Septoria_leaf_spot": "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites": "Tomato___Spider_mites",
    "Tomato___Target_Spot": "Tomato___Target_Spot",
    "Tomato___Yellow_Leaf_Curl_Virus": "Tomato___Yellow_Leaf_Curl_Virus",
    "Tomato___healthy": "Tomato___healthy",
    "Wheat___Brown_Rust": "Wheat___Brown_Rust",
    "Wheat___Septoria": "Wheat___Septoria",
    "Wheat___Smut": "Wheat___Smut",
    "Wheat___Yellow_Rust": "Wheat___Yellow_Rust",
    "Wheat___healthy": "Wheat___healthy",
}

SUPPORTED_CROPS = {"tomato", "potato", "pepper", "rice", "wheat", "cotton", "mango", "banana", "auto"}

# ── FOLLOW-UP QUESTIONS ───────────────────────────────────────
FOLLOWUP_QUESTIONS = {
    "Tomato___Late_blight": [
        {"id": "q1", "text": "Are the spots wet and water-soaked, or dry and papery?", "options": ["Wet and water-soaked", "Dry and papery"], "weights": [1.5, 0.5]},
        {"id": "q2", "text": "Can you see white fuzzy growth on the underside of the leaf?", "options": ["Yes, clearly visible", "No, not visible"], "weights": [2.0, 0.3]},
        {"id": "q3", "text": "Has it rained or been very humid in the last 3 days?", "options": ["Yes, very humid/rainy", "No, dry weather"], "weights": [1.3, 0.7]}
    ],
    "Tomato___Early_blight": [
        {"id": "q1", "text": "Do the spots have ring patterns like a bullseye?", "options": ["Yes, clear rings", "No, just plain brown spots"], "weights": [2.0, 0.4]},
        {"id": "q2", "text": "Are spots mainly on older lower leaves?", "options": ["Yes, older lower leaves", "Young upper leaves"], "weights": [1.8, 0.3]},
        {"id": "q3", "text": "Are the spots surrounded by yellow areas?", "options": ["Yes, yellow border", "No yellow border"], "weights": [1.4, 0.7]}
    ],
    "Tomato___Yellow_Leaf_Curl_Virus": [
        {"id": "q1", "text": "Are the leaves curling upward?", "options": ["Yes, curling upward", "No, leaves are flat"], "weights": [2.0, 0.3]},
        {"id": "q2", "text": "Do you see tiny white insects when you shake the plant?", "options": ["Yes, many whiteflies", "No insects seen"], "weights": [1.8, 0.5]},
        {"id": "q3", "text": "Are the young leaves yellowing while older leaves look greener?", "options": ["Yes, young leaves yellow", "No, uniform color"], "weights": [1.6, 0.5]}
    ],
    "Potato___Late_blight": [
        {"id": "q1", "text": "Are new spots appearing daily - spreading rapidly?", "options": ["Yes, spreading fast", "Slow or no spread"], "weights": [2.0, 0.4]},
        {"id": "q2", "text": "Do you see white mold on the underside of infected areas?", "options": ["Yes, white mold visible", "No white mold"], "weights": [2.0, 0.3]},
        {"id": "q3", "text": "Does the infected tissue smell rotten?", "options": ["Yes, foul smell", "No smell"], "weights": [1.5, 0.6]}
    ],
    "Rice___Leaf_Blast": [
        {"id": "q1", "text": "What shape are the lesions?", "options": ["Diamond/spindle shaped", "Irregular or round"], "weights": [2.0, 0.4]},
        {"id": "q2", "text": "Do lesions have a gray center with brown border?", "options": ["Yes, gray center brown edge", "No, uniform color"], "weights": [1.8, 0.5]},
        {"id": "q3", "text": "Are the neck/collar areas also affected?", "options": ["Yes, neck also infected", "Only leaves affected"], "weights": [1.5, 0.8]}
    ],
    "Cotton___Curl_Virus": [
        {"id": "q1", "text": "Are the leaf veins thickened and darkened?", "options": ["Yes, veins thick and dark", "No, veins look normal"], "weights": [2.0, 0.3]},
        {"id": "q2", "text": "Are small cup-like growths visible on leaf undersides?", "options": ["Yes, cup-like growths", "No such growths"], "weights": [1.8, 0.4]},
        {"id": "q3", "text": "Is the plant stunted compared to nearby healthy plants?", "options": ["Yes, much smaller", "Normal height"], "weights": [1.4, 0.7]}
    ],
    "Wheat___Yellow_Rust": [
        {"id": "q1", "text": "Are the pustules arranged in stripes along leaf veins?", "options": ["Yes, in clear stripes", "Scattered randomly"], "weights": [2.0, 0.3]},
        {"id": "q2", "text": "What color are the pustules?", "options": ["Bright yellow-orange", "Dark brown/orange"], "weights": [2.0, 0.4]},
        {"id": "q3", "text": "Is it spreading to neighboring plants quickly?", "options": ["Yes, spreading fast", "Contained to few plants"], "weights": [1.5, 0.8]}
    ],
    "Mango___Powdery_Mildew": [
        {"id": "q1", "text": "Is white powder on flowers or young fruits too?", "options": ["Yes, on flowers/fruits too", "Only on leaves"], "weights": [2.0, 0.7]},
        {"id": "q2", "text": "Are flowers or young fruits dropping prematurely?", "options": ["Yes, heavy drop", "No drop observed"], "weights": [1.8, 0.5]},
        {"id": "q3", "text": "Does the white powder wipe off easily when touched?", "options": ["Yes, wipes off easily", "Does not wipe off"], "weights": [1.6, 0.4]}
    ],
    "Banana___Sigatoka": [
        {"id": "q1", "text": "Are streaks turning from yellow to dark brown or black?", "options": ["Yes, turning black", "Still yellow streaks"], "weights": [1.8, 0.8]},
        {"id": "q2", "text": "Are multiple leaves on the same plant affected?", "options": ["Yes, most leaves affected", "Only 1-2 leaves"], "weights": [1.5, 0.7]},
        {"id": "q3", "text": "Are spots merging into large dead areas?", "options": ["Yes, large dead patches", "Still small separate spots"], "weights": [1.6, 0.7]}
    ]
}

# ── ML MODEL LOADING ──────────────────────────────────────────
model = None
class_names = {}

def load_model():
    global model, class_names
    try:
        import tensorflow as tf
        model_path = app.config['MODEL_PATH']
        names_path = app.config['CLASS_NAMES_PATH']
        if os.path.exists(model_path) and os.path.exists(names_path):
            model = tf.keras.models.load_model(model_path)
            with open(names_path, 'r') as f:
                class_names = json.load(f)
            print(f"[AI] Model loaded — {len(class_names)} classes")
        else:
            print("[AI] Model file not found — running in Demo Mode")
    except Exception as e:
        print(f"[AI] Model load error: {e} — running in Demo Mode")

def predict_disease(image_bytes, selected_crop='auto'):
    if model is None:
        return demo_prediction(selected_crop)
    try:
        import tensorflow as tf
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        predictions = model.predict(img_array, verbose=0)
        top_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][top_idx])
        predicted_class = class_names.get(str(top_idx), "Unknown")

        if selected_crop != 'auto':
            crop_cap = selected_crop.capitalize()
            crop_predictions = {
                class_names[str(i)]: float(predictions[0][i])
                for i in range(len(class_names))
                if class_names[str(i)].lower().startswith(selected_crop.lower())
            }
            if crop_predictions:
                predicted_class = max(crop_predictions, key=crop_predictions.get)
                confidence = crop_predictions[predicted_class]

        db_key = CLASS_TO_DB.get(predicted_class, predicted_class)
        disease_info = DISEASE_DATABASE.get(db_key, {
            "crop": predicted_class.split("___")[0],
            "disease": predicted_class.split("___")[1] if "___" in predicted_class else predicted_class,
            "description": "Disease information not available.",
            "chemical_treatment": "Consult local agricultural officer.",
            "organic_treatment": "Consult local agricultural officer.",
            "prevention": "Monitor regularly.",
            "yield_loss": "Unknown",
            "best_time_to_spray": "Consult expert",
            "indian_context": "Consult your nearest KVK."
        })

        severity = calculate_severity(confidence)

        return {
            "success": True,
            "predicted_class": predicted_class,
            "confidence": round(confidence * 100, 2),
            "severity": severity,
            "disease_info": disease_info,
            "mode": "CNN"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_severity(confidence):
    if confidence >= 0.85:
        return "severe"
    elif confidence >= 0.60:
        return "moderate"
    else:
        return "mild"

def demo_prediction(crop='tomato'):
    key = "Tomato___Early_blight"
    info = DISEASE_DATABASE[key]
    return {
        "success": True,
        "predicted_class": key,
        "confidence": 87.5,
        "severity": "moderate",
        "disease_info": info,
        "mode": "Demo"
    }

# ── ROUTES ────────────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', full_name=session.get('username', 'Farmer'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username','')
            email = data.get('email','')
            password = data.get('password','')
        else:
            username = request.form.get('username','')
            email = request.form.get('email','')
            password = request.form.get('password','')
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Username already exists'})
            return render_template('register.html')
        user = User(
            username=username,
            email=username + '@agrileaf.local',
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        session.permanent = True
        session['user_id'] = user.id
        session['username'] = user.username
        if request.is_json:
            return jsonify({'success': True, 'username': user.username})
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username','')
            password = data.get('password','')
        else:
            username = request.form.get('username','')
            password = request.form.get('password','')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username
            if request.is_json:
                return jsonify({'success': True, 'username': user.username})
            return redirect(url_for('index'))
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
        return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    analyses = Analysis.query.filter_by(user_id=session['user_id']).order_by(Analysis.timestamp.desc()).limit(20).all()
    return render_template('dashboard.html', user=user, analyses=analyses)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please login first'})
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'})

    try:
        file = request.files['image']
        selected_crop = (request.form.get('crop_type') or request.form.get('crop') or 'auto').lower()
        image_bytes = file.read()
        result = predict_disease(image_bytes, selected_crop)
    except Exception as e:
        return jsonify({'success': False, 'error': 'Analysis failed. Please try again.'})

    if result.get('success'):
        try:
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
            analysis = Analysis(user_id=session['user_id'],
                crop=result['disease_info'].get('crop', 'Unknown'),
                disease=result['disease_info'].get('disease', 'Unknown'),
                severity=result['severity'], confidence=result['confidence'], image_data=img_b64[:500])
            db.session.add(analysis)
            db.session.commit()
        except Exception as e:
            print('[DB Error]', e)

        info = result.get('disease_info', {})
        predicted = result.get('predicted_class', 'Unknown')
        conf = round(float(result.get('confidence', 0)), 1)
        sev = result.get('severity', 'moderate')
        is_healthy = 'healthy' in predicted.lower()
        return jsonify({
            'success': True, 'is_healthy': is_healthy, 'confidence': conf,
            'model_used': result.get('mode', 'CNN'),
            'predicted_class': predicted,
            'top_predictions': [{'class': predicted, 'confidence': conf}],
            'recommendation': {
                'disease': info.get('disease', predicted.replace('___',' ').replace('_',' ')),
                'crop': info.get('crop', predicted.split('___')[0] if '___' in predicted else 'Unknown'),
                'pathogen': info.get('pathogen', info.get('disease', '')),
                'severity_level': sev,
                'severity_description': sev.capitalize() + ' infection detected',
                'description': info.get('description', 'Disease detected by AgriLeaf AI.'),
                'symptoms': info.get('symptoms', []),
                'chemical_treatment': info.get('chemical_treatment', ''),
                'organic_treatment': info.get('organic_treatment', ''),
                'prevention': info.get('prevention', ''),
                'yield_impact': info.get('yield_loss', 'Monitor closely'),
                'best_time_to_spray': info.get('best_time_to_spray', 'Morning 6-9 AM'),
                'india_tip': info.get('indian_context', '')
            }
        })
    return jsonify(result)

@app.route('/history')
def history():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    analyses = Analysis.query.filter_by(user_id=session['user_id']).order_by(Analysis.timestamp.desc()).all()
    total = len(analyses)
    healthy = sum(1 for a in analyses if 'healthy' in a.disease.lower())
    return jsonify({'success': True, 'total': total, 'healthy_count': healthy, 'diseased_count': total - healthy,
        'history': [{'id': a.id, 'crop': a.crop, 'disease': a.disease, 'severity': a.severity,
            'confidence': round(a.confidence, 1), 'is_healthy': 'healthy' in a.disease.lower(),
            'date': a.timestamp.strftime('%d %b %Y'), 'time': a.timestamp.strftime('%I:%M %p')}
            for a in analyses]})

@app.route('/model_status')
def model_status():
    return jsonify({
        'model_loaded': model is not None,
        'num_classes': len(class_names),
        'mode': 'CNN Active' if model is not None else 'Demo Mode'
    })


@app.route('/tools')
def tools():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('tools.html', full_name=session.get('username', 'Farmer'))

@app.route('/advanced')
def advanced():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('advanced.html', full_name=session.get('username', 'Farmer'))

@app.route('/followup_questions', methods=['POST'])
def get_followup_questions():
    data = request.get_json()
    predicted_class = data.get('predicted_class', '')
    questions = FOLLOWUP_QUESTIONS.get(predicted_class, [])
    return jsonify({'success': True, 'has_questions': len(questions) > 0,
        'questions': [{'id': q['id'], 'text': q['text'], 'options': q['options']} for q in questions],
        'disease': predicted_class})

@app.route('/confirm_diagnosis', methods=['POST'])
def confirm_diagnosis():
    data = request.get_json()
    predicted_class = data.get('predicted_class', '')
    answers = data.get('answers', [])
    original_severity = data.get('severity', 'moderate')
    questions = FOLLOWUP_QUESTIONS.get(predicted_class, [])
    if not questions or not answers:
        return jsonify({'success': True, 'confirmed': True, 'adjusted_severity': original_severity, 'message': 'Diagnosis confirmed.', 'confidence_boost': 0})
    score = 0
    max_score = 0
    for i, q in enumerate(questions):
        if i < len(answers):
            answer_idx = int(answers[i])
            weight = q['weights'][answer_idx] if answer_idx < len(q['weights']) else 1.0
            score += weight
            max_score += max(q['weights'])
    ratio = score / max_score if max_score > 0 else 0.5
    if ratio >= 0.75:
        adjusted_severity = 'severe' if original_severity in ['moderate','severe'] else 'moderate'
        confirmed = True
        message = 'Symptoms strongly confirm the AI diagnosis. Act immediately.'
    elif ratio >= 0.5:
        adjusted_severity = original_severity
        confirmed = True
        message = 'Symptoms are consistent with the diagnosis. Begin treatment soon.'
    else:
        adjusted_severity = 'mild'
        confirmed = False
        message = 'Symptoms are mild or inconsistent. Monitor closely and rescan in 2-3 days.'
    return jsonify({'success': True, 'confirmed': confirmed, 'confirmation_ratio': round(ratio, 2),
        'adjusted_severity': adjusted_severity, 'confidence_boost': round((ratio - 0.5) * 20, 1), 'message': message})


@app.route('/history/clear', methods=['DELETE'])
def history_clear():
    if 'user_id' not in session:
        return jsonify({'success': False})
    Analysis.query.filter_by(user_id=session['user_id']).delete()
    db.session.commit()
    return jsonify({'success': True})

with app.app_context():
    db.create_all()
load_model()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)