import spacy
from spacy_streamlit import visualize_ner, visualize_tokens
from spacy.tokens import Doc
import streamlit as st
import jieba
from dragonmapper import hanzi, transcriptions
import requests 

# Global variables
MODELS = {"中文(zh_core_web_sm)": "zh_core_web_sm", 
          "English(en_core_web_sm)": "en_core_web_sm", 
          "日本語(ja_core_news_sm)": "ja_core_news_sm"}
models_to_display = list(MODELS.keys())
ZH_TEXT = "（中央社）中央流行疫情指揮中心宣布，今天國內新增60例COVID-19（2019冠狀病毒疾病），分別為49例境外移入，11例本土病例，是去年8月29日本土新增13例以來的新高，初步研判其中10例個案皆與桃園機場疫情有關。"
MOEDICT_URL = "https://www.moedict.tw/uni/"
ZH_REGEX = "\d{2,4}"
EN_TEXT = "(CNN) Covid-19 hospitalization rates among children are soaring in the United States, with an average of 4.3 children under 5 per 100,000 hospitalized with an infection as of the week ending January 1, up from 2.6 children the previous week, according to data from the US Centers for Disease Control and Prevention. This represents a 48% increase from the week ending December 4, and the largest increase in hospitalization rate this age group has seen over the course of the pandemic."
EN_REGEX = "(ed|ing)$"
JA_TEXT = "（朝日新聞）新型コロナウイルスの国内感染者は9日、新たに8249人が確認された。2日連続で8千人を超えたのは昨年9月11日以来、約4カ月ぶり。全国的に感染拡大が進む中、年をまたいだ1週間の感染者の過半数が30代以下だった。コロナ特措法に基づく「まん延防止等重点措置」が9日から適用された3県では、広島で過去最多の619人が確認された。"
JA_REGEX = "[たい]$"
DESCRIPTION = "spaCy自然語言處理模型展示"

# Custom tokenizer class
class JiebaTokenizer:
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        words = jieba.cut(text) # returns a generator
        tokens = list(words) # convert the genetator to a list
        spaces = [False] * len(tokens)
        doc = Doc(self.vocab, words=tokens, spaces=spaces)
        return doc

st.set_page_config(
    page_icon="🤠",
    layout="wide",
)

# Choose a language model
st.markdown(f"# {DESCRIPTION}") 
st.markdown("## 語言模型") 
selected_model = st.radio("請選擇語言", models_to_display)
nlp = spacy.load(MODELS[selected_model])
          
# Merge entity spans to tokens
nlp.add_pipe("merge_entities") 
st.markdown("---")

# Default text and regex
st.markdown("## 待分析文本") 
if selected_model == models_to_display[0]:
    # Select a tokenizer if the Chinese model is chosen
    selected_tokenizer = st.radio("請選擇斷詞模型", ["jieba-TW", "spaCy"])
    if selected_tokenizer == "jieba-TW":
        nlp.tokenizer = JiebaTokenizer(nlp.vocab)
    default_text = ZH_TEXT
    default_regex = ZH_REGEX
elif selected_model == models_to_display[1]:
    default_text = EN_TEXT 
    default_regex = EN_REGEX 
elif selected_model == models_to_display[2]:
    default_text = JA_TEXT
    default_regex = JA_REGEX 

text = st.text_area("",  default_text)
doc = nlp(text)
st.markdown("---")

# Two columns
left, right = st.columns(2)

with left:
    # Model output
    ner_labels = nlp.get_pipe("ner").labels
    visualize_ner(doc, labels=ner_labels, show_table=False, title="命名實體")
    visualize_tokens(doc, attrs=["text", "pos_", "dep_", "like_num", "head"], title="斷詞特徵")
    st.markdown("---")

with right:
    tokens = [tok.text for tok in doc]
    spaced_tokens = " | ".join(tokens)
    if selected_model == models_to_display[0]:    
        pinyin = hanzi.to_pinyin(spaced_tokens)
        st.markdown("## 原文") 
        st.write(spaced_tokens)
        st.markdown("## 拼音") 
        st.write(pinyin)
        st.markdown("## 動詞")
        verbs = [tok.text for tok in doc if tok.pos_ == "VERB"]
        if verbs:
            selected_verbs = st.multiselect("請選擇斷詞模型", verbs, verbs[0:1])
            for v in selected_verbs:
                st.write(f"### {v}")
                res = requests.get(MOEDICT_URL+v)
                if res:
                    with st.expander("點擊 + 查看單詞解釋"):
                        st.json(res.json())
                else:
                    st.write("查無結果")
            
        st.markdown("## 名詞")
        nouns = [tok.text for tok in doc if tok.pos_ == "NOUN"]
        if nouns:
            selected_nouns = st.multiselect("請選擇斷詞模型", nouns, nouns[0:1])
            for n in selected_nouns:
                st.write(f"### {n}")
                res = requests.get(MOEDICT_URL+n)
                if res:
                    with st.expander("點擊 + 查看單詞解釋"):
                        st.json(res.json())
                else:
                    st.write("查無結果")
