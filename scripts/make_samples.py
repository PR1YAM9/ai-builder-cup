"""Generate synthetic claim documents (invoices, receipts, reports) for the demo.

Run: python scripts/make_samples.py   -> writes PNGs + samples.json into samples/
All names, companies and numbers are fictional.
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "samples"
OUT.mkdir(exist_ok=True)
FONT_DIR = Path("C:/Windows/Fonts")


def font(size, bold=False):
    for name in (["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(str(FONT_DIR / name), size)
        except OSError:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
    return ImageFont.load_default()


def document(filename, header, sub, meta, lines, totals, footer, accent=(29, 78, 216)):
    W, H = 900, 1150
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 120], fill=accent)
    d.text((40, 28), header, font=font(34, True), fill="white")
    d.text((40, 76), sub, font=font(16), fill=(220, 230, 255))
    y = 150
    for k, v in meta:
        d.text((40, y), k, font=font(16, True), fill=(60, 60, 60))
        d.text((260, y), v, font=font(16), fill=(20, 20, 20))
        y += 30
    y += 20
    if lines:
        d.rectangle([40, y, W - 40, y + 36], fill=(241, 245, 249))
        d.text((52, y + 8), "Description", font=font(16, True), fill="black")
        d.text((560, y + 8), "Qty", font=font(16, True), fill="black")
        d.text((720, y + 8), "Amount", font=font(16, True), fill="black")
        y += 48
        for desc, qty, amt in lines:
            d.text((52, y), desc, font=font(16), fill="black")
            d.text((560, y), str(qty), font=font(16), fill="black")
            d.text((720, y), amt, font=font(16), fill="black")
            y += 32
            d.line([40, y - 6, W - 40, y - 6], fill=(226, 232, 240))
        y += 16
    for k, v in totals:
        d.text((520, y), k, font=font(18, True), fill="black")
        d.text((720, y), v, font=font(18, True), fill="black")
        y += 34
    y += 30
    for para in footer:
        d.text((40, y), para, font=font(15), fill=(70, 70, 70))
        y += 26
    img.save(OUT / filename)


# ---- Sample 1: legitimate rear-end collision ---------------------------------
document(
    "s1_repair_invoice.png", "Northgate Auto Body", "Collision Repair Specialists · 412 Mill Rd, Springfield · GST 29ABCDE1234F1Z5",
    [("Invoice #", "NAB-20931"), ("Invoice date", "2026-10-09"), ("Customer", "Ananya Rao"),
     ("Vehicle", "2020 Toyota Corolla, Silver · KA-05-MN-4421"), ("Damage", "Rear bumper & tail lamp (rear-end impact)")],
    [("Rear bumper cover (OEM)", 1, "$640.00"), ("Right tail lamp assembly", 1, "$310.00"),
     ("Bumper reinforcement bar", 1, "$280.00"), ("Paint & blending, rear panel", 1, "$520.00"),
     ("Labour - 6.5 hrs @ $90", 1, "$585.00")],
    [("Subtotal", "$2,335.00"), ("Tax", "$0.00"), ("TOTAL", "$2,335.00")],
    ["Work completed 2026-10-09. Payment due on insurer approval.", "Thank you for choosing Northgate Auto Body."],
)
document(
    "s1_police_report.png", "Springfield Police Dept.", "Traffic Incident Report · Non-injury",
    [("Report #", "SPD-TR-2026-118842"), ("Date / time", "2026-10-06, 18:40"), ("Location", "Elm St & 5th Ave signal"),
     ("Vehicle 1", "2020 Toyota Corolla, KA-05-MN-4421 (A. Rao) - stationary at red"),
     ("Vehicle 2", "2017 Mahindra Scorpio, KA-03-HJ-9902 (R. Menon)"), ("Officer", "Sgt. P. Kulkarni #4471")],
    [], [],
    ["Narrative: Vehicle 2 failed to stop and struck the rear of Vehicle 1 while it", "was waiting at a red signal. Rear bumper and right tail lamp of V1 damaged.",
     "Driver of V2 admitted fault at scene. No injuries reported.", "", "Signed: Sgt. P. Kulkarni"],
    accent=(30, 41, 59),
)

# ---- Sample 5: photo shows a different make than the paperwork ---------------------------------
document(
    "s5_repair_invoice.png", "Northgate Auto Body", "Collision Repair Specialists · 412 Mill Rd, Springfield · GST 29ABCDE1234F1Z5",
    [("Invoice #", "NAB-20977"), ("Invoice date", "2026-10-09"), ("Customer", "Arjun Nair"),
     ("Vehicle", "2021 Honda City, Silver · KA-05-MN-4421"), ("Damage", "Rear bumper & tail lamp (rear-end impact)")],
    [("Rear bumper cover (OEM)", 1, "$640.00"), ("Right tail lamp assembly", 1, "$310.00"),
     ("Bumper reinforcement bar", 1, "$280.00"), ("Paint & blending, rear panel", 1, "$520.00"),
     ("Labour - 6.5 hrs @ $90", 1, "$585.00")],
    [("Subtotal", "$2,335.00"), ("Tax", "$0.00"), ("TOTAL", "$2,335.00")],
    ["Work completed 2026-10-09. Payment due on insurer approval.", "Thank you for choosing Northgate Auto Body."],
)
document(
    "s5_police_report.png", "Springfield Police Dept.", "Traffic Incident Report · Non-injury",
    [("Report #", "SPD-TR-2026-119015"), ("Date / time", "2026-10-06, 18:40"), ("Location", "Elm St & 5th Ave signal"),
     ("Vehicle 1", "2021 Honda City, KA-05-MN-4421 (A. Nair) - stationary at red"),
     ("Vehicle 2", "2017 Toyota Innova, KA-03-HJ-9902 (R. Menon)"), ("Officer", "Sgt. P. Kulkarni #4471")],
    [], [],
    ["Narrative: Vehicle 2 failed to stop and struck the rear of Vehicle 1 while it", "was waiting at a red signal. Rear bumper and right tail lamp of V1 damaged.",
     "Driver of V2 admitted fault at scene. No injuries reported.", "", "Signed: Sgt. P. Kulkarni"],
    accent=(30, 41, 59),
)

# ---- Sample 2: inflated / mismatched invoice ---------------------------------
document(
    "s2_repair_invoice.png", "QuickFix Motors", "Auto repairs · Cash & card accepted",
    [("Invoice #", "QF-1187"), ("Invoice date", "2026-09-28"), ("Customer", "Vikram Shah"),
     ("Vehicle", "2019 Hyundai Creta, White"), ("Work", "Accident repair")],
    [("Front bumper replacement", 1, "$900.00"), ("Hood panel", 1, "$1,150.00"),
     ("Headlamp assembly pair (L+R)", 1, "$1,400.00"), ("Radiator", 1, "$700.00"),
     ("Labour", 1, "$600.00")],
    [("Subtotal", "$4,750.00"), ("Tax", "$0.00"), ("TOTAL", "$9,000.00")],
    ["Paid in full - cash.", ""],
    accent=(180, 83, 9),
)
document(
    "s2_estimate.png", "QuickFix Motors", "Repair estimate",
    [("Estimate #", "QF-E-1187"), ("Date", "2026-10-03"), ("Customer", "Vikram Shah"),
     ("Vehicle", "2019 Hyundai Creta, White")],
    [("Rear bumper cover", 1, "$700.00"), ("Rear quarter panel dent repair", 1, "$450.00"), ("Paint", 1, "$400.00")],
    [("ESTIMATE TOTAL", "$1,550.00")],
    ["Estimate valid for 15 days."],
    accent=(180, 83, 9),
)

# ---- Sample 3: new policy + stolen phone, receipt after incident -------------
document(
    "s3_purchase_receipt.png", "TechWorld Electronics", "Store #118 · Phoenix Mall",
    [("Receipt #", "TW-118-55602"), ("Date", "2026-10-02 14:12"), ("Cashier", "M. Iyer"), ("Payment", "Cash")],
    [("Smartphone Pro Max 1TB - Titanium", 1, "$1,599.00"), ("Screen protector", 1, "$25.00")],
    [("TOTAL", "$1,624.00")],
    ["IMEI: 35-209900-176148-1", "Returns within 7 days with receipt."],
    accent=(88, 28, 135),
)
document(
    "s3_fir_copy.png", "City Police - Lost Property", "Complaint acknowledgement (online)",
    [("Complaint #", "LP-2026-77120"), ("Filed on", "2026-10-15"), ("Item", "Mobile phone"),
     ("Reported loss date", "2026-09-30"), ("Location", "Metro Line 2, between stations")],
    [], [],
    ["Complainant states phone was misplaced/lost while commuting.", "This is an acknowledgement of an online complaint, not a verified FIR."],
    accent=(30, 41, 59),
)

# ---- Sample 4: home water damage, late report --------------------------------
document(
    "s4_plumber_invoice.png", "BlueLine Plumbing & Restoration", "Licensed contractor #PL-55821",
    [("Invoice #", "BL-3390"), ("Invoice date", "2026-06-30"), ("Customer", "Meera Joseph"),
     ("Property", "Flat 7B, Lakeview Apartments"), ("Cause", "Burst flexible hose under kitchen sink")],
    [("Emergency call-out", 1, "$150.00"), ("Hose & valve replacement", 1, "$85.00"),
     ("Water extraction & drying (3 days)", 1, "$1,200.00"), ("Kitchen cabinet base replacement", 1, "$1,450.00"),
     ("Laminate flooring 22 sq m", 1, "$1,615.00")],
    [("Subtotal", "$4,500.00"), ("Tax", "$0.00"), ("TOTAL", "$4,500.00")],
    ["Work dates: 2026-06-27 to 2026-06-30.", "Moisture readings normal on completion."],
    accent=(3, 105, 161),
)

samples = [
    {
        "label": "1 · Rear-end collision (clean)",
        "fields": {"claimant_name": "Ananya Rao", "claim_type": "auto", "claimed_amount": 2335,
                   "coverage_limit": 15000, "incident_date": "2026-10-06", "policy_start": "2024-03-01",
                   "prior_claims": 0, "date_filed": "2026-10-10",
                   "description": "On 6 Oct around 6:40pm I was stopped at the red light at Elm St & 5th Ave when a Mahindra Scorpio hit the back of my Corolla. Rear bumper and right tail light are broken. The other driver admitted fault and police came to the spot. Got it repaired at Northgate Auto Body."},
        "files": ["s1_damage_rear.jpg", "s1_repair_invoice.png", "s1_police_report.png"],
    },
    {
        "label": "2 · Inflated repair invoice",
        "fields": {"claimant_name": "Vikram Shah", "claim_type": "auto", "claimed_amount": 9000,
                   "coverage_limit": 10000, "incident_date": "2026-10-01", "policy_start": "2025-11-20",
                   "prior_claims": 1, "date_filed": "2026-10-12",
                   "description": "Someone reversed into my car in a parking lot on 1 October and damaged the back of the car. They drove off. I had it fixed at QuickFix Motors and paid cash. Claiming the full repair cost."},
        "files": ["s2_damage_front.jpg", "s2_repair_invoice.png", "s2_estimate.png"],
    },
    {
        "label": "3 · Lost phone, brand-new policy",
        "fields": {"claimant_name": "Rohit Malhotra", "claim_type": "electronics", "claimed_amount": 1600,
                   "coverage_limit": 1600, "incident_date": "2026-10-04", "policy_start": "2026-09-24",
                   "prior_claims": 3, "date_filed": "2026-10-16",
                   "description": "My phone was stolen from my bag at a cafe on 4 October. I had bought it recently. I filed a police complaint. Please reimburse the full value."},
        "files": ["s3_purchase_receipt.png", "s3_fir_copy.png"],
    },
    {
        "label": "4 · Kitchen water damage (late)",
        "fields": {"claimant_name": "Meera Joseph", "claim_type": "property", "claimed_amount": 4500,
                   "coverage_limit": 25000, "incident_date": "2026-06-27", "policy_start": "2023-01-15",
                   "prior_claims": 0, "date_filed": "2026-10-14",
                   "description": "A flexible hose under the kitchen sink burst overnight on 27 June and flooded the kitchen. A plumber fixed it and dried everything out; cabinets and flooring had to be replaced. I was travelling for work after that so I'm only filing now."},
        "files": ["s4_kitchen_water.jpg", "s4_plumber_invoice.png"],
    },
    {
        "label": "5 · Photo of a different car",
        "fields": {"claimant_name": "Arjun Nair", "claim_type": "auto", "claimed_amount": 2335,
                   "coverage_limit": 15000, "incident_date": "2026-10-06", "policy_start": "2024-03-01",
                   "prior_claims": 0, "date_filed": "2026-10-10",
                   "description": "On 6 Oct around 6:40pm I was stopped at the red light at Elm St & 5th Ave when an SUV hit the back of my Honda City. Rear bumper and right tail light are broken. The other driver admitted fault and police came to the spot. Got it repaired at Northgate Auto Body."},
        "files": ["s1_damage_rear.jpg", "s5_repair_invoice.png", "s5_police_report.png"],
    },
]
(OUT / "samples.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote", len(samples), "samples to", OUT)
