import mesa
import mesa.time
import pandas as pd

class InfectionAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.pos = None
        self.state = "Susceptible"
        self.infection_time = 0
        # Nuevo atributo para la cuarentena
        self.is_quarantined = False

    def move(self):
        # --- ESTRATEGIA 1: DISTANCIAMIENTO SOCIAL ---
        # El agente solo se mueve si supera una probabilidad aleatoria
        if self.random.random() > self.model.social_distancing_rate:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def update_status(self):
        if self.state == "Infected":
            time_infected = self.model.schedule.time - self.infection_time
            if time_infected >= self.model.recovery_time:
                self.state = "Recovered"
                # Si estaba en cuarentena, ahora puede "salir"
                if self.is_quarantined:
                    self.is_quarantined = False
                    # Lo reubicamos en la cuadrícula
                    x = self.random.randrange(self.model.grid.width)
                    y = self.random.randrange(self.model.grid.height)
                    self.model.grid.place_agent(self, (x, y))

    def infect(self):
        if self.state == "Infected":
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            for other in cellmates:
                if other.state == "Susceptible":
                    if self.random.random() < self.model.infection_rate:
                        other.state = "Infected"
                        other.infection_time = self.model.schedule.time
                        # --- ESTRATEGIA 3: CUARENTENA ---
                        if self.model.quarantine_enabled:
                            other.is_quarantined = True
                            # Lo removemos de la cuadrícula para que no interactúe
                            self.model.grid.remove_agent(other)

    def step(self):
        # Un agente en cuarentena no se mueve ni infecta, solo espera a recuperarse
        if self.is_quarantined:
            self.update_status()
        else:
            self.update_status()
            self.move()
            self.infect()


class InfectionModel(mesa.Model):
    def __init__(self, N=100, width=20, height=20, initial_infected=5,
                 infection_rate=0.1, recovery_time=15,
                 # --- NUEVOS PARÁMETROS PARA LAS ESTRATEGIAS ---
                 social_distancing_rate=0.0, # Probabilidad de 0 a 1 de no moverse
                 quarantine_enabled=False,   # Activar/Desactivar cuarentena
                 initial_vaccinated_rate=0.0 # Porcentaje de 0 a 1 de vacunados iniciales
                ):
        
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        # Parámetros del modelo y estrategias
        self.infection_rate = infection_rate
        self.recovery_time = recovery_time
        self.social_distancing_rate = social_distancing_rate
        self.quarantine_enabled = quarantine_enabled

        # Creación de agentes
        for i in range(self.num_agents):
            agent = InfectionAgent(i, self)
            
            # --- ESTRATEGIA 4: VACUNACIÓN ---
            # Algunos agentes empiezan como "Recuperados" (inmunes)
            if self.random.random() < initial_vaccinated_rate:
                agent.state = "Recovered"
            
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

            # Infectar agentes (solo si no fueron vacunados)
            if agent.state == "Susceptible" and i < (initial_infected + int(N*initial_vaccinated_rate)):
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
        self.schedule.step()
        self.datacollector.collect(self)
        if sum(1 for a in self.schedule.agents if a.state == "Infected") == 0:
            self.running = False


# --- Bloque para ejecutar la simulación ---
if __name__ == "__main__":
    SIMULATION_STEPS = 150 # Aumentamos los pasos para ver mejor los efectos

    
    model = InfectionModel(
        N=200, 
        initial_infected=10, 
        infection_rate=0.25,
        social_distancing_rate=0.5, # 50% de la gente reduce su movimiento
        quarantine_enabled=True,      # La gente se aísla al dar positivo
        initial_vaccinated_rate=0.3 # El 30% de la población está vacunada
    )
    
    model.step()
    for i in range(SIMULATION_STEPS - 1):
        if model.running:
            model.step()
        else:
            break

    results = model.datacollector.get_model_vars_dataframe()
    pd.set_option('display.max_rows', None)
    
    print("--- Resultados de la Simulación del Virus con Estrategias ---")

    print(results)


