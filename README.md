# 📸 AI Notes to Calendar

**⚠️ Projeto em desenvolvimento (WIP)**

## 🎯 Sobre o Projeto

O **AI Notes to Calendar** é uma aplicação que transforma anotações manuscritas em eventos no Google Calendar automaticamente.

A ideia é simples: você tira uma foto de um caderno, a IA interpreta o conteúdo e agenda suas tarefas sem precisar digitar nada.

## 🚀 Como funciona

1. **Captura** — o usuário tira uma foto das anotações
2. **Upload** — a imagem é enviada para o backend
3. **Análise com IA** — extração de tarefas e datas
4. **Processamento** — conversão para formato estruturado
5. **Agendamento** — criação automática no Google Calendar

## 🛠️ Tecnologias (planejadas)

* Python
* Streamlit
* Google Calendar API
* Gemini / OpenAI (visão + LLM)
* python-dotenv

## 📌 Status

Projeto em fase inicial de desenvolvimento.
As funcionalidades serão implementadas em etapas.

## 💡 Objetivo

Este projeto tem como objetivo praticar:

* Integração com APIs externas
* Processamento de dados com IA
* Autenticação OAuth
* Desenvolvimento backend em Python

## ⚙️ Configuração

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
