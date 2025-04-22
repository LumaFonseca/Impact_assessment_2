import streamlit as st
from typing import Dict, Tuple, List
import nltk
from nltk.stem import WordNetLemmatizer
import re
from collections import defaultdict

nltk.download("wordnet")
lemmatizer = WordNetLemmatizer()

# ----------------- Synonym Mapping -----------------
synonym_map = {
    # Vegetation
    "bush": "shrub", "bushes": "shrub", "shrubs": "shrub", "bushy plant": "shrub", "evergreen bushes": "shrub",
    "flowering shrubs": "shrub", "ornamental plants": "shrub", "thicket": "shrub",
    "natural meadow": "grass meadow", "grassland": "low-rise grass", "grassy field": "low-rise grass",
    "tall grass": "grass meadow", "flower bed": "wildflower meadow", "flowering plants": "wildflower meadow", "patch of grass": "low-rise grass",
    "meadow grass": "grass meadow", "ornamental grass": "grass meadow",

    # Hardscape
    "gravel walkway": "gravel path", "gravel trail": "gravel path",
    "dirt path": "open soil path", "bare soil trail": "open soil path", "bare soil path": "open soil path",
    "wood trail": "wood chip path", "wood path": "wood chip path",

    # Infrastructure
    "wooden bench": "bench", "benches": "bench", "log bench": "bench", "stone seat": "bench",
    "seating island": "bench", "tree stump": "wood stumps", "wood stump": "wood stumps", "logs":"wood logs", "wood log": "wood log",
    "picnic area": "picnic table", "picnic tables": "picnic table", "signpost": "educational sign",
    "sign": "educational sign", "signs": "educational sign", "educational signs": "educational sign",
    "biodiversity sign": "educational sign", "sign board": "educational sign", "info sign": "educational sign",
    "interpretive panel": "educational sign",
    "plaque": "event plaque", "plaques": "event plaque", "event plaques": "event plaque",
    "mini library": "bookshelf", "book hut": "bookshelf", "shared bookshelf": "bookshelf", "bookshelves": "bookshelf",

    # Biodiversity
    "bee hotel": "insect hotel", "bug house": "insect hotel", "insect hotels": "insect hotel",
    "nest box": "birdhouse", "bird box": "birdhouse", "birdhouses": "birdhouse",
    "rocks": "piled rocks", "rock stack": "piled rocks",
    "fallen log": "deadwood", "deadwood": "deadwood",
    "brush hedge": "dead hedge", "dead hedges": "dead hedge"
}

# ----------------- Reverse Map -----------------
reverse_synonym_map = defaultdict(list)
for syn, norm in synonym_map.items():
    reverse_synonym_map[norm].append(syn)

# ----------------- Maintenance Weights -----------------
maintenance_weights = {
    "grass meadow": 1, "low-rise grass": 1, "wildflower meadow": 2, "shrub": 2, "tree": 2,
    "gravel path": 2, "open soil path": 2, "wood chip path": 2,
    "bench": 2, "wood stumps": 1, "wood logs": 1, "picnic table": 2,
    "educational sign": 3, "event plaque": 2, "bookshelf": 3,
    "insect hotel": 3, "birdhouse": 2, "piled rocks": 1, "deadwood": 1, "dead hedge": 1
}

# ----------------- Proximity Pairs -----------------
proximity_keywords = {
    "gravel path": [("gravel", "path"), ("gravel", "trail")],
    "open soil path": [("bare", "soil"), ("dirt", "trail")],
    "wood chip path": [("wood", "chips"), ("mulch", "trail"), ("wood", "trail")],
    "birdhouse": [("bird", "structure"), ("nesting", "box")],
    "insect hotel": [("insect", "hotel"), ("bug", "shelter")],
    "deadwood": [("fallen", "log"), ("dead", "wood")],
    "dead hedge": [("brush", "hedge")],
    "bench": [("wood", "seating")]
}

# ----------------- Number Words -----------------
number_words = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

# ----------------- Quantity Detection -----------------
def extract_quantity_phrases(text: str, keyword: str) -> List[int]:
    pattern = r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b(?:\s+\w+){0,4}?\s+' + re.escape(keyword)
    matches = re.findall(pattern, text.lower())

    results = []
    for match in matches:
        if match.isdigit():
            results.append(int(match))
        elif match in number_words:
            results.append(number_words[match])
    return results

# ----------------- Text Helpers -----------------
def normalize_synonyms(text: str) -> str:
    text = text.lower()
    for synonym, standard in synonym_map.items():
        text = re.sub(rf"\b{re.escape(synonym)}\b", standard, text)
    return text

def lemmatize_text(text: str) -> str:
    words = text.lower().split()
    return " ".join(lemmatizer.lemmatize(word) for word in words)

def keywords_nearby(text: str, word1: str, word2: str, max_distance: int = 6) -> bool:
    words = text.lower().split()
    indices1 = [i for i, w in enumerate(words) if word1 in w]
    indices2 = [i for i, w in enumerate(words) if word2 in w]
    for i in indices1:
        for j in indices2:
            if abs(i - j) <= max_distance:
                return True
    return False

def is_negated(text: str, original_keyword: str) -> bool:
    negation_terms = ["no", "not", "without", "lacks", "lack of", "missing", "absent", "devoid of", "none of the"]
    keyword_tokens = original_keyword.lower().split()
    keyword_lemmas = [lemmatizer.lemmatize(k) for k in keyword_tokens]

    sentences = re.split(r'[.!?]', text.lower())

    for sentence in sentences:
        if not any(tok in sentence for tok in keyword_tokens):
            continue

        clean = re.sub(r"[,;]", " ", sentence)
        words = clean.split()
        lemmatized_words = [lemmatizer.lemmatize(w) for w in words]

        for term in negation_terms:
            if term in lemmatized_words:
                term_index = lemmatized_words.index(term)
                window = lemmatized_words[term_index + 1: term_index + 21]
                for i in range(len(window) - len(keyword_lemmas) + 1):
                    if window[i:i + len(keyword_lemmas)] == keyword_lemmas:
                        return True
                if re.search(term + r".*such as.*" + re.escape(original_keyword), sentence):
                    return True
    return False

# ----------------- Main Logic -----------------
def evaluate_maintenance(description: str) -> Tuple[int, str, Dict[str, int]]:
    raw_text = description.lower()
    normalized = normalize_synonyms(raw_text)
    clean_text = lemmatize_text(normalized)

    matched_elements = {}

    for keyword, weight in maintenance_weights.items():
        quantity_mentions = extract_quantity_phrases(raw_text, keyword)
        count = sum(quantity_mentions)

        found = count > 0
        if not found and keyword in proximity_keywords:
            for w1, w2 in proximity_keywords[keyword]:
                if keywords_nearby(clean_text, w1, w2):
                    count = 1
                    found = True
                    break

        if not found:
            if re.search(rf"\b{re.escape(keyword)}s?\b", clean_text):
                count = 1
                found = True

        if found:
            is_any_synonym_negated = False
            for original_syn in reverse_synonym_map.get(keyword, []):
                if is_negated(raw_text, original_syn):
                    is_any_synonym_negated = True
                    break

            if not is_any_synonym_negated:
                element_weight = count * weight
                matched_elements[f"{keyword} (x{count})"] = element_weight

    # Sum based score logic (based on weights)
    # Sum-based scoring
    
    total_weight = sum(matched_elements.values())

    if total_weight >= 20:
        score = 1
        label = "High Effort (🛠️)"
    
    elif total_weight >= 12:
        score = 2
        label = "Moderate Effort (🔧)"
    else:
        score = 3
        label = "Low Effort (✅)"

    return score, label, matched_elements

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="Landscape Maintenance Effort Evaluation", layout="centered")
st.title("🧹 Landscape Maintenance Effort Evaluation Tool")
st.markdown("Describe a landscape scenario and estimate the maintenance effort based on vegetation complexity, hardscape, infrastructure, and biodiversity microhabitats.")

description = st.text_area("📝 Paste or write your landscape description below:", height=250)

if st.button("🧹 Evaluate Maintenance Effort"):
    if description.strip():
        score, label, matches = evaluate_maintenance(description)
        st.subheader("💡 Maintenance Evaluation Results")

        if matches:
            for elem, weight in matches.items():
                st.write(f"- {elem} → weight {weight}")
        else:
            st.info("No maintenance-related elements detected in the description.")

        st.success(f"🧹 **Overall Score: {score} — {label}**")
    else:
        st.warning("Please enter a description to analyze.")




