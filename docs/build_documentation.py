"""
Build docs/AmropaliNet_Documentation.pdf - bilingual (English + Bangla) project documentation.

    python docs/build_documentation.py

Needs: fpdf2 and uharfbuzz (both in api/requirements.txt). Uses the Hind Siliguri font
bundled in mango_disease_ai/fonts. Bangla lines are wrapped here and drawn one by one,
because fpdf2's own wrapping can mis-shape wrapped Bangla lines.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "mango_disease_ai" / "fonts"
OUT = ROOT / "docs" / "AmropaliNet_Documentation.pdf"

GREEN_DARK = (27, 94, 32)
GREEN = (46, 125, 50)
TINT = (241, 247, 232)
MANGO = (251, 140, 0)
MANGO_TINT = (255, 244, 219)
INK = (29, 58, 31)
SOFT = (78, 107, 74)
MUTED = (120, 135, 115)
BORDER = (220, 235, 205)
CODE_BG = (15, 29, 19)

PAGE_W, PAGE_H = 210, 297
M = 16
W = PAGE_W - 2 * M
BOTTOM = PAGE_H - 20


# ─────────────────────────────────────────────────────────────────────────────
# Content
# ─────────────────────────────────────────────────────────────────────────────
PROBLEM_EN = (
    "Amrapali is one of the most widely grown mangoes in Bangladesh, and thousands of families in "
    "Rajshahi, Chapainawabganj, Naogaon, Dinajpur and the hill tracts depend on it for their income. "
    "Every season, fungal and bacterial diseases such as Anthracnose, Powdery Mildew, Bacterial Canker "
    "and Stem End Rot attack leaves, flowers and fruit. Most farmers cannot easily tell these diseases "
    "apart, and an agriculture officer is often far away. The usual answer is calendar-based, blanket "
    "spraying: the whole orchard is sprayed with several chemicals \"just in case\", often more often and "
    "in higher doses than needed. This creates three linked problems. First, the environment: extra "
    "fungicides and insecticides wash into soil, ponds and canals, harm the bees and other pollinators "
    "that mango flowers need, and help pathogens become resistant. Second, waste: when a disease is found "
    "late, it has already spread from tree to tree, and part of the harvest rots on the tree, in storage "
    "or during transport. Every rotten mango wastes the water, land, fertiliser and labour used to grow "
    "it. Third, livelihoods: farmers pay for chemicals they did not need and still lose fruit, while "
    "consumers face more chemical residue. Existing tools are often English-only, need expert knowledge, "
    "or do not show where the disease is. Farmers need a simple, trustworthy tool in their own language "
    "that tells them early, from one phone photo, exactly what is wrong and what to do."
)
PROBLEM_BN = (
    "আম্রপালি বাংলাদেশে সবচেয়ে বেশি চাষ হওয়া আমগুলোর একটি। রাজশাহী, চাঁপাইনবাবগঞ্জ, নওগাঁ, দিনাজপুর ও "
    "পার্বত্য অঞ্চলের হাজারো পরিবার এর আয়ের উপর নির্ভর করে। প্রতি মৌসুমে অ্যানথ্রাকনোজ, পাউডারি মিলডিউ, "
    "ব্যাকটেরিয়াল ক্যাঙ্কার ও বোঁটা পচার মতো রোগ পাতা, মুকুল ও ফলে আক্রমণ করে। বেশিরভাগ কৃষক রোগগুলো "
    "সহজে আলাদা করে চিনতে পারেন না, আর কৃষি কর্মকর্তা প্রায়ই দূরে থাকেন। তাই সাধারণ সমাধান হয় ক্যালেন্ডার "
    "মেনে পুরো বাগানে ঢালাও স্প্রে - প্রয়োজনের চেয়ে বেশি বার ও বেশি মাত্রায়। এতে তিনটি সমস্যা তৈরি হয়। "
    "প্রথমত পরিবেশ: বাড়তি ছত্রাকনাশক ও কীটনাশক মাটি, পুকুর ও খালে মেশে, আমের মুকুলে পরাগায়নকারী "
    "মৌমাছির ক্ষতি করে এবং রোগজীবাণুকে ওষুধ-প্রতিরোধী করে তোলে। দ্বিতীয়ত অপচয়: দেরিতে রোগ ধরা পড়লে তা "
    "গাছ থেকে গাছে ছড়িয়ে যায়, আর ফলের একটি অংশ গাছে, গুদামে বা পরিবহনে পচে যায়। প্রতিটি পচা আম মানে তা "
    "ফলাতে খরচ হওয়া পানি, জমি, সার ও শ্রমের অপচয়। তৃতীয়ত জীবিকা: কৃষক অপ্রয়োজনীয় রাসায়নিকের দাম দেন, "
    "তবুও ফল হারান; আর ভোক্তা পান বেশি রাসায়নিক অবশিষ্টাংশ। প্রচলিত অনেক সমাধান শুধু ইংরেজিতে, বিশেষজ্ঞ "
    "জ্ঞান লাগে, অথবা রোগ ঠিক কোথায় তা দেখায় না। কৃষকের দরকার নিজের ভাষায় একটি সহজ ও বিশ্বাসযোগ্য টুল, "
    "যা ফোনের একটি ছবি থেকেই আগেভাগে বলে দেবে ঠিক কী হয়েছে এবং কী করতে হবে।"
)
SOLUTION_EN = (
    "AmropaliNet is a free, bilingual (Bangla and English) web app that turns any phone into a mango "
    "disease doctor. The farmer takes one photo of a mango fruit or leaf. First, a two-step mango check "
    "rejects photos that are not mangoes, so advice is never based on a wrong image. Then our own deep "
    "learning model, AA-ENet (EfficientNet-B0 with CBAM attention and a Transformer encoder, trained on "
    "3,500 Amrapali images), identifies the photo as healthy or one of six diseases. Grad-CAM shows where "
    "the model looked, and the likely affected area is outlined in red, so the farmer can see the problem "
    "instead of trusting a black box. The app then gives plain-language advice: what to do now, signs to "
    "check, how the disease spreads through the garden, and how to prevent it. A one-page PDF report, in "
    "Bangla or English, can be shown to an agriculture officer or kept as a record. The same engine is "
    "published as an open Python library (mango-disease-ai on PyPI) with a REST API, so other developers, "
    "agriculture apps and researchers can reuse it. By replacing guesswork with early, exact diagnosis, "
    "AmropaliNet helps farmers treat only the sick trees with the right product, spray less, lose less "
    "fruit, and protect the soil, water and pollinators around their orchards."
)
SOLUTION_BN = (
    "আম্রপালিনেট একটি বিনামূল্যের, দুই ভাষার (বাংলা ও ইংরেজি) ওয়েব অ্যাপ, যা যেকোনো ফোনকে আমের রোগ "
    "ডাক্তারে পরিণত করে। কৃষক আমের ফল বা পাতার একটি ছবি তোলেন। প্রথমে দুই ধাপের আম যাচাই নিশ্চিত করে যে "
    "ছবিটি আমের - তাই ভুল ছবির উপর কখনো পরামর্শ দেওয়া হয় না। এরপর আমাদের নিজস্ব ডিপ লার্নিং মডেল "
    "AA-ENet (EfficientNet-B0, CBAM অ্যাটেনশন ও Transformer এনকোডার; ৩,৫০০টি আম্রপালি ছবিতে প্রশিক্ষিত) "
    "বলে দেয় আমটি সুস্থ নাকি ছয়টি রোগের কোনটিতে আক্রান্ত। Grad-CAM দেখায় মডেল কোথায় দেখেছে, আর সম্ভাব্য "
    "আক্রান্ত অংশ লাল দাগে চিহ্নিত হয় - ফলে কৃষক নিজের চোখে সমস্যাটি দেখতে পান। এরপর অ্যাপ সহজ ভাষায় "
    "পরামর্শ দেয়: এখন কী করবেন, কোন লক্ষণ দেখবেন, রোগ কীভাবে বাগানে ছড়ায় এবং কীভাবে প্রতিরোধ করবেন। "
    "বাংলা বা ইংরেজিতে এক পাতার পিডিএফ রিপোর্ট কৃষি কর্মকর্তাকে দেখানো বা রেকর্ড হিসেবে রাখা যায়। একই "
    "ইঞ্জিন ওপেন পাইথন লাইব্রেরি (PyPI-তে mango-disease-ai) ও REST API হিসেবে প্রকাশিত, তাই অন্য ডেভেলপার, "
    "কৃষি অ্যাপ ও গবেষকেরাও এটি ব্যবহার করতে পারেন। অনুমানের বদলে আগেভাগে সঠিক রোগ নির্ণয় করে আম্রপালিনেট "
    "কৃষককে শুধু অসুস্থ গাছে সঠিক ওষুধ দিতে, কম স্প্রে করতে, কম ফল হারাতে এবং বাগানের চারপাশের মাটি, "
    "পানি ও পরাগায়নকারী পোকা রক্ষা করতে সাহায্য করে।"
)

GOAL = [
    ("Help every Amrapali farmer in Bangladesh find mango disease early, from one phone photo, in their own language.",
     "বাংলাদেশের প্রতিটি আম্রপালি চাষি যেন নিজের ভাষায়, ফোনের একটি ছবি থেকেই আগেভাগে আমের রোগ শনাক্ত করতে পারেন।"),
    ("Replace blanket, just-in-case spraying with targeted treatment of only the sick trees.",
     "ঢালাও, অনুমাননির্ভর স্প্রের বদলে শুধু অসুস্থ গাছে লক্ষ্যভিত্তিক চিকিৎসা নিশ্চিত করা।"),
    ("Cut fruit loss and food waste, and protect soil, water and pollinators around orchards.",
     "ফলের ক্ষতি ও খাদ্য অপচয় কমানো এবং বাগানের চারপাশের মাটি, পানি ও পরাগায়নকারী পোকা রক্ষা করা।"),
    ("Share the AI openly (PyPI library + REST API) so others can build on it.",
     "এআই উন্মুক্তভাবে (PyPI লাইব্রেরি + REST API) দেওয়া, যাতে অন্যরাও এর উপর কাজ করতে পারে।"),
]

ENV_PROBLEMS = [
    ("Chemical overuse", "অতিরিক্ত রাসায়নিক",
     "Blanket spraying puts more fungicide and insecticide into orchards than needed.",
     "ঢালাও স্প্রেতে প্রয়োজনের চেয়ে বেশি ছত্রাকনাশক ও কীটনাশক বাগানে পড়ে।"),
    ("Soil and water pollution", "মাটি ও পানি দূষণ",
     "Residues run off into soil, ponds and canals, harming fish and soil life.",
     "অবশিষ্ট রাসায়নিক মাটি, পুকুর ও খালে মিশে মাছ ও মাটির প্রাণের ক্ষতি করে।"),
    ("Harm to pollinators", "পরাগায়নকারীর ক্ষতি",
     "Spraying during flowering hurts bees that mango flowers need for fruit set.",
     "মুকুলের সময় স্প্রে মৌমাছির ক্ষতি করে, অথচ ফল ধরতে এদের প্রয়োজন।"),
    ("Food waste", "খাদ্য অপচয়",
     "Late detection lets disease spread; rotten fruit wastes the water, land and fertiliser used to grow it.",
     "দেরিতে শনাক্ত হলে রোগ ছড়ায়; পচা ফল মানে পানি, জমি ও সারের অপচয়।"),
    ("Resistant pathogens", "ওষুধ-প্রতিরোধী জীবাণু",
     "Wrong or repeated chemicals help pathogens become resistant, needing even more chemicals.",
     "ভুল বা বারবার একই রাসায়নিক জীবাণুকে প্রতিরোধী করে, ফলে আরও বেশি রাসায়নিক লাগে।"),
    ("Tree dieback", "গাছ মরে যাওয়া",
     "Untreated canker and anthracnose weaken trees; a lost tree is lost green cover and stored carbon.",
     "চিকিৎসা না হলে ক্যাঙ্কার ও অ্যানথ্রাকনোজ গাছ দুর্বল করে; একটি গাছ হারানো মানে সবুজ আচ্ছাদন ও সঞ্চিত কার্বন হারানো।"),
]

SAVE_STEPS = [
    ("Detect early", "আগেভাগে শনাক্ত",
     "A phone photo at the first sign stops disease before it spreads, so fewer sprays are needed over the season.",
     "প্রথম লক্ষণেই ফোনের ছবি দিয়ে শনাক্ত করলে রোগ ছড়ানোর আগেই থামে, ফলে পুরো মৌসুমে কম স্প্রে লাগে।"),
    ("Diagnose correctly", "সঠিক রোগ নির্ণয়",
     "Knowing the exact disease means the right product (fungicide, bactericide or insect control) instead of a chemical mix.",
     "সঠিক রোগ জানলে রাসায়নিকের মিশ্রণের বদলে সঠিক ওষুধ (ছত্রাকনাশক, ব্যাকটেরিয়ানাশক বা পোকা দমন) দেওয়া যায়।"),
    ("Treat only what is sick", "শুধু অসুস্থ অংশের চিকিৎসা",
     "The red outline and the garden spread view show where to act: prune or treat affected trees and branches, not the whole orchard.",
     "লাল দাগ ও বাগানে ছড়ানোর চিত্র দেখায় কোথায় কাজ করতে হবে: পুরো বাগান নয়, শুধু আক্রান্ত গাছ ও ডাল ছাঁটা বা চিকিৎসা।"),
    ("Gentler methods first", "আগে নরম পদ্ধতি",
     "Advice includes pruning, orchard hygiene, neem oil for sap-sucking insects and hot-water treatment after harvest.",
     "পরামর্শে আছে ডাল ছাঁটা, বাগান পরিষ্কার রাখা, রস-চোষা পোকার জন্য নিম তেল এবং ফল তোলার পর গরম পানিতে শোধন।"),
    ("Protect flowering time", "মুকুলের সময় সুরক্ষা",
     "Fewer blanket sprays at flowering let bees and other pollinators work, helping natural fruit set.",
     "মুকুলের সময় ঢালাও স্প্রে কমলে মৌমাছি ও পরাগায়নকারী পোকা কাজ করতে পারে, প্রাকৃতিকভাবে ফল ধরে।"),
    ("Waste less food", "কম খাদ্য অপচয়",
     "Catching rot and anthracnose earlier keeps more fruit fit to eat and sell, saving the resources used to grow it.",
     "পচন ও অ্যানথ্রাকনোজ আগে ধরা পড়লে বেশি ফল খাওয়া ও বিক্রির উপযোগী থাকে, ফলানোর সম্পদও বাঁচে।"),
    ("Let nature recover", "প্রকৃতিকে সেরে উঠতে দেওয়া",
     "Season after season, a lower chemical load gives soil life, pond life and beneficial insects room to recover, and healthy trees keep growing and storing carbon.",
     "মৌসুমের পর মৌসুম রাসায়নিক কম পড়লে মাটির প্রাণ, পুকুরের প্রাণ ও উপকারী পোকা আবার বাড়তে পারে; সুস্থ গাছ বড় হতে থাকে ও কার্বন ধরে রাখে।"),
    ("Build farmer knowledge", "কৃষকের জ্ঞান বাড়ানো",
     "The disease encyclopedia teaches farmers to recognise diseases themselves, so good decisions continue even without the app.",
     "রোগ বিশ্বকোষ কৃষককে নিজে রোগ চিনতে শেখায়, ফলে অ্যাপ ছাড়াও সঠিক সিদ্ধান্ত নেওয়া যায়।"),
]

SDGS = [
    ("SDG 1", "No Poverty / দারিদ্র্য বিলোপ", (229, 36, 59),
     "Lower chemical cost and less fruit loss mean steadier income for farming families.",
     "কম রাসায়নিক খরচ ও কম ফলের ক্ষতি মানে কৃষক পরিবারের স্থির আয়।"),
    ("SDG 2", "Zero Hunger / ক্ষুধামুক্তি", (221, 166, 58),
     "More of the harvest reaches people as food.",
     "বেশি ফল খাবার হিসেবে মানুষের কাছে পৌঁছায়।"),
    ("SDG 12", "Responsible Production / দায়িত্বশীল উৎপাদন", (191, 139, 46),
     "The right treatment at the right time, with less chemical and less food waste.",
     "সঠিক সময়ে সঠিক চিকিৎসা, কম রাসায়নিক ও কম খাদ্য অপচয়।"),
    ("SDG 13", "Climate Action / জলবায়ু কার্যক্রম", (63, 126, 68),
     "Early warnings help farmers adapt as changing weather brings more disease pressure.",
     "আবহাওয়া বদলের সাথে বাড়তে থাকা রোগের ঝুঁকিতে আগাম সতর্কতা দিয়ে কৃষককে খাপ খাওয়াতে সাহায্য করে।"),
    ("SDG 15", "Life on Land / স্থলজ জীবন", (86, 192, 43),
     "Fewer blanket sprays protect soil, bees and orchard biodiversity.",
     "ঢালাও স্প্রে কমলে মাটি, মৌমাছি ও বাগানের জীববৈচিত্র্য রক্ষা পায়।"),
]

FEATURES = [
    ("Phone camera scan", "ফোন ক্যামেরা স্ক্যান", "Take a photo or choose from the gallery; large photos are resized in the browser.", "ছবি তুলুন বা গ্যালারি থেকে নিন; বড় ছবি ব্রাউজারেই ছোট হয়ে যায়।"),
    ("Mango check", "আম যাচাই", "Two-step check rejects photos that are not mangoes and says so clearly.", "দুই ধাপের যাচাই আম ছাড়া অন্য ছবি বাতিল করে এবং পরিষ্কারভাবে জানায়।"),
    ("7-class diagnosis", "৭ শ্রেণির নির্ণয়", "Healthy or one of six diseases, with the confidence for every class.", "সুস্থ অথবা ছয়টি রোগের একটি, প্রতিটি শ্রেণির নিশ্চয়তাসহ।"),
    ("Grad-CAM + affected area", "Grad-CAM + আক্রান্ত অংশ", "Heatmap of where the AI looked and the likely affected area outlined in red, with its share of the photo.", "এআই কোথায় দেখেছে তার হিটম্যাপ এবং লাল দাগে সম্ভাব্য আক্রান্ত অংশ, ছবির কত অংশ তা সহ।"),
    ("Plain-language advice", "সহজ ভাষায় পরামর্শ", "What to do now, signs to check and prevention tips.", "এখন কী করবেন, কোন লক্ষণ দেখবেন ও প্রতিরোধের উপায়।"),
    ("Garden Impact view", "বাগানে প্রভাব", "Animated view of how each disease spreads from one tree to the whole garden.", "প্রতিটি রোগ কীভাবে এক গাছ থেকে পুরো বাগানে ছড়ায় তার অ্যানিমেশন।"),
    ("Disease encyclopedia", "রোগ বিশ্বকোষ", "7 cards with real dataset photos, symptoms, spread, treatment and prevention.", "আসল ছবিসহ ৭টি কার্ড: লক্ষণ, বিস্তার, চিকিৎসা ও প্রতিরোধ।"),
    ("PDF report", "পিডিএফ রিপোর্ট", "One-page report in Bangla or English - the user chooses.", "বাংলা বা ইংরেজিতে এক পাতার রিপোর্ট - ব্যবহারকারী বেছে নেন।"),
    ("Bangla / English, light / dark", "বাংলা / ইংরেজি, লাইট / ডার্ক", "Full bilingual interface, mobile-first, readable in sunlight.", "পুরো দুই ভাষার ইন্টারফেস, মোবাইলবান্ধব, রোদেও পড়া যায়।"),
    ("Open library + REST API", "ওপেন লাইব্রেরি + REST API", "mango-disease-ai on PyPI; the website itself runs on this API.", "PyPI-তে mango-disease-ai; ওয়েবসাইটটিও এই API দিয়েই চলে।"),
]

NOVELTY = [
    ("Built for Amrapali, from Bangladesh", "আম্রপালির জন্য, বাংলাদেশ থেকে",
     "AA-ENet is our own model, trained on our own dataset of 3,500 Amrapali images (500 per class), not a generic plant model.",
     "AA-ENet আমাদের নিজস্ব মডেল, আমাদের নিজস্ব ৩,৫০০টি আম্রপালি ছবির ডেটাসেটে (প্রতি শ্রেণিতে ৫০০) প্রশিক্ষিত - সাধারণ কোনো গাছের মডেল নয়।"),
    ("Explainable, not a black box", "ব্যাখ্যাযোগ্য এআই",
     "Grad-CAM plus a red outline of the likely affected area and its share of the photo - in the app and in the PDF.",
     "Grad-CAM, লাল দাগে সম্ভাব্য আক্রান্ত অংশ ও ছবির কত অংশ - অ্যাপ ও পিডিএফ দুই জায়গাতেই।"),
    ("Safety first", "নিরাপত্তা আগে",
     "A two-step mango check stops wrong advice on photos that are not mangoes.",
     "দুই ধাপের আম যাচাই আম ছাড়া অন্য ছবিতে ভুল পরামর্শ আটকায়।"),
    ("Farmer-first Bangla", "কৃষকবান্ধব বাংলা",
     "The full interface and the PDF report are in correctly rendered Bangla, in plain words.",
     "পুরো ইন্টারফেস ও পিডিএফ রিপোর্ট সঠিকভাবে লেখা, সহজ বাংলায়।"),
    ("From one leaf to the whole garden", "এক পাতা থেকে পুরো বাগান",
     "Each result is linked to how the disease spreads in the orchard and to its environmental cost.",
     "প্রতিটি ফলাফল বাগানে রোগ ছড়ানো ও তার পরিবেশগত ক্ষতির সাথে যুক্ত।"),
    ("Open and reusable", "উন্মুক্ত ও পুনর্ব্যবহারযোগ্য",
     "The same engine is a PyPI library and REST API, so the idea can grow beyond one app.",
     "একই ইঞ্জিন PyPI লাইব্রেরি ও REST API, তাই ধারণাটি একটি অ্যাপের বাইরেও বাড়তে পারে।"),
    ("Lightweight", "হালকা ও দ্রুত",
     "About 5.8 million parameters; runs on an ordinary laptop CPU in a few seconds per photo.",
     "প্রায় ৫৮ লাখ প্যারামিটার; সাধারণ ল্যাপটপের CPU-তে প্রতি ছবিতে কয়েক সেকেন্ডে চলে।"),
]

USER_STEPS = [
    ("Open the website and choose বাংলা or English (top right).", "ওয়েবসাইট খুলুন এবং উপরে ডানে বাংলা বা English বেছে নিন।"),
    ("Tap \"Scan with camera\" (or \"Upload a photo\") and photograph one mango fruit or leaf in daylight.", "\"ক্যামেরা দিয়ে স্ক্যান\" (বা \"ছবি আপলোড\") চাপুন এবং দিনের আলোয় একটি আম বা পাতার ছবি তুলুন।"),
    ("Tap \"Check my mango\" and wait a few seconds.", "\"আম পরীক্ষা করুন\" চাপুন এবং কয়েক সেকেন্ড অপেক্ষা করুন।"),
    ("If it is not a mango, the app says so - take a clearer photo.", "ছবিটি আম না হলে অ্যাপ তা জানায় - আরও পরিষ্কার ছবি তুলুন।"),
    ("Read the result: disease name, how sure the AI is, and the garden risk.", "ফলাফল পড়ুন: রোগের নাম, এআই কতটা নিশ্চিত এবং বাগানের ঝুঁকি।"),
    ("Look at the heatmap and the red outline to see the affected area.", "হিটম্যাপ ও লাল দাগ দেখে আক্রান্ত অংশ বুঝুন।"),
    ("Follow \"What to do now\" and check the listed signs on your trees.", "\"এখন কী করবেন\" অনুসরণ করুন এবং গাছে তালিকার লক্ষণগুলো মিলিয়ে দেখুন।"),
    ("Open \"See how it spreads in the garden\" to plan which trees to check.", "\"বাগানে কিভাবে ছড়ায় দেখুন\" খুলে কোন গাছগুলো দেখবেন তা ঠিক করুন।"),
    ("Write your name and download the PDF in Bangla or English to show an agriculture officer.", "নাম লিখে বাংলা বা ইংরেজি পিডিএফ ডাউনলোড করুন এবং কৃষি কর্মকর্তাকে দেখান।"),
]

PIPELINE = [
    ("Photo", "ছবি", "Camera or gallery; resized in the browser to stay fast and under 10 MB.", "ক্যামেরা বা গ্যালারি; দ্রুত ও ১০ MB এর নিচে রাখতে ব্রাউজারেই ছোট করা হয়।"),
    ("Mango check", "আম যাচাই", "CLIP zero-shot with 18 labels, plus a second check with AA-ENet confidence.", "১৮টি লেবেলসহ CLIP জিরো-শট এবং AA-ENet এর নিশ্চয়তা দিয়ে দ্বিতীয় যাচাই।"),
    ("Diagnosis", "রোগ নির্ণয়", "AA-ENet: EfficientNet-B0 + CBAM attention + Transformer encoder, 224 x 224 input, 7 classes.", "AA-ENet: EfficientNet-B0 + CBAM অ্যাটেনশন + Transformer এনকোডার, ২২৪ x ২২৪ ইনপুট, ৭টি শ্রেণি।"),
    ("Explanation", "ব্যাখ্যা", "Grad-CAM++ on the CBAM layer; areas above 55% are outlined as the likely affected area.", "CBAM স্তরে Grad-CAM++; ৫৫% এর বেশি অংশ সম্ভাব্য আক্রান্ত অংশ হিসেবে চিহ্নিত হয়।"),
    ("Advice + report", "পরামর্শ ও রিপোর্ট", "Bilingual advice from the disease database; one-page PDF in Bangla or English.", "রোগ তথ্যভান্ডার থেকে দুই ভাষায় পরামর্শ; বাংলা বা ইংরেজিতে এক পাতার পিডিএফ।"),
]

ENDPOINTS = [
    ("GET", "/api/health", "Server and model status"),
    ("GET", "/api/diseases", "Information for all 7 classes"),
    ("POST", "/api/analyze", "image -> diagnosis JSON, heatmap, marked area"),
    ("POST", "/api/report", "image, user_name, lang=en|bn -> PDF"),
]

LIMITS = [
    ("The AI can be wrong. AmropaliNet gives guidance; for large outbreaks, farmers should talk to an agriculture officer or agronomist.",
     "এআই ভুল করতে পারে। আম্রপালিনেট পরামর্শ দেয়; বড় আক্রমণে কৃষি কর্মকর্তা বা কৃষিবিদের সাথে কথা বলা উচিত।"),
    ("The red outline is an AI estimate of the affected area, not a measurement.",
     "লাল দাগ আক্রান্ত অংশের একটি এআই অনুমান, মাপা নয়।"),
    ("The model knows 7 classes of Amrapali fruit photos; other varieties or diseases may give uncertain results.",
     "মডেলটি আম্রপালি ফলের ৭টি শ্রেণি চেনে; অন্য জাত বা রোগে ফলাফল অনিশ্চিত হতে পারে।"),
    ("The first scan needs internet once to download the mango checker (about 600 MB).",
     "প্রথম স্ক্যানে আম যাচাইকারী (প্রায় ৬০০ MB) নামাতে একবার ইন্টারনেট লাগে।"),
]

FUTURE = [
    ("Offline Android app for areas with weak internet.", "দুর্বল ইন্টারনেটের এলাকার জন্য অফলাইন অ্যান্ড্রয়েড অ্যাপ।"),
    ("Weather-based early warnings for disease-friendly days.", "রোগবান্ধব আবহাওয়ার দিনে আগাম সতর্কবার্তা।"),
    ("A dashboard for agriculture officers to see outbreaks by area.", "এলাকাভিত্তিক রোগ প্রাদুর্ভাব দেখতে কৃষি কর্মকর্তাদের ড্যাশবোর্ড।"),
    ("More mango varieties and leaf diseases; Bangla voice guidance.", "আরও আমের জাত ও পাতার রোগ; বাংলা ভয়েস নির্দেশনা।"),
]

STACK = [
    ("Programming languages / প্রোগ্রামিং ভাষা", [
        ("Python 3.10+", "AI model, image analysis, REST API server, PDF reports, documentation builder",
         "এআই মডেল, ছবি বিশ্লেষণ, REST API সার্ভার, পিডিএফ রিপোর্ট, ডকুমেন্টেশন তৈরি", "mango_disease_ai/*.py, api/main.py, run.py"),
        ("JavaScript", "Website logic: camera and upload, language and theme switch, results, animations, PDF download",
         "ওয়েবসাইটের কাজ: ক্যামেরা ও আপলোড, ভাষা ও থিম বদল, ফলাফল, অ্যানিমেশন, পিডিএফ ডাউনলোড", "static/js/main.js, i18n.js, diseases.js"),
        ("HTML5", "Structure of the web page and all sections", "ওয়েব পেজ ও সব অংশের কাঠামো", "templates/index.html"),
        ("CSS3", "Design, colours, light and dark mode, animations, mobile layout", "ডিজাইন, রং, লাইট ও ডার্ক মোড, অ্যানিমেশন, মোবাইল লেআউট", "static/css/style.css"),
        ("SVG", "Hero illustration (tree, farmer, mangoes), garden map, icons", "হিরো ছবি (গাছ, কৃষক, আম), বাগানের মানচিত্র, আইকন", "templates/index.html, main.js"),
        ("JSON", "Bangla disease text for the PDF, API responses", "পিডিএফের জন্য বাংলা রোগের তথ্য, API উত্তর", "mango_disease_ai/disease_info_bn.json"),
    ]),
    ("AI and machine learning / এআই ও মেশিন লার্নিং", [
        ("PyTorch 2.5", "Runs the AI model on a normal CPU (no GPU needed)", "সাধারণ CPU-তে এআই মডেল চালায় (GPU লাগে না)", "mango_disease_ai/model.py, inference.py"),
        ("AA-ENet (our model)", "EfficientNet-B0 + CBAM attention + Transformer encoder; 7 classes; ~5.8M parameters",
         "EfficientNet-B0 + CBAM অ্যাটেনশন + Transformer এনকোডার; ৭টি শ্রেণি; প্রায় ৫৮ লাখ প্যারামিটার", "mango_disease_ai/model.py, AA-ENet_proposed.pt"),
        ("timm", "Provides the EfficientNet-B0 backbone", "EfficientNet-B0 মূল কাঠামো দেয়", "mango_disease_ai/model.py"),
        ("CLIP (Hugging Face transformers)", "Zero-shot mango check with 18 labels", "১৮টি লেবেল দিয়ে আম যাচাই", "mango_disease_ai/inference.py"),
        ("Grad-CAM++ (own code)", "Heatmap and red outline of the likely affected area", "হিটম্যাপ ও সম্ভাব্য আক্রান্ত অংশের লাল দাগ", "mango_disease_ai/inference.py"),
        ("OpenCV, SciPy, NumPy, Pillow", "Resize photos, colour the heatmap, find and draw outlines", "ছবি ছোট করা, হিটম্যাপে রং, দাগ খোঁজা ও আঁকা", "mango_disease_ai/inference.py, core.py"),
    ]),
    ("Backend server / ব্যাকএন্ড সার্ভার", [
        ("FastAPI", "REST API: /api/analyze, /api/report, /api/health, /api/diseases + /docs page",
         "REST API: /api/analyze, /api/report, /api/health, /api/diseases + /docs পেজ", "mango_disease_ai/server.py, api/main.py"),
        ("Uvicorn", "Web server that runs the API and the website", "API ও ওয়েবসাইট চালানোর ওয়েব সার্ভার", "run.py, mango-api command"),
        ("Pydantic", "Checks API input and output", "API এর ইনপুট ও আউটপুট যাচাই", "mango_disease_ai/server.py"),
        ("python-multipart", "Receives uploaded photos", "আপলোড করা ছবি গ্রহণ", "mango_disease_ai/server.py"),
    ]),
    ("PDF and fonts / পিডিএফ ও ফন্ট", [
        ("fpdf2", "Creates the diagnosis report and this documentation", "রোগ নির্ণয় রিপোর্ট ও এই ডকুমেন্টেশন তৈরি", "mango_disease_ai/report_engine.py, docs/build_documentation.py"),
        ("uharfbuzz (HarfBuzz)", "Joins Bangla letters correctly in PDFs", "পিডিএফে বাংলা যুক্তাক্ষর সঠিকভাবে জোড়া লাগায়", "mango_disease_ai/report_engine.py"),
        ("Hind Siliguri font (OFL)", "Bangla text on the website and in PDFs", "ওয়েবসাইট ও পিডিএফে বাংলা লেখা", "mango_disease_ai/fonts/, Google Fonts"),
        ("Poppins font", "English text on the website", "ওয়েবসাইটে ইংরেজি লেখা", "templates/index.html (Google Fonts)"),
    ]),
    ("Frontend features / ফ্রন্টএন্ড", [
        ("No framework (vanilla JS)", "No React and no build step - loads fast on low-cost phones", "React বা বিল্ড ধাপ নেই - কম দামের ফোনেও দ্রুত চলে", "static/js/main.js"),
        ("Own i18n (Bangla / English)", "Instant language switch, no translation service; browser auto-translate disabled",
         "তাৎক্ষণিক ভাষা বদল, অনুবাদ সেবা ছাড়া; ব্রাউজারের স্বয়ংক্রিয় অনুবাদ বন্ধ", "static/js/i18n.js"),
        ("HTML camera capture + Canvas", "Opens the phone camera; resizes big photos before upload", "ফোনের ক্যামেরা খোলে; আপলোডের আগে বড় ছবি ছোট করে", "templates/index.html, main.js"),
        ("localStorage", "Remembers language and light/dark choice", "ভাষা ও লাইট/ডার্ক পছন্দ মনে রাখে", "static/js/main.js"),
    ]),
    ("Packaging and deployment / প্যাকেজিং ও ডিপ্লয়মেন্ট", [
        ("PyPI", "Publishes the library mango-disease-ai for developers", "ডেভেলপারদের জন্য mango-disease-ai লাইব্রেরি প্রকাশ", "pyproject.toml, README_PACKAGE.md"),
        ("setuptools, build, twine", "Build and upload the library", "লাইব্রেরি তৈরি ও আপলোড", "pyproject.toml, PUBLISH_GUIDE.md"),
        ("Docker (python:3.10-slim)", "Container for hosting, e.g. Hugging Face Spaces", "হোস্টিংয়ের জন্য কন্টেইনার, যেমন Hugging Face Spaces", "Dockerfile"),
        ("Git + GitHub", "Version control and sharing", "ভার্সন নিয়ন্ত্রণ ও শেয়ার", "github.com/Arpon-30/UI-Changes-Mango"),
    ]),
    ("Development and testing / ডেভেলপমেন্ট ও টেস্টিং", [
        ("VS Code + Anaconda", "Editor and Python environment (tf_new, Python 3.10)", "এডিটর ও পাইথন পরিবেশ (tf_new, Python 3.10)", "run.py, .vscode"),
        ("Jupyter Notebook", "Model training and research", "মডেল প্রশিক্ষণ ও গবেষণা", "last-try-mango.ipynb"),
        ("Playwright (Chromium)", "Automatic browser tests on phone and desktop sizes, both languages", "ফোন ও ডেস্কটপ আকারে, দুই ভাষায় স্বয়ংক্রিয় ব্রাউজার টেস্ট", "test scripts (development)"),
    ]),
]

FILE_MAP = [
    ("run.py", "One-click start: installs small missing packages, opens the website", "এক ক্লিকে চালু: ছোট অনুপস্থিত প্যাকেজ ইনস্টল করে, ওয়েবসাইট খোলে"),
    ("api/main.py", "Website server = library API + web pages", "ওয়েবসাইট সার্ভার = লাইব্রেরির API + ওয়েব পেজ"),
    ("mango_disease_ai/server.py", "The REST API (also the mango-api command)", "REST API (mango-api কমান্ডও এটি)"),
    ("mango_disease_ai/core.py", "analyze(): mango check -> diagnosis -> Grad-CAM", "analyze(): আম যাচাই -> রোগ নির্ণয় -> Grad-CAM"),
    ("mango_disease_ai/model.py", "AA-ENet architecture, model loading, disease data", "AA-ENet কাঠামো, মডেল লোড, রোগের তথ্য"),
    ("mango_disease_ai/inference.py", "CLIP mango check, classification, heatmap, affected area", "CLIP আম যাচাই, শ্রেণিবিন্যাস, হিটম্যাপ, আক্রান্ত অংশ"),
    ("mango_disease_ai/report_engine.py", "PDF report in English or Bangla", "ইংরেজি বা বাংলা পিডিএফ রিপোর্ট"),
    ("mango_disease_ai/AA-ENet_proposed.pt", "Trained model weights (18 MB)", "প্রশিক্ষিত মডেলের ওজন (১৮ MB)"),
    ("templates/index.html", "The web page", "ওয়েব পেজ"),
    ("static/css/style.css", "Design and animations", "ডিজাইন ও অ্যানিমেশন"),
    ("static/js/main.js", "Website logic", "ওয়েবসাইটের কাজ"),
    ("static/js/i18n.js, diseases.js", "All Bangla / English text and disease data", "সব বাংলা / ইংরেজি লেখা ও রোগের তথ্য"),
    ("static/img/", "Real dataset photos and real model outputs", "আসল ডেটাসেটের ছবি ও মডেলের আসল আউটপুট"),
    ("docs/", "This documentation and its builder", "এই ডকুমেন্টেশন ও তা তৈরির স্ক্রিপ্ট"),
]

ARCH = [
    ("Phone browser", "HTML + CSS + JavaScript"),
    ("REST API", "FastAPI + Uvicorn"),
    ("Mango check", "CLIP"),
    ("Diagnosis", "AA-ENet (PyTorch)"),
    ("Explanation", "Grad-CAM++ + OpenCV"),
    ("Report", "fpdf2 + HarfBuzz"),
]

PY_CODE = """pip install mango-disease-ai

from mango_disease_ai import analyze, generate_pdf

result = analyze("mango.jpg")
if result["is_mango"]:
    print(result["predicted_class"], result["confidence"])
    print(result["affected_percent"], "% of the photo affected")
    pdf = generate_pdf(result, user_name="Arpon", lang="bn")
    open("report.pdf", "wb").write(pdf)
else:
    print("Not a mango photo")"""

API_CODE = """pip install "mango-disease-ai[api]"
mango-api                      # http://localhost:8000/docs

curl -F "image=@mango.jpg" http://localhost:8000/api/analyze
curl -F "image=@mango.jpg" -F "user_name=Arpon" -F "lang=bn" \\
     http://localhost:8000/api/report -o report.pdf"""

JS_CODE = """const form = new FormData();
form.append("image", fileInput.files[0]);
const res = await fetch("http://localhost:8000/api/analyze", { method: "POST", body: form });
const data = await res.json();
if (res.ok) console.log(data.predicted_class, data.confidence);
else console.log(data.detail.code);   // e.g. "not_mango" """

RUN_CODE = """python -m pip install -r api/requirements.txt   # first time
python run.py                                     # opens http://localhost:8000"""


# ─────────────────────────────────────────────────────────────────────────────
# Layout helpers
# ─────────────────────────────────────────────────────────────────────────────
class Doc(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.add_font("Hind", "", str(FONTS / "HindSiliguri-Regular.ttf"))
        self.add_font("Hind", "B", str(FONTS / "HindSiliguri-Bold.ttf"))
        self.set_text_shaping(True)
        self.set_margins(M, M, M)
        self.set_auto_page_break(False)
        self.section_no = 0
        self.y_pos = M

    # text
    def f(self, size=10, bold=False):
        self.set_font("Hind", "B" if bold else "", size)

    def wrap(self, text, width):
        lines = []
        for para in str(text).split("\n"):
            cur = ""
            for word in para.split():
                cand = f"{cur} {word}".strip()
                if not cur or self.get_string_width(cand) <= width:
                    cur = cand
                else:
                    lines.append(cur)
                    cur = word
            lines.append(cur)
        return lines

    def wrap_path(self, text, width):
        """Like wrap(), but long paths/URLs without spaces are split after '/' (current font)."""
        pieces = []
        for token in str(text).split():
            if self.get_string_width(token) <= width:
                pieces.append(token)
                continue
            part = ""
            for chunk in token.replace("/", "/\u0000").split("\u0000"):
                if part and self.get_string_width(part + chunk) > width:
                    pieces.append(part)
                    part = chunk
                else:
                    part += chunk
            if part:
                pieces.append(part)
        lines, cur = [], ""
        for piece in pieces:
            cand = f"{cur} {piece}".strip()
            if not cur or self.get_string_width(cand) <= width:
                cur = cand
            else:
                lines.append(cur)
                cur = piece
        if cur:
            lines.append(cur)
        return lines

    def need(self, h):
        if self.y_pos + h > BOTTOM:
            self.add_page()

    def text_block(self, text, size=10, bold=False, color=INK, x=M, w=W, lh=None, gap=2.2):
        self.f(size, bold)
        lh = lh or size * 0.52
        lines = self.wrap(text, w)
        self.set_text_color(*color)
        for line in lines:
            self.need(lh)
            self.set_xy(x, self.y_pos)
            self.cell(w, lh, line)
            self.y_pos += lh
        self.y_pos += gap

    # page furniture
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*GREEN_DARK)
        self.rect(0, 0, PAGE_W, 9, style="F")
        self.set_fill_color(*MANGO)
        self.rect(0, 9, PAGE_W, 0.8, style="F")
        self.f(8, True)
        self.set_text_color(255, 255, 255)
        self.set_xy(M, 2.2)
        self.cell(100, 5, "AmropaliNet - Project Documentation / প্রকল্প ডকুমেন্টেশন")
        self.y_pos = 18

    def footer(self):
        if self.page_no() == 1:
            return
        self.f(8)
        self.set_text_color(*MUTED)
        self.set_xy(M, PAGE_H - 12)
        self.cell(W / 2, 5, "AIUB Student Group - arponamit.55@gmail.com")
        self.set_xy(M + W / 2, PAGE_H - 12)
        self.cell(W / 2, 5, f"{self.page_no()}", align="R")

    # building blocks
    def section(self, en, bn):
        self.section_no += 1
        self.need(62)   # keep the heading with its first lines or card
        y = self.y_pos + 2
        self.set_fill_color(*GREEN)
        self.rect(M, y, 11, 11, style="F", round_corners=True, corner_radius=2)
        self.f(12, True)
        self.set_text_color(255, 255, 255)
        self.set_xy(M, y + 1.5)
        self.cell(11, 8, str(self.section_no), align="C")
        self.set_text_color(*GREEN_DARK)
        self.f(15, True)
        self.set_xy(M + 15, y - 0.5)
        self.cell(W - 15, 7.5, en)
        self.set_text_color(*MANGO)
        self.f(12, True)
        self.set_xy(M + 15, y + 6.5)
        self.cell(W - 15, 6.5, bn)
        self.set_draw_color(*BORDER)
        self.line(M, y + 15, M + W, y + 15)
        self.y_pos = y + 19

    def sub(self, text, color=GREEN_DARK, size=11.5):
        self.need(24)   # keep the sub-heading with its first item
        self.text_block(text, size=size, bold=True, color=color, gap=1)

    def tag(self, label, color):
        self.need(8)
        self.f(7.5, True)
        wlab = self.get_string_width(label) + 5
        self.set_fill_color(*color)
        self.rect(M, self.y_pos, wlab, 5, style="F", round_corners=True, corner_radius=2.5)
        self.set_text_color(255, 255, 255)
        self.set_xy(M, self.y_pos)
        self.cell(wlab, 5, label, align="C")
        self.y_pos += 6.5

    def bilingual(self, en, bn, size=10):
        self.tag("ENGLISH", GREEN)
        self.text_block(en, size=size)
        self.tag("বাংলা", MANGO)
        self.text_block(bn, size=size + 0.3, gap=4)

    def card_pairs(self, items, numbered=False):
        """items: (title_en, title_bn, text_en, text_bn) drawn as cards."""
        for i, (ten, tbn, den, dbn) in enumerate(items, 1):
            self.f(9.5)
            h = 9 + len(self.wrap(den, W - 14)) * 4.9 + len(self.wrap(dbn, W - 14)) * 5.1 + 4
            self.need(h + 3)
            y = self.y_pos
            self.set_fill_color(*TINT)
            self.set_draw_color(*BORDER)
            self.rect(M, y, W, h, style="DF", round_corners=True, corner_radius=2.5)
            self.set_fill_color(*MANGO)
            self.rect(M, y, 2.2, h, style="F")
            self.y_pos = y + 2.5
            title = f"{i}. {ten}  /  {tbn}" if numbered else f"{ten}  /  {tbn}"
            self.text_block(title, size=10.5, bold=True, color=GREEN_DARK, x=M + 7, w=W - 14, gap=0.8)
            self.text_block(den, size=9.5, color=INK, x=M + 7, w=W - 14, gap=0.5)
            self.text_block(dbn, size=9.8, color=SOFT, x=M + 7, w=W - 14, gap=0)
            self.y_pos = y + h + 3

    def bullets(self, pairs, numbered=False):
        for i, (en, bn) in enumerate(pairs, 1):
            self.f(10)
            h = len(self.wrap(en, W - 9)) * 5.2 + len(self.wrap(bn, W - 9)) * 5.4 + 3
            self.need(h)
            y = self.y_pos
            self.f(10, True)
            self.set_text_color(*(GREEN if numbered else MANGO))
            self.set_xy(M, y)
            self.cell(8, 5.2, f"{i}." if numbered else "-")
            self.text_block(en, size=10, x=M + 8, w=W - 9, gap=0)
            self.text_block(bn, size=10.2, color=SOFT, x=M + 8, w=W - 9, gap=2.5)

    def stack_table(self, title, rows):
        """rows: (technology, what_en, what_bn, where). Three columns."""
        c1, c3 = 40, 50
        c2 = W - c1 - c3
        self.sub(title, size=11)
        # header
        self.need(8)
        y = self.y_pos
        self.set_fill_color(*GREEN_DARK)
        self.rect(M, y, W, 6.5, style="F")
        self.f(8.5, True)
        self.set_text_color(255, 255, 255)
        for x, w, label in ((M, c1, "Technology / প্রযুক্তি"), (M + c1, c2, "What it does / কী কাজ করে"),
                            (M + c1 + c2, c3, "Where used / কোথায়")):
            self.set_xy(x + 2, y + 0.4)
            self.cell(w - 4, 5.6, label)
        self.y_pos = y + 6.5
        for i, (tech, en, bn, where) in enumerate(rows):
            self.f(9)
            n1 = len(self.wrap(tech, c1 - 4))
            n2 = len(self.wrap(en, c2 - 4)) + len(self.wrap(bn, c2 - 4))
            self.set_font("Courier", "", 7.6)
            n3 = len(self.wrap_path(where, c3 - 4))
            h = max(n1 * 4.6, n2 * 4.5, n3 * 3.9) + 3
            if self.y_pos + h > BOTTOM:
                self.add_page()
            y = self.y_pos
            self.set_fill_color(*(TINT if i % 2 == 0 else (255, 255, 255)))
            self.set_draw_color(*BORDER)
            self.rect(M, y, W, h, style="DF")
            self.y_pos = y + 1.5
            self.text_block(tech, size=9, bold=True, color=GREEN_DARK, x=M + 2, w=c1 - 4, gap=0)
            self.y_pos = y + 1.5
            self.text_block(en, size=8.6, color=INK, x=M + c1 + 2, w=c2 - 4, gap=0)
            self.text_block(bn, size=8.8, color=SOFT, x=M + c1 + 2, w=c2 - 4, gap=0)
            self.set_font("Courier", "", 7.6)
            self.set_text_color(*SOFT)
            yy = y + 1.5
            for line in self.wrap_path(where, c3 - 4):
                self.set_xy(M + c1 + c2 + 2, yy)
                self.cell(c3 - 4, 3.9, line)
                yy += 3.9
            self.y_pos = y + h
        self.y_pos += 5

    def arch_flow(self, steps):
        n = len(steps)
        gap = 3.5
        bw = (W - gap * (n - 1)) / n
        self.need(26)
        y = self.y_pos
        for i, (name, tech) in enumerate(steps):
            x = M + i * (bw + gap)
            self.set_fill_color(*(GREEN if i % 2 == 0 else MANGO))
            self.rect(x, y, bw, 20, style="F", round_corners=True, corner_radius=2.5)
            self.f(8.8, True)
            self.set_text_color(255, 255, 255)
            self.set_xy(x, y + 2.5)
            self.cell(bw, 5, name, align="C")
            self.f(7.4)
            lines = self.wrap(tech, bw - 3)
            yy = y + 8.5
            for line in lines:
                self.set_xy(x, yy)
                self.cell(bw, 4, line, align="C")
                yy += 4
            if i < n - 1:
                self.set_draw_color(*INK)
                self.set_line_width(0.5)
                self.line(x + bw + 0.4, y + 10, x + bw + gap - 0.6, y + 10)
                self.set_line_width(0.2)
        self.y_pos = y + 26

    def code(self, text, title):
        lines = text.split("\n")
        h = 9 + len(lines) * 4.6 + 4
        self.need(h + 3)
        y = self.y_pos
        self.set_fill_color(*CODE_BG)
        self.rect(M, y, W, h, style="F", round_corners=True, corner_radius=2.5)
        self.f(8.5, True)
        self.set_text_color(255, 213, 79)
        self.set_xy(M + 5, y + 2)
        self.cell(W - 10, 5, title)
        self.set_font("Courier", "", 8.6)
        self.set_text_color(232, 245, 224)
        yy = y + 8.5
        for line in lines:
            self.set_xy(M + 5, yy)
            self.cell(W - 10, 4.6, line)
            yy += 4.6
        self.y_pos = y + h + 4


def word_count(text):
    return len(text.split())


# ─────────────────────────────────────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────────────────────────────────────
def build() -> Path:
    for name, text in (("PROBLEM_EN", PROBLEM_EN), ("PROBLEM_BN", PROBLEM_BN),
                       ("SOLUTION_EN", SOLUTION_EN), ("SOLUTION_BN", SOLUTION_BN)):
        assert word_count(text) <= 300, f"{name} has {word_count(text)} words (limit 300)"

    d = Doc()

    # ── Cover ────────────────────────────────────────────────────────────
    d.add_page()
    d.set_fill_color(*GREEN_DARK)
    d.rect(0, 0, PAGE_W, 128, style="F")
    d.set_fill_color(*MANGO)
    d.rect(0, 128, PAGE_W, 2.5, style="F")
    d.set_text_color(255, 213, 79)
    d.f(11, True)
    d.set_xy(M, 26)
    d.cell(W, 6, "PROJECT DOCUMENTATION  /  প্রকল্প ডকুমেন্টেশন")
    d.set_text_color(255, 255, 255)
    d.set_font("Hind", "B", 38)
    d.set_xy(M, 40)
    d.cell(W, 16, "AmropaliNet")
    d.f(17, True)
    d.set_xy(M, 60)
    d.cell(W, 9, "AI mango doctor for the farmers of Bangladesh")
    d.set_xy(M, 70)
    d.cell(W, 9, "বাংলাদেশের কৃষকদের জন্য এআই আম ডাক্তার")
    d.set_text_color(220, 240, 210)
    d.f(11)
    d.y_pos = 86
    d.text_block("One photo of an Amrapali mango - the disease, the affected area and what to do, in Bangla or English. "
                 "Detect early, spray less, waste less.", size=11, color=(220, 240, 210))
    d.text_block("আম্রপালি আমের একটি ছবি - রোগ, আক্রান্ত অংশ ও করণীয়, বাংলা বা ইংরেজিতে। "
                 "আগে শনাক্ত করুন, কম স্প্রে করুন, কম নষ্ট করুন।", size=11.3, color=(220, 240, 210))

    d.y_pos = 142
    facts = [
        ("Model / মডেল", "AA-ENet (EfficientNet-B0 + CBAM + Transformer), ~5.8M parameters"),
        ("Dataset / ডেটাসেট", "3,500 Amrapali images, 7 classes (500 each)"),
        ("Classes / শ্রেণি", "Anthracnose, Bacterial Canker, Healthy, Powdery Mildew, Scab, Sooty Mould, Stem End Rot"),
        ("Languages / ভাষা", "Bangla + English (website and PDF report)"),
        ("Open source / উন্মুক্ত", "Python library mango-disease-ai on PyPI + REST API"),
        ("Theme / বিষয়", "Environment and agriculture - SDG 1, 2, 12, 13, 15"),
    ]
    for k, v in facts:
        d.f(9.5, True)
        d.set_text_color(*MANGO)
        d.set_xy(M, d.y_pos)
        d.cell(42, 6, k)
        d.text_block(v, size=10, color=INK, x=M + 42, w=W - 42, gap=1.5)

    d.y_pos += 6
    d.set_fill_color(*TINT)
    d.set_draw_color(*BORDER)
    d.rect(M, d.y_pos, W, 47, style="DF", round_corners=True, corner_radius=3)
    y0 = d.y_pos
    d.y_pos += 4
    d.text_block("Team  /  টিম", size=11, bold=True, color=GREEN_DARK, x=M + 6, w=W - 12, gap=0.5)
    d.text_block("AIUB Student Group: Arpon, Oni, Md. Ibtihazzaman", size=10.5, x=M + 6, w=W - 12, gap=0.3)
    d.text_block("Supervised by / তত্ত্বাবধানে: Dr. Md. Saef Ullah Miah", size=10.5, x=M + 6, w=W - 12, gap=0.3)
    d.text_block("Contact / যোগাযোগ: arponamit.55@gmail.com  -  github.com/Arpon-30", size=10.5, x=M + 6, w=W - 12, gap=0.3)
    d.text_block("Library: pypi.org/project/mango-disease-ai", size=10.5, x=M + 6, w=W - 12, gap=0.3)
    d.text_block(f"Date / তারিখ: {date.today().strftime('%d %B %Y')}", size=10.5, color=SOFT, x=M + 6, w=W - 12, gap=0)
    d.y_pos = y0 + 53

    # ── Contents + 1 Goal ────────────────────────────────────────────────
    d.add_page()
    d.text_block("Contents  /  সূচিপত্র", size=13, bold=True, color=GREEN_DARK, gap=2)
    toc = ["Project goal / প্রকল্পের লক্ষ্য", "Problem statement / সমস্যা", "Environmental problems we address / পরিবেশগত সমস্যা",
           "Our solution / আমাদের সমাধান", "How we save and help recover the environment / পরিবেশ রক্ষা ও পুনরুদ্ধার",
           "Is it connected to the environment? / পরিবেশের সাথে সংযোগ", "Features / ফিচার", "Main novelty / মূল নতুনত্ব",
           "For farmers and normal users / সাধারণ ব্যবহারকারী", "For developers / ডেভেলপার", "How it works / কিভাবে কাজ করে",
           "Tech stack and where it is used / প্রযুক্তি ও ব্যবহার", "Limitations and next steps / সীমাবদ্ধতা ও পরবর্তী ধাপ"]
    ytoc = d.y_pos
    bottoms = []
    for col, items in enumerate((toc[:7], toc[7:])):
        d.y_pos = ytoc
        for i, t in enumerate(items, 1 + col * 7):
            d.text_block(f"{i}. {t}", size=9.5, color=INK, x=M + col * (W / 2), w=W / 2 - 4, gap=0.6)
        bottoms.append(d.y_pos)
    d.y_pos = max(bottoms) + 4
    d.section("Project goal", "প্রকল্পের লক্ষ্য")
    d.bilingual(
        "AmropaliNet protects Amrapali mango gardens and the environment around them by giving every farmer an "
        "early, exact and explainable diagnosis from one phone photo - so that treatment is targeted instead of blanket.",
        "আম্রপালিনেটের লক্ষ্য হলো ফোনের একটি ছবি থেকে প্রতিটি কৃষককে আগেভাগে সঠিক ও ব্যাখ্যাযোগ্য রোগ নির্ণয় দেওয়া, "
        "যাতে ঢালাও স্প্রের বদলে লক্ষ্যভিত্তিক চিকিৎসা হয় - এতে আম্রপালি বাগান ও তার চারপাশের পরিবেশ রক্ষা পায়।")
    d.bullets(GOAL, numbered=True)

    # ── 2 Problem ────────────────────────────────────────────────────────
    d.section("Problem statement (within 300 words)", "সমস্যা বিবৃতি (৩০০ শব্দের মধ্যে)")
    d.bilingual(PROBLEM_EN, PROBLEM_BN)

    # ── 3 Environmental problems ─────────────────────────────────────────
    d.section("Which environmental problems we address", "কোন পরিবেশগত সমস্যার সমাধান করি")
    d.bilingual(
        "Mango disease is not only a farm problem. The way it is handled today - late detection and blanket "
        "spraying - turns it into an environmental problem for soil, water, pollinators and food systems.",
        "আমের রোগ শুধু খামারের সমস্যা নয়। এখনকার পদ্ধতি - দেরিতে শনাক্ত ও ঢালাও স্প্রে - একে মাটি, পানি, "
        "পরাগায়নকারী ও খাদ্যব্যবস্থার জন্য পরিবেশগত সমস্যায় পরিণত করে।")
    d.card_pairs(ENV_PROBLEMS)

    # ── 4 Solution ───────────────────────────────────────────────────────
    d.section("Our solution (within 300 words)", "আমাদের সমাধান (৩০০ শব্দের মধ্যে)")
    d.bilingual(SOLUTION_EN, SOLUTION_BN)

    # ── 5 How we save / recover ──────────────────────────────────────────
    d.section("How we save and help recover the environment", "কীভাবে পরিবেশ রক্ষা ও পুনরুদ্ধারে সাহায্য করি")
    d.bilingual(
        "AmropaliNet does not spray or clean anything itself. It changes the decision the farmer makes. Step by step, "
        "better decisions mean fewer chemicals and less waste, and over the seasons this gives nature room to recover.",
        "আম্রপালিনেট নিজে কিছু স্প্রে বা পরিষ্কার করে না - এটি কৃষকের সিদ্ধান্ত বদলে দেয়। ধাপে ধাপে ভালো সিদ্ধান্ত মানে "
        "কম রাসায়নিক ও কম অপচয়, আর মৌসুমের পর মৌসুম তা প্রকৃতিকে সেরে ওঠার সুযোগ দেয়।")
    d.card_pairs(SAVE_STEPS, numbered=True)

    # ── 6 Connection ─────────────────────────────────────────────────────
    d.section("Is this project connected to the environment?", "এই প্রকল্প কি পরিবেশের সাথে যুক্ত?")
    d.bilingual(
        "Yes - directly. The chain is: one photo -> correct, early diagnosis -> targeted treatment of only the sick "
        "trees -> fewer chemicals and less fruit waste -> cleaner soil and water, safer bees and a healthier orchard.",
        "হ্যাঁ - সরাসরি। ধারাটি হলো: একটি ছবি -> আগেভাগে সঠিক রোগ নির্ণয় -> শুধু অসুস্থ গাছে লক্ষ্যভিত্তিক চিকিৎসা -> "
        "কম রাসায়নিক ও কম ফল অপচয় -> পরিষ্কার মাটি ও পানি, নিরাপদ মৌমাছি এবং সুস্থ বাগান।")
    d.sub("UN Sustainable Development Goals  /  জাতিসংঘের টেকসই উন্নয়ন লক্ষ্য")
    for code, name, color, en, bn in SDGS:
        d.f(9.5)
        h = 8 + len(d.wrap(en, W - 30)) * 4.9 + len(d.wrap(bn, W - 30)) * 5.1 + 3
        d.need(h + 2)
        y = d.y_pos
        d.set_fill_color(*color)
        d.rect(M, y, 22, h, style="F", round_corners=True, corner_radius=2.5)
        d.f(10.5, True)
        d.set_text_color(255, 255, 255)
        d.set_xy(M, y + h / 2 - 3)
        d.cell(22, 6, code, align="C")
        d.y_pos = y + 1.5
        d.text_block(name, size=10.5, bold=True, color=GREEN_DARK, x=M + 27, w=W - 30, gap=0.3)
        d.text_block(en, size=9.5, x=M + 27, w=W - 30, gap=0.3)
        d.text_block(bn, size=9.8, color=SOFT, x=M + 27, w=W - 30, gap=0)
        d.y_pos = y + h + 2.5

    # ── 7 Features ───────────────────────────────────────────────────────
    d.section("Features", "ফিচারসমূহ")
    d.card_pairs(FEATURES)

    # ── 8 Novelty ────────────────────────────────────────────────────────
    d.section("Main novelty", "মূল নতুনত্ব")
    d.card_pairs(NOVELTY, numbered=True)

    # ── 9 Normal users ───────────────────────────────────────────────────
    d.section("For farmers and normal users", "কৃষক ও সাধারণ ব্যবহারকারীর জন্য")
    d.bilingual(
        "No account, no training and no English needed. Everything works in the browser of a normal phone.",
        "কোনো অ্যাকাউন্ট, প্রশিক্ষণ বা ইংরেজি জানা লাগে না। সাধারণ ফোনের ব্রাউজারেই সব কাজ করে।")
    d.sub("Step by step  /  ধাপে ধাপে")
    d.bullets(USER_STEPS, numbered=True)

    # ── 10 Developers ────────────────────────────────────────────────────
    d.section("For developers", "ডেভেলপারদের জন্য")
    d.bilingual(
        "The AI is an open Python library, mango-disease-ai, published on PyPI. It includes the trained model, the "
        "PDF engine and a ready-made REST API. The AmropaliNet website itself runs on this same API.",
        "এআইটি একটি ওপেন পাইথন লাইব্রেরি, mango-disease-ai, যা PyPI-তে প্রকাশিত। এতে প্রশিক্ষিত মডেল, পিডিএফ ইঞ্জিন "
        "ও তৈরি REST API আছে। আম্রপালিনেট ওয়েবসাইটও এই একই API দিয়ে চলে।")
    d.code(PY_CODE, "Python  -  analyze a photo and create a Bangla PDF")
    d.code(API_CODE, "REST API  -  start the server and call it")
    d.code(JS_CODE, "JavaScript  -  call the API from a web or mobile app")
    d.sub("Endpoints  /  এন্ডপয়েন্ট")
    for method, path, what in ENDPOINTS:
        d.need(7)
        y = d.y_pos
        d.set_fill_color(*(GREEN if method == "GET" else MANGO))
        d.rect(M, y + 0.5, 13, 5, style="F", round_corners=True, corner_radius=1.5)
        d.f(8, True)
        d.set_text_color(255, 255, 255)
        d.set_xy(M, y + 0.5)
        d.cell(13, 5, method, align="C")
        d.set_font("Courier", "B", 9.5)
        d.set_text_color(*INK)
        d.set_xy(M + 16, y)
        d.cell(40, 6, path)
        d.f(9.5)
        d.set_xy(M + 58, y)
        d.cell(W - 58, 6, what)
        d.y_pos = y + 7
    d.y_pos += 2
    d.text_block("Errors return {\"detail\": {\"code\": ..., \"message\": ...}} - for example not_mango (422), "
                 "model_missing (503), bad_image (400). Full interactive docs: /docs.", size=9.5, color=SOFT)
    d.code(RUN_CODE, "Run the whole website locally")

    # ── 11 How it works ──────────────────────────────────────────────────
    d.section("How it works", "কিভাবে কাজ করে")
    d.card_pairs(PIPELINE, numbered=True)

    # ── 12 Tech stack ─────────────────────────────────────────────────────
    d.section("Tech stack and where it is used", "প্রযুক্তি ও কোথায় ব্যবহার হয়েছে")
    d.bilingual(
        "Every technology in AmropaliNet, what it does and the exact file where it is used. The whole system is "
        "open source and runs on an ordinary laptop - no GPU and no paid cloud service are needed.",
        "আম্রপালিনেটের প্রতিটি প্রযুক্তি, তার কাজ এবং ঠিক কোন ফাইলে ব্যবহার হয়েছে। পুরো সিস্টেম ওপেন সোর্স এবং সাধারণ "
        "ল্যাপটপেই চলে - GPU বা পেইড ক্লাউড সেবা লাগে না।")
    d.sub("Architecture  /  গঠন")
    d.arch_flow(ARCH)
    for title, rows in STACK:
        d.stack_table(title, rows)
    d.sub("Project folder map  /  প্রকল্পের ফোল্ডার মানচিত্র")
    for path, en, bn in FILE_MAP:
        d.f(9)
        h = max(len(d.wrap(en, W - 76)) * 4.5 + len(d.wrap(bn, W - 76)) * 4.6, 5) + 2.5
        d.need(h)
        y = d.y_pos
        d.set_font("Courier", "B", 8.2)
        d.set_text_color(*GREEN_DARK)
        yy = y
        for line in d.wrap_path(path, 70):
            d.set_xy(M, yy)
            d.cell(72, 4.5, line)
            yy += 4.5
        d.y_pos = y
        d.text_block(en, size=9, x=M + 74, w=W - 76, gap=0)
        d.text_block(bn, size=9.2, color=SOFT, x=M + 74, w=W - 76, gap=0)
        d.set_draw_color(*BORDER)
        d.line(M, y + h - 1, M + W, y + h - 1)
        d.y_pos = y + h
    d.y_pos += 3
    d.sub("One line for slides  /  স্লাইডের জন্য এক লাইনে", size=10.5)
    d.text_block("Python · PyTorch · AA-ENet (EfficientNet-B0 + CBAM + Transformer) · CLIP · Grad-CAM++ · FastAPI · "
                 "HTML / CSS / JavaScript · fpdf2 + HarfBuzz (Bangla PDF) · PyPI library · Docker",
                 size=10, bold=True, color=INK, gap=4)

    # ── 13 Limits + future ───────────────────────────────────────────────
    d.section("Limitations and next steps", "সীমাবদ্ধতা ও পরবর্তী ধাপ")
    d.sub("Honest limitations  /  সীমাবদ্ধতা")
    d.bullets(LIMITS)
    d.sub("Next steps  /  পরবর্তী ধাপ")
    d.bullets(FUTURE)

    d.need(30)
    y = d.y_pos + 2
    d.set_fill_color(*MANGO_TINT)
    d.set_draw_color(*MANGO)
    d.rect(M, y, W, 24, style="DF", round_corners=True, corner_radius=3)
    d.y_pos = y + 4
    d.text_block("Detect early. Spray less. Waste less. Protect the garden and the planet.",
                 size=12, bold=True, color=GREEN_DARK, x=M + 6, w=W - 12, gap=0.5)
    d.text_block("আগে শনাক্ত করুন। কম স্প্রে করুন। কম নষ্ট করুন। বাগান ও পৃথিবী রক্ষা করুন।",
                 size=12, bold=True, color=MANGO, x=M + 6, w=W - 12, gap=0)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    print("Written:", path)
    for name, text in (("Problem EN", PROBLEM_EN), ("Problem BN", PROBLEM_BN),
                       ("Solution EN", SOLUTION_EN), ("Solution BN", SOLUTION_BN)):
        print(f"  {name}: {word_count(text)} words")
