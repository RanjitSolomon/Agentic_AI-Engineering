#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from financial_researcher2.crew import FinancialResearcher

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
import os
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def run():
    """
    Run the financial researcher crew.
    """
    inputs = {
        'company': 'Tesla',
    }
    
    try:
        result = FinancialResearcher().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__": 
    run() 
    