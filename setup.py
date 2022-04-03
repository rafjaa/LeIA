from setuptools import setup

setup(
    name='LeIA',
    version='0.1.1',
    description='LeIA (Léxico para Inferência Adaptada) é um fork do léxico e ferramenta para análise de sentimentos VADER (Valence Aware Dictionary and sEntiment Reasoner) adaptado para textos em português, com suporte para emojis e foco na análise de sentimentos de textos expressos em mídias sociais - mas funcional para textos de outros domínios.',
    url='https://github.com/rafjaa/LeIA',
    author='Rafael J. A. Almeida',
    author_email='rafael@email.com',
    license='MIT',
    packages=['LeIA'],
    install_requires=[],

    classifiers=[
        'Development Status :: Published',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)