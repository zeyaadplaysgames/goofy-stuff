#!/usr/bin/env python3

import curses
import math

# Define formulas for Law of Sines and Law of Cosines
def law_of_sines_find_angle(a, A, b):
    try:
        B = math.degrees(math.asin(b * math.sin(math.radians(A)) / a))
        return f"Angle B: {B} degrees"
    except ValueError:
        return "Invalid input for Law of Sines."

def law_of_cosines_find_angle(a, b, c):
    try:
        C = math.degrees(math.acos((a**2 + b**2 - c**2) / (2 * a * b)))
        return f"Angle C: {C} degrees"
    except ValueError:
        return "Invalid input for Law of Cosines."

def law_of_cosines_find_side(a, b, C):
    try:
        C_rad = math.radians(C)
        c = math.sqrt(a**2 + b**2 - 2 * a * b * math.cos(C_rad))
        return f"Side c: {c}"
    except ValueError:
        return "Invalid input for Law of Cosines."

# Conversion functions
def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9

def km_to_miles(km):
    return km * 0.621371

def miles_to_km(miles):
    return miles / 0.621371

# Input handler with backspace support
def get_input(stdscr, prompt):
    stdscr.addstr(prompt)
    stdscr.refresh()
    input_str = ""
    while True:
        key = stdscr.getch()
        if key in (curses.KEY_BACKSPACE, 127, 8):  # Handle backspace (127 and 8 are for compatibility)
            if len(input_str) > 0:
                input_str = input_str[:-1]  # Remove the last character
                y, x = stdscr.getyx()
                stdscr.move(y, x - 1)  # Move cursor back one position
                stdscr.delch()  # Delete the character at the cursor
        elif key == ord('\n'):  # Enter key to finish input
            break
        elif 32 <= key <= 126:  # Handle printable characters
            input_str += chr(key)
            stdscr.addch(key)
    return input_str

# Input and calculation for the selected formula
def get_input_and_calculate(stdscr, formula):
    stdscr.clear()

    if formula == "Normal calculator (you input the equation)":
        equation = get_input(stdscr, "\nType in your equation: ")
        try:
            result = f"Result: {eval(equation)}"
        except Exception as e:
            result = f"Error: {e}"

    elif formula == "Law of Sines: Find Angle":
        a = float(get_input(stdscr, "Enter side a: "))
        A = float(get_input(stdscr, "\nEnter angle A (degrees): "))
        b = float(get_input(stdscr, "\nEnter side b: "))
        result = law_of_sines_find_angle(a, A, b)
        
    elif formula == "Law of Cosines: Find Angle":
        a = float(get_input(stdscr, "Enter side a: "))
        b = float(get_input(stdscr, "\nEnter side b: "))
        c = float(get_input(stdscr, "\nEnter side c: "))
        result = law_of_cosines_find_angle(a, b, c)
    
    elif formula == "Law of Cosines: Find Side":
        a = float(get_input(stdscr, "Enter side a: "))
        b = float(get_input(stdscr, "\nEnter side b: "))
        C = float(get_input(stdscr, "\nEnter angle C (degrees): "))
        result = law_of_cosines_find_side(a, b, C)
    
    elif formula == "Convert Celsius --> Fahrenheit":
        celsius = float(get_input(stdscr, "Enter the amount of Celsius: "))
        result = f"Fahrenheit: {celsius_to_fahrenheit(celsius)}"
    
    elif formula == "Convert Fahrenheit --> Celsius":
        fahrenheit = float(get_input(stdscr, "Enter the amount of Fahrenheit: "))
        result = f"Celsius: {fahrenheit_to_celsius(fahrenheit)}"
    
    elif formula == "Convert KM --> Miles":
        km = float(get_input(stdscr, "Enter distance in kilometers: "))
        result = f"Miles: {km_to_miles(km)}"
    
    elif formula == "Convert Miles --> KM":
        miles = float(get_input(stdscr, "Enter distance in miles: "))
        result = f"Kilometers: {miles_to_km(miles)}"
    
    stdscr.addstr(7, 0, result)
    stdscr.addstr(8, 0, "Press any key to continue...")
    stdscr.getch()

# Menu for formula selection with search functionality
def show_formula_menu(stdscr, formulas):
    curses.curs_set(1)  # Show the cursor for text input
    search_query = ""
    filtered_formulas = formulas.copy()
    selected_index = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Search for a formula (type to filter, ESC to exit):")
        stdscr.addstr(1, 0, f"Search: {search_query} \n")

        # Filter formulas based on the search query
        filtered_formulas = [formula for formula in formulas if search_query.lower() in formula.lower()]

        # Display filtered formulas
        for idx, formula in enumerate(filtered_formulas):
            if idx == selected_index:
                stdscr.addstr(idx + 2, 0, f"> {formula}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 2, 0, formula)

        # Capture key press
        key = stdscr.getch()

        # Navigate with keys
        if key == curses.KEY_UP and selected_index > 0:
            selected_index -= 1
        elif key == curses.KEY_DOWN and selected_index < len(filtered_formulas) - 1:
            selected_index += 1
        elif key == ord('\n'):  # Enter key to select formula
            if filtered_formulas:
                return filtered_formulas[selected_index]
        elif key == 27:  # ESC key to exit
            return None
        elif key in (curses.KEY_BACKSPACE, 127, 8):  # Handle backspace
            if len(search_query) > 0:
                search_query = search_query[:-1]
        elif 32 <= key <= 126:  # Handle printable characters
            search_query += chr(key)

# Main calculator loop
def calculator(stdscr):
    # Predefined formulas
    formulas = [
        "Normal calculator (you input the equation)",
        "Convert Celsius --> Fahrenheit",
        "Convert Fahrenheit --> Celsius",
        "Convert KM --> Miles",
        "Convert Miles --> KM",
        "Law of Sines: Find Angle",
        "Law of Cosines: Find Angle",
        "Law of Cosines: Find Side"
    ]

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Press '!' to select a formula, 'q' to quit. ")

        key = stdscr.getch()

        if key == ord('q'):  # Quit on 'q'
            break
        elif key == ord('!'):  # Open formula menu on '!'
            selected_formula = show_formula_menu(stdscr, formulas)
            if selected_formula:
                get_input_and_calculate(stdscr, selected_formula)

# Start the curses application
if __name__ == "__main__":
    curses.wrapper(calculator)
