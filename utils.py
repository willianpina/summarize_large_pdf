import re
import numpy as np
import pandas as pd
import faiss
import openai
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAI, ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tqdm import tqdm
from config import set_environment

class PDFSummarizer:
    set_environment()
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.loader = PyPDFLoader(file_path=file_path) if file_path else None
        self.pages = None
        self.cleaned_text = None
        self.docs = None
        self.embeddings = None
        self.df = None
        self.index = None
        self.kmeans = None
        self.centroids = None
        self.sorted_array = None
        self.extracted_docs = None
        self.final_summary = ""

    def extract_text(self):
        if not self.loader:
            raise ValueError("File loader is not initialized.")
        self.pages = self.loader.load_and_split()
        text = ' '.join([page.page_content.replace('\t', ' ') for page in self.pages[2:]])
        return text

    @staticmethod
    def clean_text_method(text):
        cleaned_text = re.sub(r' +', ' ', text)
        cleaned_text = cleaned_text.replace('\n', ' ')
        cleaned_text = re.sub(r'\s*-\s*', '', cleaned_text)
        cleaned_text = re.sub(r'Licensed to Georgia Jacob Broliogeorgiabrolio@icloud\.com \d*', '', cleaned_text)
        cleaned_text = re.sub(r'Licensed to Georgia Jacob Broliogeorgiabrolio@icloud\.com', '', cleaned_text)
        cleaned_text = re.sub(r'Esta apostila foi preparada exclusivamente para os alunos do curso Política Internacional para Futuros Diplomatas e pertence unicamente à pessoa cujos dados estão marcados acima. Seu compartilhamento, comercialização ou reprodução, com ou sem fins lucrativos, são proibidos. Em caso de dúvidas, escreva para contato@cursocacd.com\.', '', cleaned_text, flags=re.DOTALL)
        cleaned_text = re.sub(r' +', ' ', cleaned_text).strip()
        return cleaned_text

    def process_text(self):
        text = self.extract_text()
        self.cleaned_text = self.clean_text_method(text)
        return self.cleaned_text

    def get_num_tokens(self, text):
        llm = OpenAI()
        tokens = llm.get_num_tokens(text)
        return tokens

    def create_documents(self):
        text_splitter = SemanticChunker(OpenAIEmbeddings(), breakpoint_threshold_type="interquartile")
        self.docs = text_splitter.create_documents([self.cleaned_text])
        return self.docs

    @staticmethod
    def get_embeddings(text):
        response = openai.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data

    def create_embeddings(self):
        content_list = [doc.page_content for doc in self.docs]
        self.embeddings = self.get_embeddings(content_list)
        vectors = [embedding.embedding for embedding in self.embeddings]
        array = np.array(vectors)
        embeddings_series = pd.Series(list(array))
        self.df = pd.DataFrame(content_list, columns=['page_content'])
        self.df['embeddings'] = embeddings_series
        return self.df

    def train_kmeans(self, num_clusters=50):
        array = np.array(self.df['embeddings'].tolist()).astype('float32')
        num_points = array.shape[0]
        num_clusters = min(num_clusters, num_points)
        dimension = array.shape[1]
        self.kmeans = faiss.Kmeans(dimension, num_clusters, niter=20, verbose=True)
        self.kmeans.train(array)
        self.centroids = self.kmeans.centroids
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(array)
        D, I = self.index.search(self.centroids, 1)
        self.sorted_array = np.sort(I, axis=0).flatten()
        self.extracted_docs = [self.docs[i] for i in self.sorted_array]
        return self.extracted_docs

    def summarize_documents(self, progress_callback=None):
        model = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        prompt = ChatPromptTemplate.from_template("""
            Você é uma aluna de relações internacionais e está estudando para uma prova. Você receberá os textos para resumir de forma natural e coerente.
            Busque destacar os aspectos mais importantes do texto em formato de bullet points.
            Evite fazer fazer menções do tipo "o texto diz que" ou "o autor afirma que".
            Caso você não tenha recebido o texto para fazer o resumo, não escreva nada, siga adiante. Seja direto e objetivo.
            TEXTO:
            ```{text}```
            RESUMO:
            """)
        chain = prompt | model

        for i, doc in enumerate(tqdm(self.extracted_docs, desc="Processing documents")):
            new_summary = chain.invoke({"text": doc.page_content})
            self.final_summary += new_summary.content
            if progress_callback:
                progress_callback((i + 1) / len(self.extracted_docs))

        return self.final_summary

    def run(self, progress_callback=None):
        self.process_text()
        self.create_documents()
        self.create_embeddings()
        self.train_kmeans()
        summary = self.summarize_documents(progress_callback)
        return summary
