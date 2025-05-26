#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para gerar um diagrama simples da arquitetura do sistema de Quiz.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configuração da figura
plt.figure(figsize=(10, 6))
ax = plt.gca()
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Cores
redis_color = '#DC382D'  # Vermelho do Redis
postgres_color = '#336791'  # Azul do PostgreSQL
arrow_color = '#555555'
bg_color = '#F5F5F5'

# Desenhar os componentes
# Redis
redis_box = patches.Rectangle((1, 3.5), 2, 1.5, linewidth=2, edgecolor=redis_color, facecolor='white', alpha=0.8)
ax.add_patch(redis_box)
plt.text(2, 4.25, 'Redis', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(2, 3.85, 'Banco em Memória', ha='center', va='center', fontsize=10)

# Mecanismo de Ingestão
ingest_box = patches.Rectangle((4, 3.5), 2, 1.5, linewidth=2, edgecolor='green', facecolor='white', alpha=0.8)
ax.add_patch(ingest_box)
plt.text(5, 4.25, 'Mecanismo de', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(5, 3.85, 'Ingestão', ha='center', va='center', fontsize=14, fontweight='bold')

# PostgreSQL
pg_box = patches.Rectangle((7, 3.5), 2, 1.5, linewidth=2, edgecolor=postgres_color, facecolor='white', alpha=0.8)
ax.add_patch(pg_box)
plt.text(8, 4.25, 'PostgreSQL', ha='center', va='center', fontsize=14, fontweight='bold')
plt.text(8, 3.85, 'Data Warehouse', ha='center', va='center', fontsize=10)

# Setas
# Redis para Ingestão
arrow1 = patches.FancyArrowPatch((3, 4), (4, 4), 
                                connectionstyle="arc3,rad=0", 
                                arrowstyle='->', 
                                mutation_scale=20, 
                                linewidth=2, 
                                color=arrow_color)
ax.add_patch(arrow1)

# Ingestão para PostgreSQL
arrow2 = patches.FancyArrowPatch((6, 4), (7, 4), 
                                connectionstyle="arc3,rad=0", 
                                arrowstyle='->', 
                                mutation_scale=20, 
                                linewidth=2, 
                                color=arrow_color)
ax.add_patch(arrow2)

# Dados de entrada
data_in_box = patches.Rectangle((1, 1), 2, 1.5, linewidth=2, edgecolor='#888888', facecolor='white', alpha=0.8)
ax.add_patch(data_in_box)
plt.text(2, 1.75, 'Dados do Quiz', ha='center', va='center', fontsize=12, fontweight='bold')
plt.text(2, 1.35, 'Questões e Respostas', ha='center', va='center', fontsize=10)

# Seta de dados para Redis
arrow3 = patches.FancyArrowPatch((2, 2.5), (2, 3.5), 
                                connectionstyle="arc3,rad=0", 
                                arrowstyle='->', 
                                mutation_scale=20, 
                                linewidth=2, 
                                color=arrow_color)
ax.add_patch(arrow3)

# Indicadores
indicators_box = patches.Rectangle((7, 1), 2, 1.5, linewidth=2, edgecolor='#888888', facecolor='white', alpha=0.8)
ax.add_patch(indicators_box)
plt.text(8, 1.75, 'Indicadores', ha='center', va='center', fontsize=12, fontweight='bold')
plt.text(8, 1.35, 'Análises e Relatórios', ha='center', va='center', fontsize=10)

# Seta de PostgreSQL para Indicadores
arrow4 = patches.FancyArrowPatch((8, 3.5), (8, 2.5), 
                                connectionstyle="arc3,rad=0", 
                                arrowstyle='->', 
                                mutation_scale=20, 
                                linewidth=2, 
                                color=arrow_color)
ax.add_patch(arrow4)

# Título
plt.text(5, 5.5, 'Arquitetura do Sistema de Quiz', ha='center', va='center', fontsize=16, fontweight='bold')

# Salvar a figura
plt.savefig('/home/ubuntu/projeto-quiz/docs/arquitetura.png', dpi=300, bbox_inches='tight', facecolor=bg_color)
plt.close()

print("Diagrama de arquitetura gerado com sucesso!")
