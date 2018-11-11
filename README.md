# Análise de Sentimentos em Português

LeIA (Léxico para Inferência Adaptada) é um fork do léxico e ferramenta para análise de sentimentos <a href="https://github.com/cjhutto/vaderSentiment">VADER</a> (Valence Aware Dictionary and sEntiment Reasoner) adaptado para textos em português, com suporte para emojis e foco na análise de sentimentos de textos expressos em mídias sociais - mas funcional para textos de outros domínios.


Modo de uso
-----------
A biblioteca preserva a API do VADER, e o texto de entrada não precisa ser pré-processado:

<pre>
from leia import SentimentIntensityAnalyzer 

s = SentimentIntensityAnalyzer()

# Análise de texto simples
s.polarity_scores('Eu estou feliz')
#{'neg': 0.0, 'neu': 0.328, 'pos': 0.672, 'compound': 0.6249}

# Análise de texto com emoji :)
s.polarity_scores('Eu estou feliz :)')
#{'neg': 0.0, 'neu': 0.22, 'pos': 0.78, 'compound': 0.7964}

# Análise de texto com negação
s.polarity_scores('Eu não estou feliz')
#{'neg': 0.265, 'neu': 0.241, 'pos': 0.494, 'compound': 0.4404}
</pre>

A saída da análise de sentimentos é um dicionário com os seguintes campos:

- <code>pos</code>: porcentagem positiva do texto
- <code>neg</code>: porcentagem negativa do texto
- <code>neu</code>: porcentagem neutra do texto
- <code>compound</code>: valor de sentimento geral normalizado, variando de -1 (extremamente negativo) a +1 (extremamente positivo)

O valor <code>compound</code> pode ser utilizado para descrever o sentimento predominante no texto, por meio dos limites de valores:

- Sentimento positivo: <code>compound >= 0.05</code>
- Sentimento negativo: <code>compound <= -0.05</code>
- Sentimento neutro: <code>(compound > -0.05) and (compound < 0.05)</code>


Citação (BibTeX)
----------------
Se você utilizar este projeto em sua pesquisa, considere citar o repositório:

<pre>
@misc{Almeida2018,
  author = {Almeida, Rafael J. A.},
  title = {LeIA - Léxico para Inferência Adaptada},
  year = {2018},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/rafjaa/LeIA}}
}
</pre>


O léxico VADER original é descrito no _paper_:

<pre>
@inproceedings{gilbert2014vader,
  title={Vader: A parsimonious rule-based model for sentiment analysis of social media text},
  author={Gilbert, CJ Hutto Eric},
  booktitle={Eighth International Conference on Weblogs and Social Media (ICWSM-14). Available at (20/04/16) http://comp. social. gatech. edu/papers/icwsm14. vader. hutto. pdf},
  year={2014}
}
</pre>
