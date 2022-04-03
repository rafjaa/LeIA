"""
LeIA.

LeIA (Léxico para Inferência Adaptada) é um fork do léxico e ferramenta para análise de sentimentos
VADER (Valence Aware Dictionary and sEntiment Reasoner) adaptado para textos em português,
com suporte para emojis e foco na análise de sentimentos de textos expressos em mídias sociais
- mas funcional para textos de outros domínios.
"""

__version__ = "0.1.1"
__author__ = 'Rafael J. A. Almeida'
__credits__ = ' Núcleo de Tecnologia da Informação (NTINF) da Universidade Federal de São João del-Rei - UFSJ'

from .leia import SentimentIntensityAnalyzer, SentiText, negated, normalize, allcap_differential, scalar_inc_dec