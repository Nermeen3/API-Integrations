# Google-Maps-API

This Python Script does the following:
1. Extract a list of cities stored in a txt file
2. Loops through each city and defines a search query to find opticians in the current city
3. Uses Google Maps API to exctract details about the opticians
4. Details include: Name, Address, Rating, Rating Amount, Phone Number, Website
5. The script also uses Maps Pagination to show results (each page shows only 20 cards)
6. Formulate the results in json format
7. Append the json list to the results.csv file
