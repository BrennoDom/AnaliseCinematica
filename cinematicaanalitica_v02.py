# -*- coding: utf-8 -*-
"""cinematicaAnalitica.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aBLAF8IP5RhUfjwVetf8lhbBzQ3AES8Q
"""
#comentario
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
#from transforms3d.euler import euler2mat

##############################
def euler2mat(roll, pitch, yaw, M):
    
    R_x = np.array([[1, 0, 0,0],
                    [0, np.cos(roll), -np.sin(roll),0],
                    [0, np.sin(roll), np.cos(roll),0],
                    [0,0,0,1]])
    
    R_y = np.array([[np.cos(pitch), 0, np.sin(pitch),0],
                    [0, 1, 0,0],
                    [-np.sin(pitch), 0, np.cos(pitch),0],
                    [0,0,0,1]])
    
    R_z = np.array([[np.cos(yaw), -np.sin(yaw), 0,0],
                    [np.sin(yaw), np.cos(yaw), 0,0],
                    [0, 0, 0,0],
                    [0,0,0,1]])

    # Matriz de rotação combinada
    R = np.dot(R_z, np.dot(R_y, R_x))
    
    
    return np.dot(R,M)

############ CINEMÁTICA GERAL ############
def ler_thetas(in_theta1,in_theta2,in_theta3,in_theta4):


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

    # Imprime para verificar
    print(theta1_bruto)

    #criando os vetores para armazenar os ângulos corrigidos em radianos
    theta1 = np.zeros(len(theta1_degree))
    theta2 = np.zeros(len(theta1_degree))
    theta3 = np.zeros(len(theta1_degree))
    theta4 = np.zeros(len(theta1_degree))
    
    thetas = [0] * len(theta1_degree)
    # Corrigindo os ângulos e convertendo para radianos
    for i in range(len(theta1_degree)):

      theta1[i] = m.radians(theta1_degree[i] + in_theta1)
      theta2[i] = m.radians(theta2_degree[i] + in_theta2)
      theta3[i] = m.radians(theta3_degree[i] + in_theta3)
      theta4[i] = m.radians(theta4_degree[i] + in_theta4)
      thetas[i] = [theta1[i],theta2[i],theta3[i],theta4[i]]

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

      Parâmetros utilizados no código:
        a -> comprimento do link [mm];
        α -> ângulo de torção entre os eixos Z de dois links consecutivos [rad];
        d -> deslocamento linear do link (para juntas prismáticas) [mm];
        θ -> deslocamento angular do link (para juntas de revolução) [rad].

      Retorna:
        A -> matriz 4x4 de transformação homogênea.

    """

   # Definindo a matriz de transformação homogênea de acordo com os parâm. DH
    A = np.array([[m.cos(theta), -m.sin(theta)*m.cos(alpha), m.sin(theta)*m.sin(alpha), a*m.cos(theta)],
                  [m.sin(theta),  m.cos(theta)*m.cos(alpha), -m.cos(theta)*m.sin(alpha), a*m.sin(theta)],
                  [           0,               m.sin(alpha),               m.cos(alpha),              d],
                  [           0,                          0,                          0,               1]])

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

def erro_percentual(dh, adams):
    
    erro = []

    for i in range(len(dh)):
        
        if adams[i] == 0.0 and abs(dh[i]) < 1e-15:
            
            e = 0
            
        elif adams[i] == 0.0 and abs(dh[i]) > 1e-15:
            
            ep = 1e-15
            e = (abs(dh[i]-adams[i])/abs(adams[i]+ep))*100
            
        else:
            if dh[i] == 0.0:
                
                ep = 1e-15
                e = (abs(dh[i]-adams[i]+ep)/abs(adams[i]))*100
            else:
                e = (abs(dh[i]-adams[i])/abs(adams[i]))*100
        
        erro.append(e)
        
        print(i)
        
    return erro

def erro_percentual2(dh, adams):
    
    erro = []

    for i in range(len(dh)):
        
        adam = adams[i]
        
        if adam == 0.0:
            
            adam = 1e-15
        
        e = (abs(dh[i]-adams[i])/adam)*100
        
        if e > 20 or e < -20:
            
            e = 0
        
        erro.append(e)
        
        print(i)
        
    return erro

def rmsd(dh,adams):
    
    '''
    RMSD = Desvio da raiz quadrada média
    i = variável i
    N = número de pontos de dados não faltantes
    xi = série temporal de observações
    xd = série temporal estimada
    '''
    
    soma = 0
    
    for i in range(len(dh)):
        
        soma = soma + m.pow(dh[i]-adams[i],2)
        
    rmsd = m.sqrt(soma/len(dh))
    
    return rmsd
    

# Função principal - main
if __name__ == '__main__':
        L = [136.01, 141.42, 152.64]
      

        DH_a1 = [L[0],L[1],L[2],0]
        DH_a2 = [L[2],L[1],L[0],0]

        DH_alpha = [0,0,0,0]
        DH_d = [0,0,0,0]
        thetas = ler_thetas(53.97,-45.84,-66.52,-31.61)

        STEP1PATA2 = "./teste2/step1/XeYPata2.tab"
        STEP2PATA2 = "./teste2/step2/XeYPata2.tab"
        STEP1PATA1 = "./teste2/step1/XeYPata1.tab"
        STEP2PATA1 = "./teste2/step2/XeYPata1.tab"
        STEPSPATA1 = "./teste2/Steps/XeYPata1.tab"
        # Lendo os dados de posição do arquivo do ADAMs
        Step1Pata2 = read(STEP1PATA2, 1)
        Step2Pata2 = read(STEP2PATA2,1)
        Step1Pata1 = read(STEP1PATA1, 1)
        Step2Pata1 = read(STEP2PATA1,1)
        StepsPata1 = read(STEPSPATA1,1)
        timeread  = StepsPata1["Time      "]
        time_step = len(timeread)
        # AQUI VEM A FUNÇÃO DE IDENTIFICAÇÃO DOS PONTOS DE MUDANÇA DE BASE
        aux = 0
        flag_changes = 0
        N = StepsPata1.shape[0]

        P1_norma = np.zeros(N)

        for k in range(N):
            P1_norma[k] = np.linalg.norm(StepsPata1.iloc[k, 1:3])

        changes = []
        for k in range(0,N-1):
            if (P1_norma[k] == P1_norma[k + 1]) and (flag_changes == 0):
                aux += 1
                flag_changes = 1
                changes.append(k)
            else:
                if P1_norma[k] == P1_norma[k + 1]:
                    flag_changes = 1
                elif (P1_norma[k - 1] == P1_norma[k]) and (flag_changes == 1):
                    aux += 1
                    changes.append(k+1)
                    flag_changes = 0
                else:
                    flag_changes = 0

         # AQUI VEM A FUNÇÃO DE MUDANÇA DE BASE
        flag = False
        cinematica_x = []
        cinematica_y = []
        cinematica_x2 = []
        cinematica_y2 = []
        theta1 = []
        theta2 = []
        matrix1 = np.identity(4)
        
        #marcadores para quebrar o vetor quanto hà mudança de base
        inicio = 0
        final = 0 
        
        
        for i in range(time_step):
            
                final = changes[0]
                
                theta1.append([thetas[i][0],thetas[i][1],thetas[i][2],thetas[i][3]]) 
                theta2.append([thetas[i][3],thetas[i][2],thetas[i][1],thetas[i][0]])
                for j in range(len(changes)):
                       
                    if i == changes[j]:
                        if flag:
                            flag = False
                        else:
                            flag = True
                if flag:
                    matrix =  kinematic(DH_a1, DH_alpha, DH_d, theta1[i], np.identity(4))
                    matrix1 = matrix[3]
                    posicao1_y = matrix[3][:3,3][1]
                    posicao1_x = matrix[3][:3,3][0]
                    cinematica_x.append(matrix[3][:3,3][0]) # Posição X do manipulador
                    cinematica_y.append(matrix[3][:3,3][1]+10) # Posição Y ajustada - origem do ADAMs (0,20,0)
                    
                    if cinematica_x2==[]:
                        
                        cinematica_x2.append(0.0)
                        cinematica_y2.append(0.0+10)     
                    else:
                        cinematica_x2.append(cinematica_x2[-1])
                        cinematica_y2.append(cinematica_y2[-1])
                    
                
                else:
                    matrix =  kinematic(DH_a2, DH_alpha, DH_d, theta2[i], euler2mat(0, m.pi, m.pi, matrix1))
                    matrix2 = matrix[3]
                    cinematica_x2.append(matrix[3][:3,3][0]) # Posição X do manipulador
                    cinematica_y2.append(matrix[3][:3,3][1]+10) # Posição Y ajustada - origem do ADAMs (0,20,0)
                    
                    if i == changes[j] and i != 0: #resolvendo BUG
                        cinematica_x[changes[j]-1]= cinematica_x[changes[j]-2]
                
                    if cinematica_x == []:
                        
                        cinematica_x.append(0.0)
                        cinematica_y.append(0.0)
                    else:
                        cinematica_x.append(cinematica_x[-1])
                        cinematica_y.append(cinematica_y[-1])
                
                inicio = final
                
        
        #PLOT
        # Extraindo as posições X, Y e Z do arquivo do ADAMs
        adams_time = Step1Pata2["Time      "]
        adams_Pata2_x = Step1Pata2[".MARKER_65.Translational_Displacement.X"]
        adams_Pata2_x2 = Step2Pata2[".MARKER_50.Translational_Displacement.X"]
        adams_Pata2_y = Step1Pata2[".MARKER_65.Translational_Displacement.Y"]
        adams_Pata2_y2 = Step2Pata2[".MARKER_50.Translational_Displacement.Y"]
        adams_Pata1_x = Step1Pata1[".MARKER_61.Translational_Displacement.X"]
        adams_Pata1_x2 = Step2Pata1[".MARKER_39.Translational_Displacement.X"]
        adams_Pata1_y = Step1Pata1[".MARKER_61.Translational_Displacement.Y"]
        adams_Pata1_y2 = Step2Pata1[".MARKER_39.Translational_Displacement.Y"]       
        
        last_time_step = (adams_time.to_numpy()[len(adams_time)-1])
        adams_time_2 = adams_time + last_time_step
        
        #JUNTANDO TUDO
        time = pd.Series.to_list(pd.concat([adams_time,adams_time_2])) 
        pata1x_adams = pd.Series.to_list(pd.concat([adams_Pata1_x,adams_Pata1_x2]))
        pata2x_adams = pd.Series.to_list(pd.concat([adams_Pata2_x,adams_Pata2_x2]))
        pata1y_adams = pd.Series.to_list(pd.concat([adams_Pata1_y,adams_Pata1_y2]))
        pata2y_adams = pd.Series.to_list(pd.concat([adams_Pata2_y,adams_Pata2_y2]))
        
        
        #Calculo do Erro Quadrático Médio
        erro_1x = rmsd(cinematica_x2,pata1x_adams)
        erro_1y = rmsd(cinematica_y2,pata1y_adams)
        
        erro_2y = rmsd(cinematica_y,pata2y_adams)
        erro_2x = rmsd(cinematica_x,pata2x_adams)
        
        #Calculo do vetor de erro ponto a ponto
        errop_1x = erro_percentual2(cinematica_x2,pata1x_adams)
        errop_1y = erro_percentual2(cinematica_y2,pata1y_adams)
        
        errop_2y = erro_percentual2(cinematica_y,pata2y_adams)
        errop_2x = erro_percentual2(cinematica_x,pata2x_adams)
        
    
        # Criando os gráficos para comparar:
        # 1 - Posições convergidas pelo código;
        # 2 - Posições retiradas do Software - ADAMs
        
        fig,(ax1,ax2) = plt.subplots(nrows=1,ncols=2)
        ax1.set_xlabel('Tempo [s]')
        ax1.set_ylabel('Posição [mm]')
        ax1.set_title("Comparativo das posições")
        
        color = 'tab:red'
        ax1.plot(time, pata1x_adams,  color = color, linestyle = 'dashed', label='Pata 1 X') 
        ax1.plot(time, cinematica_x2,  color = color, linestyle = 'dotted', label='Pata 1 X - DH') 
        
        color = 'tab:blue'
        ax1.plot(time, pata1y_adams,  color = color, linestyle = 'dashed', label='Pata 1 Y')
        ax1.plot(time, cinematica_y2,  color = color, linestyle = 'dotted', label='Pata 1 Y - DH')
        
        color = 'tab:green'
        ax1.plot(time, pata2x_adams,  color = color, linestyle = 'dashed', label='Pata 2 X')
        ax1.plot(time, cinematica_x,   color = color, linestyle = 'dotted', label='Pata 2 X - DH')
        
        color = 'tab:orange'
        ax1.plot(time, pata2y_adams,  color = color, linestyle = 'dashed', label='Pata 2 Y')
        ax1.plot(time, cinematica_y,  color = color, linestyle = 'dotted', label='Pata 2 Y - DH')
        
        ax2.set_ylabel('Percentual [%]')
        ax2.set_title("Erro")
        ax2.plot(time, errop_1x, color = 'tab:red', label = 'Pata 1 X')
        ax2.plot(time, errop_2x, color = 'tab:green', label = 'Pata 2 X')
        ax2.plot(time, errop_1y, color = 'tab:blue', label = 'Pata 1 Y')
        ax2.plot(time, errop_2y, color = 'tab:orange', label = 'Pata 2 Y')
        
        fig.tight_layout()


        # Adicionando legenda para identificar as curvas de acordo com as cores
        ax1.legend()
        ax2.legend()
        # Exibindo a janela gráfica
        plt.show()
        
    
        print("O Erro Quadrático Médio é: \n")
        print("Step 1 - X: ", erro_2x, "\n")
        print("Step 1 - Y: ", erro_2y, "\n")
        print("Step 2 - X: ", erro_1x, "\n")
        print("Step 2 - Y: ", erro_1y, "\n")
