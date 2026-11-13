"""Camada de Serviços / Integração: HTTP + JSON com as APIs do IBGE."""
import gzip
import json
import urllib.error
import urllib.request

from ibgenomes.models import Estado, Municipio, NomesLocalidade

BASE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades"
BASE_NOMES = "https://servicodados.ibge.gov.br/api/v3/nomes/2022/localidade"


class ApiError(Exception):
    """Falha de comunicação com a API do IBGE (mensagem amigável)."""


def _get_json(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if raw[:2] == b"\x1f\x8b":  # a API do IBGE pode responder em gzip
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ApiError(f"A API do IBGE respondeu com erro {e.code}.") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise ApiError("Não foi possível conectar à API do IBGE. Verifique a internet.") from e
    except json.JSONDecodeError as e:
        raise ApiError("Resposta inválida da API do IBGE.") from e


class LocalidadesService:
    """API de Localidades (estados e municípios)."""

    def listar_estados(self) -> list[Estado]:
        data = _get_json(f"{BASE_LOCALIDADES}/estados?orderBy=nome")
        return [Estado.from_json(d) for d in data]

    def listar_municipios(self, estado_id: int) -> list[Municipio]:
        data = _get_json(f"{BASE_LOCALIDADES}/estados/{estado_id}/municipios?orderBy=nome")
        return [Municipio.from_json(d) for d in data]


class NomesService:
    """API de Nomes (Censo 2022) - consulta encadeada pelo id da localidade."""

    def buscar_por_localidade(self, localidade_id: int) -> NomesLocalidade:
        data = _get_json(f"{BASE_NOMES}/{localidade_id}")
        if isinstance(data, list):  # a API devolve lista quando há resultado único
            data = data[0] if data else {}
        return NomesLocalidade.from_json(data)
