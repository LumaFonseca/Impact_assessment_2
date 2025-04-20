import streamlit as st
from typing import Dict, Tuple

# ----------------- Evaluation Logic -----------------

def evaluate_criteria(description: str) -> Dict[str, Dict[str, str | int]]:
    scores = {}

    # Vegetation Layers
    if any(x in description.lower() for x in ["wildflower", "shrubs", "low-rise", "canopy", "trees", "layers"]):
        score = 3
        comment = "Multiple vegetation layers observed, supporting diverse niches."
    elif "some layering" in description.lower() or "grass and trees" in description.lower():
        score = 2
        comment = "Some layering, but not highly diverse."
    else:
        score = 1
        comment = "Limited vertical structure."

    scores["vegetation_layers"] = {"score": score, "comment": comment}

    # Species Variety
    if "variety of species" in description.lower() or "diverse plant species" in description.lower():
        score = 3
        comment = "High diversity of plant species visible."
    elif "some mix" in description.lower():
        score = 2
        comment = "Moderate species variety."
    else:
        score = 1
        comment = "Limited or uniform species present."

    scores["species_variety"] = {"score": score, "comment": comment}

    # Vegetation Density
    if "dense" in description.lower():
        score = 3
        comment = "Vegetation is dense, providing good habitat."
    elif "moderate" in description.lower():
        score = 2
        comment = "Moderate vegetation coverage."
    else:
        score = 1
        comment = "Sparse vegetation areas observed."

    scores["vegetation_density"] = {"score": score, "comment": comment}

    # Biodiversity Hotspots
    if any(x in description.lower() for x in ["birdhouse", "insect hotel", "deadwood", "rock pile"]):
        features = sum(x in description.lower() for x in ["birdhouse", "insect hotel", "deadwood", "rock pile"])
        if features >= 2:
            score = 3
            comment = "Multiple biodiversity features present."
        else:
            score = 2
            comment = "One biodiversity feature detected."
    else:
        score = 1
        comment = "No biodiversity hotspots visible."

    scores["biodiversity_hotspots"] = {"score": score, "comment": comment}

    return scores

def calculate_overall_score(scores: Dict[str, Dict[str, int]]) -> Tuple[int, str]:
    total = sum(scores[criterion]["score"] for criterion in scores)
    average = round(total / 4)

    rating = {
        1: "Weak Performance",
        2: "Moderate Performance",
        3: "Strong Performance"
    }

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

st.title("🌿 Biodiversity Performance Assessment Tool")

st.markdown("Describe a landscape scenario and evaluate its biodiversity performance across vegetation layers, species variety, density, and presence of biodiversity hotspots.")

# Input box
description = st.text_area("📝 Paste or write your landscape description below:", height=250)

if st.button("🧠 Assess Biodiversity"):
    if description.strip():
        results = assess_biodiversity(description)
        
        st.subheader("📊 Biodiversity Assessment Results")

        for criterion, data in results["criteria_scores"].items():
            st.markdown(f"**{criterion.replace('_', ' ').title()}**")
            st.write(f"Score: {data['score']} — {data['comment']}")

        st.success(f"🌱 **Overall Score: {results['overall_score']} — {results['overall_comment']}**")
    else:
        st.warning("Please enter a description to analyze.")
