"""
Warehouse Route Optimizer
-------------------------

This program:
1. Reads a CSV transportation network
2. Finds the best warehouse node automatically
3. Shows the best routes to every location

CSV Format:
Location A,Location B,Distance,Time,Fuel
"""

import csv
import heapq
import os


# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
def load_database(file_path):

    graph = {}
    locations = set()

    with open(file_path, 'r') as file:

        reader = csv.DictReader(file)

        for row in reader:

            a = row["Location A"]
            b = row["Location B"]

            distance = float(row["Distance"])
            time = float(row["Time"])
            fuel = float(row["Fuel"])

            locations.add(a)
            locations.add(b)

            if a not in graph:
                graph[a] = {}

            graph[a][b] = {
                "Distance": distance,
                "Time": time,
                "Fuel": fuel
            }

    return graph, sorted(list(locations))


# ---------------------------------------------------------
# DIJKSTRA SHORTEST PATH
# ---------------------------------------------------------
def dijkstra(graph, start, metric):

    pq = []
    heapq.heappush(pq, (0, start, [start]))

    visited = {}
    results = {}

    while pq:

        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue

        visited[node] = cost
        results[node] = (cost, path)

        if node not in graph:
            continue

        for neighbor in graph[node]:

            edge_cost = graph[node][neighbor][metric]

            heapq.heappush(
                pq,
                (cost + edge_cost, neighbor, path + [neighbor])
            )

    return results


# ---------------------------------------------------------
# FIND BEST WAREHOUSE
# ---------------------------------------------------------
def find_best_warehouse(graph, locations, metric):

    best_node = None
    best_total = float("inf")
    best_routes = None

    for node in locations:

        routes = dijkstra(graph, node, metric)

        total_cost = 0

        for loc in routes:
            if loc != node:
                total_cost += routes[loc][0]

        if total_cost < best_total:

            best_total = total_cost
            best_node = node
            best_routes = routes

    return best_node, best_total, best_routes


# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------
def main():

    print("\nWarehouse Route Optimizer")
    print("-------------------------")

    # Ask user for file path
    file_path = input("\nEnter path to Database.csv: ")

    # Check if file exists
    if not os.path.exists(file_path):
        print("\nError: File not found.")
        return

    graph, locations = load_database(file_path)

    print("\nChoose optimization metric:")
    print("1 - Distance")
    print("2 - Time")
    print("3 - Fuel")

    choice = input("\nEnter choice: ")

    if choice == "1":
        metric = "Distance"
    elif choice == "2":
        metric = "Time"
    elif choice == "3":
        metric = "Fuel"
    else:
        print("Invalid choice.")
        return

    warehouse, total, routes = find_best_warehouse(
        graph,
        locations,
        metric
    )

    print("\n--------------------------------")
    print(f"Best Warehouse Location: {warehouse}")
    print(f"Optimization Metric: {metric}")
    print(f"Total {metric}: {round(total,2)}")
    print("--------------------------------\n")

    print("Best Delivery Routes:\n")

    for loc in routes:

        if loc == warehouse:
            continue

        cost, path = routes[loc]

        route = " -> ".join(path)

        print(f"{route} = {round(cost,2)}")


# ---------------------------------------------------------
# RUN PROGRAM
# ---------------------------------------------------------
if __name__ == "__main__":
    main()