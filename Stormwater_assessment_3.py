import streamlit as st
from typing import Dict
import re

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
    "single tree": "isolated tree", "several trees": "tree cluster", "dense tree cluster": "tree cluster", "trees cluster":"tree cluster"
}

# Density keywords and multipliers
density_map = {
    "sparse": 0.5, "scattered": 0.5, "patchy": 0.5, "thin": 0.5,
    "moderate": 0.5, "some": 0.5, "few": 0.5,
    "dense": 1, "thick": 1, "lush": 1, "abundant": 1
}

def normalize_text(text: str) -> str:
    for syn, standard in synonym_map.items():
        text = re.sub(rf"\b{re.escape(syn)}\b", standard, text.lower())
    return text

def get_density_multiplier(description: str, veg: str) -> float:
    window_size = 6
    description_words = description.lower().split()
    veg_words = veg.lower().split()

    multipliers = []

    for i, word in enumerate(description_words):
        if word == veg_words[0]:
            start = max(0, i - window_size)
            end = min(len(description_words), i + window_size + 1)
            context = description_words[start:end]
            found = False
            for density, multiplier in density_map.items():
                if density in context:
                    multipliers.append(multiplier)
                    found = True
                    break
            if not found:
                multipliers.append(1.0)

    return max(multipliers) if multipliers else 1.0

# ----------------- New Surface Evaluation -----------------
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

# ----------------- Assessment Logic -----------------
def assess_stormwater(description: str) -> Dict:
    description = normalize_text(description)

    # ---- Surface Area Assessment ----
    surface_counts = {"permeable": 0, "semi-permeable": 0, "impermeable": 0}
    for surface, category in surface_types.items():
        if re.search(rf"\b{re.escape(surface)}\b", description):
            surface_counts[category] += 1

    # New permeable balance evaluation
    surface_score, surface_comment = evaluate_permeable_balance(surface_counts)

    # ---- Vegetation Assessment ----
    veg_score_raw = 0
    veg_found = []
    for veg, base_weight in vegetation_weights.items():
        if re.search(rf"\b{re.escape(veg)}\b", description):
            density_multiplier = get_density_multiplier(description, veg)
            weighted_score = base_weight * density_multiplier
            veg_score_raw += weighted_score
            veg_found.append(f"{veg} (base {base_weight} × density {density_multiplier} = {weighted_score})")

    if veg_score_raw >= 8:
        veg_score = 3
    elif veg_score_raw >= 4:
        veg_score = 2
    else:
        veg_score = 1

    veg_comment = ", ".join(veg_found) if veg_found else "No significant water-retentive vegetation found."

    # ---- Overall Performance ----
    overall = round((surface_score + veg_score) / 2)
    rating = {1: "Weak Performance", 2: "Moderate Performance", 3: "Strong Performance"}

    return {
        "permeable_surface": {"score": surface_score, "comment": surface_comment},
        "vegetation_retention": {"score": veg_score, "comment": veg_comment},
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
        st.success(f"💧 **Overall Score: {results['overall_score']} — {results['overall_comment']}**")
    else:
        st.warning("Please provide a description to evaluate.")
