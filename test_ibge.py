"""Testes dos Models (offline) e smoke test dos Services (usa a API real)."""
import unittest

from ibgenomes.models import NomesLocalidade
from ibgenomes.services import LocalidadesService, NomesService


class ModelTests(unittest.TestCase):
    def test_parse_nomes(self):
        d = {"localidade": 35,
             "homens": [{"nome": "jose", "frequencia": 10}],
             "mulheres": [{"nome": "maria", "frequencia": 20}],
             "sobrenomes": [{"nome": "silva", "frequencia": 5}]}
        n = NomesLocalidade.from_json(d)
        self.assertEqual(n.homens[0].nome, "Jose")
        self.assertEqual(n.mulheres[0].frequencia, 20)
        self.assertEqual(n.sobrenomes[0].nome, "Silva")

    def test_parse_vazio(self):
        self.assertEqual(NomesLocalidade.from_json({}).homens, [])


class ApiTests(unittest.TestCase):
    def test_encadeado(self):
        estados = LocalidadesService().listar_estados()
        self.assertEqual(len(estados), 27)
        sp = next(e for e in estados if e.sigla == "SP")
        nomes = NomesService().buscar_por_localidade(sp.id)
        self.assertTrue(nomes.mulheres and nomes.homens)

    def test_municipio(self):
        muns = LocalidadesService().listar_municipios(35)
        self.assertEqual(len(muns), 645)
        sp = next(m for m in muns if m.nome == "São Paulo")
        self.assertTrue(NomesService().buscar_por_localidade(sp.id).homens)


if __name__ == "__main__":
    unittest.main()
