import streamlit as st
import pandas as pd
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
import os

# Set the path to the nltk_data folder in your project
nltk_data_path = os.path.join(os.getcwd(), "punkt_tab")  # Adjusted path to your local punkt_tab directory

# Point NLTK to this folder
nltk.data.path.append(nltk_data_path)

# Ensure the punkt tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    st.error("❌ NLTK punkt tokenizer not found. Please make sure it's included in your project.")
    st.stop()  # Stop the app gracefully if the corpus is missing

def load_sample_texts():
    """
    Loads climate-related narrative and returns as list of sentences.
    """
    text = """
    Nepal’s monsoon season often brings heavy rains, causing nationwide floods and landslides.
    In July 2024, western Nepal recorded its highest rainfall ever—624 mm in 24 hours—
    causing damage to infrastructure, water supply, irrigation and agriculture worth USD 11 million.
    This surpassed the previous record of 540 mm in Kulekhani in July 1993.

    The extreme rainfall from September 2024, resulted in over 250 fatalities and USD 342 million 
    in damages to different sectors such as hydropower, water supply, road, houses, and irrigation, 
    and unprecedented flooding in Kathmandu.

    Meanwhile, warming temperatures over the last three decades have caused the glacier area in 
    Nepal to decrease by 25%. High-elevation areas are warming faster than lower ones, a phenomenon 
    known as “elevation-dependent warming.” This trend may reduce glacier ice mass by up to two-thirds 
    in the Himalayan region if the current trends in greenhouse gas emissions continue.

    Even in the optimistic scenarios of the 1.5-degree world, one third of the glacier ice would be gone 
    in the Himalayan region. This may cause an increase in melt runoff or ‘peak flows’ in the coming decades. 
    Peak flow in the central Himalayas is expected to occur towards the mid-century, followed by decreased glacier flow, 
    adversely affecting downstream communities that rely on glacier meltwater.
    """

    # Split into sentences
    blob = TextBlob(text)
    return [str(sentence).strip() for sentence in blob.sentences]

def analyze_sentiment(texts):
    """
    Returns a DataFrame with sentiment polarity and subjectivity.
    """
    results = []
    for sentence in texts:
        blob = TextBlob(sentence)
        results.append({
            "Text": sentence,
            "Polarity": round(blob.sentiment.polarity, 3),
            "Subjectivity": round(blob.sentiment.subjectivity, 3)
        })
    return pd.DataFrame(results)

def extract_keywords(texts, num_keywords=10):
    """
    Extracts most frequent keywords from the input texts.
    """
    all_words = []
    for text in texts:
        blob = TextBlob(text.lower())
        all_words += blob.words

    common_words = Counter(all_words).most_common(num_keywords)
    return pd.DataFrame(common_words, columns=["Keyword", "Frequency"])

def plot_wordcloud(texts):
    """
    Generate and display a word cloud from input texts.
    """
    combined_text = " ".join(texts)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
