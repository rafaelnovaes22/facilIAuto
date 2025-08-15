# 🔧 ESTRUTURA TÉCNICA PARA IMPLEMENTAÇÃO

## 📋 **TEMPLATE DE IMPLEMENTAÇÃO**

### **Baseado no modelo de sucesso do perfil trabalho/negócios**

---

# 🚗 **PERFIL URBANO - Código Técnico**

## **Adição ao `CRITERIOS_USO`**

```python
"urbano": {
    # PESO ALTO (20% cada)
    "economia_combustivel_urbana": {
        "peso": 20,
        "consumo_cidade_minimo": 12,  # km/l
        "cilindradas_ideais": [1.0, 1.4],
        "marcas_economicas": ["Honda", "Toyota", "Chevrolet", "Nissan"],
        "tecnologias_eco": ["flex", "start_stop", "híbrido"]
    },
    
    "facilidade_manobra": {
        "peso": 20,
        "categorias_ideais": ["Hatch", "Sedan Compacto"],
        "comprimento_max": 4.2,  # metros
        "raio_giro_max": 5.0,    # metros
        "sistemas_assistencia": ["sensores", "camera_re", "park_assist"]
    },
    
    # PESO MÉDIO (15% cada)
    "tecnologia_conectividade": {
        "peso": 15,
        "essenciais": ["central_multimidia", "bluetooth", "usb"],
        "desejados": ["android_auto", "apple_carplay", "wifi"],
        "navegacao": ["gps_integrado", "waze_nativo"],
        "subsegmento_boost": {"executivo": 1.5}
    },
    
    "seguranca_urbana": {
        "peso": 15,
        "basicos_obrigatorios": ["abs", "airbag_duplo", "cintos_3pontos"],
        "avancados": ["controle_estabilidade", "assistente_frenagem"],
        "visibilidade": ["faróis_led", "retrovisores_eletricos"],
        "subsegmento_boost": {"primeiro_carro": 1.3}
    },
    
    # PESO BAIXO (≤10%)
    "custo_manutencao_urbana": {
        "peso": 10,
        "marcas_economicas": ["Chevrolet", "Fiat", "Volkswagen", "Renault"],
        "pecas_disponiveis": True,
        "rede_autorizada": ["ampla", "acessivel"],
        "intervalos_revisao": {"ideal_km": 10000, "max_km": 15000}
    },
    
    "praticidade_urbana": {
        "peso": 5,
        "porta_malas_litros": {"minimo": 250, "ideal": 350},
        "altura_solo": {"minimo": 14, "maximo": 18},  # cm
        "portas": {"minimo": 4, "ideal": 5},
        "facilidades": ["vidros_eletricos", "travamento_central"]
    },
    
    "conforto_urbano": {
        "peso": 3,
        "clima": ["ar_condicionado", "ventilacao_eficiente"],
        "ergonomia": ["direcao_assistida", "bancos_regulaveis"],
        "ruido": ["isolamento_acustico", "motor_silencioso"]
    },
    
    "sustentabilidade_urbana": {
        "peso": 2,
        "tipos_motor": ["flex", "híbrido", "elétrico"],
        "emissoes": ["euro_5", "proconve_l6"],
        "eficiencia": ["baixa_pegada_carbono"]
    }
}
```

## **Lógica de Avaliação (Adicionar ao `_avaliar_criterio`)**

```python
elif criterio == "economia_combustivel_urbana":
    score_parcial = 0.0
    fatores = []
    
    # Avalia consumo na cidade
    consumo = carro.get("consumo_cidade", carro.get("consumo", 0))
    if consumo >= configs.get("consumo_cidade_minimo", 0):
        score_parcial += 0.5
        fatores.append(f"consumo cidade {consumo} km/l")
    
    # Avalia cilindrada ideal
    cilindrada = carro.get("cilindrada", 0)
    if cilindrada in configs.get("cilindradas_ideais", []):
        score_parcial += 0.3
        fatores.append(f"motor {cilindrada} econômico")
    
    # Verifica marca econômica
    marca = carro.get("marca", "")
    if marca in configs.get("marcas_economicas", []):
        score_parcial += 0.2
        fatores.append(f"marca {marca} econômica")
    
    if fatores:
        score = score_parcial
        razao = f"Economia urbana: {' e '.join(fatores)}"
        ponto_forte = "Baixo custo operacional na cidade"

elif criterio == "facilidade_manobra":
    score_parcial = 0.0
    fatores = []
    
    # Verifica categoria ideal
    categoria = carro.get("categoria", "")
    if categoria in configs.get("categorias_ideais", []):
        score_parcial += 0.6
        fatores.append(f"{categoria} compacto")
    
    # Verifica comprimento (se disponível)
    comprimento = carro.get("comprimento", 0)
    if comprimento > 0 and comprimento <= configs.get("comprimento_max", 4.5):
        score_parcial += 0.2
        fatores.append("dimensões adequadas")
    
    # Verifica sistemas de assistência
    opcionais = carro.get("opcionais", [])
    sistemas = configs.get("sistemas_assistencia", [])
    tem_sistemas = sum(1 for sistema in sistemas if any(sistema in opcional.lower() for opcional in opcionais))
    if tem_sistemas > 0:
        score_parcial += 0.2
        fatores.append("sistemas de auxílio")
    
    if fatores:
        score = score_parcial
        razao = f"Manobra: {' e '.join(fatores)}"
        ponto_forte = "Fácil de manobrar e estacionar"

elif criterio == "tecnologia_conectividade":
    opcionais = carro.get("opcionais", [])
    essenciais = configs.get("essenciais", [])
    desejados = configs.get("desejados", [])
    
    # Conta itens essenciais
    tem_essenciais = sum(1 for item in essenciais if any(item in opcional.lower() for opcional in opcionais))
    # Conta itens desejados  
    tem_desejados = sum(1 for item in desejados if any(item in opcional.lower() for opcional in opcionais))
    
    if tem_essenciais >= len(essenciais) * 0.7:  # 70% dos essenciais
        score_base = 0.7
        score_bonus = min((tem_desejados / len(desejados)) * 0.3, 0.3)
        score = score_base + score_bonus
        razao = f"Tecnologia: {tem_essenciais} essenciais + {tem_desejados} desejados"
        ponto_forte = "Conectividade moderna"

elif criterio == "seguranca_urbana":
    score_parcial = 0.0
    fatores = []
    
    # Verifica básicos obrigatórios
    opcionais = carro.get("opcionais", [])
    basicos = configs.get("basicos_obrigatorios", [])
    tem_basicos = sum(1 for item in basicos if any(item in opcional.lower() for opcional in opcionais))
    
    if tem_basicos >= len(basicos) * 0.8:  # 80% dos básicos
        score_parcial += 0.6
        fatores.append("sistemas básicos")
    
    # Verifica segurança geral
    seguranca = carro.get("seguranca", 0)
    if seguranca >= 4:
        score_parcial += 0.4
        fatores.append(f"{seguranca} estrelas")
    
    if fatores:
        score = score_parcial
        razao = f"Segurança urbana: {' e '.join(fatores)}"
        ponto_forte = "Proteção adequada no trânsito"

# ... continuar para outros critérios urbanos
```

## **Sugestões Específicas (Atualizar `gerar_sugestoes_uso`)**

```python
elif uso == "urbano":
    sugestoes.extend([
        "🚗 Para cidade: priorize carros compactos (Hatch/Sedan pequeno)",
        "⛽ Economia urbana: busque consumo ≥12 km/l na cidade",
        "🅿️ Facilidade estacionamento: carros ≤4,2m são ideais",
        "📱 Conectividade: central multimídia + Bluetooth são essenciais",
        "🛡️ Segurança urbana: ABS + airbag duplo + controle estabilidade",
        "🔧 Manutenção: Chevrolet, Fiat, VW têm peças acessíveis",
        "💡 Primeiro carro: foque em economia + segurança básica",
        "💼 Executivo: tecnologia + conforto valorizam o veículo",
        "👴 Aposentado: simplicidade + confiabilidade são prioridade"
    ])
```

---

# ✈️ **PERFIL VIAGEM - Código Técnico**

## **Adição ao `CRITERIOS_USO`**

```python
"viagem": {
    # PESO ALTO (20% cada)
    "performance_rodovia": {
        "peso": 20,
        "potencia_minima": 120,  # HP
        "torque_minimo": 150,    # Nm
        "aceleracao_max": 12,    # 0-100 km/h em segundos
        "velocidade_cruzeiro": {"confortavel": 120, "maxima": 180},
        "subsegmento_boost": {"executivo": 1.3, "aventureiro": 1.2}
    },
    
    "seguranca_rodoviaria": {
        "peso": 20,
        "sistemas_obrigatorios": ["abs", "esp", "controle_tracao"],
        "airbags_minimos": 4,
        "assistencias": ["cruise_control", "alerta_colisao", "frenagem_automatica"],
        "estrutura": ["carroceria_reforçada", "zonas_deformacao"],
        "avaliacao_minima": 4  # estrelas
    },
    
    # PESO MÉDIO (15% cada)
    "espaco_viagem": {
        "peso": 15,
        "porta_malas_litros": {"minimo": 400, "ideal": 600},
        "bagageiro_teto": True,
        "bancos_reclinaveis": True,
        "espaco_pernas": {"traseiro_minimo": 80},  # cm
        "subsegmento_boost": {"turismo_familiar": 1.4}
    },
    
    "conforto_viagem": {
        "peso": 15,
        "bancos": ["ergonomicos", "apoio_lombar", "regulagem_altura"],
        "clima": ["ar_digital", "zonas_independentes"],
        "tecnologia": ["sistema_som_premium", "carregamento_wireless"],
        "conveniencia": ["piloto_automatico", "volante_multifuncional"]
    },
    
    # PESO BAIXO (≤10%)
    "autonomia_combustivel": {
        "peso": 10,
        "tanque_minimo": 50,     # litros
        "consumo_rodovia": 8,    # km/l mínimo
        "autonomia_minima": 400, # km
        "indicador_consumo": True
    },
    
    "robustez_viagem": {
        "peso": 5,
        "altura_solo": {"minima": 16, "ideal": 20},  # cm
        "suspeensao": ["independente", "amortecedores_gas"],
        "pneus": ["perfil_adequado", "estepe_completo"],
        "subsegmento_boost": {"aventureiro": 2.0}
    },
    
    "tecnologia_viagem": {
        "peso": 3,
        "navegacao": ["gps_offline", "mapas_atualizados"],
        "conectividade": ["wifi_hotspot", "multiplas_usb"],
        "entretenimento": ["telas_traseiras", "sistema_audio_premium"]
    },
    
    "versatilidade_viagem": {
        "peso": 2,
        "configuracoes": ["bancos_rebativeis", "assoalho_plano"],
        "acessorios": ["rack_teto", "engate_reboque"],
        "adaptabilidade": ["diferentes_terrenos", "cargas_variadas"]
    }
}
```

---

# 👨‍👩‍👧‍👦 **PERFIL FAMÍLIA - Código Técnico**

## **Adição ao `CRITERIOS_USO`**

```python
"familia": {
    # PESO ALTO (25% cada)
    "seguranca_familiar": {
        "peso": 25,
        "sistemas_obrigatorios": ["isofix", "abs", "esp", "airbag_cortina"],
        "airbags_minimos": 6,
        "portas_crianca": True,
        "vidros_temperados": True,
        "avaliacao_minima": 5,  # estrelas
        "subsegmento_boost": {"familia_pequena": 1.2}
    },
    
    "espaco_familiar": {
        "peso": 25,
        "lugares_minimos": {"pequena": 5, "media": 7, "grande": 8},
        "isofix_pontos": {"minimos": 2, "ideais": 3},
        "espaco_pernas": {"traseiro": 85, "terceira_fileira": 70},  # cm
        "altura_interna": {"minima": 95},  # cm
        "configuracoes": ["bancos_rebativeis", "acesso_terceira_fileira"]
    },
    
    # PESO MÉDIO (15% cada)
    "praticidade_familiar": {
        "peso": 15,
        "portas": {"minimas": 4, "ideais": 5},
        "abertura_portas": {"ampla": True, "eletrica": "desejavel"},
        "porta_malas": {"minimo": 300, "ideal": 500, "bancos_rebatidos": 1000},
        "altura_embarque": {"maxima": 65},  # cm
        "facilidades": ["tampa_malas_eletrica", "sensor_estacionamento"]
    },
    
    "conforto_entretenimento": {
        "peso": 15,
        "clima": ["ar_traseiro", "zonas_independentes"],
        "bancos": ["capitao", "regulagem_individual"],
        "entretenimento": ["telas_individuais", "entrada_headphones"],
        "conveniencia": ["porta_objetos", "compartimentos_diversos"],
        "subsegmento_boost": {"familia_media": 1.3, "familia_grande": 1.4}
    },
    
    # PESO BAIXO (≤10%)
    "facilidade_acesso": {
        "peso": 10,
        "portas_deslizantes": {"van": True, "desejavel": "outros"},
        "degraus_baixos": True,
        "apoios_mao": True,
        "largura_abertura": {"minima": 65},  # cm
        "subsegmento_boost": {"familia_grande": 1.5}
    },
    
    "economia_familiar": {
        "peso": 5,
        "consumo_misto": {"minimo": 8, "ideal": 10},  # km/l
        "tanque_adequado": {"minimo": 45},  # litros
        "autonomia": {"minima": 350},  # km
        "manutencao": ["intervalos_longos", "custos_baixos"]
    },
    
    "durabilidade_familiar": {
        "peso": 3,
        "estrutura": ["reforçada", "resistente_desgaste"],
        "interior": ["materiais_laváveis", "resistente_riscos"],
        "mecanica": ["robusta", "baixa_manutencao"],
        "garantia": {"minima": 3}  # anos
    },
    
    "versatilidade_familiar": {
        "peso": 2,
        "modularidade": ["bancos_removiveis", "configuracao_variavel"],
        "adaptabilidade": ["carga", "passageiros", "misto"],
        "acessorios": ["ganchos", "redes", "organizadores"]
    }
}
```

---

# 🔧 **INSTRUÇÕES DE IMPLEMENTAÇÃO**

## **Passo 1: Atualizar `CRITERIOS_USO`**
- Substituir critérios atuais pelos novos (detalhados acima)
- Manter peso total = 100% por perfil

## **Passo 2: Implementar lógica `_avaliar_criterio`**
- Adicionar casos `elif` para cada novo critério
- Seguir padrão: score_parcial + fatores + razão + ponto_forte

## **Passo 3: Atualizar `gerar_sugestoes_uso`**
- Expandir de 3 para 8+ sugestões por perfil
- Incluir subsegmentos específicos
- Adicionar valores técnicos concretos

## **Passo 4: Atualizar `get_descricao_uso`**
- Descrições mais detalhadas
- Incluir subsegmentos
- Mencionar critérios principais

## **Passo 5: Criar Testes Unitários**
- 1 teste por critério principal
- Validar scoring para cada subsegmento
- Confirmar sugestões específicas

## **Passo 6: Validação E2E**
- Testar com dados reais
- Comparar scores antes/depois
- Validar relevância das sugestões

---

**Status**: 🎯 **ESTRUTURA TÉCNICA COMPLETA** - Pronta para implementação