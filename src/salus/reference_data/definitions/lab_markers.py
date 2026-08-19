"""Code-defined lab marker reference — single source of truth.

Each entry carries the marker's identity (shared with the metric system) plus
the lab-specific metadata: category and reference/optimal ranges. The metric
definitions in `metric_type_mapping.py` are derived from this list.
"""

LAB_MARKERS: list[dict] = [
    # Lipid panel
    {"code": "total_cholesterol", "name": "Total Cholesterol", "unit": "mg/dL", "category": "lipid", "reference_low": None, "reference_high": 200.0, "optimal_low": None, "optimal_high": 180.0, "description": "Gesamtcholesterin im Blut.", "sort_order": 200},
    {"code": "hdl_cholesterol", "name": "HDL Cholesterol", "unit": "mg/dL", "category": "lipid", "reference_low": 40.0, "reference_high": None, "optimal_low": 60.0, "optimal_high": None, "description": "„Gutes“ Cholesterin.", "sort_order": 201},
    {"code": "ldl_cholesterol", "name": "LDL Cholesterol", "unit": "mg/dL", "category": "lipid", "reference_low": None, "reference_high": 130.0, "optimal_low": None, "optimal_high": 100.0, "description": "„Schlechtes“ Cholesterin.", "sort_order": 202},
    {"code": "triglycerides", "name": "Triglycerides", "unit": "mg/dL", "category": "lipid", "reference_low": None, "reference_high": 150.0, "optimal_low": None, "optimal_high": 100.0, "description": "Neutralfette im Blut.", "sort_order": 203},
    {"code": "non_hdl_cholesterol", "name": "Non-HDL Cholesterol", "unit": "mg/dL", "category": "lipid", "reference_low": None, "reference_high": 160.0, "optimal_low": None, "optimal_high": 130.0, "description": "Gesamtcholesterin minus HDL.", "sort_order": 204},

    # Complete blood count (CBC)
    {"code": "wbc", "name": "White Blood Cells", "unit": "10³/µL", "category": "cbc", "reference_low": 4.0, "reference_high": 11.0, "optimal_low": 4.5, "optimal_high": 10.0, "description": "Leukozyten.", "sort_order": 210},
    {"code": "rbc", "name": "Red Blood Cells", "unit": "10⁶/µL", "category": "cbc", "reference_low": 4.5, "reference_high": 5.9, "optimal_low": 4.7, "optimal_high": 5.7, "description": "Erythrozyten.", "sort_order": 211},
    {"code": "hemoglobin", "name": "Hemoglobin", "unit": "g/dL", "category": "cbc", "reference_low": 13.5, "reference_high": 17.5, "optimal_low": 14.0, "optimal_high": 17.0, "description": "Hämoglobin (Sauerstofftransport).", "sort_order": 212},
    {"code": "hematocrit", "name": "Hematocrit", "unit": "%", "category": "cbc", "reference_low": 40.0, "reference_high": 50.0, "optimal_low": 41.0, "optimal_high": 49.0, "description": "Anteil roter Blutkörperchen.", "sort_order": 213},
    {"code": "mcv", "name": "MCV", "unit": "fL", "category": "cbc", "reference_low": 80.0, "reference_high": 100.0, "optimal_low": 82.0, "optimal_high": 98.0, "description": "Mittleres Erythrozytenvolumen.", "sort_order": 214},
    {"code": "mch", "name": "MCH", "unit": "pg", "category": "cbc", "reference_low": 27.0, "reference_high": 33.0, "optimal_low": 28.0, "optimal_high": 32.0, "description": "Mittleres Hämoglobin pro Erythrozyt.", "sort_order": 215},
    {"code": "mchc", "name": "MCHC", "unit": "g/dL", "category": "cbc", "reference_low": 32.0, "reference_high": 36.0, "optimal_low": 32.0, "optimal_high": 36.0, "description": "Mittlere Hämoglobin-Konzentration.", "sort_order": 216},
    {"code": "platelets", "name": "Platelets", "unit": "10³/µL", "category": "cbc", "reference_low": 150.0, "reference_high": 400.0, "optimal_low": 180.0, "optimal_high": 380.0, "description": "Thrombozyten (Blutgerinnung).", "sort_order": 217},
    {"code": "neutrophils", "name": "Neutrophils", "unit": "%", "category": "cbc", "reference_low": 40.0, "reference_high": 75.0, "optimal_low": 45.0, "optimal_high": 70.0, "description": "Neutrophile Granulozyten.", "sort_order": 218},
    {"code": "lymphocytes", "name": "Lymphocytes", "unit": "%", "category": "cbc", "reference_low": 20.0, "reference_high": 45.0, "optimal_low": 20.0, "optimal_high": 40.0, "description": "Lymphozyten.", "sort_order": 219},
    {"code": "monocytes", "name": "Monocytes", "unit": "%", "category": "cbc", "reference_low": 2.0, "reference_high": 10.0, "optimal_low": 3.0, "optimal_high": 8.0, "description": "Monozyten.", "sort_order": 220},
    {"code": "eosinophils", "name": "Eosinophils", "unit": "%", "category": "cbc", "reference_low": 0.0, "reference_high": 6.0, "optimal_low": 0.0, "optimal_high": 5.0, "description": "Eosinophile Granulozyten.", "sort_order": 221},
    {"code": "basophils", "name": "Basophils", "unit": "%", "category": "cbc", "reference_low": 0.0, "reference_high": 2.0, "optimal_low": 0.0, "optimal_high": 1.0, "description": "Basophile Granulozyten.", "sort_order": 222},

    # Metabolic
    {"code": "glucose_fasting", "name": "Fasting Glucose", "unit": "mg/dL", "category": "metabolic", "reference_low": 70.0, "reference_high": 100.0, "optimal_low": 70.0, "optimal_high": 90.0, "description": "Nüchtern-Blutzucker.", "sort_order": 230},
    {"code": "hba1c", "name": "HbA1c", "unit": "%", "category": "metabolic", "reference_low": None, "reference_high": 5.7, "optimal_low": None, "optimal_high": 5.4, "description": "Langzeit-Blutzucker (3 Monate).", "sort_order": 231},
    {"code": "insulin_fasting", "name": "Fasting Insulin", "unit": "µIU/mL", "category": "metabolic", "reference_low": 2.0, "reference_high": 20.0, "optimal_low": 2.0, "optimal_high": 8.0, "description": "Nüchtern-Insulin.", "sort_order": 232},
    {"code": "homa_ir", "name": "HOMA-IR", "unit": "", "category": "metabolic", "reference_low": None, "reference_high": 2.0, "optimal_low": None, "optimal_high": 1.5, "description": "Insulinresistenz-Index.", "sort_order": 233},

    # Thyroid
    {"code": "tsh", "name": "TSH", "unit": "mIU/L", "category": "thyroid", "reference_low": 0.4, "reference_high": 4.0, "optimal_low": 0.5, "optimal_high": 2.5, "description": "Thyreoidea-stimulierendes Hormon.", "sort_order": 240},
    {"code": "ft3", "name": "Free T3", "unit": "pg/mL", "category": "thyroid", "reference_low": 2.0, "reference_high": 4.4, "optimal_low": 2.5, "optimal_high": 4.0, "description": "Freies Triiodthyronin.", "sort_order": 241},
    {"code": "ft4", "name": "Free T4", "unit": "ng/dL", "category": "thyroid", "reference_low": 0.8, "reference_high": 1.8, "optimal_low": 1.0, "optimal_high": 1.6, "description": "Freies Thyroxin.", "sort_order": 242},
    {"code": "tpo_antibodies", "name": "TPO Antibodies", "unit": "IU/mL", "category": "thyroid", "reference_low": None, "reference_high": 35.0, "optimal_low": None, "optimal_high": 34.0, "description": "Schilddrüsen-Antikörper.", "sort_order": 243},

    # Hormones
    {"code": "testosterone_total", "name": "Total Testosterone", "unit": "ng/dL", "category": "hormone", "reference_low": 300.0, "reference_high": 1000.0, "optimal_low": 400.0, "optimal_high": 900.0, "description": "Gesamt-Testosteron.", "sort_order": 250},
    {"code": "testosterone_free", "name": "Free Testosterone", "unit": "pg/mL", "category": "hormone", "reference_low": 5.0, "reference_high": 21.0, "optimal_low": 7.0, "optimal_high": 18.0, "description": "Freies Testosteron.", "sort_order": 251},
    {"code": "estradiol", "name": "Estradiol", "unit": "pg/mL", "category": "hormone", "reference_low": 10.0, "reference_high": 40.0, "optimal_low": 15.0, "optimal_high": 35.0, "description": "Östradiol.", "sort_order": 252},
    {"code": "progesterone", "name": "Progesterone", "unit": "ng/mL", "category": "hormone", "reference_low": 0.1, "reference_high": 0.9, "optimal_low": 0.2, "optimal_high": 0.8, "description": "Progesteron (Follikelphase).", "sort_order": 253},
    {"code": "cortisol", "name": "Cortisol", "unit": "µg/dL", "category": "hormone", "reference_low": 5.0, "reference_high": 25.0, "optimal_low": 8.0, "optimal_high": 20.0, "description": "Cortisol (morgens).", "sort_order": 254},
    {"code": "dhea_s", "name": "DHEA-S", "unit": "µg/dL", "category": "hormone", "reference_low": 80.0, "reference_high": 560.0, "optimal_low": 120.0, "optimal_high": 480.0, "description": "Dehydroepiandrosteron-Sulfat.", "sort_order": 255},

    # Vitamins & iron
    {"code": "vitamin_d_25oh", "name": "Vitamin D (25-OH)", "unit": "ng/mL", "category": "vitamin", "reference_low": 30.0, "reference_high": 100.0, "optimal_low": 40.0, "optimal_high": 60.0, "description": "Vitamin-D-Spiegel.", "sort_order": 260},
    {"code": "vitamin_b12", "name": "Vitamin B12", "unit": "pg/mL", "category": "vitamin", "reference_low": 200.0, "reference_high": 900.0, "optimal_low": 400.0, "optimal_high": 700.0, "description": "Vitamin-B12-Spiegel.", "sort_order": 261},
    {"code": "folate", "name": "Folate", "unit": "ng/mL", "category": "vitamin", "reference_low": 3.0, "reference_high": 20.0, "optimal_low": 5.0, "optimal_high": 17.0, "description": "Folsäure.", "sort_order": 262},
    {"code": "ferritin", "name": "Ferritin", "unit": "ng/mL", "category": "vitamin", "reference_low": 30.0, "reference_high": 300.0, "optimal_low": 50.0, "optimal_high": 150.0, "description": "Eisenspeicher.", "sort_order": 263},
    {"code": "iron", "name": "Iron", "unit": "µg/dL", "category": "vitamin", "reference_low": 60.0, "reference_high": 170.0, "optimal_low": 70.0, "optimal_high": 150.0, "description": "Serum-Eisen.", "sort_order": 264},
    {"code": "transferrin", "name": "Transferrin", "unit": "mg/dL", "category": "vitamin", "reference_low": 200.0, "reference_high": 360.0, "optimal_low": 215.0, "optimal_high": 340.0, "description": "Eisentransport-Protein.", "sort_order": 265},
    {"code": "transferrin_saturation", "name": "Transferrin Saturation", "unit": "%", "category": "vitamin", "reference_low": 20.0, "reference_high": 50.0, "optimal_low": 25.0, "optimal_high": 45.0, "description": "Eisensättigung von Transferrin.", "sort_order": 266},

    # Inflammation
    {"code": "crp_hs", "name": "hs-CRP", "unit": "mg/L", "category": "inflammation", "reference_low": None, "reference_high": 3.0, "optimal_low": None, "optimal_high": 1.0, "description": "Hochsensitives C-reaktives Protein.", "sort_order": 270},
    {"code": "esr", "name": "ESR", "unit": "mm/h", "category": "inflammation", "reference_low": 0.0, "reference_high": 20.0, "optimal_low": 0.0, "optimal_high": 15.0, "description": "Blutsenkungsgeschwindigkeit.", "sort_order": 271},
]
