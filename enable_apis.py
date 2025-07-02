#!/usr/bin/env python3
"""
Script para habilitar APIs necessárias no Google Cloud
"""

import json
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Configurações
CREDENTIALS_FILE = '/home/ubuntu/mvp-feedback/google-credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/service.management'
]

def enable_apis():
    """Habilita as APIs necessárias"""
    
    # Carregar credenciais
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    
    # Obter project_id do arquivo de credenciais
    with open(CREDENTIALS_FILE, 'r') as f:
        creds_data = json.load(f)
        project_id = creds_data['project_id']
    
    print(f"Project ID: {project_id}")
    
    # APIs para habilitar
    apis_to_enable = [
        'sheets.googleapis.com',
        'drive.googleapis.com',
        'serviceusage.googleapis.com'
    ]
    
    try:
        # Conectar ao Service Usage API
        service = build('serviceusage', 'v1', credentials=credentials)
        
        for api in apis_to_enable:
            print(f"Habilitando API: {api}")
            
            # Habilitar API
            operation = service.services().enable(
                name=f'projects/{project_id}/services/{api}'
            ).execute()
            
            print(f"✅ API {api} habilitada com sucesso!")
            
        print(f"\n✅ Todas as APIs foram habilitadas!")
        return True
        
    except Exception as e:
        print(f"Erro ao habilitar APIs: {e}")
        return False

if __name__ == "__main__":
    print("=== Habilitando APIs do Google Cloud ===\n")
    
    if enable_apis():
        print("\n=== APIs habilitadas com sucesso! ===")
        print("Aguarde alguns minutos e execute novamente o script do dashboard.")
    else:
        print("\n❌ Erro ao habilitar APIs")

