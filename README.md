# S&OP MVP JAMEF

Aplicação Streamlit para análise da demanda projetada, passagem operacional e simulação de restrições B2C no planejamento de Peak Season.

## Escopo do MVP

1. Resumo Executivo — parcial, somente com indicadores suportados pelas bases.
2. Demandas e Restrições — prioridade funcional do MVP.
3. Dimensionamento de Pessoas — estrutura inicial e contrato de dados.
4. Dimensionamento de Veículos — estrutura inicial e contrato de dados.
5. Reconciliação de Custos — estrutura inicial e contrato de dados.

## Bases iniciais esperadas

Os arquivos abaixo devem ser disponibilizados localmente em `data/input/` e não serão versionados:

- `134_Baseline_Diario_Cliente_Rota.parquet`
- `136_Base_Simulacao_Filial_Etapa.parquet`

## Execução local

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app/app.py
```

## Princípio de arquitetura

As páginas recebem filtros, chamam serviços e renderizam resultados. Regras de negócio ficam em `app/services/`. Contratos dos dados ficam em `data_contracts/`.
