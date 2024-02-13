import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st

# Streamlitアプリケーションの作成
def app():
    st.title('薬事違反検出システム')

    # ユーザーがURLリスト(urls.csv)をアップロード
    uploaded_file = st.file_uploader("URLリスト(urls.csv)をアップロードしてください", type=['csv'])

    if uploaded_file is not None:
        urls_df = pd.read_csv(uploaded_file)
        urls = urls_df['URL'].tolist()

        # 辞書.csvと成分名.csvの内容を読み込む
        # これらのファイルはアプリケーションに組み込まれているか、あるいはアクセス可能なパスに配置されている必要があります。
        # 以下のパスは環境に合わせて適宜調整してください。
        dict_df = pd.read_csv('辞書.csv')
        component_df = pd.read_csv('成分名.csv')

        all_detected_results = []
        for url in urls:
            article_text = fetch_article_content(url)
            detected_words = detect_violations(article_text, dict_df, component_df)
            for result in detected_words:
                result['URL'] = url  # 検出された単語にURLを追加
                all_detected_results.append(result)

        # 検出結果を表示
        if all_detected_results:
            st.write(pd.DataFrame(all_detected_results))
        else:
            st.write("検出された薬事違反はありません。")

def fetch_article_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            article_text = soup.get_text(separator=' ', strip=True)
            return article_text
    except Exception as e:
        print(f"Error fetching the URL {url}: {e}")
    return ""

def detect_violations(article_text, dict_df, component_df):
    detected = []
    for _, row in dict_df.iterrows():
        search_term = row.get('検索用')
        word = row.get('単語')
        if (pd.notna(search_term) and search_term.lower() in article_text.lower()) or \
           (pd.notna(word) and word.lower() in article_text.lower()):
            reason = row.get('備考／解説', 'No specific reason')
            detected_word = search_term if pd.notna(search_term) else word
            detected.append({'単語': detected_word, '理由': reason})

    for _, row in component_df.iterrows():
        keyword = row.get('KW')
        if pd.notna(keyword) and keyword.lower() in article_text.lower():
            reason = row.get('修正タイトル', 'No specific reason from component name')
            detected.append({'単語': keyword, '理由': reason})

    return detected

if __name__ == '__main__':
    app()
