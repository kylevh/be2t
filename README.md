# Snapshot Analyzer

A Python-based desktop application for analyzing and viewing snapshots of backend testing coverage data using tkinter gui.

## Project Overview

The Snapshot Analyzer allows users to:
- Browse projects and their snapshots through an calendar
- View snapshot data for specific dates
- Generate .xlsx files from snapshot data
- View coverage over time

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.11.5 or higher
- VSCode (optional)

### Installing Python

1. 

## Project Structure
    beatt/
    ├── configs/ # Configuration files
    │ └── settings.ini
    ├── core/ # Core business logic
    │ ├── models/
    │ └── services/
    ├── ui/ # User interface components
    │ ├── components/ # Reusable UI components
    │ └── pages/ # Application pages
    ├── utils/ # Utility functions
    └── launch.py # Main entry point

    soap/
    └── snapshots/
        ├── YYYY-MM-DD/ # Date folders
        │ ├── Project1/ # Project folders
        │ │ ├── YYYY-MM-DD_HH-MM-SS.json # Snapshot files
        │ │ └── ...
        │ └── Project2/
        │ └── ...
        └── ...
    └── BEATT-Snapshot-Generator.xml # SOAPUI Groovy script for generating snapshots

## Running the application

1. Ensure you're in the PYTHON project root directory
2. Simply run ```py launch.py```
3. The python gui should launch on your desktop and you should then be able to browse existing projects within the repo

## Usage Guide

1. **Project Selection**
   - Use the dropdown menu in the sidebar to select a project
   - Available projects will be automatically loaded from the snapshots directory

2. **Date Selection**
   - Use the calendar interface to select a date of the snapshot
   - Dates with available snapshots are clickable

3. **Navigation**
   - Use the sidebar buttons to switch between page functions (home, projects, settings, etc..)