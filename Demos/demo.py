import agents

def test_compare_agents() :
    environment = agents.VacuumeEnvironment
    agentList = [agents.TableDrivenVacuumAgent,agents.RandomVacuumAgent, agents.ReflexVacuumAgent]

    result = agents.compare_agents(environment, agentList,[(1,0),(2,0),(0,0)])
    for i in range(0,len(result)):
        print("{}'s avg performance: {}".format(result[i][0].__name__,result[i][1]))
    #performance_ModelBasedVacummAgent = result[0][1]
    #performance_ReflexVacummAgent = result[1][1]

    # The performance of ModelBasedVacuumAgent will be at least as good as that of
    # ReflexVacuumAgent, since ModelBasedVacuumAgent can identify when it has
    # reached the terminal state (both locations being clean) and will perform
    # NoOp leading to 0 performance change, whereas ReflexVacuumAgent cannot
    # identify the terminal state and thus will keep moving, leading to worse
    # performance compared to ModelBasedVacuumAgent.
    #assert performance_ReflexVacummAgent <= performance_ModelBasedVacummAgent


class vacuumSim():
    def __init__(self):
        self.vacuumEnvironment = agents.VacuumeEnvironment()
    
    def startSim(self):
        self.vacuumEnvironment.add_thing(agents.TraceAgent(agents.ReflexVacuumAgent()))
        self.vacuumEnvironment.add_thing(agents.TraceAgent(agents.TableDrivenVacuumAgent()))
        self.vacuumEnvironment.run(10)

def main():
   #vacSim=vacuumSim()
   #vacSim.startSim()
    test_compare_agents()


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  