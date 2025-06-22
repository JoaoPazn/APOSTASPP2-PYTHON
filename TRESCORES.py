import random
import time

def adicionar_dinheiro(dinh):
    try:
        valor = float(input("Digite quanto irá adicionar à carteira: "))
        dinh += valor
    except ValueError:
        print("Valor inválido!")
    return dinh

def menu():
    dinh = 0
    while True:
        print(f'''
1. Apostar
2. Adicionar dinheiro
3. Sair

Carteira: {dinh}
''')
        sel = input(">")
        if sel == "1":
            dinh = apostas(dinh)
        elif sel == "2":
            dinh = adicionar_dinheiro(dinh)
        elif sel == "3":
            break
        else:
            print("Opção inválida.")

def checksame(suacor, multiplicador, aposta, dinh):
    seuNumero = random.randint(0,15)
    sorteado = random.randint(0,15)
    print(f"Sua cor : {suacor}")
    
    if suacor == "Preto":
        if sorteado < seuNumero:
            cor_mais_proxima = "Vermelho"
        elif sorteado > seuNumero:
            cor_mais_proxima = "Branco"
        else:
            cor_mais_proxima = "Preto"

    elif suacor == "Vermelho":
        if seuNumero - 5 <= sorteado <= seuNumero + 5:
            cor_mais_proxima = "Preto"
        else:
            cor_mais_proxima = "Branco"

    elif suacor == "Branco":
        if seuNumero - 5 <= sorteado <= seuNumero + 5:
            cor_mais_proxima = "Preto"
        else:
            cor_mais_proxima = "Vermelho"
    time.sleep(2)
    print(f"Cor sorteada : {cor_mais_proxima}")
    time.sleep(2)
    ganho = multiplicador * aposta
    if seuNumero == sorteado:
        print(f'''Parabéns! você ganhou
premio : {ganho}''')
        dinh += ganho
    elif seuNumero != sorteado:
        print("Você perdeu!")
        dinh -= ganho 
    
    return dinh




def apostas(dinh):
    try:
        apost = float(input("Digite quanto irá apostar: "))
    except ValueError:
        print("Valor inválido!")
        return dinh
    
    if apost > dinh:
        print("Valor insuficiente na carteira!")
        return dinh
    
    while True:
        try:
            multi = float(input("Digite o multiplicador esperado (ex.: 1.5) : ").replace(",","."))
            break
        except ValueError:
            print("Valor inválido! Digite um número decimal (ex.: 1.5 ou 1,5).")
    
    if (multi*apost) > dinh:
        print("Multiplicador muito alto em relação a aposta.")
        return dinh

    while True:
        suaCor = input("Digite sua cor 1 - vermelho | 2 - preto | 3 - branco: ")

        if suaCor == "1":
            suaCor = "Vermelho"
            break
        elif suaCor == "2":
            suaCor = "Preto"
            break
        elif suaCor == "3":
            suaCor = "Branco"
            break
        else:
            print("Opção inválida! Digite apenas 1, 2 ou 3.")
    dinh = checksame(suaCor, multi, apost, dinh)    
    return dinh
        

menu()