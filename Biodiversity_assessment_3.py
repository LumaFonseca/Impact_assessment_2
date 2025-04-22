import streamlit as st
from typing import Dict, Tuple
import nltk
from nltk.stem import WordNetLemmatizer
import re

nltk.download("wordnet")
lemmatizer = WordNetLemmatizer()

# ----------------- Synonym Map -----------------
synonym_map = {
    "shrubs": "shrub", "bushy plant": "shrub", "evergreen bushes": "shrub", "flowering shrubs": "shrub",
    "ornamental plants": "shrub", "thicket": "shrub", "bush": "shrub", "bushes": "shrub",
    "patch of grass": "low-rise grass", "grassland": "low-rise grass", "grassy field": "low-rise grass",
    "meadow grass": "grass meadow", "ornamental grass": "grass meadow", "natural meadow": "grass meadow",
    "tall grass": "grass meadow", "flowering plants": "wildflower meadow", "flower bed": "wildflower meadow",
    "young tree": "isolated tree with small canopy", "single tree": "isolated tree with small canopy",
    "insect hotels": "insect hotel", "bee hotel": "insect hotel", "bug house": "insect hotel", "pollinator box": "insect hotel",
    "deadwoods": "deadwood", "habitat log": "deadwood", "fallen log": "deadwood", "tree stump": "deadwood",
    "stack of wood": "wood pile", "rocks": "piled rocks", "rock stack": "piled rocks", "pile of rocks": "piled rocks",
    "rock piles": "piled rocks", "piled rock": "piled rocks", "rock pile": "piled rocks",  "hollow logs": "hollow log", "hollow tree": "hollow log",
    "birdhouses": "birdhouse", "nesting box": "birdhouse", "bird box": "birdhouse", "dead hedges": "dead hedge"
}

# ----------------- Text Normalization -----------------
def normalize_synonyms(text: str, synonym_map: Dict[str, str]) -> str:
    text = text.lower()
    for synonym, standard in synonym_map.items():
        text = re.sub(rf"\b{re.escape(synonym)}\b", standard, text)
    return text

def lemmatize_text(text: str) -> str:
    words = text.lower().split()
    return " ".join(lemmatizer.lemmatize(word) for word in words)

# ----------------- Proximity -----------------
def keywords_nearby(text: str, phrase1: str, phrase2: str, max_distance: int = 6) -> bool:
    words = text.lower().split()
    tokens1 = phrase1.split()
    tokens2 = phrase2.split()

    indices1 = [i for i in range(len(words) - len(tokens1) + 1)
                if words[i:i+len(tokens1)] == tokens1]
    indices2 = [i for i in range(len(words) - len(tokens2) + 1)
                if words[i:i+len(tokens2)] == tokens2]

    for i in indices1:
        for j in indices2:
            if abs(i - j) <= max_distance:
                return True
    return False

# ----------------- Improved Negation -----------------
def is_negated(text: str, keyword: str) -> bool:
    negation_terms = ["no", "not", "without", "lacks", "lack of", "missing", "absent", "devoid of", "none of the"]
    keyword_tokens = keyword.lower().split()
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

                if re.search(term + r".*such as.*" + re.escape(keyword), sentence):
                    return True
    return False

# ----------------- Evaluation Logic -----------------
def evaluate_criteria(description: str) -> Dict[str, Dict[str, str | int]]:
    normalized_description = normalize_synonyms(description, synonym_map)
    clean_description = lemmatize_text(normalized_description)
    scores = {}

    def keyword_matches(keywords):
        matched = []
        negated = []
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", clean_description):
                if is_negated(description, kw):
                    negated.append(kw)
                else:
                    matched.append(kw)
        return matched, negated

    # --- Vegetation Layers ---
    vegetation_keywords = [
        "grass meadow", "low-rise grass", "wildflower meadow",
        "shrub", "isolated tree with small canopy", "isolated tree with large canopy",
        "isolated tree with a small canopy", "isolated tree with a large canopy",
        "single tree with small canopy", "single tree with large canopy",
        "sparse tree cluster", "dense tree cluster"
    ]
    veg_matched, veg_negated = keyword_matches(vegetation_keywords)
    score = 3 if len(veg_matched) >= 4 else 2 if len(veg_matched) >= 2 else 1
    comment = f"{len(veg_matched)} matches: {', '.join(veg_matched)}" if veg_matched else "Limited vegetation layers detected."
    if veg_negated:
        comment += f" (Skipped negated: {', '.join(veg_negated)})"
    scores["vegetation_layers"] = {"score": score, "comment": comment}

    # --- Species Variety ---
    high_variety = [
        "diverse species variety", "diverse specie variety", "high species variety", "numerous species", "vibrant mix",
        "broad range of species", "many type of flowering plant", "visible diversity of species",
        "colorful plant mix", "diverse mix", "variety of flowering species", "multiple colors and forms",
        "visually rich planting", "diverse palette", "rich mix of plants", "structured plant diversity",
        "species variety is diverse", "wide array", "ecological diversity", "species variety across the space is diverse", "the species variety is diverse",
        "species variety across the space is high","species variety appears diverse"

    ]
    moderate_variety = [
        "moderate species variety", "moderate specie variety", "balanced variety", "curated but not overly complex", "moderate to diverse",
        "some species variety", "moderate mix", "some plant diversity", "fair variety", "not overly complex palette",
        "species variety is moderate", "species variety across the space is moderate", "the species variety is moderate",
        "species variety across the space is low","species variety appears moderate"
    ]
    high_matched, high_negated = keyword_matches(high_variety)
    mod_matched, mod_negated = keyword_matches(moderate_variety)

    if not high_matched and (
        keywords_nearby(clean_description, "species", "diverse") or
        keywords_nearby(clean_description, "species variety", "diverse") or
        keywords_nearby(clean_description, "variety", "diverse") or
        keywords_nearby(clean_description, "mix", "species")
    ):
        high_matched.append("species + diverse (proximity match)")

    if not mod_matched and (
        keywords_nearby(clean_description, "species", "moderate") or
        keywords_nearby(clean_description, "species variety", "moderate") or
        keywords_nearby(clean_description, "variety", "moderate")
    ):
        mod_matched.append("species + moderate (proximity match)")

    if high_matched:
        score = 3
        comment = f"High variety: {', '.join(high_matched)}"
        if high_negated:
            comment += f" (Skipped negated: {', '.join(high_negated)})"
    elif mod_matched:
        score = 2
        comment = f"Moderate variety: {', '.join(mod_matched)}"
        if mod_negated:
            comment += f" (Skipped negated: {', '.join(mod_negated)})"
    else:
        score = 1
        comment = "Limited or sparse species variety."
    scores["species_variety"] = {"score": score, "comment": comment}

    # --- Vegetation Density ---
    high_density = [
        "the vegetation is dense", "thick vegetation", "lush vegetation", "cover the ground entirely",
        "rich and textured vegetative carpet", "dense vegetation zones", "dense vegetation", "vegetation density is dense", "vegetation density is high"
    ]
    moderate_density = [
        "moderate vegetation", "moderate density", "partial coverage", "moderate plant mass",
        "moderate vegetation density", "moderate plant coverage", "the vegetation is moderately dense", "moderate to dense", "vegetation density is moderate"
    ]
    high_matched, high_negated = keyword_matches(high_density)
    mod_matched, mod_negated = keyword_matches(moderate_density)

    if not high_matched:
        if (
        keywords_nearby(clean_description, "vegetation", "dense") or
        keywords_nearby(clean_description, "vegetation density", "dense")
    ):
            high_matched.append("vegetation + dense (proximity match)")
        elif keywords_nearby(clean_description, "vegetation density", "high"):
            high_matched.append("vegetation density + high (proximity match)")


    if not mod_matched and (
        keywords_nearby(clean_description, "vegetation", "moderate") or
        keywords_nearby(clean_description, "vegetation density", "moderate")
    ):
        mod_matched.append("vegetation + moderate (proximity match)")

    if high_matched:
        score = 3
        comment = f"Dense: {', '.join(high_matched)}"
        if high_negated:
            comment += f" (Skipped negated: {', '.join(high_negated)})"
    elif mod_matched:
        score = 2
        comment = f"Moderate: {', '.join(mod_matched)}"
        if mod_negated:
            comment += f" (Skipped negated: {', '.join(mod_negated)})"
    else:
        score = 1
        comment = "Sparse or low vegetation coverage."
    scores["vegetation_density"] = {"score": score, "comment": comment}

    # --- Biodiversity Hotspots ---
    hotspot_keywords = [
        "birdhouse", "bird house", "insect hotel", "bug hotel", "piled rocks",
        "deadwood", "dead wood", "dead hedge", "hollow log", "log", "wood pile"
    ]
    matched, negated = keyword_matches(hotspot_keywords)
    count = len(matched)
    score = 3 if count >= 3 else 2 if count >= 1 else 1
    comment = f"{count} hotspot(s): {', '.join(matched)}"
    if negated:
        comment += f" (Skipped negated: {', '.join(negated)})"
    scores["biodiversity_hotspots"] = {"score": score, "comment": comment}

    return scores

def calculate_overall_score(scores: Dict[str, Dict[str, int]]) -> Tuple[int, str]:
    total = sum(scores[criterion]["score"] for criterion in scores)
    average = round(total / 4)
    rating = {1: "Weak Performance", 2: "Moderate Performance", 3: "Strong Performance"}
    return average, rating[average]

def assess_biodiversity(description: str) -> Dict:
    scores = evaluate_criteria(description)
    overall_score, overall_comment = calculate_overall_score(scores)
    return {
        "criteria_scores": scores,
        "overall_score": overall_score,
        "overall_comment": overall_comment
    }

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="Biodiversity Assessment", layout="centered")

st.title("🌺 Biodiversity Performance Assessment Tool")

st.markdown("Describe a landscape scenario and evaluate its biodiversity performance across diversity of vegetation layers, species variety, density of vegetation, and presence of biodiversity microhabitat spots.")

description = st.text_area("📝 Paste or write your landscape description below:", height=250)

if st.button("🌺 Assess Biodiversity"):
    if description.strip():
        results = assess_biodiversity(description)
        st.subheader("💡 Biodiversity Assessment Results")
        for criterion, data in results["criteria_scores"].items():
            st.markdown(f"**{criterion.replace('_', ' ').title()}**")
            st.write(f"Score: {data['score']} — {data['comment']}")
        st.success(f"🌺 **Overall Score: {results['overall_score']} — {results['overall_comment']}**")
    else:
        st.warning("Please enter a description to analyze.")
