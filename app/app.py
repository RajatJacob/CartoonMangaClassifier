import streamlit as st
from PIL import Image
import joblib
import numpy as np


@st.cache_resource()
def load_model():
    svc = joblib.load('image_to_features_model.joblib')
    model = joblib.load('features_to_classes.joblib')
    class_names = ['Cartoon', 'Manga']

    def classify_image(img: Image):
        label = svc.predict(model.predict(np.array([img])))[0]
        return class_names[label]

    return classify_image


def main():
    st.title("Image Uploader")
    classify_image = load_model()

    uploaded_image = st.file_uploader(
        "Choose an image...",
        type=["jpg", "jpeg", "png"]
    )
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        label = classify_image(image)
        st.markdown(f'# {label}')
        st.image(image, caption="Uploaded Image",
                 use_column_width=True)


if __name__ == "__main__":
    main()
