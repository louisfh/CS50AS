import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.

    Args:
        Source = Id of first actor
        Target = Id of second actor

    Returns:
        A list of tuples, each tuple consisting of the (movie_id, person_id)
        pair on the shortest path between the source and target actors.
        E.g. if the return value of shortest_path were [(1, 2), (3, 4)],
        Source starred in movie 1 with person 2,
        Person 2 starred in movie 3 with person 4,
        and person 4 is the target.
        If there is no path, returns None
    """

    #initialise start node
    start = Node(state = source,    #node.state = actor ID
                 parent = None,        #node.parent = parent node
                 action = None)        #node.action = movie child costarred with parent in

    #Initialise a queue frontier (Queue => Breadth-first-search)
    frontier = QueueFrontier()
    frontier.add(start)
    numexplored = 0
    actorsexplored = set()
    path = []

    while True:

        testInc = 0
        testInc += 1
        if frontier.empty():                #Frontier empty => no solution
            raise Exception("No Solution")
        ####DEBUGGING PRINT####
        #else:
            #print(f"Frontier not empty, round {testInc}.")

        node = frontier.remove()
        numexplored += 1

        #DEBUG print(f"Nodes Explored = {numexplored}. Current node = {node.state}")


        #If node is the target, return the route taken to get there
        if node.state == target:
            #DEBUG print(f"Triggered node.state == target_id. node.state = {node.state}")
            while node.parent is not None:
                path.append((node.action, node.state))
                node = node.parent
            #print(path)
            return path

        # If node is not target, explore node
        # i.e. add all costarring actor nodes to frontier
        # note neighbors function returns list of (film, costar) tuples
        #testvar = neighbors_for_person(node.state)
        #DEBUG for i in testvar:
            #print(i)
            #break
        for movie_id, costar in neighbors_for_person(node.state):
            if costar == target:
                child = Node(state = costar,
                             parent = node,
                             action = movie_id)
                break
            if not frontier.contains_state(costar) and costar not in actorsexplored:
                child = Node(state = costar,
                             parent = node,
                             action = movie_id)
                frontier.add(child)
                #DEBUG print(f"Child: {child.state} created and added to frontier.")

        #mark node as explored
        actorsexplored.add(node.state)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
