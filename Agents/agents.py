from utils import distance_squared, turn_heading
from statistics import mean

import random
import copy
import collections

loc_A, loc_B, loc_C = (0,0), (1, 0), (2, 0)

class Thing:
    def __repr__(self):
        return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

    def is_alive(self):
        """Things that are 'alive' should return true."""
        return hasattr(self, 'alive') and self.alive

    def show_state(self):
        """Display the agent's internal state. Subclasses should override."""
        print("I don't know how to show_state.")

    def display(self, canvas, x, y, width, height):
        """Display an image of this Thing on the canvas."""
        # Do we need this?
        pass

class Agent(Thing):

    def __init__(self,program=None):
        self.alive = True
        self.performance = 0

        if program is None or not isinstance(program, collections.Callable):
            print("Can't find a valid program for {}, falling back to default.".format(self.__class__.__name__))
            def program(percept):
                return eval(input('Percept={}; action? '.format(percept)))
        
        self.program = program;


def TraceAgent(agent):
    """Wrap the agent's program to print its input and output. This will let
    you see what the agent is doing in the environment."""
    old_program = agent.program

    def new_program(percept):
        action = old_program(percept)
        print('{} perceives {} and does {}.'.format(agent, percept, action))
        return action
    agent.program = new_program
    return agent


#---------------------------------------------------------------------------------------#
def SimpleReflexAgentProgram(rules, interpret_input):
    """This agent takes action based solely on the percept. [Figure 2.10]"""
    def program(percept):
        state = interpret_input(percept)
        rule = rule_match(state, rules)
        action = rule.action
        return action
    return program


def rule_match(state, rules):
    """Find the first rule that matches state."""
    for rule in rules:
        if rule.matches(state):
            return rule
#-----------------------------------------------------------------------------------------#

class Environment:
    def __init__(self):
        self.things = []
        self.agents = []
    
    def thing_classes(self):
        return []

        
    def percept(self,agent):
        raise NotImplementedError
    
    def add_thing(self, thing, location=None):
        if not isinstance(thing,Thing):
            thing = Agent(thing)
        if thing in self.things:
            print('Cant add the same thing twice')
        else:
            if location is not None:
                thing.location = location
            else:
                thing.location = self.default_location()

            #thing.location = location if location is not None else self.default_location()
            self.things.append(thing)
            if isinstance(thing,Agent):
                thing.performance = 0
                self.agents.append(thing)
                
    def is_done(self):
        """By default, we're done when we can't find a live agent."""
        return not any(agent.is_alive() for agent in self.agents)

    def step(self,count):

        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    actions.append(agent.program(self.percept(agent))) #add the action returned by the program based on the percept of the agent.
                else:
                    #evaluateAgent(agent,count)
                    actions.append("")
           
            for (agent,action) in zip(self.agents,actions):
                self.execute_action(agent,action)
            
    def run(self, steps=1000):
        for step in range(steps):
            if self.is_done():
                return
            self.step(step)
        
        
        '''if self.agents: #used to evaluate any remaining agents performance that are still alive after steps are ran
            for agent in self.agents:
                self.evaluateAgent(agent,steps)'''

    def evaluateAgent(self,agent,count):
        print('{}\'s overall performance: {}'.format(agent,float(agent.performance/count)))

class VacuumeEnvironment(Environment):
    def __init__(self,initialState=None):
        super().__init__()
        if initialState == None:
            self.status = { loc_A: random.choice(['Clean','Dirty']),
                            loc_B: random.choice(['Clean','Dirty']),
                            loc_C: random.choice(['Clean','Dirty'])}
        else:
            self.status = initialState

        print(self.status)
        self.dirtProb = 20

    def thing_classes(self): 
        return [ReflexVacuumAgent]

    def percept(self,agent):
        return(agent.location,self.status[agent.location])

    def execute_action(self, agent, action):
        if action == 'Right' and agent.location == loc_A:
            agent.location = loc_B
            agent.performance -= 1
        
        elif action == 'Right' and agent.location == loc_B:
            agent.location = loc_C
            agent.performance -= 1
        
        elif action == 'Left' and agent.location == loc_B:
            agent.location = loc_A
            agent.performance -= 1
        
        elif action == 'Left' and agent.location == loc_C:
            agent.location = loc_B
            agent.performance -= 1
        
        elif action == 'Suck':
            if self.status[agent.location]=='Dirty':
                agent.performance += 10
           
            self.status[agent.location]='Clean'

        agent.performance -= self.verifyStatus()
        #self.updateEnvironment()

    def default_location(self,locat=None):
        location = random.choice([loc_A,loc_B,loc_C])
        if locat:
            location = locat
        return location

    def verifyStatus(self):
        penalty = 0
        for locs in self.status.values():
            if locs == "Dirty":
                penalty+=1
        
        return penalty
    
    def updateEnvironment(self):
        for loc in self.status:
            if self.status[loc] == 'Clean' and  random.randint(0,99)<= self.dirtProb:
                self.status[loc] = 'Dirty'
                print("Location {}, is now dirty.".format(loc))
            


#---------------------------------------------------------------------

def TableDrivenAgentProgram(table):
    percepts=[]

    def program(percept):
        percepts.append(percept)
        action =  table.get(tuple(percepts))
        return action
    return program

def RandomAgentProgram(actions):
    """An agent that chooses an action at random, ignoring all percepts."""
    return lambda percept: random.choice(actions)

#---------------------------------------------------------------------

def  ReflexVacuumAgent():
    """A reflex agent for the three-state vacuum environment. [Figure 2.8]"""
    def program(percept):    
        location, status = percept
        if status == 'Dirty':
            return 'Suck'
        elif location == loc_A:
            return 'Right'
        elif location == loc_C:
            return 'Left'
        elif location == loc_B:
            return random.choice(['Right','Left'])
    return Agent(program)


def TableDrivenVacuumAgent():
    """[Figure 2.3]"""
    table = {((loc_A, 'Clean'),): 'Right',
             ((loc_A, 'Clean'), (loc_B, 'Dirty'),): 'Suck',
             ((loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'),): 'Right',
             ((loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_C,'Clean'),): 'NoOp',
             ((loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_C, 'Dirty'),): 'Suck',
             ((loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_C, 'Dirty'),(loc_C,'Clean'),): 'NoOp',

             ((loc_A, 'Dirty'),): 'Suck',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'),): 'Right',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'),): 'Right',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Clean'),): 'NoOp',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C,'Dirty'),): 'Suck',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'), (loc_C,'Clean'),): 'NoOp',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'),): 'Suck',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'),(loc_B, 'Clean'),): 'Right',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'),(loc_C,'Clean'),): 'NoOp',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_C, 'Dirty'),): 'Suck',
             ((loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_C, 'Dirty'),(loc_C,'Clean'),): 'NoOp',

             ((loc_A, 'Clean'), (loc_B, 'Clean'),): 'Right',
             ((loc_A, 'Clean'), (loc_B, 'Clean'),(loc_C, 'Clean'),): 'NoOp',
             ((loc_A, 'Clean'), (loc_B, 'Clean'),(loc_C, 'Dirty'),): 'Suck',
             ((loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'), (loc_C, 'Clean'),): 'NoOp',

             ((loc_B, 'Clean'),): 'Left',
             ((loc_B, 'Clean'),(loc_A, 'Clean'),): 'Right',
             ((loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B,'Clean'),): 'Right',
             ((loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C,'Clean'),): 'NoOp',
             ((loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'),): 'Suck',
             ((loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'), (loc_C, 'Clean'),): 'NoOp',

             ((loc_B, 'Clean'), (loc_A, 'Dirty'),): 'Suck',
             ((loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'),): 'Right',
             ((loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'),): 'Right',
             ((loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Clean'),): 'Right',
             ((loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'),(loc_B, 'Clean'),(loc_C, 'Dirty'),): 'Suck',
             ((loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Clean'),): 'NoOp',
             ((loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'), (loc_C, 'Clean'),): 'NoOp',

             ((loc_B, 'Dirty'),): 'Suck',
             ((loc_B, 'Dirty'),(loc_B, 'Clean'),): 'Left',
             ((loc_B, 'Dirty'),(loc_B, 'Clean'),(loc_A, 'Clean'),): 'Right',
             ((loc_B, 'Dirty'),(loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B,'Clean'),): 'Right',
             ((loc_B, 'Dirty'),(loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C,'Clean'),): 'NoOp',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'),): 'Suck',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'), (loc_C,'Clean')): 'NoOp',

             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'),): 'Suck',
             ((loc_B,'Dirty'),(loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'),): 'Right',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty')): 'Suck',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'),(loc_B,'Clean')): 'Right',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'),(loc_B, 'Clean'),(loc_C,'Dirty')): 'Suck',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'),(loc_C, 'Dirty'),(loc_C,'Clean')): 'NoOp',
             ((loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'),(loc_B,'Clean')): 'Right',
             ((loc_B,'Dirty'),(loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'),): 'Suck',
             ((loc_B,'Dirty'),(loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Clean'),): 'NoOp',
             ((loc_B,'Dirty'),(loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'), (loc_B, 'Clean'), (loc_C, 'Dirty'),(loc_C, 'Clean'),): 'NoOp',

             ((loc_C, 'Clean'),): 'Left',
             ((loc_C, 'Clean'), (loc_B, 'Dirty'),): 'Suck',
             ((loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'),): 'Left',
             ((loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Clean'),): 'NoOp',
             ((loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'),): 'Suck',
             ((loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'),): 'NoOp',

             ((loc_C, 'Clean'),): 'Left',
             ((loc_C, 'Clean'), (loc_B, 'Clean'),): 'Left',
             ((loc_C, 'Clean'), (loc_B, 'Clean'), (loc_A, 'Clean'),): 'NoOp',
             ((loc_C, 'Clean'), (loc_B, 'Clean'), (loc_A, 'Dirty'),): 'Suck',
             ((loc_C, 'Clean'), (loc_B, 'Clean'), (loc_A, 'Dirty'), (loc_A, 'Clean'),): 'NoOp',

             ((loc_C, 'Dirty'),): 'Suck',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'),): 'Left',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Clean'),): 'Left',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Clean'),(loc_A,'Dirty')): 'Suck',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Clean'), (loc_A, 'Clean')): 'NoOp',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Clean'), (loc_A, 'Dirty'),(loc_A,'Clean')): 'NoOp',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Dirty'),): 'Suck',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'),): 'Left',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Clean'),): 'NoOp',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'),): 'Suck',
             ((loc_C, 'Dirty'), (loc_C, 'Clean'), (loc_B, 'Dirty'), (loc_B, 'Clean'), (loc_A, 'Dirty'),(loc_A, 'Clean'),): 'NoOp',

             }
    return Agent(TableDrivenAgentProgram(table))


def RandomVacuumAgent():
    """Randomly choose one of the actions from the vacuum environment."""
    return Agent(RandomAgentProgram(['Right', 'Left', 'Suck', 'NoOp']))



#----------------------------------------------------------------------------#
def compare_agents(EnvFactory, AgentFactories, location,n=3, steps=1000):

    """See how well each of several agents do in n instances of an environment.
    Pass in a factory (constructor) for environments, and several for agents.
    Create n instances of the environment, and run each agent in copies of
    each one for steps. Return a list of (agent, average-score) tuples."""
    envs = [EnvFactory() for i in range(n)]
    result_List = []
    count = 0
    for A in AgentFactories:
        result_List.append((A ,test_agent(A, steps,copy.deepcopy(envs),location[count])))
        count = count+1
    return result_List
    '''
    return [(A, test_agent(A, steps, copy.deepcopy(envs),(1,0)))
            for A in AgentFactories]'''


def test_agent(AgentFactory, steps, envs,location):
    """Return the mean score of running an agent in each of the envs, for steps"""
    def score(env):
        agent = AgentFactory()
        print(location)
        env.add_thing(agent,location)
        env.run(steps)
        return agent.performance
    return mean(map(score, envs))

