from datetime import datetime
import random
from PIL import Image
import io
import base64
import requests
import json
import streamlit as st


def process_uploaded_file(uploaded_file):
    """Process uploaded image file and return base64 encoded string."""
    if uploaded_file is not None:
        try:
            bytes_data = uploaded_file.getvalue()
            img = Image.open(io.BytesIO(bytes_data))
            img.verify()
            base64_str = base64.b64encode(bytes_data).decode("utf-8")
            return base64_str
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
    return None
