# Runway Exit Optimizer Prototype

Early version of the optimization portion of [AREA](https://github.com/tejadaR/AREA).

Runway Exit Optimizer Prototype finds the optimal runway exit a landing aircraft should take based on several costs
associated with airline operations. It uses a linear program to find the optimal exit and outputs the results and
optimal costs to a CSV file. The analyzed airports are PHX, ATL, BWI, and DEN.

Disclaimer: The cost values used in this iteration of the optimization approach are outdated and inconsistent with
those of [AREA](https://github.com/tejadaR/AREA). Other features such as using weather to influence touchdown position
are also not implemented.

## Running Locally

### Requirements

1. Python 3.6+
2. pip or other package manager

### Set Up

1. `git clone https://github.com/FetsMilazzo/REOP`
2. `cd REOP`
3. `pip install -r requirements.txt`

### Running

1. `py main.py`
