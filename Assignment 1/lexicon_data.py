"""Raw lexicon data: stems, irregular forms and derivational families (Tasks 5-8)."""

NOUNS = """fracture lesion kidney artery biopsy vein wound infection ulcer tumour cyst rash symptom surgery allergy
therapy pharmacy clinic ward bed nurse doctor patient physician surgeon neurologist cardiologist nephrologist
radiologist anaesthetist incision suture drain catheter cannula syringe tablet capsule injection infusion dose
prescription medication drug antibiotic analgesic vaccine fever cough headache nausea vomiting dizziness fatigue
pain swelling bruise abscess infarction embolism thrombosis stroke seizure pneumonia asthma diabetes hypertension
anaemia arthritis hepatitis nephritis gastritis bronchitis dermatitis meningitis appendicitis tonsillitis cystitis
colitis fibrosis stenosis sclerosis neuropathy nephropathy cardiomyopathy appendectomy nephrectomy
cholecystectomy mastectomy hysterectomy tonsillectomy colectomy laminectomy thyroidectomy splenectomy amputation
transplant graft implant stent pacemaker bandage dressing plaster splint cast femur tibia fibula humerus radius
ulna rib skull spine pelvis hip knee ankle shoulder elbow wrist liver lung heart brain bladder bowel stomach
colon spleen pancreas thyroid nerve muscle tendon ligament joint bone skin blood urine specimen sample culture
scan ultrasound pressure pulse temperature rhythm oxygen saturation discharge admission review plan outcome
complication recovery rehabilitation physiotherapy appointment referral diagnosis analysis child tooth foot
vertebra bacterium appendix index box fix finding examination procedure operation stitch scar
fluid dehydration inflammation bleeding healing hernia polyp stone cancer carcinoma lymphoma sepsis shock
trauma burn sprain dislocation concussion laceration contusion edema oedema rhinitis sinusitis otitis
tinnitus vertigo migraine epilepsy dementia depression anxiety insomnia obesity cholesterol glucose insulin
creatinine urea sodium potassium haemoglobin platelet leukocyte antibody antigen allergen nutrition diet""".split()

VERBS = """treat admit discharge operate diagnose infect refer prescribe monitor observe examine remove repair resect
suture stop visit open fix study plan transfer reduce improve worsen complain present develop recover swell ache
vomit bleed heal go have do be give take feel break begin hold keep sleep send find get see eat lose undergo leave
tell cough sneeze fracture dislocate sprain bruise inject infuse administer ventilate intubate extubate
resuscitate immobilise sterilise dress bandage cut stitch clean irrigate drain aspirate biopsy scan image review
assess record document report order request advise instruct counsel educate consult attend arrive depart wait
rest walk mobilise stand sit drink smoke exercise gain play commit omit occur drop rub permit submit make""".split()

ADJECTIVES = """mild severe high low acute chronic benign malignant stable critical weak sick sore deep thick thin large
small poor good bad normal abnormal fatal tender swollen painful healthy young old hot cold fit mobile
unstable moderate minor major recurrent persistent sudden gradual elevated reduced diffuse localised
bilateral unilateral superficial""".split()

# Combining forms / roots used only in derivation (counted as stems for lexicon size).
ROOTS = """nephr nephro cardi cardio operat infect path neur hepat gastr arthr derm hyper hypo hemat haemat
oste pulmon ren cerebr vascul thorac gynae uro angi bronch col cyst my""".split()

# Verbs that double their final consonant (stressed final CVC).
DOUBLING = {"admit", "stop", "plan", "refer", "transfer", "scan", "drop", "rub", "permit", "submit",
            "commit", "omit", "occur", "begin", "get", "sit"}
ADJ_DOUBLING = {"thin", "hot", "fit"}
# Adjectives taking -er/-est (others are periphrastic: more X / most X).
ADJ_ER = {"mild", "high", "low", "weak", "sick", "sore", "deep", "thick", "thin", "large", "small",
          "young", "old", "hot", "cold", "fit", "poor", "good", "bad"}
ADJ_IRREGULAR = {"good": ("better", "best"), "bad": ("worse", "worst")}

IRREGULAR_PLURAL = {
    "child": "children", "diagnosis": "diagnoses", "analysis": "analyses", "vertebra": "vertebrae",
    "bacterium": "bacteria", "tooth": "teeth", "foot": "feet", "appendix": "appendices", "index": "indices",
    "stenosis": "stenoses", "fibrosis": "fibroses", "thrombosis": "thromboses", "sclerosis": "scleroses",
}

IRREGULAR_VERB = {
    "be": {"+3SG": "is", "+PAST": "was", "+PASTPART": "been", "+PROG": "being"},
    "go": {"+3SG": "goes", "+PAST": "went", "+PASTPART": "gone"},
    "have": {"+3SG": "has", "+PAST": "had", "+PASTPART": "had", "+PROG": "having"},
    "do": {"+3SG": "does", "+PAST": "did", "+PASTPART": "done"},
    "bleed": {"+PAST": "bled", "+PASTPART": "bled"},
    "give": {"+PAST": "gave", "+PASTPART": "given"},
    "take": {"+PAST": "took", "+PASTPART": "taken"},
    "feel": {"+PAST": "felt", "+PASTPART": "felt"},
    "break": {"+PAST": "broke", "+PASTPART": "broken"},
    "begin": {"+PAST": "began", "+PASTPART": "begun"},
    "hold": {"+PAST": "held", "+PASTPART": "held"},
    "keep": {"+PAST": "kept", "+PASTPART": "kept"},
    "sleep": {"+PAST": "slept", "+PASTPART": "slept"},
    "send": {"+PAST": "sent", "+PASTPART": "sent"},
    "find": {"+PAST": "found", "+PASTPART": "found"},
    "get": {"+PAST": "got", "+PASTPART": "got"},
    "see": {"+PAST": "saw", "+PASTPART": "seen"},
    "eat": {"+PAST": "ate", "+PASTPART": "eaten"},
    "lose": {"+PAST": "lost", "+PASTPART": "lost"},
    "undergo": {"+PAST": "underwent", "+PASTPART": "undergone"},
    "leave": {"+PAST": "left", "+PASTPART": "left"},
    "tell": {"+PAST": "told", "+PASTPART": "told"},
    "swell": {"+PASTPART": "swollen"},
    "sit": {"+PAST": "sat", "+PASTPART": "sat"},
    "stand": {"+PAST": "stood", "+PASTPART": "stood"},
    "drink": {"+PAST": "drank", "+PASTPART": "drunk"},
}

# Inflectional affix inventory (>= 20 allomorphs) documented for Tasks 5/7.
INFLECTIONAL_AFFIXES = [
    ("-s", "+PL / +3SG"), ("-es", "+PL / +3SG after sibilant or consonant+o"), ("-ies", "+PL / +3SG after C+y"),
    ("-ves", "+PL f/fe -> ves"), ("-ed", "+PAST/+PASTPART"), ("-d", "+PAST after silent e"),
    ("-ied", "+PAST after C+y"), ("-ing", "+PROG"), ("-ying", "+PROG die/lie"), ("-en", "+PASTPART (irregular)"),
    ("-n", "+PASTPART (irregular)"), ("-er", "+COMP"), ("-est", "+SUPER"), ("-r", "+COMP after e"),
    ("-st", "+SUPER after e"), ("-ier", "+COMP after C+y"), ("-iest", "+SUPER after C+y"),
    ("-ae", "+PL Latin"), ("-a", "+PL Latin"), ("-ices", "+PL Latin"), ("-ren", "+PL child"), ("-ses", "+PL Greek -sis"),
    ("-'s", "+POSS"), ("-s'", "+POSS.PL"),
]

# (base/root, affix or second part, derived lemma, pos). Attested forms only (no free concatenation).
DERIVED = [
    ("operate", "-ation", "operation", "N"), ("operation", "-al", "operational", "ADJ"),
    ("infect", "-ion", "infection", "N"), ("infection", "-ous", "infectious", "ADJ"),
    ("treat", "-able", "treatable", "ADJ"), ("treat", "-ment", "treatment", "N"),
    ("nephro", "-logy", "nephrology", "N"), ("cardio", "-logy", "cardiology", "N"),
    ("nephr", "-ectomy", "nephrectomy", "N"), ("appendic", "-ectomy", "appendectomy", "N"),
    ("nephr", "-itis", "nephritis", "N"), ("arthr", "-itis", "arthritis", "N"), ("hepat", "-itis", "hepatitis", "N"),
    ("gastr", "-itis", "gastritis", "N"), ("derm", "-itis", "dermatitis", "N"),
    ("fibr", "-osis", "fibrosis", "N"), ("thromb", "-osis", "thrombosis", "N"),
    ("an", "-aemia", "anaemia", "N"), ("leuk", "-aemia", "leukaemia", "N"),
    ("amputate", "-ation", "amputation", "N"), ("obstruct", "-ive", "obstructive", "ADJ"),
    ("ren", "-al", "renal", "ADJ"), ("hepat", "-ic", "hepatic", "ADJ"), ("cardi", "-ac", "cardiac", "ADJ"),
    ("neur", "-ologist", "neurologist", "N"), ("path", "-ology", "pathology", "N"),
    ("pathology", "-ical", "pathological", "ADJ"), ("transport", "-er", "transporter", "N"),
    ("hyper", "tension", "hypertension", "N"), ("hypo", "glycaemia", "hypoglycaemia", "N"),
    ("hyper", "glycaemia", "hyperglycaemia", "N"), ("re", "operation", "reoperation", "N"),
    ("re", "treat", "retreat", "V"), ("un", "healed", "unhealed", "ADJ"), ("un", "treated", "untreated", "ADJ"),
    ("hyper", "thyroid", "hyperthyroid", "ADJ"), ("hypo", "thyroid", "hypothyroid", "ADJ"),
    ("post", "operative", "postoperative", "ADJ"), ("pre", "operative", "preoperative", "ADJ"),
]
DERIVATIONAL_AFFIXES = ["-itis", "-ectomy", "-ology", "-osis", "-aemia", "-ation", "-able", "-ive", "-al",
                        "-ic", "-ist", "-er", "-ment", "-ion", "-ous", "-ac", "nephro-", "hyper-", "hypo-",
                        "re-", "un-", "post-", "pre-"]
