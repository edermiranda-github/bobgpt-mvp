#!/usr/bin/env python3
"""
Script para criar dashboard no Google Looker Studio
conectado à planilha de feedback do Google Sheets
"""

import json
import requests
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import time

# Configurações
CREDENTIALS_FILE = '/home/ubuntu/mvp-feedback/google-credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/analytics.readonly'
]

def create_sample_data():
    """Cria dados de exemplo para demonstrar o dashboard"""
    
    # Carregar credenciais
    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    
    # Conectar ao Google Sheets
    sheets_service = build('sheets', 'v4', credentials=credentials)
    
    # Criar planilha de feedback
    spreadsheet_body = {
        'properties': {
            'title': 'Feedback - Casei com a Garota da Capa'
        },
        'sheets': [{
            'properties': {
                'title': 'Respostas'
            }
        }]
    }
    
    try:
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet_body
        ).execute()
        
        spreadsheet_id = spreadsheet['spreadsheetId']
        print(f"Planilha criada: {spreadsheet_id}")
        
        # Adicionar cabeçalhos
        headers = [
            'Timestamp', 'Idioma', 'Nota Capa', 'Nota Título', 
            'Nota História', 'Nota Recomendação', 'Feedback Texto', 'Feedback Audio'
        ]
        
        # Dados de exemplo
        sample_data = [
            headers,
            ['2025-01-02 10:30:00', 'pt', 5, 4, 5, 5, 'Livro incrível! A história me tocou profundamente.', ''],
            ['2025-01-02 11:15:00', 'en', 4, 5, 4, 4, 'Great book! Very inspiring story.', ''],
            ['2025-01-02 14:20:00', 'pt', 5, 5, 5, 5, 'Recomendo para todos! Uma jornada emocionante.', ''],
            ['2025-01-02 16:45:00', 'pt', 3, 4, 4, 3, 'Boa história, mas a capa poderia ser melhor.', ''],
            ['2025-01-02 18:30:00', 'en', 5, 5, 5, 5, 'Amazing journey! Loved every page.', ''],
            ['2025-01-02 20:10:00', 'pt', 4, 4, 5, 4, 'História inspiradora, me fez refletir muito.', '']
        ]
        
        # Inserir dados
        body = {
            'values': sample_data
        }
        
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Respostas!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Dados inseridos: {result.get('updatedCells')} células")
        
        # Tornar a planilha pública para leitura
        drive_service = build('drive', 'v3', credentials=credentials)
        
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission
        ).execute()
        
        print("Planilha configurada como pública para leitura")
        
        # URLs importantes
        sheets_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        looker_url = f"https://lookerstudio.google.com/reporting/create?c.reportId=new&ds.ds0.connector=sheets&ds.ds0.datasourceId={spreadsheet_id}"
        
        print(f"\n=== LINKS IMPORTANTES ===")
        print(f"Planilha Google Sheets: {sheets_url}")
        print(f"Criar Dashboard Looker Studio: {looker_url}")
        
        # Salvar informações em arquivo
        info = {
            'spreadsheet_id': spreadsheet_id,
            'sheets_url': sheets_url,
            'looker_url': looker_url,
            'webhook_url': 'https://bobgpt.app.n8n.cloud/webhook/feedback-webhook'
        }
        
        with open('/home/ubuntu/mvp-feedback/dashboard_info.json', 'w') as f:
            json.dump(info, f, indent=2)
        
        return spreadsheet_id, sheets_url, looker_url
        
    except Exception as e:
        print(f"Erro ao criar planilha: {e}")
        return None, None, None

def create_dashboard_template():
    """Cria template HTML para dashboard simples"""
    
    template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Feedback do Livro</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e3f2fd 0%, #f8f9fa 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #42a5f5;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1.1em;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }
        
        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
        }
        
        .feedback-list {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin-top: 30px;
        }
        
        .feedback-item {
            padding: 15px;
            border-left: 4px solid #64b5f6;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 0 10px 10px 0;
        }
        
        .feedback-meta {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
        }
        
        .feedback-text {
            font-style: italic;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard de Feedback</h1>
            <p>Casei com a Garota da Capa</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="totalRespostas">6</div>
                <div class="stat-label">Total de Respostas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="mediaGeral">4.5</div>
                <div class="stat-label">Média Geral</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="recomendacao">83%</div>
                <div class="stat-label">Taxa de Recomendação</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="idiomas">2</div>
                <div class="stat-label">Idiomas</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">Avaliações por Categoria</div>
                <canvas id="categoryChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">Distribuição de Notas</div>
                <canvas id="ratingChart"></canvas>
            </div>
        </div>
        
        <div class="feedback-list">
            <h2 style="margin-bottom: 20px; color: #333;">Últimos Feedbacks</h2>
            <div class="feedback-item">
                <div class="feedback-meta">02/01/2025 - Português - Notas: 5,4,5,5</div>
                <div class="feedback-text">"Livro incrível! A história me tocou profundamente."</div>
            </div>
            <div class="feedback-item">
                <div class="feedback-meta">02/01/2025 - English - Notas: 4,5,4,4</div>
                <div class="feedback-text">"Great book! Very inspiring story."</div>
            </div>
            <div class="feedback-item">
                <div class="feedback-meta">02/01/2025 - Português - Notas: 5,5,5,5</div>
                <div class="feedback-text">"Recomendo para todos! Uma jornada emocionante."</div>
            </div>
        </div>
    </div>
    
    <script>
        // Gráfico de Categorias
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'bar',
            data: {
                labels: ['Capa', 'Título', 'História', 'Recomendação'],
                datasets: [{
                    label: 'Média das Notas',
                    data: [4.3, 4.5, 4.7, 4.2],
                    backgroundColor: [
                        'rgba(100, 181, 246, 0.8)',
                        'rgba(66, 165, 245, 0.8)',
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(21, 101, 192, 0.8)'
                    ],
                    borderColor: [
                        'rgba(100, 181, 246, 1)',
                        'rgba(66, 165, 245, 1)',
                        'rgba(33, 150, 243, 1)',
                        'rgba(21, 101, 192, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5
                    }
                }
            }
        });
        
        // Gráfico de Distribuição
        const ratingCtx = document.getElementById('ratingChart').getContext('2d');
        new Chart(ratingCtx, {
            type: 'doughnut',
            data: {
                labels: ['5 Estrelas', '4 Estrelas', '3 Estrelas', '2 Estrelas', '1 Estrela'],
                datasets: [{
                    data: [12, 8, 2, 1, 0],
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(100, 181, 246, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(244, 67, 54, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>"""
    
    with open('/home/ubuntu/mvp-feedback/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("Dashboard template criado: dashboard.html")

if __name__ == "__main__":
    print("=== Configurando Dashboard de Feedback ===\n")
    
    # Criar planilha e dados de exemplo
    spreadsheet_id, sheets_url, looker_url = create_sample_data()
    
    if spreadsheet_id:
        print(f"\n✅ Planilha configurada com sucesso!")
        print(f"ID: {spreadsheet_id}")
        
        # Criar dashboard template
        create_dashboard_template()
        print(f"✅ Dashboard template criado!")
        
        print(f"\n=== PRÓXIMOS PASSOS ===")
        print(f"1. Acesse a planilha: {sheets_url}")
        print(f"2. Para criar dashboard no Looker Studio: {looker_url}")
        print(f"3. Ou use o dashboard local: http://localhost:8080/dashboard.html")
        
    else:
        print("❌ Erro ao configurar planilha")

