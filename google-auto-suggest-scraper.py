import streamlit as st
import pandas as pd
import requests

def install_bs4():
  subprocess.check_call([sys.executable, "-m", "pip", "install", "bs4"])

try:
  from bs4 import BeautifulSoup
except:
  install_bs4()
  from bs4 import BeautifulSoup

def get_google_suggestions(query, hl='en'):
    url = f"https://www.google.com/complete/search?hl={hl}&output=toolbar&q={query}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'xml')
    suggestions = [suggestion['data'] for suggestion in soup.find_all('suggestion')]
    return suggestions

def get_extended_suggestions(base_query, hl='en'):
    extended_suggestions = set()
    extended_suggestions.update(get_google_suggestions(base_query, hl))
    for char in 'abcdefghijklmnopqrstuvwxyz':
        extended_suggestions.update(get_google_suggestions(base_query + ' ' + char, hl))
    return list(extended_suggestions)

def capture_suggestions(header, query, all_suggestions):
    st.write(f"\n{header}:")
    suggestions = get_extended_suggestions(query)
    all_suggestions[header] = suggestions
    for i, suggestion in enumerate(suggestions, 1):
        st.write(f"{i}. {suggestion}")

def download_csv(all_suggestions):
    df = pd.DataFrame({k: pd.Series(v) for k, v in all_suggestions.items()})
    return df.to_csv().encode('utf-8')

base_query = st.text_input("Enter a search query: ")

if base_query:
    all_suggestions = {}
    capture_suggestions("Google Suggest completions", base_query, all_suggestions)
    capture_suggestions("Can questions", "Can " + base_query, all_suggestions)
    capture_suggestions("How questions", "How " + base_query, all_suggestions)
    capture_suggestions("Where questions", "Where " + base_query, all_suggestions)
    capture_suggestions("Versus", base_query + " versus", all_suggestions)
    capture_suggestions("For", base_query + " for", all_suggestions)

    st.download_button(
        label="Download CSV",
        data=download_csv(all_suggestions),
        file_name="google_suggestions.csv",
        mime='text/csv'
    )
