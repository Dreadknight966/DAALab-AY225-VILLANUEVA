🌐 Network Path Finder
CSV-Based Graph Visualizer with Shortest Path Algorithm

An interactive tool that converts a CSV file of network connections into a dynamic graph and calculates the optimal path between nodes.

The program generates a standalone HTML visualization where users can:

Upload a CSV

Visualize the network

Compute the shortest route based on distance, time, or fuel

✨ Features

✔ Interactive network graph visualization
✔ Drag & drop CSV upload
✔ Shortest path calculation (Dijkstra's Algorithm)
✔ Optimize routes by:

📍 Distance (km)

⏱ Time (minutes)

⛽ Fuel (liters)

✔ Displays route metrics and node hops
✔ Option to show all edge values
✔ Modern UI with highlighted paths

🖥 System Requirements
Requirement	Version
Python	3.7 or newer
Browser	Chrome / Edge / Firefox / Opera
Internet	Required for visualization library

Check your Python version:

python --version
📦 Required Python Libraries

Install the following libraries before running the program.

Library	Purpose
pyvis	Network graph visualization
matplotlib	Graph plotting utilities
pandas	CSV data processing
⚙ Installation

Install all dependencies with one command:

pip install pyvis matplotlib pandas

If using Python 3:

pip3 install pyvis matplotlib pandas
🧑‍💻 Recommended Development Environment
Editor

Visual Studio Code

Download
https://code.visualstudio.com/

Recommended VS Code Extensions
Extension	Purpose
Python (Microsoft)	Python development support
Live Server	Easily preview HTML files

Install from VS Code marketplace.

🚀 Running the Program
1️⃣ Save the Script

Save the file as:

generate_network.py
2️⃣ Run the Python Script

Open a terminal in the project folder and run:

python generate_network.py

Output example:

Generated: /project/node_map.html
Open it in any modern browser and upload your CSV to get started.
3️⃣ Open the Visualization

Open the generated file:

node_map.html

You can:

Double click the file

Open with your browser

Use Live Server in VS Code

Supported browsers:

Google Chrome

Microsoft Edge

Firefox

Opera

📊 Using the Application

1️⃣ Upload a CSV file

Drag & drop

Click Browse Files

2️⃣ Choose

Start Node

End Node

Optimization criteria

3️⃣ Click

Find Shortest Path

The system will:

Display the network

Highlight the optimal route

Show route metrics

Display other values along the same path

📄 CSV File Format

Your CSV must contain a header row with the following columns.

Column	Description
From Node	Starting node
To Node	Destination node
Distance (km)	Distance between nodes
Time (mins)	Travel time
Fuel (Liters)	Fuel consumption

Column order does not matter, but names must contain:

From
To
Distance
Time
Fuel
📄 Example CSV
From Node,To Node,Distance (km),Time (mins),Fuel (Liters)
A,B,5,10,0.5
B,C,4,8,0.4
A,C,10,15,0.9
C,D,7,12,0.7

🧠 Algorithm Used

This project uses two main algorithms to generate and analyze the node network.

Algorithm	Purpose
🌐 Force-Directed Graph Layout (Barnes–Hut)	Automatically positions nodes in the network
📍 Dijkstra’s Algorithm	Finds the shortest path between nodes
🌐 Network Layout

The visualization uses the Barnes–Hut force-directed layout provided by the vis-network library.

In this simulation:

🔋 Nodes repel each other

🪢 Edges act like springs pulling connected nodes together

🌍 Gravity keeps the graph centered

This physics-based layout automatically spreads nodes so the network remains clear and readable.

📍 Shortest Path Algorithm

To find the optimal route between nodes, the program uses Dijkstra’s Algorithm, which works on a weighted graph.

Each edge contains three possible weights:

📏 Distance (km)

⏱ Time (mins)

⛽ Fuel (liters)

The user selects which metric to optimize, and the algorithm finds the minimum cost path between the selected start and end nodes.

Example
A → B → D → F

The selected route is then highlighted in the network visualization, while other nodes and edges are dimmed.

📂 Project Structure
network-path-finder
│
├── generate_network.py
├── node_map.html      (generated after running the script)
└── README.md
⚙ Algorithm Used

This project uses Dijkstra's Algorithm to determine the shortest path between nodes in a weighted graph.

The algorithm minimizes one of the following metrics:

Distance

Time

Fuel consumption

📤 Output

Running the Python script generates:

node_map.html

This file contains:

the network visualization

shortest path algorithm

interactive interface

CSV upload functionality

No backend server is required.

📜 License

This project is intended for educational and academic use.