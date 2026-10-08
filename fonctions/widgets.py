"""Native optional selectors supported by current Streamlit."""
import streamlit as st

def selectbox(label, options, **kwargs):
    kwargs.setdefault('index', None)
    return st.selectbox(label, options, **kwargs)

def button_selector(options, **kwargs):
    choices = list(options)
    selected = st.segmented_control('Vue / View', choices, default=choices[0], **kwargs)
    return choices.index(selected) if selected in choices else 0
