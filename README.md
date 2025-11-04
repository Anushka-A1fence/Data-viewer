1. python -m venv venv
2. `windows venv/scripts/activate` OR `linux source venv/bin/activate`
3. pip install -r requirements.txt
4. python main.py
 
1 Introduction
1.1 Purpose

The Parent Node Finder is a web-based application that identifies and displays the hierarchical relationships between devices based on their MAC IDs. It simplifies analyzing device connections and parent–child mappings in networks such as IoT or mesh-based systems.

1.2 Scope

This tool accepts user inputs for root MAC addresses and a dataset file containing MAC relationships. It outputs all related nodes while removing duplicates, sorting results, and showing the total count of discovered MAC addresses.

2. System Overview

The system provides a web interface that allows users to:

Input a dataset file and root MAC addresses.

Run the analysis to discover related MAC nodes.

View, sort, and count the resulting unique MAC addresses.

3. Features
Feature	Description
MAC ID Lookup	Accepts root MAC inputs and retrieves connected or descendant nodes.
Duplicate Removal	Automatically filters out repeated MAC IDs.
Sorting Functionality	Allows sorting results for better readability.
Unique Node Counting	Displays the total number of unique MACs identified.
Clean UI	Simple and intuitive web interface for easy use.