# SK hynix Financial Data Agent

SK하이닉스(000660) DART 공시 기반 재무데이터 수집·분석·GitHub Pages 대시보드입니다.

[![Dashboard](https://img.shields.io/badge/🔗%20대시보드-바로가기-0A66C2?style=for-the-badge)](https://hsc-class02.github.io/seokjun_skhynix/)

## Dashboard
🔗 [대시보드 바로가기](https://hsc-class02.github.io/seokjun_skhynix/)

## Data
- Source: OpenDART
- Company: SK hynix Inc. (DART corp code: 00164779)
- Target periods: Annual, Half-year, Quarterly
- Historical target: 2010 onward where DART/API data are available
- Monthly update: 1st day of each month at 02:00 KST
- Raw API responses and normalized data are retained in the repository.

## Main indicators
Revenue, gross profit, SG&A, operating income, income before tax, net income, controlling-interest net income, EBITDA, total assets, cash & cash equivalents, receivables, inventories, PP&E, total liabilities, interest-bearing debt, equity, operating/investing/financing cash flow, CAPEX, FCF and derived ratios.

## Ratios
Gross margin, operating margin, net margin, EBITDA margin, ROA, ROE, ROIC (where calculable), current ratio, quick ratio, debt-to-equity, equity ratio, debt dependency, interest coverage, net debt/EBITDA, asset turnover, DSO, DIO, DPO, CCC, revenue growth and CFO/net income.

## Domestic peer firms
| Peer | Ticker | Rationale |
|---|---:|---|
| Samsung Electronics | 005930 | Korea's closest large-scale semiconductor/memory peer |
| DB HiTek | 000990 | Korean semiconductor foundry peer |
| Hanmi Semiconductor | 042700 | Korean semiconductor equipment peer |
| Jusung Engineering | 036930 | Korean semiconductor equipment/process peer |
| LX Semicon | 108320 | Korean semiconductor design/solution peer |

Peers are provided for domestic industry benchmarking; they are not identical business-model peers.

## Project structure
- `scripts/fetch_dart.py`: DART data collection and normalization
- `scripts/analyze.py`: financial statement and ratio calculations
- `scripts/build_dashboard.py`: static dashboard generation
- `.github/workflows/monthly_dart_update.yml`: monthly automation
- `data/raw/`: raw API responses
- `data/processed/`: normalized analytical data
- `docs/`: GitHub Pages site

## API Secret
Set repository secret:
`OPENDART_API_KEY`

Do not put the API key in source files, README, or commits.
