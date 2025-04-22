import streamlit as st
import pandas as pd
import io

# ---------- CSS: Reduce side padding ----------
st.markdown("""
    <style>
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Criteria and Custom Options ----------
group_reflection = [
    "Aesthetic Appeal",
    "Comfort Feeling",
    "Educational Meaning",
    "Opportunities for Recreation/Socialization"
]

impact_visualization = [
    "Opportunities for Biodiversity to Thrive",
    "Maintenance Efforts"
]

all_criteria = group_reflection + impact_visualization

criterion_options = {
    "Aesthetic Appeal": [
        "",  # Default empty
        "🔴 It feels ugly, with no sense of beauty or creativity in the design",
        "🟡 It looks fine, nothing particularly striking, but it blends well with the surroundings.",
        "🟢 It looks stunning! The space creates a harmonious and inspiring environment!"
    ],
    "Comfort Feeling": [
        "",
        "🔴 It’s uncomfortable! it is a unwelcome place with no proper amenities",
        "🟡 It’s okay. I would stay here for a short time, but I wouldn’t stay for too long.",
        "🟢 I would feel at ease here, it is a very welcoming and relaxing place"
    ],
    "Educational Meaning": [
        "",
        "🔴 There’s no educational value here, it’s just a space without any explanation or purpose.",
        "🟡 There might be something to learn here, but it’s not very obvious or well-communicated.",
        "🟢 This place teaches me so much! The signage, plant diversity, make learning about nature engaging and insightful."
    ],
    "Opportunities for Recreation/Socialization": [
        "",
        "🔴 There’s no sense of community or opportunity for interaction in this place. I would not gather with friends and spend time for recreational activities here.",
        "🟡 I could practice some recreational activities here, but it doesn’t feel particularly social or dynamic.",
        "🟢 This is a vibrant space! It’s perfect for meeting friends, walking, and engaging with the community."
    ],
    "Opportunities for Biodiversity to Thrive": [
        "",
        "🔴 Weak – The site lacks diversity in both vegetation layers and species. Vegetation is sparse, with no signs of microhabitat features that support biodiversity.",
        "🟡 Moderate – The site shows some diversity in vegetation layers and species. Vegetation cover is moderate, and there are some, but limited microhabitat features that offer some support for biodiversity.",
        "🟢 Strong – The site show a rich diversity in vegetation layers and species. Vegetation is dense and well-distributed, with abundant microhabitat features."
    ],
    "Maintenance Efforts": [
        "",
        "🔴 High effort – The site present vegetation types and infrastructure that requires very frequently maintenance, such as mowing, trimming and inspections.",
        "🟡 Moderate effort – The site features elements that need only occasional maintenance to remain functional.",
        "🟢 Low effort – The site has resilient vegetation and minimal infrastructure features, which requires very little upkeep."
    ]
}

# ---------- Session State Setup ----------
if 'images_uploaded' not in st.session_state:
    st.session_state.images_uploaded = None
if 'active_image' not in st.session_state:
    st.session_state.active_image = 0
if 'responses' not in st.session_state:
    st.session_state.responses = [{} for _ in range(4)]
if 'show_summary' not in st.session_state:
    st.session_state.show_summary = False
if 'favorites' not in st.session_state:
    st.session_state.favorites = [False, False, False, False]
if 'comparison_notes' not in st.session_state:
    st.session_state.comparison_notes = ["", ""]
if 'viewing_comparison' not in st.session_state:
    st.session_state.viewing_comparison = False

# ---------- Re-upload Button ----------
if st.session_state.images_uploaded and not st.session_state.show_summary:
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🔄", help="Re-upload images"):
            st.session_state.images_uploaded = None
            st.session_state.active_image = 0
            st.session_state.responses = [{} for _ in range(4)]
            st.session_state.favorites = [False, False, False, False]
            st.session_state.comparison_notes = ["", ""]
            st.session_state.show_summary = False
            st.session_state.viewing_comparison = False
            st.rerun()

# ---------- Upload Section ----------
if not st.session_state.images_uploaded:
    uploaded_images = st.file_uploader(
        "Upload 4 Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
    )

    if uploaded_images and len(uploaded_images) == 4:
        st.session_state.images_uploaded = uploaded_images
        st.rerun()
    elif uploaded_images:
        st.warning("Please upload exactly 4 images.")

# ---------- Evaluation View ----------
elif not st.session_state.show_summary:
    uploaded_images = st.session_state.images_uploaded

    st.markdown("### Landscape Reflection and Evaluation")

    thumbnail_cols = st.columns(4)
    for i, col in enumerate(thumbnail_cols):
        with col:
            if st.button(f"Image {i+1}", key=f"thumb_button_{i}"):
                st.session_state.active_image = i
            st.image(uploaded_images[i], use_container_width=True)

    index = st.session_state.active_image
    st.image(uploaded_images[index], use_container_width=True)

    st.markdown("**How do you feel about this landscape?**")
    for criterion in group_reflection:
        response = st.selectbox(
            label=criterion,
            options=criterion_options[criterion],
            index=criterion_options[criterion].index(st.session_state.responses[index].get(criterion, "")),
            key=f"{criterion}_thumb_{index}"
        )
        st.session_state.responses[index][criterion] = response

    st.markdown("**See the impact of this landscape in the long term:**")
    for criterion in impact_visualization:
        response = st.selectbox(
            label=criterion,
            options=criterion_options[criterion],
            index=criterion_options[criterion].index(st.session_state.responses[index].get(criterion, "")),
            key=f"{criterion}_thumb_{index}"
        )
        st.session_state.responses[index][criterion] = response

    if st.button("💾 Save Progress for This Image"):
        st.success("Progress saved.")

    if st.button("📊 Go to Summary"):
        st.session_state.show_summary = True
        st.rerun()

# ---------- Comparison Page ----------
elif st.session_state.viewing_comparison:
    st.markdown("#### Your favorite landscape scenarios")
    st.caption("What types of activities do you see yourself doing on this landscape?")

    favorite_indices = [i for i, fav in enumerate(st.session_state.favorites) if fav]
    images = st.session_state.images_uploaded

    for idx, image_index in enumerate(favorite_indices):
        col_img, col_text = st.columns([2, 3])
        with col_img:
            st.markdown(f"**Image {image_index + 1}**")
            st.image(images[image_index], use_container_width=True)
        with col_text:
            st.session_state.comparison_notes[idx] = st.text_area(
                label="",
                value=st.session_state.comparison_notes[idx],
                key=f"note_{idx}",
                height=150
            )

    st.markdown("---")
    if st.button("🔙 Go Back to Summary"):
        st.session_state.viewing_comparison = False
        st.rerun()

    if st.button("✅ Submit All Reflections & Export to CSV"):
        data = []
        for i in range(4):
            image_label = f"Image {i+1}"
            note = ""
            if i in favorite_indices:
                idx = favorite_indices.index(i)
                note = st.session_state.comparison_notes[idx]
            for crit in all_criteria:
                rating = st.session_state.responses[i].get(crit, "")
                data.append({
                    "Image": image_label,
                    "Criterion": crit,
                    "Rating": rating,
                    "Note": note
                })

        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.success("Reflections submitted!")
        st.download_button(
            label="📥 Download Reflections CSV",
            data=csv_data,
            file_name="landscape_reflections.csv",
            mime="text/csv"
        )

# ---------- Summary Page ----------
elif st.session_state.show_summary:
    st.markdown("#### Summary of Evaluations")
    images = st.session_state.images_uploaded
    responses = st.session_state.responses

    star_cols = st.columns(5)
    star_cols[0].write("")
    for i in range(4):
        with star_cols[i + 1]:
            star_label = ("★" if st.session_state.favorites[i] else "☆") + f" Image {i+1}"
            if st.button(star_label, key=f"star_{i}"):
                st.session_state.favorites[i] = not st.session_state.favorites[i]
                if st.session_state.favorites.count(True) == 2:
                    st.session_state.viewing_comparison = True
                st.rerun()

    cols = st.columns(5)
    cols[0].markdown("**Criteria**")
    for i in range(4):
        with cols[i + 1]:
            st.image(images[i], use_container_width=True)

    for criterion in all_criteria:
        row = st.columns(5)
        row[0].markdown(f"**{criterion}**")
        for i in range(4):
            full_text = st.session_state.responses[i].get(criterion, "")
            emoji = full_text[:2] if full_text and full_text[0] in "🔴🟡🟢" else ""

            tooltip_html = f"""
            <div title="{full_text}" style='font-size: 1.2rem; text-align: center; cursor: help;'>
                {emoji}
            </div>
            """

            row[i + 1].markdown(tooltip_html, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔙 Go Back to Evaluation"):
        st.session_state.show_summary = False
        st.session_state.viewing_comparison = False
        st.rerun()
