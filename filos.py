import threading
import time
import random

class Filosofo(threading.Thread):
    def __init__(self, nome, garfo_esquerda, garfo_direita, refeicoes_necessarias):
        threading.Thread.__init__(self)
        self.nome = nome
        self.garfo_esquerda = garfo_esquerda
        self.garfo_direita = garfo_direita
        self.refeicoes_necessarias = refeicoes_necessarias
        self.refeicoes_feitas = 0
        
    def pensar(self):
        print(f"{self.nome} está pensando...")
        time.sleep(random.uniform(0.1, 0.5))
    
    def comer(self):
        print(f"{self.nome} está comendo (refeição {self.refeicoes_feitas + 1} de {self.refeicoes_necessarias})")
        time.sleep(random.uniform(0.2, 0.6))
        self.refeicoes_feitas += 1
    
    def pegar_garfos(self):
        """Tenta pegar os dois garfos. Se não conseguir o segundo, devolve o primeiro."""
        if self.nome % 2 == 0:  # Filósofos pares: ESQUERDA primeiro
            self.garfo_esquerda.acquire()
            print(f"{self.nome} pegou garfo esquerdo")
            
            # Tenta pegar o direito sem bloquear
            if self.garfo_direita.acquire(blocking=False):
                print(f"{self.nome} pegou garfo direito")
                return True
            else:
                print(f"{self.nome} não conseguiu o direito - devolvendo o esquerdo")
                self.garfo_esquerda.release()
                return False
                
        else:  # Filósofos ímpares: DIREITA primeiro
            self.garfo_direita.acquire()
            print(f"{self.nome} pegou garfo direito")
            
            if self.garfo_esquerda.acquire(blocking=False):
                print(f"{self.nome} pegou garfo esquerdo")
                return True
            else:
                print(f"{self.nome} não conseguiu o esquerdo - devolvendo o direito")
                self.garfo_direita.release()
                return False
    
    def largar_garfos(self):
        self.garfo_esquerda.release()
        self.garfo_direita.release()
        print(f"{self.nome} largou os garfos")
    
    def run(self):
        while self.refeicoes_feitas < self.refeicoes_necessarias:
            self.pensar()
            if self.pegar_garfos():  # Só come se conseguir os dois!
                self.comer()
                self.largar_garfos()
            # Se não conseguiu, volta a pensar
        print(f"{self.nome} terminou de comer!")

def main():
    NUM_FILOSOFOS = 5
    REFEICOES_POR_FILOSOFO = 3
    
    garfos = [threading.Semaphore(1) for _ in range(NUM_FILOSOFOS)]
    
    filosofos = []
    for i in range(NUM_FILOSOFOS):
        esquerda = garfos[i]
        direita = garfos[(i + 1) % NUM_FILOSOFOS]
        filosofo = Filosofo(i, esquerda, direita, REFEICOES_POR_FILOSOFO)
        filosofos.append(filosofo)
    
    for filosofo in filosofos:
        filosofo.start()
    
    for filosofo in filosofos:
        filosofo.join()
    
    print("\nTodos os filósofos terminaram de comer!")

if __name__ == "__main__":
    main()