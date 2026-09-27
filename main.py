import os
import random
import time
from scraper import get_bestseller_products
from review_scraper import get_amazon_reviews
from content_generator import generate_post, generate_guide
from link_checker import check_asin, DEAD
from wordpress_poster import post_to_wordpress, is_duplicate_asin

# ============================================================
# 검증된 아마존 베스트셀러 목록 (스킨케어/뷰티/생활용품 위주)
# 구매자 리뷰·스펙 조사 기반으로 글이 작성됩니다 (직접 사용 후기로 지어내지 않음)
# ============================================================

STEADY_SELLERS = [

    # ── 스킨케어 ──────────────────────────────────────────────
    {
        "title": "CeraVe Moisturizing Cream, 19 oz",
        "price": "$19.99", "rating": "4.8 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00TTD9BRC?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00TTD9BRC",
        "features": [
            "Developed with dermatologists — gentle enough for eczema-prone skin",
            "3 essential ceramides restore and lock in the skin's moisture barrier",
            "Hyaluronic acid draws moisture into skin and keeps it there all day",
            "One 19 oz tub lasts 2–3 months with daily use — extremely cost-effective",
            "Fragrance-free and non-comedogenic — won't clog pores or irritate skin",
            "Works on both face and body — simplifies your skincare routine",
        ],
    },
    {
        "title": "COSRX Snail Mucin 96% Power Repairing Essence, 3.38 fl.oz",
        "price": "$19.99", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00PBX3L7K?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00PBX3L7K",
        "features": [
            "96% snail secretion filtrate fades red marks and acne scars over time",
            "Lightweight gel texture absorbs in seconds — no sticky residue",
            "Works under moisturizer and makeup without pilling",
            "Visibly reduces redness and uneven texture in 2–4 weeks",
            "Fragrance-free and alcohol-free — safe for sensitive and acne-prone skin",
            "One bottle lasts 3–4 months with daily use",
        ],
    },
    {
        "title": "Hero Cosmetics Mighty Patch Original, 36 Count",
        "price": "$13.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B074PVTPBW?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B074PVTPBW",
        "features": [
            "Hydrocolloid patches visibly shrink pimples overnight while you sleep",
            "Absorbs pus and oil from whiteheads — turns white when full",
            "Protects pimples from bacteria, picking, and makeup",
            "Ultra-thin patches stay on all night and are barely visible",
            "Works in 6–8 hours — wake up to noticeably flatter, less red skin",
            "Drug-free and gentle enough for sensitive skin",
        ],
    },
    {
        "title": "The Ordinary Glycolic Acid 7% Exfoliating Toner, 8.1 fl oz",
        "price": "$11.60", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B06XPNB27T?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B06XPNB27T",
        "features": [
            "7% glycolic acid dissolves dead skin cells for visibly smoother texture",
            "Skin looks more radiant after the first few uses",
            "Also works on body — great for keratosis pilaris on arms and legs",
            "Lightweight water formula — apply with cotton pad after cleansing",
            "Improves absorption of serums and moisturizers applied after",
            "Budget-friendly alternative to expensive exfoliating treatments",
        ],
    },
    {
        "title": "Paula's Choice SKIN PERFECTING 2% BHA Liquid Exfoliant, 4 oz",
        "price": "$35.00", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00949CTQQ?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00949CTQQ",
        "features": [
            "2% salicylic acid unclogs pores and reduces blackheads without scrubbing",
            "Visibly minimizes pore size with regular use over 4–6 weeks",
            "Works deep inside pores — removes the buildup a regular cleanser can't reach",
            "Gentle enough to use daily — no flaking or over-drying",
            "Cruelty-free and fragrance-free — no animal testing",
            "Cult favorite with millions of bottles sold worldwide",
        ],
    },
    {
        "title": "TruSkin Vitamin C Serum for Face, 1 fl oz",
        "price": "$19.99", "rating": "4.3 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01M0QASHJ?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B01M0QASHJ",
        "features": [
            "Vitamin C + Vitamin E + Hyaluronic Acid — three key brightening ingredients",
            "Fades dark spots and sun damage over 4–8 weeks of consistent use",
            "Skin looks more even-toned and glowy within the first 2–3 weeks",
            "Lightweight — layers easily under SPF and moisturizer",
            "Plant-based formula with aloe vera — feels soothing on application",
            "One of the most affordable vitamin C serums that actually delivers results",
        ],
    },
    {
        "title": "La Roche-Posay Toleriane Double Repair Face Moisturizer, 2.5 fl oz",
        "price": "$20.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01N9SPQHX?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B01N9SPQHX",
        "features": [
            "Ceramide + niacinamide formula repairs the skin barrier in just 1 hour",
            "Skin stays hydrated all day — no mid-day tightness or flakiness",
            "Lightweight enough to wear under makeup without caking or pilling",
            "Fragrance-free and paraben-free — dermatologist-tested for sensitive skin",
            "Works for both AM and PM routine — one product for both steps",
            "Trusted by dermatologists — used in clinical settings for sensitive skin patients",
        ],
    },
    {
        "title": "CeraVe AM Facial Moisturizing Lotion with SPF 30, 3 oz",
        "price": "$15.99", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B077TQR4DP?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B077TQR4DP",
        "features": [
            "Moisturizer and SPF 30 sunscreen in one step — simplifies the morning routine",
            "Niacinamide helps calm redness and even out skin tone over time",
            "Dries to a clean, non-greasy finish — perfect under makeup",
            "Broad spectrum UVA/UVB protection prevents photoaging",
            "Ceramide formula maintains the skin barrier throughout the day",
            "Fragrance-free — works for sensitive and acne-prone skin types",
        ],
    },
    {
        "title": "Neutrogena Hydro Boost Water Gel Moisturizer, 1.7 oz",
        "price": "$17.99", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00NR1YQHM?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00NR1YQHM",
        "features": [
            "Hyaluronic acid gel floods skin with moisture and locks it in all day",
            "Water-gel texture melts into skin in seconds — no heavy feeling",
            "Skin feels plump and bouncy immediately after application",
            "Oil-free and non-comedogenic — safe for oily and combination skin",
            "Works as a day moisturizer, night moisturizer, or makeup primer",
            "Visible difference in skin plumpness within 1 week of daily use",
        ],
    },
    {
        "title": "Anua Heartleaf 77% Soothing Toner, 8.45 fl oz",
        "price": "$21.00", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B09TPXP89F?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B09TPXP89F",
        "features": [
            "77% heartleaf extract calms red, irritated skin within minutes",
            "Feels like cool water on sunburned or reactive skin",
            "Alcohol-free formula — won't sting or dry out sensitive skin",
            "Doubles as a hydrating mist — refreshing throughout the day",
            "Korean skincare bestseller loved for its immediate soothing effect",
            "Works great after exfoliation or retinol to calm any irritation",
        ],
    },
    {
        "title": "Vanicream Gentle Facial Cleanser, 8 fl oz",
        "price": "$12.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00QY1XZ4W?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00QY1XZ4W",
        "features": [
            "Gentle enough to use twice daily without stripping the skin barrier",
            "Leaves no residue — skin feels clean but never tight or squeaky",
            "Free from dyes, fragrance, lanolin, parabens, and formaldehyde",
            "Dermatologist-recommended for eczema, rosacea, and sensitive skin",
            "Pump dispenser is hygienic and easy to use in the shower",
            "One bottle lasts 2–3 months with twice-daily use",
        ],
    },
    {
        "title": "Rael Miracle Invisible Pimple Patches, 96 Count",
        "price": "$14.99", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B07QZKRHBS?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B07QZKRHBS",
        "features": [
            "96 patches in two sizes — one for small whiteheads, one for larger pimples",
            "Hydrocolloid technology absorbs fluid and visibly flattens pimples overnight",
            "Nearly invisible — can wear during the day under makeup",
            "Prevents picking and scarring by creating a protective barrier",
            "One of the most affordable per-patch options available",
            "Korean skincare formula — gentle on all skin types including sensitive",
        ],
    },
    {
        "title": "CeraVe Foaming Facial Cleanser for Oily Skin, 19 oz",
        "price": "$16.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01N1LL62W?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B01N1LL62W",
        "features": [
            "Removes excess oil and dirt without over-drying — skin stays balanced",
            "Niacinamide calms redness and reduces visible pore size over time",
            "Rich foam rinses completely clean — no leftover residue",
            "19 oz value size lasts 3–4 months with twice-daily use",
            "Fragrance-free and non-comedogenic — won't cause breakouts",
            "Works great as a morning cleanser for oily and combination skin",
        ],
    },
    {
        "title": "Medicube Zero Pore Pads 2.0, 70 Pads",
        "price": "$24.00", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B0BTHNPCQ8?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B0BTHNPCQ8",
        "features": [
            "Pre-soaked pads exfoliate and tighten pores in one swipe",
            "AHA + BHA + PHA triple acid blend removes dead skin gently",
            "Pores look noticeably smaller after 2–3 weeks of regular use",
            "Both sides — textured for exfoliation, soft for patting in",
            "#1 bestselling toner pad on Amazon for multiple quarters",
            "Replace your toner and exfoliator in one product — saves time and money",
        ],
    },

    # ── 헤어케어 ──────────────────────────────────────────────
    {
        "title": "Olaplex No. 3 Hair Perfector, 3.3 fl oz",
        "price": "$28.00", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00SNM5F6G?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00SNM5F6G",
        "features": [
            "Repairs broken disulfide bonds in hair — the root cause of damage and breakage",
            "Hair feels stronger and snaps less within the first 1–2 uses",
            "Apply to damp hair for 10 minutes — works as a weekly treatment",
            "Visible reduction in frizz and split ends after consistent use",
            "Salon-grade formula available for home use at a fraction of salon prices",
            "Works on color-treated, bleached, chemically straightened, or heat-damaged hair",
        ],
    },
    {
        "title": "Nizoral Anti-Dandruff Shampoo, 7 fl oz",
        "price": "$14.97", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00AINMFAC?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00AINMFAC",
        "features": [
            "1% ketoconazole kills the fungus that causes dandruff at the source",
            "Dandruff visibly reduces within 2–4 uses — flakes gone in days",
            "Use twice a week — leave on for 3–5 minutes before rinsing",
            "Works when regular shampoos have failed — medical-grade active ingredient",
            "Also helps with seborrheic dermatitis and itchy scalp",
            "Gentle enough for color-treated hair",
        ],
    },
    {
        "title": "Moroccanoil Treatment Original, 3.4 fl oz",
        "price": "$46.00", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B002JH06KE?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B002JH06KE",
        "features": [
            "Argan oil instantly detangles and smooths hair before blow-drying",
            "Hair dries 40–50% faster when used as a heat protectant",
            "Controls frizz in humid weather — lasts all day",
            "A few drops go a long way — 3.4 oz bottle lasts 3–6 months",
            "Suitable for all hair types from fine to coarse, straight to curly",
            "Used by professional stylists worldwide",
        ],
    },
    {
        "title": "OGX Renewing Argan Oil of Morocco Shampoo, 13 fl oz",
        "price": "$9.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B005DKZWFS?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B005DKZWFS",
        "features": [
            "Argan oil hydrates and softens hair from the first wash",
            "Hair feels noticeably smoother and shinier after just 2–3 uses",
            "Sulfate-free formula is gentle enough for daily use",
            "Rich lather rinses clean without leaving a heavy residue",
            "Pairs perfectly with the matching conditioner for best results",
            "Salon-quality ingredients at a drugstore price",
        ],
    },
    {
        "title": "Not Your Mother's Curl Talk Defining Cream, 8 fl oz",
        "price": "$9.99", "rating": "4.3 out of 5 stars",
        "link": "https://www.amazon.com/dp/B06XH7GS5C?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B06XH7GS5C",
        "features": [
            "Defines curls without crunch or stiffness — bouncy, natural movement",
            "Rice protein and shea butter add moisture and reduce frizz",
            "Apply to wet hair, scrunch, and air dry or diffuse for defined curls",
            "Works for 2B–4C curl types — versatile for a range of textures",
            "Budget-friendly alternative to much pricier curl creams",
            "No sulfates, parabens, or drying alcohol",
        ],
    },

    # ── 뷰티 도구/기기 ─────────────────────────────────────────
    {
        "title": "Revlon One-Step Volumizer Hair Dryer and Hot Air Brush",
        "price": "$34.99", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01LSUQSB0?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B01LSUQSB0",
        "features": [
            "Dries and volumizes hair in one step — no separate round brush needed",
            "Cuts blow-dry time in half compared to regular dryer and brush combo",
            "Oval barrel creates volume at the roots that lasts all day",
            "Ionic technology reduces frizz while drying",
            "Three heat and speed settings — low, high, and cool shot",
            "Lightweight at just over 1 lb — easy to hold during styling",
        ],
    },
    {
        "title": "Finishing Touch Flawless Facial Hair Remover",
        "price": "$19.99", "rating": "4.3 out of 5 stars",
        "link": "https://www.amazon.com/dp/B072LNFZQQ?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B072LNFZQQ",
        "features": [
            "Removes facial peach fuzz painlessly in seconds — no redness or irritation",
            "18-karat gold-plated head glides over skin without nicking",
            "Completely silent — can use discreetly anywhere",
            "Built-in LED light reveals even the finest hairs",
            "Results last up to 4 weeks — smoother skin and better makeup application",
            "Runs on 1 AAA battery — no charging needed",
        ],
    },
    {
        "title": "Real Techniques Miracle Complexion Sponge, 2 Pack",
        "price": "$11.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B076MV3X8H?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B076MV3X8H",
        "features": [
            "Flat edge covers large areas fast, rounded top blends under eyes and nose",
            "Wet it and it expands to double its size — softer and streak-free application",
            "Foundation looks airbrushed instead of cakey",
            "Works with liquid, cream, and powder formulas",
            "Two sponges in the pack — use one wet, one dry, or have a backup",
            "Much more affordable than designer beauty blenders",
        ],
    },
    {
        "title": "Tweezerman Stainless Steel Slant Tweezer",
        "price": "$22.00", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B000T7FCWQ?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B000T7FCWQ",
        "features": [
            "Slant tip grabs even the finest, shortest hairs on the first try",
            "Precision-calibrated tension — not too tight, not too loose",
            "Surgical-grade stainless steel stays sharp for years",
            "Free sharpening for life — send them in and they'll sharpen for free",
            "Used by professional makeup artists and estheticians",
            "Once you try Tweezerman, cheap tweezers become frustrating",
        ],
    },

    # ── 생활/홈케어 ───────────────────────────────────────────
    {
        "title": "Bissell Little Green Portable Carpet Cleaner, 1400B",
        "price": "$89.99", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B0053QWOQ4?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B0053QWOQ4",
        "features": [
            "Sprays water, scrubs, and suctions up stains in a single pass",
            "Removes pet accidents, wine, coffee, and mud from carpets and upholstery",
            "Compact size — fits in a closet and pulls out only when needed",
            "48 oz tank is enough to clean multiple stains before refilling",
            "Works on car seats, couch cushions, and area rugs — not just carpet",
            "Saves the cost of professional carpet cleaning for spot messes",
        ],
    },
    {
        "title": "Angry Mama Microwave Cleaner",
        "price": "$8.99", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B08BKZP45P?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B08BKZP45P",
        "features": [
            "Fill with water and vinegar, microwave 7 minutes — steam loosens all grime",
            "Stuck-on food wipes off with zero scrubbing after steaming",
            "Fun design that kids actually enjoy using — makes cleaning less of a chore",
            "Reusable — use it every week for a consistently clean microwave",
            "No harsh chemicals needed — vinegar and water does the job",
            "One of the most satisfying cleaning purchases you'll make",
        ],
    },
    {
        "title": "OXO Good Grips Shower Squeegee",
        "price": "$11.99", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00MZBY9CM?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B00MZBY9CM",
        "features": [
            "30-second daily squeegee after showering prevents soap scum buildup entirely",
            "Soft rubber blade glides smoothly across glass and tile without scratching",
            "Comfortable non-slip grip — easy to use even with wet hands",
            "Hook hole for hanging — dries quickly between uses",
            "Eliminates the need for weekly scrubbing sessions on shower walls",
            "One of those small habits that saves hours of deep cleaning per year",
        ],
    },
    {
        "title": "Command Large Picture Hanging Strips, 14 Pairs",
        "price": "$14.98", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B073XS3CHW?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B073XS3CHW",
        "features": [
            "Holds up to 16 lbs — strong enough for large framed prints and mirrors",
            "Removes cleanly with no nail holes and no wall damage",
            "Perfect for renters who can't drill into walls",
            "Interlocking strips click together — frame goes up level on the first try",
            "Works on smooth walls, tile, metal, and wood surfaces",
            "14 pairs hang up to 7 large frames — great value for a whole apartment",
        ],
    },
    {
        "title": "Scotch-Brite Scrub Dots Non-Scratch Scrubber, 6 Pack",
        "price": "$7.99", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B09SQR53MC?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B09SQR53MC",
        "features": [
            "Non-scratch dots scrub away baked-on food without damaging non-stick pans",
            "Scrubby side on top, absorbent sponge on bottom — two functions in one",
            "Holds its shape and lasts twice as long as regular flat sponges",
            "Bright colors — easy to designate one for dishes, one for counters",
            "Rinses clean and dries fast — resists developing that wet sponge smell",
            "Six sponges last a typical household about 6–8 weeks",
        ],
    },
    {
        "title": "simplehuman 10 Liter Slim Step Trash Can",
        "price": "$39.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B000Q3QB7Q?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B000Q3QB7Q",
        "features": [
            "10-liter size fits neatly beside the toilet or under a small desk",
            "Fingerprint-resistant brushed steel stays looking clean between wipes",
            "Silent, slow-close lid — no clanging noise when it shuts",
            "Custom-fit liner pockets inside lid keep bags snug and invisible",
            "Durable stainless steel construction — lasts 10+ years vs cheap plastic",
            "Opens hands-free with one foot press — hygienic in the bathroom",
        ],
    },
    {
        "title": "Brita Standard Water Filter Replacement, 3 Pack",
        "price": "$19.99", "rating": "4.8 out of 5 stars",
        "link": "https://www.amazon.com/dp/B002IEVJRY?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B002IEVJRY",
        "features": [
            "Each filter lasts 2 months — 3-pack covers 6 months of filtered water",
            "Reduces chlorine taste, zinc, copper, mercury, and cadmium from tap water",
            "Tap water tastes noticeably better — you actually drink more water",
            "Replaces roughly 750 plastic water bottles per filter",
            "Easy twist-and-lock install — takes under 30 seconds to swap filters",
            "Compatible with all standard Brita pitchers and dispensers",
        ],
    },
    {
        "title": "Casabella Infuse Microfiber Mop with Spray",
        "price": "$29.99", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B08P4PD77Y?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B08P4PD77Y",
        "features": [
            "Built-in spray bottle lets you mop without carrying a separate bucket",
            "Microfiber pad traps dust and hair that regular mops push around",
            "Refillable bottle — use your own cleaning solution or just water",
            "Washable pad — throw it in the washing machine and reuse",
            "360-degree swivel head reaches under furniture and into corners easily",
            "Lightweight — cleaning the whole floor doesn't leave your arms tired",
        ],
    },

    # ── 주방 소형 가전 ─────────────────────────────────────────
    {
        "title": "Ninja AF101 Air Fryer, 4 Quart",
        "price": "$89.99", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B07FDJMC9Q?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B07FDJMC9Q",
        "features": [
            "4-quart basket fits a meal for 2–3 people — perfect for weeknight dinners",
            "Fries chicken wings crispy outside and juicy inside in 20 minutes — no oil needed",
            "Preheats in 3 minutes — much faster than waiting for an oven",
            "Air fry, roast, reheat, and dehydrate — four cooking functions in one",
            "Dishwasher-safe basket and crisper plate — cleanup takes under 2 minutes",
            "Uses 75% less fat than traditional deep frying",
        ],
    },
    {
        "title": "Instant Pot Duo 7-in-1 Electric Pressure Cooker, 6 Quart",
        "price": "$89.99", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00FLYWNYQ?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B00FLYWNYQ",
        "features": [
            "Cooks a whole chicken in 25 minutes — what takes the oven 90 minutes",
            "7 functions in one pot: pressure cook, slow cook, rice, steam, sauté, yogurt, warm",
            "6-quart size comfortably feeds a family of 4–6 people",
            "Set it and walk away — no stirring, no monitoring, no burning",
            "Inner pot and lid are dishwasher-safe — easy cleanup",
            "Replaces 7 kitchen appliances and frees up counter and cabinet space",
        ],
    },
    {
        "title": "Vitamix 5200 Blender, 64 oz",
        "price": "$399.95", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B008H4SLV6?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B008H4SLV6",
        "features": [
            "Aircraft-grade stainless steel blades pulverize seeds, stems, and ice completely smooth",
            "Smoothies are silky with zero chunks — even with kale and frozen berries",
            "Powerful enough to make hot soup by friction alone — no microwave needed",
            "Variable speed dial lets you control texture from chunky to completely smooth",
            "Self-cleaning — add water and dish soap, run for 60 seconds, done",
            "7-year full warranty — built to last decades, not years",
        ],
    },
    {
        "title": "Keurig K-Slim Coffee Maker, Single Serve",
        "price": "$89.99", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B07RQ3S8BN?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B07RQ3S8BN",
        "features": [
            "Brews an 8, 10, or 12 oz cup in under 2 minutes — perfect for busy mornings",
            "Only 5 inches wide — fits on even the most cramped kitchen counter",
            "Works with all standard K-Cup pods — thousands of flavors available",
            "Removable 46 oz reservoir — refill every 3–4 days instead of daily",
            "Brew the exact cup size you want — no waste from making a full pot",
            "Auto off feature turns off after 5 minutes — saves energy",
        ],
    },
    {
        "title": "Lodge 12 Inch Pre-Seasoned Cast Iron Skillet",
        "price": "$34.90", "rating": "4.8 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00G2XGC88?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B00G2XGC88",
        "features": [
            "Gets screaming hot and holds heat evenly — steakhouse-quality sear at home",
            "Pre-seasoned and ready to cook — just start cooking, no break-in needed",
            "Goes from stovetop to 500°F oven without any issue",
            "Gets more non-stick with every use as the seasoning builds up",
            "Works on all heat sources including induction and campfire",
            "One skillet that can replace multiple pans — lasts a lifetime",
        ],
    },
    {
        "title": "Hamilton Beach 2-Speed Hand Blender, 59765",
        "price": "$29.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B0002COKMO?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B0002COKMO",
        "features": [
            "Blend soups directly in the pot — no pouring hot liquid into a countertop blender",
            "Whisk attachment makes whipped cream in 2 minutes with zero mess",
            "Stainless steel blending shaft is dishwasher safe",
            "Only 2 lbs — easy to hold steady while blending",
            "Blends smoothies, sauces, baby food, and salad dressings in seconds",
            "Much easier to clean than a full-sized blender — rinse under running water",
        ],
    },
    {
        "title": "OXO Good Grips 3-Piece Mixing Bowl Set",
        "price": "$28.99", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B0000CFLJA?tag=followrefer20-20",
        "image": "", "category": "kitchen", "asin": "B0000CFLJA",
        "features": [
            "Non-slip base keeps bowls from sliding while mixing — huge quality-of-life upgrade",
            "Angled interior surface lets you see measurements from above",
            "Pour spout channels batter, batter, and liquids cleanly — no drips",
            "Three sizes: 1.5qt, 3qt, 5qt — covers everything from whisking eggs to mixing dough",
            "Nesting design — all three bowls stack inside each other for compact storage",
            "Dishwasher safe — toss them in after baking and forget about it",
        ],
    },

    # ── 건강/웰니스 ───────────────────────────────────────────
    {
        "title": "Hydro Flask 32 oz Wide Mouth Water Bottle",
        "price": "$44.95", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01ACAXEIQ?tag=followrefer20-20",
        "image": "", "category": "fitness", "asin": "B01ACAXEIQ",
        "features": [
            "Keeps water ice cold for 24 hours — even on a hot summer day outdoors",
            "32 oz capacity — hits the 'drink 8 glasses a day' goal in just 2 refills",
            "Wide mouth fits standard ice cubes and is easy to fill at the gym",
            "Powder coat finish means it doesn't sweat or slip out of your hand",
            "Survived years of being dropped, tossed in bags, and left in hot cars",
            "Lifetime warranty — Hydro Flask replaces it if anything goes wrong",
        ],
    },
    {
        "title": "Theragun Prime Percussion Massage Gun",
        "price": "$199.00", "rating": "4.5 out of 5 stars",
        "link": "https://www.amazon.com/dp/B08P9YSVBF?tag=followrefer20-20",
        "image": "", "category": "fitness", "asin": "B08P9YSVBF",
        "features": [
            "16mm amplitude reaches deep into muscle tissue for real percussive therapy",
            "5 speed settings from 1750–2400 PPM — gentle warm-up or intense recovery",
            "QuietForce technology runs at 65 dB — quieter than a conversation",
            "2.5-hour battery life — enough for a week of daily sessions on one charge",
            "4 attachments for different muscle groups and body areas",
            "Pairs with an app that guides you through recovery routines",
        ],
    },
    {
        "title": "Listerine Cool Mint Antiseptic Mouthwash, 1.5L",
        "price": "$8.97", "rating": "4.8 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01ET9CKTU?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B01ET9CKTU",
        "features": [
            "Kills 99.9% of germs that cause bad breath, plaque, and gingivitis",
            "30 seconds of rinsing reaches areas a toothbrush physically cannot",
            "Noticeable reduction in gum bleeding within 2 weeks of twice-daily use",
            "Cool mint flavor leaves mouth feeling clean for hours after use",
            "1.5-liter bottle lasts a family of 4 about 6–8 weeks",
            "ADA-accepted — clinically proven to improve gum health",
        ],
    },
    {
        "title": "Oral-B Pro 1000 Electric Toothbrush",
        "price": "$49.94", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B003UKM9CO?tag=followrefer20-20",
        "image": "", "category": "home", "asin": "B003UKM9CO",
        "features": [
            "Round head removes up to 300% more plaque along the gumline than a manual brush",
            "Built-in 2-minute timer automatically stops to signal when brushing is done",
            "Pressure sensor flashes when you push too hard — prevents gum damage",
            "One charge lasts 2 weeks with twice-daily use",
            "Compatible with all Oral-B replacement heads — wide variety available",
            "Noticeable difference in how clean teeth feel within the first week",
        ],
    },
    {
        "title": "Fitbit Inspire 3 Health Fitness Tracker",
        "price": "$79.95", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B09BKMFK7B?tag=followrefer20-20",
        "image": "", "category": "fitness", "asin": "B09BKMFK7B",
        "features": [
            "Tracks steps, calories, heart rate, sleep, and stress — all from your wrist",
            "Sleep score tells you whether you actually got quality rest, not just hours",
            "10-day battery life — charge it on Sunday, forget about it for a week",
            "Slim 0.35-inch profile — lighter and less bulky than most smartwatches",
            "Menstrual health tracking helps predict cycles and symptoms",
            "Water-resistant to 50 meters — wear it in the shower and pool",
        ],
    },
    {
        "title": "Amazon Basics Foam Roller for Exercise, 18 Inch",
        "price": "$20.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00XM2MRGI?tag=followrefer20-20",
        "image": "", "category": "fitness", "asin": "B00XM2MRGI",
        "features": [
            "18-inch length covers the full back, IT band, calves, and hamstrings",
            "Firm density provides real muscle pressure — not so soft it does nothing",
            "5 minutes of rolling after a workout noticeably reduces next-day soreness",
            "Doubles as a yoga prop and balance tool for core exercises",
            "Lightweight at 1.1 lbs — easy to take to the gym or pack for travel",
            "At this price, it's the most cost-effective recovery tool available",
        ],
    },

    # ── 개인용품 ──────────────────────────────────────────────
    {
        "title": "Native Deodorant, Natural Deodorant for Women and Men, 2.65 oz",
        "price": "$14.99", "rating": "4.4 out of 5 stars",
        "link": "https://www.amazon.com/dp/B01N7WHVS9?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B01N7WHVS9",
        "features": [
            "Aluminum-free formula keeps you odor-free for 24 hours without harsh chemicals",
            "Coconut oil and shea butter keep underarms soft — no irritation or dryness",
            "Goes on dry — no white marks on dark shirts",
            "Probiotic formula actually fights odor-causing bacteria instead of just masking it",
            "Tons of scents available — something for everyone",
            "Made in the USA with no parabens, sulfates, or silicone",
        ],
    },
    {
        "title": "Dove Body Wash Deep Moisture, 30.6 oz",
        "price": "$8.97", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B008DK8RUW?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B008DK8RUW",
        "features": [
            "NutriumMoisture technology deposits moisturizers onto skin while cleansing",
            "Skin feels noticeably softer after the very first shower",
            "Rich, creamy lather that rinses completely clean without a slippery residue",
            "30.6 oz bottle lasts 6–8 weeks with daily use",
            "No alcohol — safe for dry and sensitive skin types",
            "Replaces body wash and moisturizer in one step — saves time in the shower",
        ],
    },
    {
        "title": "Neutrogena Makeup Remover Wipes, 25 Count, 3 Pack",
        "price": "$17.99", "rating": "4.7 out of 5 stars",
        "link": "https://www.amazon.com/dp/B00BEEPFYE?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B00BEEPFYE",
        "features": [
            "Removes waterproof mascara and full-coverage foundation in one gentle wipe",
            "No harsh rubbing needed — effective enough to clean with a light swipe",
            "Alcohol-free formula doesn't sting eyes or irritate skin",
            "Individually sealed in a resealable pack — stays moist until the last wipe",
            "75 total wipes across 3 packs — enough for 2–3 months",
            "Convenient for travel, gym bag, or quick makeup fixes on the go",
        ],
    },
    {
        "title": "EOS Shea Better Body Lotion, Vanilla Cashmere, 16 fl oz",
        "price": "$12.99", "rating": "4.6 out of 5 stars",
        "link": "https://www.amazon.com/dp/B09KGXYVPQ?tag=followrefer20-20",
        "image": "", "category": "beauty", "asin": "B09KGXYVPQ",
        "features": [
            "Shea butter absorbs in 60 seconds — no sticky, greasy wait time",
            "Skin stays moisturized for 24 hours — still soft even the next morning",
            "Vanilla cashmere scent is warm and not overwhelming — compliment magnet",
            "Made with 95% naturally derived ingredients",
            "Large 16 oz pump bottle lasts 6–8 weeks with daily use",
            "#2 bestselling body lotion on Amazon — loved by millions of customers",
        ],
    },
]

CATEGORIES = [
    "kitchen", "beauty", "fitness", "home", "baby", "pet-supplies",
]

def pick_single(lang):
    """죽은 링크·이미 올린 상품은 건너뛰고 한 개 고르기."""
    candidates = STEADY_SELLERS[:]
    random.shuffle(candidates)
    if random.random() < 0.2:
        scraped = get_bestseller_products(random.choice(["beauty", "kitchen", "home"]), count=1)
        candidates = scraped + candidates
    for p in candidates[:10]:
        asin = p.get("asin", "")
        if asin and is_duplicate_asin(asin):
            continue
        status = check_asin(asin)
        p["_link_status"] = status
        print(f"  {p['title'][:45]} → link {status}")
        if status == DEAD:
            continue
        return p
    return None


def pick_guide():
    """같은 카테고리 3개로 비교 추천글."""
    by_cat = {}
    for p in STEADY_SELLERS:
        by_cat.setdefault(p["category"], []).append(p)
    cats = [c for c, ps in by_cat.items() if len(ps) >= 3]
    cat = random.choice(cats)
    pool = by_cat[cat][:]
    random.shuffle(pool)
    chosen = []
    for p in pool:
        status = check_asin(p.get("asin", ""))
        p["_link_status"] = status
        print(f"  {p['title'][:45]} → link {status}")
        if status != DEAD:
            chosen.append(p)
        if len(chosen) == 3:
            break
    return cat, chosen


def main():
    lang = os.environ.get("BLOG_LANG", "en")
    print(f"=== AutoBlog Start (lang={lang}) ===")

    wait = random.randint(0, 1800)
    print(f"Waiting {wait//60} minutes...")
    time.sleep(wait)

    post = None
    if random.random() < 0.3:
        cat, products = pick_guide()
        if len(products) >= 2:
            print(f"Today: {cat} buying guide ({len(products)} products)")
            post = generate_guide(products, cat, lang=lang)

    if post is None:
        product = pick_single(lang)
        if not product:
            print("No usable product found.")
            return
        print(f"Today: review — {product['title'][:50]}")
        if not product.get("reviews"):
            product["reviews"] = get_amazon_reviews(f"https://www.amazon.com/dp/{product.get('asin','')}")
        post = generate_post(product, lang=lang)

    result = post_to_wordpress(post, lang=lang)
    if result:
        print(f"  Published: {result.get('link', 'ok')}")
    print(f"\n=== AutoBlog Done (lang={lang}) ===")


if __name__ == "__main__":
    main()
