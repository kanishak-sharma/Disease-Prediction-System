"""Health knowledge shown next to each prediction.

General, widely-accepted wellness guidance only. It supports - never replaces - a doctor.

RULES: (input name, operator, value, level, message)
  level: "watch" = keep an eye on it, "see" = book a doctor visit, "urgent" = get care promptly.
"""

LEVEL_ORDER = {"watch": 0, "see": 1, "urgent": 2}
LEVEL_LABEL = {"watch": "Keep an eye on it", "see": "See a doctor soon", "urgent": "Get medical care promptly"}

KNOWLEDGE = {
    "diabetes": dict(
        about="Diabetes means the body cannot keep blood sugar in a healthy range, either because it makes too little insulin or cannot use it well. Left uncontrolled it damages eyes, kidneys, nerves and the heart, but early detection and lifestyle change can prevent or delay most complications.",
        risk_factors=["Overweight, especially around the waist", "Family history of diabetes", "Age 45 or more", "Little physical activity", "High blood pressure", "Diabetes during a past pregnancy"],
        remedies={
            "low": ["Keep a healthy weight and stay active: 150 minutes of brisk walking a week.", "Choose whole grains, pulses and vegetables over refined flour and sugary drinks.", "Get fasting blood sugar checked once a year after age 35."],
            "moderate": ["Walk for 20-30 minutes after your largest meal. It lowers the blood-sugar rise.", "Cut sugary drinks, sweets and white bread. Swap in oats, millets, brown rice, dal and green vegetables.", "Eat on a regular schedule and avoid very large dinners.", "Fenugreek (methi) seeds soaked overnight, cinnamon and bitter gourd (karela) are traditional aids. Evidence is modest, so use them as extras and not as medicine.", "Aim to lose 5-7% of body weight if overweight. This alone cuts diabetes risk by more than half in studies.", "Sleep 7-8 hours. Poor sleep raises blood sugar."],
            "high": ["Book a blood test now (fasting glucose, HbA1c). Do not wait for symptoms.", "Until you are seen: avoid sweets and sugary drinks, drink plenty of water and keep meals small and regular.", "Daily 30-minute walk, unless a doctor advises against it.", "Do not start or stop any diabetes medicine or herbal product without your doctor.", "Check your feet daily for cuts or sores, and keep your skin moisturised."],
        },
        red_flags=["Extreme thirst and passing urine very often", "Unexplained weight loss", "Blurred vision", "Cuts or sores that will not heal", "Fruity-smelling breath, vomiting, drowsiness or confusion (emergency)"],
        tests=["HbA1c", "Fasting plasma glucose", "Oral glucose tolerance test", "Lipid profile", "Kidney function and urine albumin"],
        rules=[
            ("Glucose", ">=", 140, "see", "2-hour glucose of 140 or more is above normal (prediabetes range). 200 or more is in the diabetes range."),
            ("Glucose", ">=", 200, "urgent", "2-hour glucose of 200 or more is in the diabetes range. Please see a doctor this week."),
            ("BMI", ">=", 25, "watch", "BMI of 25 or more is overweight. Losing even a little weight lowers diabetes risk."),
            ("BMI", ">=", 30, "see", "BMI of 30 or more is obese and raises diabetes risk a lot."),
            ("BloodPressure", ">=", 90, "see", "Diastolic pressure of 90 or more suggests high blood pressure."),
            ("BloodPressure", ">=", 120, "urgent", "Diastolic pressure of 120 or more is a hypertensive crisis. Seek care today."),
            ("Insulin", ">", 166, "see", "Insulin above 166 µU/mL suggests the body is resisting insulin."),
            ("DiabetesPedigreeFunction", ">=", 0.8, "watch", "Strong family history of diabetes. Check your sugar every year."),
            ("Age", ">=", 45, "watch", "Screening every 1-3 years is recommended from age 45."),
        ],
    ),
    "heart": dict(
        about="Heart disease usually means the arteries that feed the heart are narrowed by fatty deposits, which can cause chest pain and heart attacks. It builds silently for years, so blood pressure, cholesterol and stress-test results give early warning.",
        risk_factors=["High blood pressure", "High LDL ('bad') cholesterol", "Smoking and tobacco", "Diabetes", "Family history of early heart disease", "Obesity and little exercise", "Chronic stress and poor sleep"],
        remedies={
            "low": ["Keep moving: 30 minutes of brisk activity on most days.", "Eat more vegetables, fruit, nuts, pulses and fish. Limit fried food and packaged snacks.", "Check blood pressure and cholesterol once a year after age 30."],
            "moderate": ["Cut salt: aim for under 5 g a day (about one teaspoon). Avoid pickles, papad and packaged snacks.", "Swap saturated fat (ghee, butter, palm oil) for olive, mustard or groundnut oil in small amounts.", "Add oats, flaxseed, garlic, nuts (a handful of almonds or walnuts) and plenty of green vegetables.", "Walk briskly for 30 minutes daily, and build up slowly.", "Stop smoking. Heart attack risk drops by half within a year of quitting.", "Practise 10 minutes of slow breathing or meditation daily to bring blood pressure down."],
            "high": ["Book a cardiology or general physician visit this week. A heart check includes an ECG, lipid profile and often a treadmill test.", "Avoid heavy exertion until you have been checked.", "Stop smoking and alcohol. Eat a low-salt, low-fat diet.", "Keep a log of any chest discomfort: when it happens, how long it lasts, and what you were doing.", "Do not take heart medicines or aspirin on your own without a doctor's advice."],
        },
        red_flags=["Chest pain, pressure or tightness lasting more than a few minutes", "Pain spreading to the arm, jaw, neck or back", "Breathlessness at rest, cold sweat or nausea", "Fainting or a racing, irregular heartbeat", "Any of these is an emergency: call your local emergency number now"],
        tests=["ECG", "Treadmill stress test (TMT) or echocardiogram", "Lipid profile", "Blood pressure monitoring", "HbA1c / fasting glucose"],
        rules=[
            ("trestbps", ">=", 130, "watch", "Systolic blood pressure of 130 or more is above the ideal range."),
            ("trestbps", ">=", 140, "see", "Systolic pressure of 140 or more is high blood pressure (hypertension)."),
            ("trestbps", ">=", 180, "urgent", "Systolic pressure of 180 or more is dangerously high. Seek care today."),
            ("chol", ">=", 200, "watch", "Cholesterol of 200 or more is borderline high."),
            ("chol", ">=", 240, "see", "Cholesterol of 240 or more is high. Ask about a lipid profile and treatment."),
            ("fbs", ">=", 1, "see", "Fasting blood sugar above 120 mg/dL can point to diabetes, which strongly raises heart risk."),
            ("exang", ">=", 1, "see", "Chest pain during exercise (angina) needs a medical check."),
            ("cp", "==", 0, "watch", "In this dataset, people with confirmed heart disease most often reported no typical chest pain, so a quiet heart can still be at risk."),
            ("cp", "==", 3, "see", "Typical angina (pressure-like chest pain with effort) needs a medical check."),
            ("oldpeak", ">=", 2, "see", "ST depression of 2 mm or more after exercise suggests the heart is short of blood supply under stress."),
            ("ca", ">=", 1, "see", "One or more blocked major vessels was found on imaging."),
            ("thal", "==", 3, "see", "A reversible defect on the thallium test means part of the heart gets too little blood during exercise."),
            ("restecg", ">=", 1, "watch", "The resting ECG is not fully normal."),
        ],
    ),
    "parkinsons": dict(
        about="Parkinson's disease is a slowly progressing condition in which brain cells that make dopamine are lost. It first shows up as tremor, stiffness and slow movement. It cannot be cured, but medicines, exercise and therapy keep people independent for many years, and early diagnosis helps.",
        risk_factors=["Age above 60", "Family history", "Past serious head injury", "Long exposure to pesticides or industrial chemicals", "Being male (slightly higher risk)"],
        remedies={
            "low": ["Stay physically active: walking, cycling, yoga and dancing all help balance and brain health.", "Challenge your brain: read, learn, do puzzles and stay social.", "Wear a helmet and protect against head injuries."],
            "moderate": ["Exercise 30 minutes most days. Tai chi, yoga, cycling and brisk walking improve balance and flexibility.", "Eat plenty of vegetables, fruit, berries and nuts, and drink enough water. Fibre and fluids ease constipation.", "Sleep at a regular time and keep the bedroom dark and cool.", "Do not self-treat. Arrange a neurologist review if the movement symptoms are new or getting worse."],
            "high": ["See a neurologist (ideally one who treats movement disorders) for a proper examination. Only a clinical exam can confirm Parkinson's.", "Bring a list of symptoms, when each began, and a short phone video of any tremor or walking changes.", "Supportive steps while you wait: daily gentle exercise, balance practice by a wall or chair, speech exercises such as reading aloud with a strong voice, and a fall-proofed home (no loose rugs, good lighting).", "Eat high-fibre meals and drink fluids for constipation. Take protein away from medicine times if you are later prescribed levodopa, as your doctor will advise.", "There are no home remedies that treat Parkinson's. Supportive habits help but must go along with medical care."],
        },
        red_flags=["Falls or repeated near-falls", "Trouble swallowing or choking while eating", "Sudden confusion or hallucinations", "Rapidly worsening stiffness or inability to move"],
        tests=["Neurological examination", "Brain MRI to rule out other causes", "DaT scan (in selected cases)", "Cognitive screening (MoCA)", "Review of current medicines"],
        rules=[
            ("Age", ">=", 60, "watch", "Parkinson's becomes more common after age 60."),
            ("UPDRS", ">=", 40, "see", "A motor-score (UPDRS) above 40 suggests noticeable movement difficulty."),
            ("MoCA", "<", 26, "see", "A MoCA score under 26 suggests a thinking or memory problem worth checking."),
            ("FunctionalAssessment", "<", 5, "see", "Daily functioning is clearly reduced. A doctor can look for the cause."),
            ("Tremor", ">=", 1, "see", "A tremor at rest is a typical early sign and should be checked."),
            ("Rigidity", ">=", 1, "see", "Stiff muscles that do not loosen up should be checked."),
            ("Bradykinesia", ">=", 1, "see", "Slowness of movement is the central feature of Parkinson's and should be checked."),
            ("PosturalInstability", ">=", 1, "urgent", "Balance problems raise the risk of falls. Seek a neurological review soon."),
            ("SpeechProblems", ">=", 1, "watch", "A soft or slurred voice can be an early sign."),
            ("FamilyHistoryParkinsons", ">=", 1, "watch", "Family history raises risk slightly. It is not a diagnosis."),
            ("SleepQuality", "<", 4, "watch", "Poor sleep affects health and can also be an early non-motor symptom."),
        ],
    ),
    "breast": dict(
        about="This check looks at the shape and size of cells taken from a breast lump with a fine needle. Cells that are bigger, more irregular and with more notches tend to be malignant (cancerous). Most breast lumps are benign, and early detection makes breast cancer highly treatable.",
        risk_factors=["Age above 40", "Family history of breast or ovarian cancer (BRCA gene changes)", "Having no or late pregnancies / not breastfeeding", "Obesity after menopause", "Alcohol and tobacco", "Long-term hormone therapy"],
        remedies={
            "low": ["Do a monthly breast self-check and see a doctor for any new lump or change.", "Keep a healthy weight, exercise regularly and limit alcohol.", "Women over 40 should discuss yearly mammograms with their doctor."],
            "moderate": ["Have the report reviewed by a doctor even though risk looks lower. A model cannot replace a pathologist.", "Healthy habits support recovery and prevention: plant-rich diet, regular exercise, no tobacco, little or no alcohol.", "Keep a note of the lump's size and whether it changes over weeks."],
            "high": ["Please see a breast specialist or oncologist promptly. Early treatment makes the biggest difference.", "Ask about a core biopsy, ultrasound or mammogram, and about hormone-receptor testing.", "Bring all reports and imaging. Consider taking someone you trust to appointments.", "While you wait, eat well, rest, and stay gently active. A balanced diet and light exercise help you cope with treatment.", "No home remedy treats or cures cancer. Avoid anyone who claims otherwise and do not delay medical care for herbal treatments."],
        },
        red_flags=["A new hard, painless lump in the breast or armpit", "Change in breast size or shape", "Skin dimpling, redness or an orange-peel texture", "Nipple turning inward or bloody nipple discharge", "Persistent breast or nipple pain"],
        tests=["Clinical breast examination", "Ultrasound / mammography", "Core-needle biopsy", "Hormone-receptor and HER2 testing (if malignant)"],
        rules=[
            ("mean_radius", ">=", 15, "see", "Average cell radius of 15 or more is larger than usual benign cells."),
            ("mean_concave_points", ">=", 0.05, "see", "Many concave points (a notched outline) is typical of malignant cells."),
            ("worst_radius", ">=", 17, "see", "A very large worst-case cell radius is a warning sign."),
            ("worst_concave_points", ">=", 0.13, "see", "A high worst-case concave-points value is typical of malignant cells."),
            ("mean_concavity", ">=", 0.1, "watch", "Higher concavity means the cell outline is more irregular."),
        ],
    ),
    "kidney": dict(
        about="Chronic kidney disease (CKD) is a slow, long-term loss of kidney function. Kidneys clean the blood and balance salts and water. CKD often has no symptoms until it is advanced, so blood and urine tests are the only early warning. Catching it early can slow or stop its progress.",
        risk_factors=["Diabetes", "High blood pressure", "Family history of kidney disease", "Age above 60", "Long-term painkiller (NSAID) use", "Obesity and smoking", "Past kidney stones or repeated infections"],
        remedies={
            "low": ["Drink enough water through the day (pale-yellow urine is a good guide).", "Keep blood pressure and blood sugar in the healthy range.", "Avoid long-term use of painkillers such as ibuprofen or diclofenac without advice."],
            "moderate": ["Reduce salt (under 5 g a day) and processed food.", "Drink water regularly unless your doctor limits fluids.", "Avoid regular painkillers (NSAIDs) and unregulated herbal or 'kidney-cleanse' products.", "Control blood pressure and blood sugar. These are the two biggest protectors of your kidneys.", "Ask your doctor for a creatinine and eGFR test plus urine albumin check once a year."],
            "high": ["See a doctor or nephrologist soon for kidney function tests (eGFR) and a urine test.", "Until then, avoid NSAID painkillers, herbal supplements and high-protein supplements.", "Cut salt, and ask the doctor whether you should limit potassium foods (banana, coconut water, potato, tomato) and phosphorus (colas, processed foods).", "Check your blood pressure at home and write the numbers down.", "Do not restrict fluids or follow a dialysis diet on your own. The right plan depends on your tests."],
        },
        red_flags=["Much less urine than usual, or none", "Swelling of feet, ankles or face", "Shortness of breath", "Persistent nausea, vomiting or loss of appetite", "Confusion, muscle cramps or a very slow heartbeat (can mean high potassium - emergency)"],
        tests=["Serum creatinine and eGFR", "Urine albumin-to-creatinine ratio", "Ultrasound of the kidneys", "Electrolytes (sodium, potassium)", "Complete blood count"],
        rules=[
            ("sc", ">", 1.3, "see", "Creatinine above 1.3 mg/dL suggests the kidneys are not filtering as well as they should."),
            ("sc", ">=", 5, "urgent", "Creatinine of 5 mg/dL or more suggests severe kidney failure. Seek care today."),
            ("bu", ">", 20, "see", "Blood urea above 20 mg/dL is high."),
            ("hemo", "<", 12, "see", "Haemoglobin under 12 g/dL (anaemia) is common in kidney disease."),
            ("pot", ">", 5.1, "see", "High potassium can affect the heart rhythm."),
            ("pot", ">=", 6, "urgent", "Potassium of 6 or more is dangerous for the heart. Seek care now."),
            ("pot", "<", 3.5, "see", "Low potassium should be checked."),
            ("sod", "<", 135, "see", "Low sodium should be checked."),
            ("bp", ">=", 90, "see", "Diastolic pressure of 90 or more can both cause and result from kidney disease."),
            ("al", ">=", 1, "see", "Protein (albumin) in the urine is the earliest sign of kidney damage."),
            ("su", ">=", 1, "watch", "Sugar in the urine can mean diabetes, a leading cause of kidney disease."),
            ("bgr", ">=", 200, "see", "Random blood glucose of 200 or more suggests diabetes."),
            ("pe", ">=", 1, "see", "Swollen feet can be a sign that the kidneys are holding on to fluid."),
            ("htn", ">=", 1, "watch", "Blood pressure control protects the kidneys."),
            ("dm", ">=", 1, "watch", "With diabetes, have your kidneys checked every year."),
        ],
    ),
    "liver": dict(
        about="The liver filters the blood, makes proteins and bile, and stores energy. Liver disease (fatty liver, hepatitis, cirrhosis) often causes no symptoms early on, and blood tests of liver enzymes are the first clue. Many liver problems, especially fatty liver, can be reversed with lifestyle changes.",
        risk_factors=["Heavy alcohol use", "Obesity and fatty liver", "Hepatitis B or C infection", "Diabetes", "Some medicines and herbal products", "Family history"],
        remedies={
            "low": ["Keep alcohol low or avoid it altogether.", "Maintain a healthy weight and exercise regularly.", "Get vaccinated against hepatitis B (and A) if you have not been."],
            "moderate": ["Avoid alcohol until your liver tests are reviewed.", "Cut fried, sugary and ultra-processed food. A Mediterranean-style diet helps fatty liver.", "Drink coffee in moderation (2-3 cups): studies link it to lower liver-scarring risk.", "Lose 5-10% of body weight if overweight. This can reverse fatty liver.", "Check with your doctor before using painkillers (paracetamol in high doses harms the liver) or herbal supplements."],
            "high": ["See a doctor soon for a full liver panel, and ask about an ultrasound and hepatitis B and C tests.", "Stop all alcohol. Do not take supplements, 'liver tonics' or painkillers unless a doctor approves.", "Eat small, regular, low-fat, moderate-salt meals with plenty of vegetables and fruit.", "Drink clean boiled or filtered water and avoid raw street food (hepatitis A and E come from contaminated food and water).", "Do not rely on herbal liver remedies (such as turmeric or milk-thistle products) as treatment. Some supplements can themselves injure the liver."],
        },
        red_flags=["Yellowing of the skin or eyes (jaundice)", "Dark urine and pale stools", "Swelling of the belly or legs", "Vomiting blood or black stools (emergency)", "Severe tiredness, itching or confusion"],
        tests=["Liver function tests (ALT, AST, ALP, bilirubin, albumin)", "Liver ultrasound", "Hepatitis B and C screening", "FibroScan (liver stiffness)", "Blood sugar and lipid profile"],
        rules=[
            ("Total_Bilirubin", ">", 1.2, "see", "Total bilirubin above 1.2 mg/dL is high and can cause jaundice."),
            ("Total_Bilirubin", ">=", 3, "urgent", "Bilirubin of 3 or more usually shows visible jaundice. See a doctor promptly."),
            ("Direct_Bilirubin", ">", 0.3, "see", "Direct bilirubin above 0.3 mg/dL is high."),
            ("Alamine_Aminotransferase", ">", 56, "see", "ALT above 56 IU/L suggests liver-cell injury."),
            ("Alamine_Aminotransferase", ">=", 200, "urgent", "ALT 200 or more is a marked rise. See a doctor within days."),
            ("Aspartate_Aminotransferase", ">", 40, "see", "AST above 40 IU/L suggests liver-cell injury."),
            ("Alkaline_Phosphotase", ">", 147, "watch", "ALP above 147 IU/L can point to bile-duct or bone problems."),
            ("Albumin", "<", 3.5, "see", "Albumin under 3.5 g/dL means the liver may be making too little protein."),
            ("Albumin_and_Globulin_Ratio", "<", 1.0, "watch", "A low albumin/globulin ratio can reflect chronic liver disease."),
        ],
    ),
}

GENERAL_TIPS = [
    ("Move daily", "30 minutes of brisk walking lowers the risk of diabetes, heart, kidney and liver disease."),
    ("Eat colourful", "Half your plate vegetables and fruit, plus pulses, whole grains and nuts."),
    ("Sleep 7-8 hours", "Poor sleep raises blood pressure, blood sugar and weight."),
    ("Drink water", "Enough fluids help the kidneys and the whole body."),
    ("No tobacco, little alcohol", "The two biggest avoidable risks for heart, liver and cancer."),
    ("Get yearly check-ups", "Blood pressure, sugar, cholesterol, kidney and liver tests catch silent problems early."),
]

DISCLAIMER = ("This tool is a student machine-learning project for education and awareness. It is **not** a medical device "
              "and does not give a diagnosis. Always consult a qualified doctor about your health. In an emergency, "
              "call your local emergency number.")

_OPS = {
    ">=": lambda a, b: a >= b, ">": lambda a, b: a > b, "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b, "==": lambda a, b: a == b,
}


def flagged(key: str, values: dict) -> list[dict]:
    """Rules triggered by these inputs, most serious first. For the same input only the
    most serious triggered rule is kept (so 200+ glucose does not also show the 140+ message)."""
    best: dict[str, tuple] = {}
    for feat, op, thr, level, msg in KNOWLEDGE[key]["rules"]:
        if feat in values and _OPS[op](float(values[feat]), thr):
            cur = best.get(feat)
            if cur is None or LEVEL_ORDER[level] >= LEVEL_ORDER[cur[0]]:
                best[feat] = (level, msg)
    out = [dict(feature=f, level=l, message=m) for f, (l, m) in best.items()]
    return sorted(out, key=lambda r: -LEVEL_ORDER[r["level"]])


def overall_advice_level(flags: list[dict], prob: float) -> str:
    worst = max((LEVEL_ORDER[f["level"]] for f in flags), default=-1)
    if worst == 2:
        return "urgent"
    if worst == 1 or prob >= 0.66:
        return "see"
    if worst == 0 or prob >= 0.33:
        return "watch"
    return "ok"
