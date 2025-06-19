import random
import time

multi = 0

# Valores
Banana = ["B", 0.6]
Maca = ["M", 1]
Laranja = ["L", 1.3]
Uva = ["U", 1.8]
Jabuticaba = ["J", 2.5]
Goiaba = ["G", 5]
Manga = ["MA", 20]

def checarapostas(valor):
    if valor == Banana[0]:
        return Banana[1]
    elif valor == Maca[0]:
        return Maca[1]
    elif valor == Laranja[0]:
        return Laranja[1]
    elif valor == Uva[0]:
        return Uva[1]
    elif valor == Jabuticaba[0]:
        return Jabuticaba[1]
    elif valor == Goiaba[0]:
        return Goiaba[1]
    elif valor == Manga[0]:
        return Manga[1]
    else:
        return 0 

def ordem(Array_Apostas):
    multi = 0
    # Linhas
    for i in range(0, 9, 3):
        if Array_Apostas[i] == Array_Apostas[i+1] == Array_Apostas[i+2]:
            multi += checarapostas(Array_Apostas[i])
    # Colunas
    for i in range(3):
        if Array_Apostas[i] == Array_Apostas[i+3] == Array_Apostas[i+6]:
            multi += checarapostas(Array_Apostas[i])
    # Diagonais
    if Array_Apostas[0] == Array_Apostas[4] == Array_Apostas[8]:
        multi += checarapostas(Array_Apostas[0])
    if Array_Apostas[2] == Array_Apostas[4] == Array_Apostas[6]:
        multi += checarapostas(Array_Apostas[2])
    # Bônus para todos iguais
    if all(elem == Array_Apostas[0] for elem in Array_Apostas):        
        multi += 10
    return multi 

def gerar_slot():
    Slot = []
    for _ in range(9):
        GAMB = random.randint(1, 1000)
        if GAMB <= 400:
            Slot.append(Banana[0])
        elif GAMB <= 650:
            Slot.append(Maca[0])
        elif GAMB <= 800:
            Slot.append(Laranja[0])
        elif GAMB <= 900:
            Slot.append(Uva[0])
        elif GAMB <= 975:
            Slot.append(Jabuticaba[0])
        elif GAMB <= 990:
            Slot.append(Goiaba[0])
        else:
            Slot.append(Manga[0])
    return Slot

def mostrar_slot(Slot):
    print(f'''
{Slot[0]} | {Slot[1]} | {Slot[2]}
--+---+--
{Slot[3]} | {Slot[4]} | {Slot[5]}
--+---+--
{Slot[6]} | {Slot[7]} | {Slot[8]}
''')

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
        Slot = gerar_slot()
        multi = ordem(Slot)
        mostrar_slot(Slot)
        time.sleep(2)

        lucro = apost * multi
        dinh = dinh - apost + lucro

        print(f"Multiplicador: {multi}x")
        print(f"Você ganhou: {lucro:.2f}")
        print(f"Nova carteira: {dinh:.2f}")

        if dinh < apost:
            print("Você não tem saldo suficiente para continuar com essa aposta.")
            break

        cont = input("Continuar? (1 - sim / 0 - não): ")
        if cont != "1":
            break

    return dinh

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

menu()
