"""
Multi-agent system emulating an ecosystem of virtual bugs eating each other
"""
import random
import sys
import os
import json
import shutil


# Species IDs:
PLANT = 1
HERBIVORE = 2
CARNIVORE = 3


# Other IDs:
_help = 'help'  # documentation

# ***** EXPERIMENT PARAMETERS

# Biotope settings:
biotope_settings = {
    _help: """
    Settings of biotope. In this version, only biotope size is specified
    """,
    'size_x': 300,
    'size_y': 200
}

# Organisms settings:
cost = {
    _help: """
    Each activity or capacity of an organism may cost it energy. This is
    the amount of energy that cost each of them:
    """,
    'to have the capacity of moving': 2,
    'to move': 5,
    'to have the capacity of hunting': 4,
    'to hunt': 10,
    'to have the capacity of procreating': 0,
    'to procreate': 15
}
minimum_energy_required_to = {
    'move': 30,
    'hunt': 30,
    'procreate': 100
}
photosynthesis_capacity = 5

initial_num_of_organisms = {
    _help: """
    The number of organisms of each species that are created before
    the experiment starts
    """,
    PLANT: 1000,
    HERBIVORE: 300,
    CARNIVORE: 100
}

initial_energy_reserve = 10000

max_lifespan = {
    _help: """
    The maximum age an organism of each species can reach
    """,
    PLANT: 40,
    HERBIVORE: 35,
    CARNIVORE: 100
}

procreation_probability = {
    _help: """
    The probability that an organism procreate each time it acts
    """,
    PLANT: 0.50,
    HERBIVORE: 0.10,
    CARNIVORE: 0.02
}

# ***************************


class Ecosystem(object):
    """ Environment of the ecosystem where organisms can live and evolve

    Role:
        - create and initialize organisms
        - handle adding of new organisms to ecosystem
        - produce changes in ecosystem in each time step (evolve)
    """

    def __init__(self):
        self.time = 0
        self.size_x = biotope_settings['size_x']
        self.size_y = biotope_settings['size_y']
        self.initialize_biotope()
        self.initialize_organisms()

    def initialize_biotope(self):
        """ Initialize biotope
        """
        self.biotope = {}
        self.biotope_free_locs = set()
        for x in range(0, self.size_x):
            for y in range(0, self.size_y):
                self.biotope_free_locs.add((x, y))

    def initialize_organisms(self):
        """ Method to initialize a set of organisms

        It uses the settings stored in self.organisms_settings
        """
        num_plants = initial_num_of_organisms[PLANT]
        num_herbivores = initial_num_of_organisms[HERBIVORE]
        num_carnivores = initial_num_of_organisms[CARNIVORE]
        id = 0
        print "Creating plants..."
        # Create plants
        locations_list = random.sample(self.biotope_free_locs, num_plants)
        for random_location in locations_list:
            id += 1
            self.add_organism(Organism(species=PLANT,
                                       parent_ecosystem=self,
                                       location=random_location,
                                       energy_reserve=initial_energy_reserve))

        print "Creating hervibores..."
        # Create hervibores
        locations_list = random.sample(self.biotope_free_locs, num_herbivores)
        for random_location in locations_list:
            id += 1
            self.add_organism(Organism(species=HERBIVORE,
                                       parent_ecosystem=self,
                                       location=random_location,
                                       energy_reserve=initial_energy_reserve))

        print "Creating carnivores..."
        # Create carnivores
        locations_list = random.sample(self.biotope_free_locs, num_carnivores)
        for random_location in locations_list:
            id += 1
            self.add_organism(Organism(species=CARNIVORE,
                                       parent_ecosystem=self,
                                       location=random_location,
                                       energy_reserve=initial_energy_reserve))

    def add_organism(self, organism):
        """ Add organism to ecosytem

        Args:
            organism (Organism): Organism objects to be added to ecosystem
            id (int): Id assigned to organism
        """
        (x, y) = organism.location
        self.biotope[(x, y)] = organism
        self.biotope_free_locs.remove((x, y))

    def remove_organism(self, organism):
        """ Remove organism from ecosysem

        Note: Organisms objects are not deleted manually. We rely on
              Python garbage collector.

        Args:
            organism (Organism): Organism to be removed from ecosystem
        """
        (x, y) = organism.location
        """
        if not (x, y) in self.biotope.keys():
            print "Fatal error!!"
            return
        """
        del self.biotope[(x, y)]  # delete reference from dict
        self.biotope_free_locs.add((x, y))

    def update_organism_location(self, organism):
        """ Update interval variables related to a given organism

        Args:
            organism (Organism): Organism to be removed from ecosystem
        """
        old_location = organism.old_location
        del self.biotope[old_location]
        self.biotope_free_locs.add(old_location)

        new_location = organism.location
        self.biotope[new_location] = organism
        self.biotope_free_locs.remove(new_location)

        organism.old_location = organism.location

    def get_surrounding_free_locations(self, center):
        """ Get a list of free locations around a given center

        Args:
            center (tuple): (x, y) coordinates of center
        Returns:
            (set): Set of free locations around center
        """
        (center_x, center_y) = center
        surrounding_free_locs = set()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0) and (dy == 0):
                    break  # avoid checking center itself
                x = (center_x + dx) % self.size_x
                y = (center_y + dy) % self.size_y
                if (x, y) in self.biotope_free_locs:
                    surrounding_free_locs.add((x, y))
        return surrounding_free_locs

    def get_surrounding_organisms(self, center):
        """ Get a list of organisms around a given center

        Args:
            center (tuple): (x, y) coordinates of center
        Returns:
            (set): Set of organisms
        """
        (center_x, center_y) = center
        surrounding_organisms = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (dx == 0) and (dy == 0):
                    break  # avoid checking center itself
                x = (center_x + dx) % self.size_x
                y = (center_y + dy) % self.size_y
                if (x, y) in self.biotope.keys():
                    organism = self.biotope[(x, y)]
                    surrounding_organisms.append(organism)
        return surrounding_organisms

    def evolve(self):
        """ Evolve one time step the whole ecosystem
        """
        curr_organisms = self.biotope.values()
        for organism in curr_organisms:
            if organism.is_alive:  # still alive
                organism.act()
        self.time += 1


class Organism(object):
    """ Organism: agent of ecosystem
    """

    def __init__(self, species, parent_ecosystem, location, energy_reserve):
        """ Initialize organism

        Args:
            species (str): Species of the organism
            parent_ecosystem (Ecosystem): Parent ecosystem
            location (tuple): (x, y) coordinates of organism
        """
        # Relative to ecosystem
        self.parent_ecosystem = parent_ecosystem
        self.location = location
        self.old_location = location  # useful for parent_ecosystem to track it
        # Genes:
        self.species = species
        self.death_age = random.randint(0, max_lifespan[species])
        # State:
        self.age = 0
        self.energy_reserve = energy_reserve
        self.is_alive = True
        self.number_of_deaths = 0

    def act(self):
        if not self.is_alive:
            print "Error"
            return
        if self.species == PLANT:
            self.do_photosynthesis()
        self.do_move()
        if not self.is_alive:
            return
        self.do_hunt()
        if not self.is_alive:
            return
        self.do_procreate_if_possible()
        if not self.is_alive:
            return
        self.do_age()

    def do_age(self):
        """ Increase self.age and die if reach self.death_age
        """
        self.age += 1
        if self.age > self.death_age:
            self.do_die(cause_of_death='age')

    def do_spend_energy(self, amount_of_energy):
        self.energy_reserve -= amount_of_energy
        if self.energy_reserve <= 0:
            self.do_die(cause_of_death='starvation')

    def has_enough_energy_to(self, action):
        if self.energy_reserve > minimum_energy_required_to[action]:
            return True
        else:
            return False

    def do_move(self):
        """ Move organism to a free location in ecosystem
            If the organism has the attribute "energy_reserve", then
            it has to spend energy in order to move
        """
        if self.species == PLANT:  # Plants don't move
            return

        # Having the capacity of moving requires energy spending:
        if hasattr(self, "energy_reserve"):
            if self.has_enough_energy_to('move'):
                self.do_spend_energy(amount_of_energy=cost[
                    'to have the capacity of moving'])
            if not self.is_alive:
                # It may have died of starvation because of the energy spending
                return

        free_locs = self.parent_ecosystem.get_surrounding_free_locations(
            self.location)
        if len(free_locs) > 0:
            if hasattr(self, "energy_reserve"):
                self.do_spend_energy(amount_of_energy=cost[
                    'to move'])
            if not self.is_alive:
                # It may have died of starvation because of the energy spending
                return
            new_location = random.sample(free_locs, 1)[0]
            self.location = new_location
            # Moving requires energy spending:
            self.parent_ecosystem.update_organism_location(self)

    def do_die(self, cause_of_death=None):
        """ Make organism dissapear from ecosystem
        """
        if self.is_alive:
            self.is_alive = False
            self.parent_ecosystem.remove_organism(self)

    def is_eatable(self, pray):
        """ True if pray can be eaten by self

        Args:
            pray (Organism): Organism to be eaten
        Returns:
            (bool): True if pray can be eaten
        """
        eatable = False
        if self.species == CARNIVORE and pray.species == HERBIVORE:
            eatable = True
        if self.species == HERBIVORE and pray.species == PLANT:
            eatable = True
        return eatable

    def do_hunt(self):
        """ Find food nearby and eat it
            If the organism has the attribute "energy_reserve", then
            it has to spend energy in order to hunt
        """
        if self.species == PLANT:
            return   # plants don't eat. This save computing time

        # Having the capacity of hunting requires energy spending:
        if hasattr(self, "energy_reserve"):
            if self.has_enough_energy_to("hunt"):
                self.do_spend_energy(amount_of_energy=cost[
                    'to have the capacity of hunting'])
            if not self.is_alive:
                # It may have died of starvation because of the energy spending
                return

        surr_organisms = self.parent_ecosystem.get_surrounding_organisms(
            self.location)
        random.shuffle(surr_organisms)
        for surr_organism in surr_organisms:
            if self.is_eatable(surr_organism):
                prey = surr_organism
                """ OTHER POSIBILITY:
                self.age = 0  # The benefit of eating is getting younger
                """
                self.energy_reserve += prey.energy_reserve
                prey.do_die(cause_of_death='hunted')
                # Eating requires energy spending:
                if hasattr(self, "energy_reserve"):
                    self.do_spend_energy(amount_of_energy=cost[
                        'to hunt'])
                break

    def do_photosynthesis(self):
        if hasattr(self, "energy_reserve"):
            self.energy_reserve += photosynthesis_capacity

    def do_procreate_if_possible(self):
        """ Procreate if possible
            If the organism has the attribute "energy_reserve", then
            it has to spend energy in order to procreate
        """
        # Having the capacity of procreating requires energy spending:
        if hasattr(self, "energy_reserve"):
            if self.has_enough_energy_to("procreate"):
                self.do_spend_energy(amount_of_energy=cost[
                    'to have the capacity of procreating'])
            if not self.is_alive:
                # It may have died of starvation because of the energy spending
                return

        if random.random() < procreation_probability[self.species]:
            free_locs = self.parent_ecosystem.get_surrounding_free_locations(
                self.location)
            if len(free_locs) == 0:
                return  # no empty space for procreation!
            baby_location = random.sample(free_locs, 1)[0]
            # The organism share its energy reserve with its baby:
            baby_energy_reserve = self.energy_reserve / 2
            self.energy_reserve /= 2
            baby = Organism(
                self.species,
                self.parent_ecosystem,
                baby_location,
                baby_energy_reserve)
            self.parent_ecosystem.add_organism(baby)
            # Procreating requires energy spending:
            if hasattr(self, "energy_reserve"):
                self.do_spend_energy(amount_of_energy=cost[
                    'to procreate'])


class Exporter(object):
    """ Class to export ecosystem history to a folder.
    It exports a .json file for time slice containing all the organisms.
    """
    def __init__(self, parent_ecosystem, dst_folder):
        """ Initialize Exporter
        Args:
            parent_ecosystem (Ecosystem): Ecosystem to be exported
            dst_folder (str): Destination folder
        """
        self.dst_folder = dst_folder
        self.parent_ecosystem = parent_ecosystem
        self.export_initial_settings()

    def export_initial_settings(self):
        """ Export ecosystem.py to experiment folder
        All settings are accessible to ecosystem.py
        """
        experiment_name = os.path.split(self.dst_folder.strip('/'))[1]
        settings_folder = os.path.join(self.dst_folder, 'settings')
        if not os.path.isdir(settings_folder):
            os.makedirs(settings_folder)
        # Copy script to folder experiment
        dst_experiment_script_path = os.path.join(settings_folder,
                                                  experiment_name + '.py')
        shutil.copy(os.path.realpath(__file__), dst_experiment_script_path)

    def export_time_slice(self):
        """ Export data for current time slice of parent_ecosystem
        """
        curr_time = self.parent_ecosystem.time
        file_name = str(curr_time) + '.json'
        thousands = int(curr_time / 1000) * 1000
        thousands_folder = '{0}_to_{1}'.format(str(thousands),
                                               str(thousands + 999))
        dst_file_path = os.path.join(self.dst_folder, thousands_folder,
                                     file_name)
        if not os.path.isdir(os.path.dirname(dst_file_path)):
            os.makedirs(os.path.dirname(dst_file_path))
        dict_organisms = {}
        for location, organism in self.parent_ecosystem.biotope.iteritems():
            dict_organisms[str(location)] = organism.species
        with open(dst_file_path, 'w') as f:
            json.dump(dict_organisms, f)


def main():
    """ Main function of ecosystem
    """
    ecosystem = Ecosystem()
    exporter = Exporter(ecosystem, sys.argv[1])

    while True:
        exporter.export_time_slice()
        ecosystem.evolve()
        print "Time:", ecosystem.time

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: python ecosystem.py dst_folder"
        sys.exit(1)
    main()