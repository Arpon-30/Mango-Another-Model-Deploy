/* AmropaliNet - 7 classes in English and Bangla.
   Treatment lists mirror DISEASE_INFO in model.py. */
window.MANGO_DISEASES = [
    {
        key: "Anthracnose",
        emoji: "🍂",
        tone: "#B5541C",
        sci: "Colletotrichum gloeosporioides",
        parts: ["leaf", "flower", "fruit", "branch"],
        risk: "high",
        name: { en: "Anthracnose", bn: "অ্যানথ্রাকনোজ" },
        short: {
            en: "Black spots on leaves, flowers and fruit.",
            bn: "পাতা, মুকুল ও ফলে কালো দাগ।"
        },
        desc: {
            en: "The most common fungal disease of mango. It burns the flowers, spots the leaves and hides inside fruit until it ripens.",
            bn: "আমের সবচেয়ে পরিচিত ছত্রাক রোগ। মুকুল পুড়িয়ে দেয়, পাতায় দাগ ফেলে এবং পাকা পর্যন্ত ফলের ভেতরে লুকিয়ে থাকে।"
        },
        spread: {
            en: "Rain splash, dew and humid air carry spores from dead twigs and leaves to new flowers and fruit.",
            bn: "বৃষ্টির ছিটা, শিশির ও আর্দ্র বাতাস মরা ডাল-পাতা থেকে জীবাণু নতুন মুকুল ও ফলে নিয়ে যায়।"
        },
        season: {
            en: "Flowering time and the rainy season.",
            bn: "মুকুল আসার সময় ও বর্ষাকাল।"
        },
        symptoms: {
            en: [
                "Dark brown to black irregular spots on leaves",
                "Water-soaked lesions that enlarge rapidly",
                "Premature leaf drop and defoliation",
                "Blossom blight and twig dieback",
                "Fruit rot that remains latent until ripening"
            ],
            bn: [
                "পাতায় গাঢ় বাদামি থেকে কালো অনিয়মিত দাগ",
                "পানি-ভেজা দাগ যা দ্রুত বড় হয়",
                "সময়ের আগে পাতা ঝরে পড়া",
                "মুকুল পুড়ে যাওয়া ও ডাল শুকিয়ে যাওয়া",
                "ফল পাকার সময় পচন দেখা দেয়"
            ]
        },
        remedies: {
            en: [
                "Apply copper-based fungicides (Bordeaux mixture)",
                "Use systemic fungicides like Carbendazim or Mancozeb",
                "Prune and destroy infected branches and leaves to improve ventilation",
                "Post-harvest: hot water treatment (50-55°C for 5-10 minutes) to reduce decay",
                "Maintain good orchard hygiene and spacing"
            ],
            bn: [
                "কপারভিত্তিক ছত্রাকনাশক (বোর্দো মিশ্রণ) প্রয়োগ করুন",
                "কার্বেন্ডাজিম বা ম্যানকোজেবের মতো অন্তর্বাহী ছত্রাকনাশক ব্যবহার করুন",
                "আক্রান্ত ডাল ও পাতা ছেঁটে নষ্ট করুন, বাতাস চলাচল বাড়ান",
                "ফল তোলার পর গরম পানিতে শোধন (৫০-৫৫°C, ৫-১০ মিনিট)",
                "বাগান পরিষ্কার রাখুন ও গাছের মাঝে দূরত্ব বজায় রাখুন"
            ]
        },
        prevent: {
            en: ["Remove fallen leaves and dead twigs", "Spray before flowers open in humid weather", "Do not harvest in the rain"],
            bn: ["ঝরা পাতা ও মরা ডাল সরিয়ে ফেলুন", "আর্দ্র আবহাওয়ায় মুকুল ফোটার আগে স্প্রে করুন", "বৃষ্টির মধ্যে ফল তুলবেন না"]
        }
    },
    {
        key: "Bacterial Canker",
        emoji: "🦠",
        tone: "#8E6A00",
        sci: "Xanthomonas campestris pv. mangiferaeindicae",
        parts: ["leaf", "fruit", "branch"],
        risk: "high",
        name: { en: "Bacterial Canker", bn: "ব্যাকটেরিয়াল ক্যাঙ্কার" },
        short: {
            en: "Raised black spots with yellow edges.",
            bn: "হলুদ কিনারাসহ উঁচু কালো দাগ।"
        },
        desc: {
            en: "A bacterial disease that attacks leaves, twigs and fruit. Cracked, oozing spots make fruit unfit for market, especially in wet years.",
            bn: "ব্যাকটেরিয়াজনিত রোগ যা পাতা, ডাল ও ফলে আক্রমণ করে। ফাটা ও রস-ঝরা দাগে ফল বাজারে বিক্রির অযোগ্য হয়, বিশেষ করে বর্ষার বছরে।"
        },
        spread: {
            en: "Wind-driven rain, wounds, infected saplings and unclean pruning tools move bacteria from tree to tree.",
            bn: "ঝড়-বৃষ্টি, ক্ষতস্থান, আক্রান্ত চারা ও অপরিষ্কার ছাঁটাই যন্ত্র এক গাছ থেকে আরেক গাছে জীবাণু ছড়ায়।"
        },
        season: {
            en: "Monsoon and stormy weather.",
            bn: "বর্ষা ও ঝড়ো আবহাওয়া।"
        },
        symptoms: {
            en: [
                "Water-soaked angular lesions on leaves",
                "Yellow halo surrounding dark lesions",
                "Cracking and gummosis on twigs and branches",
                "Lesions may ooze a yellow bacterial exudate",
                "Severe cases lead to defoliation and fruit drop"
            ],
            bn: [
                "পাতায় পানি-ভেজা কোণাকার দাগ",
                "কালো দাগের চারপাশে হলুদ বলয়",
                "ডালে ফাটল ও আঠা বের হওয়া",
                "দাগ থেকে হলুদ রস বের হতে পারে",
                "বেশি হলে পাতা ও ফল ঝরে পড়ে"
            ]
        },
        remedies: {
            en: [
                "Spray copper oxychloride (0.3%) at 15-day intervals",
                "Apply Streptomycin sulfate (500 ppm) sprays",
                "Prune and burn infected plant materials",
                "Avoid overhead irrigation to reduce humidity",
                "Apply copper-based bactericides during the rainy season"
            ],
            bn: [
                "১৫ দিন পরপর কপার অক্সিক্লোরাইড (০.৩%) স্প্রে করুন",
                "স্ট্রেপটোমাইসিন সালফেট (৫০০ ppm) স্প্রে করুন",
                "আক্রান্ত অংশ ছেঁটে পুড়িয়ে ফেলুন",
                "আর্দ্রতা কমাতে গাছের ওপর দিয়ে সেচ দেবেন না",
                "বর্ষায় কপারভিত্তিক ব্যাকটেরিয়ানাশক দিন"
            ]
        },
        prevent: {
            en: ["Plant only healthy saplings", "Clean pruning tools between trees", "Plant windbreaks around the garden"],
            bn: ["শুধু সুস্থ চারা লাগান", "প্রতি গাছের পর ছাঁটাই যন্ত্র পরিষ্কার করুন", "বাগানের চারপাশে বাতাস-রোধী গাছ লাগান"]
        }
    },
    {
        key: "Healthy",
        emoji: "🌿",
        tone: "#2E7D32",
        sci: "Mangifera indica (Normal)",
        parts: [],
        risk: "none",
        name: { en: "Healthy", bn: "সুস্থ" },
        short: {
            en: "No disease found. Keep it that way.",
            bn: "কোনো রোগ নেই। এভাবেই যত্ন নিন।"
        },
        desc: {
            en: "Clean colour, smooth skin and no spots. The tree is in good health.",
            bn: "সুন্দর রং, মসৃণ ত্বক, কোনো দাগ নেই। গাছ ভালো আছে।"
        },
        spread: {
            en: "Nothing to spread. Regular checks keep the whole garden safe.",
            bn: "ছড়ানোর মতো কিছু নেই। নিয়মিত পরীক্ষায় পুরো বাগান নিরাপদ থাকে।"
        },
        season: {
            en: "Check every 1-2 weeks, more often at flowering.",
            bn: "প্রতি ১-২ সপ্তাহে দেখুন, মুকুলের সময় আরও ঘন ঘন।"
        },
        symptoms: {
            en: [
                "Vibrant green leaf coloration",
                "Smooth and glossy leaf surface",
                "No spots, lesions, or discoloration",
                "Normal leaf shape and size",
                "Healthy growth pattern"
            ],
            bn: [
                "উজ্জ্বল সবুজ পাতা",
                "মসৃণ ও চকচকে পাতা",
                "কোনো দাগ বা বিবর্ণতা নেই",
                "স্বাভাবিক আকার ও আকৃতি",
                "সুস্থ বৃদ্ধি"
            ]
        },
        remedies: {
            en: [
                "Continue regular monitoring of the plant",
                "Maintain balanced fertilization schedule",
                "Ensure proper irrigation practices",
                "Keep orchard clean and well-maintained",
                "Monitor for early signs of pest or disease"
            ],
            bn: [
                "নিয়মিত গাছ পর্যবেক্ষণ চালিয়ে যান",
                "সুষম সার প্রয়োগ করুন",
                "সঠিকভাবে সেচ দিন",
                "বাগান পরিষ্কার রাখুন",
                "পোকা বা রোগের প্রথম লক্ষণের দিকে নজর রাখুন"
            ]
        },
        prevent: {
            en: ["Use compost and balanced fertiliser", "Prune for sunlight and air", "Scan a leaf whenever something looks odd"],
            bn: ["জৈব সার ও সুষম সার দিন", "আলো-বাতাসের জন্য ডাল ছাঁটুন", "সন্দেহ হলেই একটি পাতা স্ক্যান করুন"]
        }
    },
    {
        key: "Powdery Mildew",
        emoji: "🌫️",
        tone: "#6B7C8F",
        sci: "Oidium mangiferae",
        parts: ["leaf", "flower", "fruit"],
        risk: "high",
        name: { en: "Powdery Mildew", bn: "পাউডারি মিলডিউ" },
        short: {
            en: "White powder on flowers and young leaves.",
            bn: "মুকুল ও কচি পাতায় সাদা পাউডার।"
        },
        desc: {
            en: "A white powdery fungus on flowers, young leaves and baby fruit. It can cut the season's fruit set sharply.",
            bn: "মুকুল, কচি পাতা ও গুটি আমে সাদা পাউডারের মতো ছত্রাক। মৌসুমের ফলন অনেক কমিয়ে দিতে পারে।"
        },
        spread: {
            en: "Light spores fly on the wind across the whole garden, fastest in dry days with cool nights.",
            bn: "হালকা জীবাণু বাতাসে উড়ে পুরো বাগানে ছড়ায়, শুকনো দিন ও ঠান্ডা রাতে সবচেয়ে দ্রুত।"
        },
        season: {
            en: "Flowering time (late winter to early spring).",
            bn: "মুকুল আসার সময় (শীতের শেষ থেকে বসন্তের শুরু)।"
        },
        symptoms: {
            en: [
                "White powdery coating on leaf surfaces",
                "Affected leaves curl and distort",
                "Flower panicles covered in white powder",
                "Premature flower and fruit drop",
                "Reduced fruit set and yield"
            ],
            bn: [
                "পাতার ওপর সাদা পাউডারের আবরণ",
                "আক্রান্ত পাতা কুঁকড়ে যায়",
                "মুকুল সাদা পাউডারে ঢেকে যায়",
                "মুকুল ও গুটি আগেভাগে ঝরে পড়ে",
                "ফল ধরা ও ফলন কমে যায়"
            ]
        },
        remedies: {
            en: [
                "Spray wettable sulfur (0.2%) or Karathane",
                "Apply Triadimefon (0.1%) fungicide",
                "Use sulfur-based fungicides during the dry season",
                "Ensure good orchard ventilation through proper pruning",
                "Apply fungicides starting at the early flowering stage"
            ],
            bn: [
                "ভেজা গন্ধক (০.২%) বা কারাথেন স্প্রে করুন",
                "ট্রায়াডিমেফন (০.১%) ছত্রাকনাশক দিন",
                "শুকনো মৌসুমে গন্ধকভিত্তিক ছত্রাকনাশক ব্যবহার করুন",
                "সঠিক ছাঁটাই করে বাতাস চলাচল বাড়ান",
                "মুকুল আসার শুরুতেই ছত্রাকনাশক দিন"
            ]
        },
        prevent: {
            en: ["Check flowers every few days in winter", "Keep the canopy open", "Spray early - not after the powder spreads"],
            bn: ["শীতে কয়েক দিন পরপর মুকুল দেখুন", "গাছের ভেতর খোলামেলা রাখুন", "আগেভাগে স্প্রে করুন - পাউডার ছড়ানোর পরে নয়"]
        }
    },
    {
        key: "Scab",
        emoji: "🔶",
        tone: "#8D6E63",
        sci: "Elsinoë mangiferae",
        parts: ["leaf", "fruit", "branch"],
        risk: "medium",
        name: { en: "Scab", bn: "স্ক্যাব (দাদ রোগ)" },
        short: {
            en: "Rough, corky, raised spots.",
            bn: "খসখসে, কর্কের মতো উঁচু দাগ।"
        },
        desc: {
            en: "A fungus that leaves rough, corky patches on leaves, twigs and fruit. The fruit is still edible but loses market value.",
            bn: "ছত্রাক যা পাতা, ডাল ও ফলে খসখসে কর্কের মতো দাগ ফেলে। ফল খাওয়া যায় কিন্তু বাজারদর কমে যায়।"
        },
        spread: {
            en: "Rain splash and humid weather spread spores to young leaves and fruit; infected nursery plants carry it to new gardens.",
            bn: "বৃষ্টির ছিটা ও আর্দ্র আবহাওয়ায় কচি পাতা ও ফলে ছড়ায়; আক্রান্ত নার্সারির চারা নতুন বাগানে নিয়ে যায়।"
        },
        season: {
            en: "From flower buds until fruit is half grown.",
            bn: "মুকুলের কুঁড়ি থেকে ফল অর্ধেক বড় হওয়া পর্যন্ত।"
        },
        symptoms: {
            en: [
                "Dark brown to gray corky scab lesions",
                "Raised, rough-textured spots on leaves",
                "Distortion of young leaves and shoots",
                "Small raised grey-to-brownish lesions on fruit",
                "Leaves may become deformed or crinkled"
            ],
            bn: [
                "গাঢ় বাদামি থেকে ধূসর কর্কের মতো দাগ",
                "পাতায় উঁচু, খসখসে দাগ",
                "কচি পাতা ও ডগা বেঁকে যায়",
                "ফলে ছোট উঁচু ধূসর-বাদামি দাগ",
                "পাতা কুঁচকে বা বিকৃত হতে পারে"
            ]
        },
        remedies: {
            en: [
                "Apply Zineb or Maneb fungicides",
                "Spray copper oxychloride at 15-day intervals",
                "Remove and destroy dead leaves and twigs",
                "Apply copper-based fungicides from flower bud emergence",
                "Continue treatment until the fruit reaches half size"
            ],
            bn: [
                "জিনেব বা ম্যানেব ছত্রাকনাশক দিন",
                "১৫ দিন পরপর কপার অক্সিক্লোরাইড স্প্রে করুন",
                "মরা পাতা ও ডাল সরিয়ে নষ্ট করুন",
                "মুকুলের কুঁড়ি বের হলেই কপারভিত্তিক ছত্রাকনাশক দিন",
                "ফল অর্ধেক বড় হওয়া পর্যন্ত চিকিৎসা চালিয়ে যান"
            ]
        },
        prevent: {
            en: ["Buy saplings from a trusted nursery", "Clear fallen leaves before the rains", "Protect young fruit early"],
            bn: ["বিশ্বস্ত নার্সারি থেকে চারা কিনুন", "বর্ষার আগে ঝরা পাতা পরিষ্কার করুন", "কচি ফল শুরু থেকেই রক্ষা করুন"]
        }
    },
    {
        key: "Sooty Mould",
        emoji: "🖤",
        tone: "#37474F",
        sci: "Capnodium mangiferae",
        parts: ["leaf", "fruit", "branch"],
        risk: "medium",
        name: { en: "Sooty Mould", bn: "সুটি মোল্ড (কালো ঝুল)" },
        short: {
            en: "Black soot layer that wipes off.",
            bn: "কালো ঝুলের আস্তর যা মুছলে ওঠে।"
        },
        desc: {
            en: "A black coating that grows on the sticky honeydew of hoppers, mealybugs and scale insects. It blocks sunlight from the leaves.",
            bn: "হপার, ছাতরা ও স্কেল পোকার আঠালো মধুরসের ওপর জন্মানো কালো আস্তর। পাতায় সূর্যের আলো পৌঁছাতে দেয় না।"
        },
        spread: {
            en: "It follows the insects. Hoppers and mealybugs walk and fly between trees, and ants protect them.",
            bn: "পোকার সাথে সাথে ছড়ায়। হপার ও ছাতরা পোকা গাছে গাছে যায়, আর পিঁপড়া তাদের রক্ষা করে।"
        },
        season: {
            en: "Flowering to fruiting, when hoppers are active.",
            bn: "মুকুল থেকে ফল ধরা পর্যন্ত, যখন হপার পোকা সক্রিয়।"
        },
        symptoms: {
            en: [
                "Black sooty coating covering leaf surfaces",
                "Coating easily wiped off revealing green leaf",
                "Presence of scale insects or aphids nearby",
                "Reduced photosynthesis and plant vigor",
                "Black velvety coating on twigs and fruits"
            ],
            bn: [
                "পাতার ওপর কালো ঝুলের আবরণ",
                "মুছলে নিচে সবুজ পাতা দেখা যায়",
                "আশেপাশে স্কেল পোকা বা জাবপোকা",
                "গাছের খাদ্য তৈরি ও শক্তি কমে যায়",
                "ডাল ও ফলে কালো মখমলের মতো আস্তর"
            ]
        },
        remedies: {
            en: [
                "Control the sap-sucking insects first (use insecticides or neem oil)",
                "Spray starch solution to remove sooty coating",
                "Prune heavily infected, dense branches to increase light",
                "Apply systemic insecticides to eliminate hoppers and mealybugs",
                "Maintain good air circulation in the orchard"
            ],
            bn: [
                "আগে রস-চোষা পোকা দমন করুন (কীটনাশক বা নিম তেল)",
                "কালো আস্তর তুলতে মাড়ের দ্রবণ স্প্রে করুন",
                "ঘন আক্রান্ত ডাল ছেঁটে আলো বাড়ান",
                "হপার ও ছাতরা পোকা দমনে অন্তর্বাহী কীটনাশক দিন",
                "বাগানে ভালো বাতাস চলাচল রাখুন"
            ]
        },
        prevent: {
            en: ["Try neem oil first - it is gentler on bees", "Band trunks to stop ants", "Check leaf undersides for insects"],
            bn: ["প্রথমে নিম তেল দিন - মৌমাছির জন্য নিরাপদ", "পিঁপড়া আটকাতে কাণ্ডে বাঁধন দিন", "পাতার নিচে পোকা আছে কিনা দেখুন"]
        }
    },
    {
        key: "Stem End Rot",
        emoji: "⚫",
        tone: "#5D4037",
        sci: "Lasiodiplodia theobromae",
        parts: ["fruit", "branch"],
        risk: "high",
        name: { en: "Stem End Rot", bn: "বোঁটা পচা রোগ" },
        short: {
            en: "Rot starting at the stalk of ripe fruit.",
            bn: "পাকা ফলের বোঁটা থেকে পচন শুরু।"
        },
        desc: {
            en: "A fungus that starts at the stalk end after harvest and quickly turns the fruit soft and black. It causes heavy losses in storage and transport.",
            bn: "ফল তোলার পর বোঁটার দিক থেকে শুরু হয়ে দ্রুত ফল নরম ও কালো করে ফেলে। সংরক্ষণ ও পরিবহনে বড় ক্ষতি করে।"
        },
        spread: {
            en: "The fungus lives in dead twigs and bark, enters through the stalk at harvest, then spreads fruit to fruit in crates.",
            bn: "ছত্রাক মরা ডাল ও বাকলে থাকে, ফল তোলার সময় বোঁটা দিয়ে ঢোকে, তারপর ঝুড়িতে এক ফল থেকে আরেক ফলে ছড়ায়।"
        },
        season: {
            en: "Harvest, storage and transport in hot, humid weather.",
            bn: "গরম ও আর্দ্র আবহাওয়ায় ফল তোলা, সংরক্ষণ ও পরিবহনের সময়।"
        },
        symptoms: {
            en: [
                "Dark brown to black rotting starting at stem end",
                "Soft, water-soaked lesion spreading rapidly",
                "White to gray fungal growth on rotted area",
                "Pulp becomes soft and brown",
                "Rapid deterioration after harvest"
            ],
            bn: [
                "বোঁটার দিক থেকে গাঢ় বাদামি থেকে কালো পচন",
                "নরম, পানি-ভেজা দাগ দ্রুত ছড়ায়",
                "পচা অংশে সাদা-ধূসর ছত্রাক",
                "শাঁস নরম ও বাদামি হয়ে যায়",
                "ফল তোলার পর দ্রুত নষ্ট হয়"
            ]
        },
        remedies: {
            en: [
                "Hot water treatment (52°C for 5 min) post-harvest",
                "Apply Prochloraz (0.05%) fungicide dip",
                "Avoid harvesting immature fruit and prevent mechanical injury",
                "Pre-harvest sprays of carbendazim to reduce incidence",
                "Post-harvest hot water dips with or without fungicides"
            ],
            bn: [
                "ফল তোলার পর গরম পানিতে শোধন (৫২°C, ৫ মিনিট)",
                "প্রোক্লোরাজ (০.০৫%) ছত্রাকনাশকে ডুবিয়ে নিন",
                "অপরিপক্ব ফল তুলবেন না, ফলে আঘাত লাগতে দেবেন না",
                "তোলার আগে কার্বেন্ডাজিম স্প্রে করুন",
                "তোলার পর ছত্রাকনাশকসহ বা ছাড়া গরম পানিতে ডুবান"
            ]
        },
        prevent: {
            en: ["Harvest with a short stalk left on", "Remove dead twigs after harvest", "Keep crates clean and shaded"],
            bn: ["বোঁটা কিছুটা রেখে ফল তুলুন", "ফল তোলার পর মরা ডাল সরান", "ঝুড়ি পরিষ্কার ও ছায়ায় রাখুন"]
        }
    }
];
