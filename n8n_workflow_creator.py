#!/usr/bin/env python3
"""
Script para criar workflow no n8n via API
Este script cria o workflow de automação para o MVP de feedback do livro
"""

import requests
import json
import base64

# Configurações do n8n
N8N_URL = "https://bobgpt.app.n8n.cloud"
N8N_EMAIL = "edersouzamiranda@gmail.com"
N8N_PASSWORD = "28:vWZd;pNw'AD;"

def authenticate_n8n():
    """Autentica no n8n e retorna o token de sessão"""
    login_url = f"{N8N_URL}/rest/login"
    
    login_data = {
        "emailOrLdapLoginId": N8N_EMAIL,
        "password": N8N_PASSWORD
    }
    
    session = requests.Session()
    response = session.post(login_url, json=login_data)
    
    if response.status_code == 200:
        print("✅ Autenticação no n8n realizada com sucesso")
        return session
    else:
        print(f"❌ Erro na autenticação: {response.status_code}")
        print(response.text)
        return None

def create_workflow(session):
    """Cria o workflow de automação para o MVP"""
    
    # Definição do workflow
    workflow_data = {
        "name": "MVP Feedback Livro - Automação",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "feedback-webhook",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "id": "webhook-node",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "webhookId": "feedback-webhook"
            },
            {
                "parameters": {
                    "url": "={{ $json.feedback_audio }}",
                    "options": {
                        "response": {
                            "response": {
                                "responseFormat": "file"
                            }
                        }
                    }
                },
                "id": "download-audio",
                "name": "Download Audio",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300],
                "continueOnFail": true
            },
            {
                "parameters": {
                    "authentication": "serviceAccount",
                    "serviceAccountEmail": "agente-manus-mvp@manus-bobgpt.iam.gserviceaccount.com",
                    "operation": "upload",
                    "fileId": {
                        "__rl": true,
                        "value": "1BQxvQqJ8K9vZ2mF3nH4pL5rS6tU7wX8y",
                        "mode": "list",
                        "cachedResultName": "Áudios do Feedback MVP"
                    },
                    "name": "=audio_{{ $('Webhook').item.json.timestamp }}.{{ $json.fileExtension }}",
                    "options": {}
                },
                "id": "upload-to-drive",
                "name": "Upload to Google Drive",
                "type": "n8n-nodes-base.googleDrive",
                "typeVersion": 3,
                "position": [680, 300],
                "continueOnFail": true,
                "credentials": {
                    "googleApi": {
                        "id": "google-service-account",
                        "name": "Google Service Account"
                    }
                }
            },
            {
                "parameters": {
                    "authentication": "serviceAccount",
                    "serviceAccountEmail": "agente-manus-mvp@manus-bobgpt.iam.gserviceaccount.com",
                    "operation": "appendOrUpdate",
                    "documentId": {
                        "__rl": true,
                        "value": "1ABC123DEF456GHI789JKL",
                        "mode": "list",
                        "cachedResultName": "Feedback do Livro MVP"
                    },
                    "sheetName": {
                        "__rl": true,
                        "value": "gid=0",
                        "mode": "list",
                        "cachedResultName": "Sheet1"
                    },
                    "columnToMatchOn": "A",
                    "valueToMatchOn": "={{ $('Webhook').item.json.timestamp }}",
                    "options": {
                        "cellFormat": "USER_ENTERED",
                        "useAppend": true
                    },
                    "dataToSend": "defineBelow",
                    "valuesToSend": {
                        "IdiomaSelecionado": "={{ $('Webhook').item.json.idioma }}",
                        "Timestamp": "={{ $('Webhook').item.json.timestamp }}",
                        "NotaCapa": "={{ $('Webhook').item.json.nota_capa }}",
                        "NotaTitulo": "={{ $('Webhook').item.json.nota_titulo }}",
                        "NotaHistoria": "={{ $('Webhook').item.json.nota_historia }}",
                        "NotaRecomendacao": "={{ $('Webhook').item.json.nota_recomendacao }}",
                        "FeedbackTexto": "={{ $('Webhook').item.json.feedback_texto || '' }}",
                        "FeedbackAudioLink": "={{ $('Upload to Google Drive').item.json.webViewLink || '' }}"
                    }
                },
                "id": "save-to-sheets",
                "name": "Save to Google Sheets",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4,
                "position": [900, 300],
                "credentials": {
                    "googleApi": {
                        "id": "google-service-account",
                        "name": "Google Service Account"
                    }
                }
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ { \"status\": \"success\", \"message\": \"Feedback recebido com sucesso!\" } }}"
                },
                "id": "response-node",
                "name": "Response",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1120, 300]
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {
                            "node": "Download Audio",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Download Audio": {
                "main": [
                    [
                        {
                            "node": "Upload to Google Drive",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Upload to Google Drive": {
                "main": [
                    [
                        {
                            "node": "Save to Google Sheets",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Save to Google Sheets": {
                "main": [
                    [
                        {
                            "node": "Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {
            "executionOrder": "v1"
        },
        "pinData": {},
        "versionId": "1"
    }
    
    # Criar o workflow
    create_url = f"{N8N_URL}/rest/workflows"
    response = session.post(create_url, json=workflow_data)
    
    if response.status_code == 200 or response.status_code == 201:
        workflow_info = response.json()
        print("✅ Workflow criado com sucesso!")
        print(f"ID do Workflow: {workflow_info.get('id')}")
        
        # Obter a URL do webhook
        webhook_url = f"{N8N_URL}/webhook/feedback-webhook"
        print(f"🔗 URL do Webhook: {webhook_url}")
        
        return workflow_info, webhook_url
    else:
        print(f"❌ Erro ao criar workflow: {response.status_code}")
        print(response.text)
        return None, None

def setup_google_credentials(session):
    """Configura as credenciais do Google Service Account"""
    
    # Ler o arquivo de credenciais
    with open('/home/ubuntu/mvp-feedback/google-credentials.json', 'r') as f:
        credentials_data = json.load(f)
    
    # Configurar credencial no n8n
    credential_data = {
        "name": "Google Service Account",
        "type": "googleApi",
        "data": {
            "serviceAccountEmail": credentials_data["client_email"],
            "privateKey": credentials_data["private_key"]
        }
    }
    
    create_cred_url = f"{N8N_URL}/rest/credentials"
    response = session.post(create_cred_url, json=credential_data)
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ Credenciais do Google configuradas com sucesso!")
        return response.json()
    else:
        print(f"❌ Erro ao configurar credenciais: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🚀 Iniciando configuração do n8n...")
    
    # Autenticar
    session = authenticate_n8n()
    if not session:
        return
    
    # Configurar credenciais do Google
    print("\n📋 Configurando credenciais do Google...")
    setup_google_credentials(session)
    
    # Criar workflow
    print("\n⚙️ Criando workflow de automação...")
    workflow_info, webhook_url = create_workflow(session)
    
    if workflow_info and webhook_url:
        print("\n🎉 Configuração do n8n concluída!")
        print(f"🔗 URL do Webhook para usar no Typebot: {webhook_url}")
        
        # Salvar informações importantes
        with open('/home/ubuntu/mvp-feedback/webhook_info.txt', 'w') as f:
            f.write(f"Webhook URL: {webhook_url}\n")
            f.write(f"Workflow ID: {workflow_info.get('id')}\n")
        
        return webhook_url
    else:
        print("❌ Falha na configuração do n8n")
        return None

if __name__ == "__main__":
    webhook_url = main()

