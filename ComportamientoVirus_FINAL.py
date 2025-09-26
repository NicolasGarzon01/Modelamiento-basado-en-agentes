import mesa
import mesa.time
import pandas as pd

class InfectionAgent(mesa.Agent):
    """
    Representa a un agente (individuo) en la simulación.
    """
    def __init__(self, unique_id, model):
        # Inicialización manual para esquivar la instalación corrupta
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        
        # Atributos específicos de nuestro modelo
        self.state = "Susceptible"
        self.infection_time = 0

    def move(self):
        """Mueve al agente a una celda vecina aleatoria."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def update_status(self):
        """
        Verifica si el agente debe recuperarse.
        """
        if self.state == "Infected":
            time_infected = self.model.schedule.time - self.infection_time
            if time_infected >= self.model.recovery_time:
                self.state = "Recovered"

    def infect(self):
        """
        Intenta contagiar a otros agentes en la misma celda.
        """
        if self.state == "Infected":
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            if len(cellmates) > 1:
                for other_agent in cellmates:
                    if other_agent.state == "Susceptible":
                        if self.random.random() < self.model.infection_rate:
                            other_agent.state = "Infected"
                            other_agent.infection_time = self.model.schedule.time

    def step(self):
        """
        Secuencia de acciones del agente en cada paso de tiempo.
        """
        self.update_status()
        self.move()
        self.infect()


class InfectionModel(mesa.Model):
    """
    El modelo principal que contiene a todos los agentes y el entorno.
    """
    def __init__(self, N=100, width=20, height=20, initial_infected=5,
                 infection_rate=0.1, recovery_time=15):
        
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        self.infection_rate = infection_rate
        self.recovery_time = recovery_time

        for i in range(self.num_agents):
            agent = InfectionAgent(i, self)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

            if i < initial_infected:
                agent.state = "Infected"
                agent.infection_time = self.schedule.time
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Susceptible": lambda m: sum(1 for a in m.schedule.agents if a.state == "Susceptible"),
                "Infected": lambda m: sum(1 for a in m.schedule.agents if a.state == "Infected"),
                "Recovered": lambda m: sum(1 for a in m.schedule.agents if a.state == "Recovered"),
            }
        )

    def step(self):
        """Avanza la simulación un paso en el tiempo."""
        self.schedule.step()             # 1. Agentes actúan PRIMERO
        self.datacollector.collect(self) # 2. Registra datos DESPUÉS
        
        if sum(1 for agent in self.schedule.agents if agent.state == "Infected") == 0:
            self.running = False


# --- Bloque para ejecutar la simulación ---
if __name__ == "__main__":
    SIMULATION_STEPS = 100
    model = InfectionModel(N=100, initial_infected=5, infection_rate=0.2)
    
    # El primer estado (paso 0) debe registrarse antes de empezar
    model.step()

    # El bucle principal
    for i in range(SIMULATION_STEPS - 1): # Restamos 1 porque ya hicimos el primer paso
        if model.running:
            model.step()
        else:
            break

    results = model.datacollector.get_model_vars_dataframe()

    pd.set_option('display.max_rows', None)
    
    print("--- Resultados de la Simulación del Virus ---")
    print(results)