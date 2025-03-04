### BICIKLI

A  bicycle  race  is  being  organized  in  a  land  far,  far  away.  There  are  N  town  in  the  land,  numbered  1  
through N. There are also M one-way roads between the towns. The race will start in town 1 and end 
in town 2. How many different ways can the route be set? Two routes are considered different if they do not use 
the exact same roads. 


#### Input: 
The first line of input contains two integers N and M (1 ≤ N ≤ 10 000, 1 ≤ M ≤ 100 000), the number 
of towns and roads. Each of the next M lines contains two different integers A and B, representing a road between towns A 
and B. Towns may be connected by more than one road. 


#### Output: 
Output the number of distinct routes that can be set on a single line. If that number has more than nine 
digits, output only the last nine digits of the number. If there are infinitely many routes, output "inf".


#### Sample:

!!! question "Test 1"
    ???+ "Input"
        ```
        6 7 
        1 3 
        1 4 
        3 2 
        4 2 
        5 6 
        6 5 
        3 4
        ```
    ???+ "Output"
        ```
        3
        ```

!!! question "Test 2"
    ???+ "Input"
        ```
        6 8 
        1 3 
        1 4 
        3 2 
        4 2 
        5 6 
        6 5 
        3 4 
        4 3 
        ```
    ???+ "Output"
        ```
        inf
        ```

!!! question "Test 3"
    ???+ "Input"
        ```
        31 60 
        1 3 
        1 3 
        3 4 
        3 4 
        4 5 
        4 5 
        5 6 
        5 6 
        6 7 
        6 7 
        ... 
        ... 
        ... 
        28 29 
        28 29 
        29 30 
        29 30 
        30 31 
        30 31 
        31 2 
        31 2
        ```
    ???+ "Output"
        ```
        073741824
        ```