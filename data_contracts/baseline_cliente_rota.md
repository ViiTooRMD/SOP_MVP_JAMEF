# Contrato — Baseline diário cliente-rota

Arquivo esperado: `134_Baseline_Diario_Cliente_Rota.parquet`.

Granularidade esperada: data + cliente + rota + tipo de operação.

Domínios funcionais mínimos a validar após o upload:

- Data de referência.
- Identificador e nome do cliente.
- Origem, destino e rota.
- Classificação B2B/B2C.
- Filial.
- Frete.
- Peso.
- Volume.
- Quantidade de CT-es.

Os nomes, tipos, nulabilidade e chaves serão registrados a partir do schema real, sem inferência.
