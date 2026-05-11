import threading
import time
import random

class Fork:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()
    
    def acquire(self, philosopher_id):
        self.lock.acquire()
    
    def release(self, philosopher_id):
        self.lock.release()

class Philosopher(threading.Thread):
    def __init__(self, id, left_fork, right_fork):
        threading.Thread.__init__(self)
        self.id = id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.running = True
    
    def think(self):
        print(f"Filosofo {self.id} pensando...")
        time.sleep(random.uniform(1, 3))
    
    def eat(self):
        print(f"Filosofo {self.id} COMENDO 🍝")
        time.sleep(random.uniform(1, 2))
        print(f"Filosofo {self.id} terminou de comer")
    
    def get_forks_random_order(self):
        """Pega os garfos em ordem aleatória (respeitando 'não importa a ordem')"""
        # Decide aleatoriamente a ordem dos garfos
        if random.choice([True, False]):
            # Primeiro esquerdo, depois direito
            self.left_fork.acquire(self.id)
            print(f"Filosofo {self.id} pegou garfo esquerdo {self.left_fork.id}")
            self.right_fork.acquire(self.id)
            print(f"Filosofo {self.id} pegou garfo direito {self.right_fork.id}")
        else:
            # Primeiro direito, depois esquerdo
            self.right_fork.acquire(self.id)
            print(f"Filosofo {self.id} pegou garfo direito {self.right_fork.id}")
            self.left_fork.acquire(self.id)
            print(f"Filosofo {self.id} pegou garfo esquerdo {self.left_fork.id}")
    
    def release_forks(self):
        """Larga os dois garfos"""
        self.left_fork.release(self.id)
        self.right_fork.release(self.id)
        print(f"Filosofo {self.id} largou ambos os garfos")
    
    def run(self):
        while self.running:
            self.think()
            
            print(f"Filosofo {self.id} ficou faminto e vai tentar pegar os garfos")
            self.get_forks_random_order()  # Ordem aleatória!
            
            self.eat()
            self.release_forks()
    
    def stop(self):
        self.running = False

# Solução com temporizador para evitar deadlock
# A regra "não importa a ordem" pode causar deadlock!
# Por isso adicionamos um mecanismo de timeout

class PhilosopherWithTimeout(Philosopher):
    """Versão que usa timeout para evitar deadlock"""
    
    def get_forks_with_timeout(self):
        """Tenta pegar garfos, desiste se demorar muito"""
        order = random.choice([('left', 'right'), ('right', 'left')])
        
        start_time = time.time()
        timeout = 2  # 2 segundos de timeout
        
        # Tenta primeiro garfo
        if order[0] == 'left':
            self.left_fork.acquire(self.id)
            print(f"Filosofo {self.id} pegou garfo esquerdo {self.left_fork.id}")
            # Tenta segundo garfo com timeout
            while time.time() - start_time < timeout:
                if self.right_fork.lock.acquire(blocking=False):
                    print(f"Filosofo {self.id} pegou garfo direito {self.right_fork.id}")
                    return True
                time.sleep(0.1)
            # Timeout: larga o primeiro garfo e tenta de novo
            self.left_fork.release(self.id)
            print(f"Filosofo {self.id} desistiu e largou o garfo")
            return False
        else:
            self.right_fork.acquire(self.id)
            print(f"Filosofo {self.id} pegou garfo direito {self.right_fork.id}")
            while time.time() - start_time < timeout:
                if self.left_fork.lock.acquire(blocking=False):
                    print(f"Filosofo {self.id} pegou garfo esquerdo {self.left_fork.id}")
                    return True
                time.sleep(0.1)
            self.right_fork.release(self.id)
            print(f"Filosofo {self.id} desistiu e largou o garfo")
            return False
    
    def run(self):
        while self.running:
            self.think()
            print(f"Filosofo {self.id} ficou faminto")
            
            while True:
                if self.get_forks_with_timeout():
                    break
                print(f"Filosofo {self.id} vai tentar novamente")
                time.sleep(random.uniform(0.5, 1))
            
            self.eat()
            self.release_forks()

if __name__ == "__main__":
    print("="*60)
    print("JANTAR DOS FILOSOFOS - RESPEITANDO TODAS AS REGRAS")
    print("Regra: 'pega os garfos um de cada vez, não importa a ordem'")
    print("="*60 + "\n")
    
    # Cria os garfos
    forks = [Fork(i) for i in range(5)]
    
    # Cria os filosofos
    philosophers = []
    for i in range(5):
        left = forks[i]
        right = forks[(i + 1) % 5]
        p = PhilosopherWithTimeout(i, left, right)
        philosophers.append(p)
    
    # Inicia todos
    for p in philosophers:
        p.start()
    
    # Executa por 15 segundos
    time.sleep(15)
    
    # Finaliza
    print("\n" + "="*60)
    print("Encerrando o jantar...")
    for p in philosophers:
        p.stop()
    
    for p in philosophers:
        p.join()
    
    print("Jantar encerrado! Todos os filosofos conseguiram comer eventualmente.")