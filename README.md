# IBGE Data Insights – Nomes mais comuns por localidade

Aplicação desktop (Python + Tkinter) que consome **duas APIs públicas do IBGE em cadeia**:

1. **API de Localidades** – popula os dropdowns de Estado e Município.
2. **API de Nomes (Censo 2022)** – ao selecionar a localidade, usa o `id` para buscar
   `https://servicodados.ibge.gov.br/api/v3/nomes/2022/localidade/{id}` e exibe os nomes mais
   comuns de **homens**, **mulheres** e os **sobrenomes**.

## Integrantes do grupo
- Kaue Alves Naback
- Vinicius de Souza Freira
- Kauã de Castro Oliveira

## Como executar
Requisitos: Python 3.10+ com Tkinter (já incluso no instalador oficial do Python). Não há dependências externas.

```bash
python main.py
```
Testes (os de API precisam de internet): `python -m unittest test_ibge -v`

## Como usar
- Escolha **Estado** → selecione o estado: os nomes aparecem automaticamente.
- Escolha **Município** → selecione o estado, depois o município: os nomes daquele município aparecem.

## Arquitetura em camadas
```
ibgenomes/
  models/     # Estado, Municipio, Frequencia, NomesLocalidade (mapeiam o JSON)
  services/   # LocalidadesService e NomesService (HTTP + JSON, tratamento de erros)
  ui/app.py   # Apresentação: dropdowns (Combobox) e listas (Treeview)
main.py       # Composição das camadas
```
As requisições rodam em threads separadas, então a janela não trava durante a consulta, e respostas antigas
não sobrescrevem a seleção mais recente.
