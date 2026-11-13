"""Camada de Modelos: classes que mapeiam o JSON das APIs do IBGE."""
from dataclasses import dataclass, field


@dataclass
class Estado:
    id: int
    sigla: str
    nome: str

    @classmethod
    def from_json(cls, d: dict) -> "Estado":
        return cls(id=d["id"], sigla=d["sigla"], nome=d["nome"])

    def __str__(self) -> str:
        return f"{self.nome} ({self.sigla})"


@dataclass
class Municipio:
    id: int
    nome: str

    @classmethod
    def from_json(cls, d: dict) -> "Municipio":
        return cls(id=d["id"], nome=d["nome"])

    def __str__(self) -> str:
        return self.nome


@dataclass
class Frequencia:
    nome: str
    frequencia: int

    @classmethod
    def from_json(cls, d: dict) -> "Frequencia":
        return cls(nome=d["nome"].title(), frequencia=int(d["frequencia"]))


@dataclass
class NomesLocalidade:
    localidade: int
    homens: list[Frequencia] = field(default_factory=list)
    mulheres: list[Frequencia] = field(default_factory=list)
    sobrenomes: list[Frequencia] = field(default_factory=list)

    @classmethod
    def from_json(cls, d: dict) -> "NomesLocalidade":
        def lista(chave: str) -> list[Frequencia]:
            return [Frequencia.from_json(x) for x in d.get(chave) or []]

        return cls(
            localidade=d.get("localidade", 0),
            homens=lista("homens"),
            mulheres=lista("mulheres"),
            sobrenomes=lista("sobrenomes"),
        )
