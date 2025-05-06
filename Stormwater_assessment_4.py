import streamlit as st
from typing import Dict
import re
import string

# ----------------- Surface Categories -----------------
surface_types = {
    "asphalt": "impermeable", "concrete": "impermeable", "paved": "impermeable",
    "gravel": "semi-permeable", "gravel path": "semi-permeable", "gravel walkway": "semi-permeable",
    "open soil": "semi-permeable", "dirt": "semi-permeable", "bare soil": "semi-permeable",
    "grass": "permeable", "meadow": "permeable", "shrub": "permeable", "grasses": "permeable", "shrubs": "permeable",
    "wood chip": "permeable", "mulch": "permeable", "wildflower": "permeable", "tree cluster": "permeable", "trees cluster": "permeable"
}

# ----------------- Vegetation Weights -----------------
vegetation_weights = {
    "low-rise grass": 1,
    "grass meadow": 2,
    "wildflower meadow": 3,
    "shrub": 3,
    "isolated tree": 2,
    "tree cluster": 4
}

# Synonyms normalization
synonym_map = {
    "bush": "shrub", "bushes": "shrub", "shrubs": "shrub", "bushy plant": "shrub", "evergreen bushes": "shrub",
    "flowering shrubs": "shrub", "ornamental plants": "shrub", "thicket": "shrub",
    "natural meadow": "grass meadow", "grassland": "low-rise grass", "grassy field": "low-rise grass", "grass": "low-rise grass",
    "grasses": "low-rise grass", "tall grass": "grass meadow", "flower bed": "wildflower meadow", "flowering plants": "wildflower meadow",
    "patch of grass": "grass meadow", "meadow grass": "grass meadow", "ornamental grass": "grass meadow",
    "single tree": "isolated tree", "several trees": "tree cluster", "dense tree cluster": "tree cluster", "trees cluster": "tree cluster"
}

def normalize_text(text: str) -> str:
    for syn, standard in synonym_map.items():
        text = re.sub(rf"\b{re.escape(syn)}\b", standard, text.lower())
    return text

# ----------------- Utility: Proximity Check -----------------
def keywords_nearby(text: str, phrase1: str, phrase2: str, max_distance: int = 10) -> bool:
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "but", "of", "for", "to"}
    text_clean = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = [w for w in text_clean.split() if w not in stop_words]

    tokens1 = phrase1.lower().split()
    tokens2 = phrase2.lower().split()

    positions1 = [i for i, word in enumerate(words) if word in tokens1]
    positions2 = [i for i, word in enumerate(words) if word in tokens2]

    for i in positions1:
        for j in positions2:
            if abs(i - j) <= max_distance:
                return True
    return False

# ----------------- Surface Evaluation -----------------
def evaluate_permeable_balance(surface_counts: Dict[str, int]) -> (int, str):
    permeable = surface_counts["permeable"]
    semi_impermeable = surface_counts["semi-permeable"]
    impermeable = surface_counts["impermeable"]

    comparison_value = semi_impermeable + impermeable

    if permeable > comparison_value:
        score = 3
    elif permeable == comparison_value:
        score = 2
    else:
        score = 1

    comment = (f"Permeable surfaces = {permeable}; "
               f"Semi-permeable + Impermeable = {comparison_value} "
               f"(Semi-permeable: {semi_impermeable}, Impermeable: {impermeable})")

    return score, comment

# ----------------- Density Evaluation with Proximity -----------------
def evaluate_density(description: str) -> (int, str):
    description = description.lower()

    high_density_keywords = ["dense vegetation", "dense planting", "dense coverage"]
    moderate_density_keywords = ["moderate vegetation", "moderate planting", "moderate coverage"]

    # --- Direct keyword check ---
    for kw in high_density_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", description):
            return 3, f"Dense vegetation detected directly: '{kw}'"

    for kw in moderate_density_keywords:
        if re.search(rf"\b{re.escape(kw)}\b", description):
            return 2, f"Moderate vegetation detected directly: '{kw}'"

    # --- Proximity fallback check ---
    if keywords_nearby(description, "vegetation", "dense") or keywords_nearby(description, "vegetation density", "dense"):
        return 3, "Dense vegetation detected via proximity match."

    if keywords_nearby(description, "vegetation", "moderate") or keywords_nearby(description, "vegetation density", "moderate"):
        return 2, "Moderate vegetation detected via proximity match."

    return 1, "Sparse or low vegetation coverage."

# ----------------- Assessment Logic -----------------
def assess_stormwater(description: str) -> Dict:
    description = normalize_text(description)

    # ---- Surface Area Assessment ----
    surface_counts = {"permeable": 0, "semi-permeable": 0, "impermeable": 0}
    for surface, category in surface_types.items():
        if re.search(rf"\b{re.escape(surface)}\b", description):
            surface_counts[category] += 1

    surface_score, surface_comment = evaluate_permeable_balance(surface_counts)

    # ---- Vegetation Assessment ----
    veg_score_raw = 0
    veg_found = []
    for veg, base_weight in vegetation_weights.items():
        if re.search(rf"\b{re.escape(veg)}\b", description):
            weighted_score = base_weight
            veg_score_raw += weighted_score
            veg_found.append(f"{veg} (weight {base_weight})")

    # Normalize based on a reasonable diversity threshold 
    diversity_threshold = 12
    veg_score = round((veg_score_raw / diversity_threshold) * 3)

    # Clamp score between 1 and 3
    veg_score = min(max(veg_score, 1), 3)

    veg_comment = ", ".join(veg_found) if veg_found else "No significant water-retentive vegetation found."

    # ---- Density Assessment ----
    density_score, density_comment = evaluate_density(description)

    # ---- Overall Performance ----
    overall = round((surface_score + veg_score + density_score) / 3)
    rating = {1: "Weak Performance", 2: "Moderate Performance", 3: "Strong Performance"}

    return {
        "permeable_surface": {"score": surface_score, "comment": surface_comment},
        "vegetation_retention": {"score": veg_score, "comment": veg_comment},
        "vegetation_density": {"score": density_score, "comment": density_comment},
        "overall_score": overall,
        "overall_comment": rating[overall]
    }

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="Stormwater Infiltration Assessment", layout="centered")

st.title("💧 Stormwater Infiltration & Retention Assessment Tool")

st.markdown("Describe a landscape and assess its potential for stormwater infiltration and retention based on surface types, vegetation, and vegetation density.")

description = st.text_area("📝 Enter your landscape description:", height=250)

if st.button("💧 Assess Stormwater Infiltration"):
    if description.strip():
        results = assess_stormwater(description)
        st.subheader("🔎 Assessment Results")
        st.markdown(f"**Permeable Surface Area**: Score {results['permeable_surface']['score']} — {results['permeable_surface']['comment']}")
        st.markdown(f"**Vegetation for Water Retention**: Score {results['vegetation_retention']['score']} — {results['vegetation_retention']['comment']}")
        st.markdown(f"**Vegetation Density**: Score {results['vegetation_density']['score']} — {results['vegetation_density']['comment']}")
        st.success(f"💧 **Overall Score: {results['overall_score']} — {results['overall_comment']}**")
    else:
        st.warning("Please provide a description to evaluate.")
