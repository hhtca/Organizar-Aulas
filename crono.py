import re
from typing import List, Dict

class Aula:
    def __init__(self, aula: str, professor: str, duracao_min: int):
        self.aula = aula
        self.professor = professor
        self.duracao_min = duracao_min

class Intervalo:
    def __init__(self, inicio: int, fim: int):
        self.inicio = inicio
        self.fim = fim

    def conflita_com(self, outro: 'Intervalo') -> bool:
        return self.inicio < outro.fim and outro.inicio < self.fim

def carregar_aulas(caminho: str) -> List[Aula]:
    aulas = []
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            for numero_linha, linha in enumerate(arquivo, start=1):
                linha = linha.strip()

                if not linha:
                    continue

                if '-' not in linha:
                    print(f"❌ Linha {numero_linha} ignorada: não contém separador '-': \"{linha}\"")
                    continue

                partes = linha.split('-')
                if len(partes) < 2:
                    print(f"❌ Linha {numero_linha} ignorada: formato inválido (esperado: Aula - Prof. Nome Duração)")
                    continue

                nome_aula = partes[0].strip()
                info_professor = partes[1].strip()

                if not info_professor:
                    print(f"❌ Linha {numero_linha} ignorada: nome do professor ausente.")
                    continue

                palavras = info_professor.split()
                nome_professor = palavras[1] if len(palavras) >= 2 else palavras[0]

                matcher = re.search(r"-?\d+", info_professor)
                duracao_valida = False
                duracao = 0

                if matcher:
                    try:
                        duracao = int(matcher.group())
                        duracao_valida = duracao > 0
                    except ValueError:
                        duracao_valida = False

                if not duracao_valida:
                    print(f"❌ Linha {numero_linha} ignorada: duração inválida ou não positiva: \"{linha}\"")
                    continue

                aulas.append(Aula(nome_aula, nome_professor, duracao))

    except IOError as e:
        print("Erro ao ler o arquivo:", e)

    return aulas

def gerar_cronograma(aulas: List[Aula]) -> List[str]:
    cronograma = []
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
    agenda_professores: Dict[str, List[Intervalo]] = {}
    indice_aula = 0

    for dia in dias_semana:
        cronograma.append(f"📅 {dia}")
        indice_aula = alocar_turno(aulas, cronograma, indice_aula, 9, 12, agenda_professores)
        indice_aula = alocar_turno(aulas, cronograma, indice_aula, 13, 17, agenda_professores)
        cronograma.append("17:00 Reunião de professores (obrigatória)")

        if indice_aula >= len(aulas):
            break

    return cronograma

def alocar_turno(aulas: List[Aula], cronograma: List[str], indice_atual: int,
                 hora_inicio: int, hora_fim: int, agenda: Dict[str, List[Intervalo]]) -> int:

    hora_atual = hora_inicio
    minuto_atual = 0
    fim_turno_minutos = hora_fim * 60

    while indice_atual < len(aulas):
        aula = aulas[indice_atual]
        inicio = hora_atual * 60 + minuto_atual
        fim = inicio + aula.duracao_min

        if fim > fim_turno_minutos:
            break

        novo_horario = Intervalo(inicio, fim)
        horarios_ocupados = agenda.get(aula.professor, [])

        conflito = any(h.conflita_com(novo_horario) for h in horarios_ocupados)

        if not conflito:
            horario_formatado = f"{hora_atual:02d}:{minuto_atual:02d}"
            cronograma.append(f"{horario_formatado} {aula.aula} - Prof. {aula.professor} {aula.duracao_min} min")
            horarios_ocupados.append(novo_horario)
            agenda[aula.professor] = horarios_ocupados

            minuto_atual += aula.duracao_min
            hora_atual += minuto_atual // 60
            minuto_atual %= 60
            indice_atual += 1
        else:
            indice_atual += 1

    return indice_atual

if __name__ == "__main__":
    caminho_arquivo = "aulas.txt"
    aulas = carregar_aulas(caminho_arquivo)
    if not aulas:
        print("Nenhuma aula válida encontrada.")
    else:
        cronograma = gerar_cronograma(aulas)
        for linha in cronograma:
            print(linha)
