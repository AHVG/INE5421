""" 
========= INSTRUÇÕES ========= 
    - Todo o código deve estar contido no arquivo main.py
    - O arquivo main.py deve conter uma função main que será chamada pelo VPL,
      essa função deve conter uma linha de código que recebe a string de entrada do VPL.
      Um exemplo de como isso pode ser feito está no arquivo main.py fornecido.
    - Você pode criar funções fora da main se preferir, mas se certifique de que a main chama essas funções.
    - Caso você prefira fazer o exercício em uma IDE e quiser testar o código localmente, 
        é só passar a string de entrada como argumento na hora de executar o código. 
            Exemplo: python3 main.py "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C"
        
Formato da saída:   <<automato finito determinístico><automato finito determinístico mínimo>>
                    <<3;{A};{D};{a,b};{A},a,{A};{A},a,{B};{A},b,{A};{B},b,{C};{C},b,{D}><3;{A};{D};{a,b};{A},a,{A};{A},a,{B};{A},b,{A};{B},b,{C};{C},b,{D}>>

DICA: O programa avalia somente o que está dentro das tags <>.
"""

from sys import argv

def main():
    
    vpl_input = argv[1]

    

if __name__ == "__main__":
    main()