# -*- coding: utf-8 -*-
"""cinematicaAnalitica.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aBLAF8IP5RhUfjwVetf8lhbBzQ3AES8Q
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 16:47:58 2024

@author: valeria.luz
"""


# Códigozinho teste
# Importando as bibliotecas necessárias
import numpy as np
import math as m
import pandas as pd
import matplotlib.pyplot as plt
from transforms3d.euler import euler2mat

##############################
def rotate_matrix(roll, pitch, yaw, matrix):
    # Generate 3×3 rotation matrix
    R = euler2mat(roll, pitch, yaw, 'sxyz')
    
    
    M = np.identity(4)
    M[:3, :3] = R  
    M[:3, 3] = 0   
    
    #print(matrix @ M)
    
    return matrix @ M  # Matriz resultante

############ CINEMÁTICA GERAL ############
def ler_thetas(in_theta1,in_theta2,in_theta3,in_theta4,changes):

    arquivo1 = "./Steps/junta1.tab"
    arquivo2 = "./Steps/junta2.tab"
    arquivo3 = "./Steps/junta3.tab"
    arquivo4 = "./Steps/junta4.tab"
    
    # Lendo os dados brutos dos ângulos com tempo e angulação
    # Muda conforme o seu .txt
    # read(arquivo1, x), x-> quantas linhas excluí
    theta1_bruto = read(arquivo1, 2)
    theta2_bruto = read(arquivo2, 2)
    theta3_bruto = read(arquivo3, 2)
    theta4_bruto = read(arquivo4, 2)

    # Extraindo apenas a coluna de ângulos [deg] dos Data lidos
    theta1_degree =  theta1_bruto['MOTION_1.ANG']
    theta2_degree =  theta2_bruto['MOTION_2.ANG']
    theta3_degree =  theta3_bruto['MOTION_3.ANG']
    theta4_degree =  theta4_bruto['MOTION_4.ANG']

    # Criando os vetores para armazenar os ângulos corrigidos em radianos
    theta1 = np.zeros(len(theta1_degree))
    theta2 = np.zeros(len(theta1_degree))
    theta3 = np.zeros(len(theta1_degree))
    theta4 = np.zeros(len(theta1_degree))
    
    thetas = [0] * len(theta1_degree)

    theta1_ = in_theta1
    theta2_ = in_theta2
    theta3_ = in_theta3
    theta4_ = in_theta4


    
    for i in range(len(theta1_degree)):

        for j in range(len(changes)):
        # Identifica posição inicial do passo    
            if i== changes[j]:
                theta1_ = theta1[i-1]
                theta2_ = theta2[i-1]
                theta3_ = theta3[i-1]
                theta4_ = theta4[i-1]
        # Ajusta a posição atual da junta para a real com a posição inicial do passo
        theta1[i] = theta1_degree[i] + theta1_
        theta2[i] = theta2_degree[i] + theta2_
        theta3[i] = theta3_degree[i] + theta3_
        theta4[i] = theta4_degree[i] + theta4_
        # Adicionando no array e Convertendo para radianos
        thetas[i] = [m.radians(theta1[i]),m.radians(theta2[i]),m.radians(theta3[i]),m.radians(theta4[i])]
    return thetas

# Função para ler um arquivo CSV contendo os parâmetros de Denavit-Hartenberg DH
def read(data, cabecalho):

    """
         data -> caminho para o arquivo CSV;
    cabecalho -> número de linhas do cabeçalho.

    Retorna:
           df -> DataFrame pandas contendo os dados lidos.
    """

    # Criando o DataFrame a partir do arquivo CSV
    #    header -> linha do arquivo CSV que contém os rótulos das colunas;
    # sep='\s+' -> valores separados por um ou mais espaços em branco.
    df = pd.read_csv(data, header = cabecalho, sep = '\s+')

    return df

# Função que calcula a Matriz de Transformação Homogênea Generalizada
def A(a, alpha, d, theta):
    """
      Estrutura da Matriz de Transformação Homogênea:

        T = [ R_3x3  p_3x1
              0_1x3    1  ]

        • R_3x3: submatriz que representa a rotação do link;
        • p_3x1: vetor de translação (posição);
        • Última linha: [0,0,0,1] mantém a matriz homogênea.

      Parâmetros:
        a -> comprimento do link [mm];
        α -> ângulo de torção entre os eixos Z de dois links consecutivos [rad];
        d -> deslocamento linear do link (para juntas prismáticas) [mm];
        θ -> deslocamento angular do link (para juntas de revolução) [rad].

      Retorna:
        A -> matriz 4x4 de transformação homogênea.
    """
    A = np.array([
        [np.cos(theta), -np.sin(theta) * np.cos(alpha),  np.sin(theta) * np.sin(alpha), a * np.cos(theta)],
        [np.sin(theta),  np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), a * np.sin(theta)],
        [            0,               np.sin(alpha),               np.cos(alpha),               d],
        [            0,                          0,                          0,               1]
    ])

    return A

# Função que calcula a cinemática de um robô baseado nos parâmetros DH
def kinematic(DH_a, DH_alpha, DH_d, DH_theta, M):

    """

      Parâmetros utilizados no código:
        DH_a -> lista de comprimento dos links;
        DH_α -> lista de ângulos de torção;
        DH_d -> lista de deslocamentos lineares (juntas prismáticas);
        DH_θ -> lista de deslocamentos angulares (juntas de revolução).

      Retorna:
           pose -> lista de matrizes de rotação (3x3) de cada junta;
        posicao -> lista dos vetores de posição (3x1) de cada junta.

    """
    n_links = len(DH_theta)
    T = [0] * n_links
    for i in range(n_links):
        DHi = A(DH_a[i], DH_alpha[i], DH_d[i], DH_theta[i])
        T[i] = np.dot(M,DHi)
        M = T[i]
    
    #print(T)
    return T #retorna uma lista com todos as matrizes
def normalization():
    N = StepsPata1.shape[0]  # Número de linhas
    P1_norma = np.linalg.norm(StepsPata1.iloc[:, 1:3], axis=1)  # Norma Euclidiana (√(X² + Y²))
    
    changes = []  # Lista para armazenar os índices das mudanças
    previous_value = P1_norma[0]  # Valor inicial
    in_change = False  # Estado de mudança

    for k in range(1, N):
        if P1_norma[k] != previous_value:  
            if not in_change:
                changes.append(k-1)  # Registra início da mudança
                in_change = True  # Entra no estado de mudança
        else:
            if in_change:
                changes.append(k)  # Registra fim da mudança
                in_change = False  # Sai do estado de mudança

        previous_value = P1_norma[k]  # Atualiza valor anterior

    print(changes)
    return changes
# Função principal - main
if __name__ == '__main__':
        L = [136.01, 141.42, 152.64] #Parâmetros do robô comprimento dos elos
       


        DH_a1 = [L[0],L[1],L[2],0] #Parâmetros do robô DH
        DH_a2 = [L[2],L[1],L[0],0] #Parâmetros do robô DH

        DH_alpha = [0,0,0,0] #Parâmetros do robô DH
        DH_d = [0,0,0,0] #Parâmetros do robô DH
 

        STEPSPATA1 = "./Steps/XeYPata1.tab"
        STEPSPATA2 = "./Steps/XeYPata2.tab"
        # Lendo os dados de posição do arquivo do ADAMs

        StepsPata1 = read(STEPSPATA1,1)
        StepsPata2 = read(STEPSPATA2,1)
        timeread  = StepsPata1["Time      "]
        time_step = len(timeread)
        changes = normalization() # Identificação dos pontos de troca de cinemática

        thetas = ler_thetas(53.97,-45.84,-66.52,-31.61, changes) # Posições iniciais das juntas e mudanças na base para identificar posição inicial de cada passo

        flag = True # Flag de mudança na base
        cinematica_x = [] # Resultado da posição X da 1º base
        cinematica_y = [] # Resultado da posição Y da 1º base
        cinematica_x2 = [] # Resultado da posição X da 2º base
        cinematica_y2 = [] # Resultado da posição Y da 2º base
        theta1 = [] # Thetas da 1º base
        theta2 = [] # Thetas da 2º base
        _matrix1 = np.identity(4) # Matriz identidade para início
        _matrix2 = np.identity(4) # Matriz identidade para início
        for i in range(time_step):
                
                theta1.append([thetas[i][0],thetas[i][1],thetas[i][2],thetas[i][3]]) 
                theta2.append([thetas[i][3],thetas[i][2],thetas[i][1],thetas[i][0]])

                matrix1 =  kinematic(DH_a1, DH_alpha, DH_d, theta1[i], _matrix2) # Cálculo cinemática para base 1
                matrix2 =  kinematic(DH_a2, DH_alpha, DH_d, theta2[i], _matrix1) # Cálculo cinemática para base 2

                for j in range(len(changes)): # Identificação de iteração de mudança de base
                    
                    if i== changes[j]:
                        if flag:
                            flag = False
                        else:
                            flag = True

                if flag: # 1º base

                    _matrix1=matrix1[3]
                    _matrix1=rotate_matrix(0.0, 3.14, 0.0,_matrix1) # Rotação da matriz, para casar na próxima cinemática
                    cinematica_x.append(_matrix1[:3,3][0]) # Posição X do manipulador
                    cinematica_y.append(_matrix1[:3,3][1]+10) # Posição Y ajustada - origem do ADAMs (0,20,0)
                    cinematica_x2.append(_matrix2[:3,3][0])
                    cinematica_y2.append(_matrix2[:3,3][1]+10) 

                else: # 2º base

                    _matrix2=matrix2[3]
                    _matrix2=rotate_matrix(0.0, 3.14, 0.0,_matrix2) # Rotação da matriz, para casar na próxima cinemática
                    cinematica_x.append(_matrix1[:3,3][0])
                    cinematica_y.append(_matrix1[:3,3][1]+10) 
                    cinematica_x2.append(_matrix2[:3,3][0]) # Posição X do manipulador
                    cinematica_y2.append(_matrix2[:3,3][1]+10) # Posição Y ajustada - origem do ADAMs (0,20,0)

        #PLOT
        # Extraindo as posições X, Y e Z do arquivo do ADAMs
        adams_time = StepsPata1["Time      "]
        StepsX_Pata1 = StepsPata1["X"]
        StepsY_Pata1 = StepsPata1["Y"]
        StepsX_Pata2 = StepsPata2["X"]
        StepsY_Pata2 = StepsPata2["Y"]    
        # Rename column to remove trailing spaces
        StepsPata1.rename(columns={"Time      ": "Time"}, inplace=True)

        # Identify reset points
        reset_indices = StepsPata1[StepsPata1["Time"].diff() < 0].index

        #print(reset_indices)
        # Initialize time offset and create a copy of the time column
        time_offset = 6
        last_time = 0
        adams_time = StepsPata1["Time"].copy()

        # Adjust time values
        for idx in reset_indices:
            last_time = adams_time.loc[idx - 1]
            adams_time.loc[idx:] += time_offset

        # Store adjusted time back into the DataFrame
        StepsPata1["Adjusted_Time"] = adams_time

        # Retrieve the last time step
        last_time_step = adams_time.iloc[-1]

        # Criando os gráficos para comparar:
        # 1 - Posições convergidas pelo código;
        # 2 - Posições retiradas do Software - ADAMs
        
        plt.plot(adams_time.to_numpy(), StepsX_Pata1.to_numpy(), color='black', linestyle = 'dashed',
                 #label='PATA1 X ADAMS'
                 )
        plt.plot(adams_time.to_numpy(), StepsX_Pata2.to_numpy(), color='black', linestyle = 'dashed',
                 #label='PATA1 X ADAMS'
                 )
        plt.plot(adams_time.to_numpy(), StepsY_Pata1.to_numpy(), color='black', linestyle = 'dashed',
                 #label='PATA2 Y ADAMS'
                 )
        plt.plot(adams_time.to_numpy(), StepsY_Pata2.to_numpy(), color='black', linestyle = 'dashed',
                 label='ADAMS Reference'
                 )
 
        plt.plot(adams_time.to_numpy(), cinematica_x, color='b', linestyle = 'dotted',
                 label='PATA1 X - DH')
        plt.plot(adams_time.to_numpy(), cinematica_y, color='y', linestyle = 'dotted',
                 label='PATA1 Y - DH')
        plt.plot(adams_time.to_numpy(), cinematica_x2, color='r', linestyle = 'dotted',
                 label='PATA2 X - DH')
        plt.plot(adams_time.to_numpy(), cinematica_y2, color='g', linestyle = 'dotted',
                 label='PATA2 Y - DH')
        # Renomeando os eixos e o título do gráfico
        plt.xlabel("Tempo [s]")
        plt.ylabel("Deslocamento [mm]")
        plt.title("Comparativo")

        # Adicionando legenda para identificar as curvas de acordo com as cores
        plt.legend()

        # Exibindo a janela gráfica
        plt.show()
