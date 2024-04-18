# GPT 20B Fine-tuning, RAG & Public API Deployment

## Overview
This project focuses on fine-tuning the GPT-neo-x model with 20B parameters using the arxiv-cs-ml Hugging Face dataset. <br><br>
Additionally, it implements QLoRA to significantly reduce the number of trainable parameters to 0.08%, enabling faster training within a Colab environment under 4-bits quantization. <br><br>
RAG (Retrieval-Augmented Generation) with cosine-similarity retrieval has been deployed to optimize model outputs and minimize hallucination. <br><br>
Lastly,  the LLM is enabled on a public url API.<br>

## Features
- Fine-tuned GPT-neo-x 20 B model on <code style="color : name_color">Hugging Face</code> with <code style="color : name_color">**QLoRA**</code>, reducing trainable parameters to 0.08%, facilitating faster training in <code style="color : name_color">4-bits quantization</code>.
- Utilized arxiv-cs-ml Hugging Face dataset for fine-tuning.
- Deployed <code style="color : name_color">RAG</code> with cosine-similarity retrieval to enhance output optimization and reduce hallucination.
- Deployed LLM API on public url with <code style="color : name_color">FastAPI & Ngrok</code>.

## Installation
1. Clone the repository;
2. Run all in <code style="color : name_color">Hosting an LLM as an API.ipynb</code> and enable <code style="color : name_color">ngrok authtoken</code>;
3. Run <code style="color : name_color">ChattyTune.py</code> for simple UI / Test in Colab.

## Reference
[Youtube for LLM API](https://www.youtube.com/watch?v=duV27TUwH7c)
