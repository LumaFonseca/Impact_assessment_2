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
    "Kauneuden kokemus",
    "Mukavuuden tunne",
    "Luonnosta oppiminen",
    "Mahdollisuudet virkistäytymiseen ja sosiaaliseen kanssakäymiseen"
]

impact_visualization = [
    "Monimuotoisuuden edistäminen",
    "Kunnossapidon tarve",
    "Hulevesien suodatus ja hallinta"
]

all_criteria = group_reflection + impact_visualization

criterion_options = {
    "Kauneuden kokemus": [
        "",
        "🔴 Maisema näyttää rumalta, eikä siinä ole kauneuden tai luovuuden tunnetta.",
        "🟡 Maisema näyttää ihan tavalliselta, siinä ei ole mitään erityistä mutta se sopii hyvin ympäristöön.",
        "🟢 Maisema näyttää upealta! Se tuntuu inspiroivalta ja eläväiseltä."
    ],
    "Mukavuuden tunne": [
        "",
        "🔴 Maisema näyttää epämukavalta. Se ei ole kutsuva eikä siellä ole mukavuuksia.",
        "🟡 Maisema näyttää ihan tavalliselta. Olisin täällä hetken, mutta en pysyisi kauaa.",
        "🟢 Kokisin täällä rauhan tunteen, se on kutsuva ja rentouttava paikka."
    ],
    "Luonnosta oppiminen": [
        "",
        "🔴 Täällä ei ole oppimisen mahdollisuuksia, se on vain tila ilman mitään selitystä tai tarkoitusta.",
        "🟡 Täällä voisi oppia jotain, mutta se ei ole kovin selkeästi esitetty.",
        "🟢 Tämä paikka voisi opettaa minulle paljon. Opasteet ja luonnon monimuotoisuus mahdollistavat luonnosta oppimisen kiinnostavin tavoin."
    ],
    "Mahdollisuudet virkistäytymiseen ja sosiaaliseen kanssakäymiseen": [
        "",
        "🔴 Täällä ei ole yhteisöllisyyden tunnetta tai mahdollisuuksia sosiaaliseen kanssakäymiseen.",
        "🟡 Voisin tehdä jotain aktiviteetteja täällä mutta se ei tunnu kovin virkistävältä paikalta.",
        "🟢 Tämä on eläväinen paikka! Se on täydellinen paikka muiden tapaamiseen, kävelemiseen ja yhteisön kanssa kokoontumiseen."
    ],
    "Monimuotoisuuden edistäminen": [
        "",
        "🔴 Heikko – Maisemassa ei ole monimuotoisuutta.",
        "🟡 Keskimääräinen – Maisemassa on hieman monimuotoisuutta.",
        "🟢 Vahva – Maisemassa on paljon monimuotoisuutta."
    ],
    "Kunnossapidon tarve": [
        "",
        "🔴 Korkea kunnossapidon tarve.",
        "🟡 Keskikohtainen kunnossapidon tarve.",
        "🟢 Matala kunnossapidon tarve."
    ],
    "Hulevesien suodatus ja hallinta": [
        "",
        "🔴 Heikko – paljon päällystettyjä pintoja.",
        "🟡 Keskikohtainen – joitain läpäiseviä pintoja.",
        "🟢 Erinomainen – paljon läpäisevää maaperää ja kasvillisuutta."
    ]
}

# ---------- Session State Setup ----------
if 'images_uploaded' not in st.session_state:
    st.session_state.images_uploaded = None
if 'active_image' not in st.session_state:
    st.session_state.active_image = 0
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'show_summary' not in st.session_state:
    st.session_state.show_summary = False
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
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
            st.session_state.responses = []
            st.session_state.favorites = []
            st.session_state.comparison_notes = ["", ""]
            st.session_state.show_summary = False
            st.session_state.viewing_comparison = False
            st.rerun()

# ---------- Upload Section ----------
if not st.session_state.images_uploaded:
    uploaded_images = st.file_uploader(
        "Upload 1 to 4 Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
    )

    if uploaded_images and 1 <= len(uploaded_images) <= 4:
        st.session_state.images_uploaded = uploaded_images
        num_images = len(uploaded_images)
        st.session_state.responses = [{} for _ in range(num_images)]
        st.session_state.favorites = [False for _ in range(num_images)]
        st.session_state.comparison_notes = ["", ""]
        st.session_state.active_image = 0
        st.session_state.show_summary = False
        st.session_state.viewing_comparison = False
        st.rerun()
    elif uploaded_images:
        st.warning("Please upload between 1 and 4 images.")

# ---------- Evaluation View ----------
elif not st.session_state.show_summary:
    uploaded_images = st.session_state.images_uploaded
    num_images = len(uploaded_images)

    st.markdown("### Maiseman reflektointi ja arviointi")

    thumbnail_cols = st.columns(num_images)
    for i, col in enumerate(thumbnail_cols):
        with col:
            if st.button(f"Kuva {i+1}", key=f"thumb_button_{i}"):
                st.session_state.active_image = i
            st.image(uploaded_images[i], use_container_width=True)

    index = st.session_state.active_image
    st.image(uploaded_images[index], use_container_width=True)

    st.markdown("**Minkälaisena koet tämän maiseman?**")
    for criterion in group_reflection:
        response = st.selectbox(
            label=criterion,
            options=criterion_options[criterion],
            index=criterion_options[criterion].index(st.session_state.responses[index].get(criterion, "")),
            key=f"{criterion}_thumb_{index}"
        )
        st.session_state.responses[index][criterion] = response

    st.markdown("**Maiseman vaikutus pitkällä aikavälillä:**")
    for criterion in impact_visualization:
        response = st.selectbox(
            label=criterion,
            options=criterion_options[criterion],
            index=criterion_options[criterion].index(st.session_state.responses[index].get(criterion, "")),
            key=f"{criterion}_impact_{index}"
        )
        st.session_state.responses[index][criterion] = response

    if st.button("💾 Save Progress for This Image"):
        st.success("Progress saved.")

    if st.button("📊 Go to Summary"):
        st.session_state.show_summary = True
        st.rerun()

# ---------- Comparison Page ----------
elif st.session_state.viewing_comparison:
    st.markdown("#### Sinun lempi maisemakuvat")
    st.caption("Mitä aktiviteettejä voisit kuvitella tekeväsi tässä maisemassa?")

    favorite_indices = [i for i, fav in enumerate(st.session_state.favorites) if fav]
    images = st.session_state.images_uploaded

    for idx, image_index in enumerate(favorite_indices):
        col_img, col_text = st.columns([2, 3])
        with col_img:
            st.markdown(f"**Kuva {image_index + 1}**")
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
        for i in range(len(images)):
            image_label = f"Kuva {i+1}"
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
    images = st.session_state.images_uploaded
    responses = st.session_state.responses
    num_images = len(images)

    st.markdown("#### Arvioinnin yhteenveto")

    star_cols = st.columns(num_images + 1)
    star_cols[0].write("")
    for i in range(num_images):
        with star_cols[i + 1]:
            star_label = ("★" if st.session_state.favorites[i] else "☆") + f" Kuva {i+1}"
            if st.button(star_label, key=f"star_{i}"):
                if not st.session_state.favorites[i]:
                    # Only allow selecting if fewer than 2 are already selected
                    if st.session_state.favorites.count(True) < 2:
                        st.session_state.favorites[i] = True
                else:
                    # Allow unselecting
                    st.session_state.favorites[i] = False
                st.rerun()

    cols = st.columns(num_images + 1)
    cols[0].markdown("**kriteerit**")
    for i in range(num_images):
        with cols[i + 1]:
            st.image(images[i], use_container_width=True)

    for criterion in all_criteria:
        row = st.columns(num_images + 1)
        row[0].markdown(f"**{criterion}**")
        for i in range(num_images):
            full_text = st.session_state.responses[i].get(criterion, "")
            emoji = full_text[:2] if full_text and full_text[0] in "🔴🟡🟢" else ""

            tooltip_html = f"""
            <div title="{full_text}" style='font-size: 1.2rem; text-align: center; cursor: help;'>
                {emoji}
            </div>
            """
            row[i + 1].markdown(tooltip_html, unsafe_allow_html=True)

    st.markdown("---")

    # If 1 or 2 favorites have been selected, show the button to continue
    if 1 <= st.session_state.favorites.count(True) <= 2:
        if st.button("➡️ Siirry vertailemaan suosikkikuvia"):
            st.session_state.viewing_comparison = True
            st.rerun()
    else:
        st.info("Valitse yksi tai kaksi lempikuvaasi")

    if st.button("🔙 Palaa arviointiin"):
        st.session_state.show_summary = False
        st.session_state.viewing_comparison = False
        st.rerun()