"""Executa as rotas selecionadas e consolida seus resultados."""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
PASTA = Path(__file__).resolve().parent


def main():
    # Exemplo: carga_perfil.py fica disponível como "perfil".
    testes = {arquivo.stem.removeprefix("carga_"): arquivo
              for arquivo in sorted(PASTA.glob("carga_*.py"))}
    parser = argparse.ArgumentParser(description="Executa os testes de carga do TaskLab.")
    parser.add_argument("rota", nargs="?", choices=list(testes),
                        help="Teste a executar; sem argumento, executa todos.")
    argumentos = parser.parse_args()
    if not testes:
        print("Nenhum arquivo carga_*.py encontrado.")
        return 1
    if argumentos.rota:
        testes = {argumentos.rota: testes[argumentos.rota]}

    token = os.environ.get("TASKLAB_TOKEN", "").strip()
    if not token:
        try:
            token = input("Cole TASKLAB_TOKEN (access_token, sem Bearer): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExecução cancelada: token não informado.")
            return 1
    if not token:
        print("TASKLAB_TOKEN é obrigatório.")
        return 1

    relatorios = PASTA / "relatorios"
    relatorios.mkdir(parents=True, exist_ok=True)
    # Não herda opções LOCUST_* usadas em outras execuções pelo terminal.
    ambiente = {key: value for key, value in os.environ.items() if not key.upper().startswith("LOCUST_")}
    ambiente["TASKLAB_TOKEN"] = token
    ambiente["PYTHONPATH"] = str(ROOT)
    ambiente["PYTHONUNBUFFERED"] = "1"

    resultados = []
    for nome, arquivo in testes.items():
        relatorio = relatorios / f"{nome}.html"
        print(f"\nRota: {nome}", flush=True)
        comando = [
            sys.executable, "-m", "locust",
            "-f", str(arquivo),
            "--headless", "--only-summary", "--loglevel", "ERROR",
            "--html", str(relatorio), "--stop-timeout", "0",
        ]
        try:
            # Evita apresentar um relatório antigo como se fosse desta execução.
            relatorio.unlink(missing_ok=True)
            processo = subprocess.Popen(
                comando, cwd=ROOT, env=ambiente,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            inicio = time.monotonic()
            print("Executando: 0s", end="", flush=True)
            try:
                while True:
                    try:
                        resumo, detalhes = processo.communicate(timeout=1)
                        break
                    except subprocess.TimeoutExpired:
                        segundos = int(time.monotonic() - inicio)
                        print(f"\rExecutando: {segundos}s", end="", flush=True)
            except KeyboardInterrupt:
                processo.terminate()
                processo.communicate()
                print("\nExecução cancelada.")
                return 1
            print(f"\rTempo total: {int(time.monotonic() - inicio)}s")
            print(resumo.strip())
            codigo = processo.returncode
            if codigo and not resumo.strip():
                # Mostra o diagnóstico apenas quando o teste não gerou seu resumo.
                print("\n".join(detalhes.splitlines()[-12:]))
            print(f"Relatório: {relatorio}")
            if not relatorio.exists():
                print(f"Erro: relatório de {nome} não foi gerado.", flush=True)
                codigo = codigo or 1
        except OSError:
            print(f"Erro ao iniciar {nome} ou gravar seu relatório.", flush=True)
            codigo = 1
        resultados.append((nome, codigo))

    print("\nResumo final:", flush=True)
    for nome, codigo in resultados:
        resultado = "APROVADO" if codigo == 0 else "REPROVADO/ERRO"
        print(f"{nome}: {resultado} (código {codigo})", flush=True)
    return 0 if all(codigo == 0 for _, codigo in resultados) else 1


if __name__ == "__main__":
    raise SystemExit(main())
