import agents

def test_compare_agents() :
    environment = agents.VacuumeEnvironment
    agentList = [agents.TableDrivenVacuumAgent,agents.RandomVacuumAgent, agents.ReflexVacuumAgent]

    result = agents.compare_agents(environment, agentList,[(1,0),(2,0),(0,0)])
    for i in range(0,len(result)):
    print("{}'s avg performance: {}".format(result[i][0].__name__,result[i][1]))

#runs a single vacuum environment with a specific agent and step count
class vacuumSim():
    def __init__(self):
        self.vacuumEnvironment = agents.VacuumeEnvironment()
    
    def startSim(self):
        self.vacuumEnvironment.add_thing(agents.TraceAgent(agents.ReflexVacuumAgent()))
        #self.vacuumEnvironment.add_thing(agents.TraceAgent(agents.TableDrivenVacuumAgent()))
        self.vacuumEnvironment.run(10)

def main():
   
   vacSim=vacuumSim()
   vacSim.startSim()

   #test_compare_agents()  #used to compare multiple agents in the same environment conditions


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  