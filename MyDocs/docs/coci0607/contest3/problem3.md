### TROJKE

Mirko and Slavko are playing a new game, "Trojke" (Triplets). First they use a chalk to draw an N-by-N square grid on the road. Then they write letters into some of the squares. No letter is written more than once in the grid. 

The  game  consists  of  trying  to  find  three  letters  on  a  line  as  fast  as  possible.  Three  letters  are  considered  to  be  on  the  same  line  if  there  is  a  line  going  through  the  centre  of  each  of  the  three  squares. 

After a while it gets harder to find new triplets. Mirko  and  Slavko  need  a  program  that  counts  all  the  triplets, so that they know if the game is over or they need to search further. 


#### Input:

The first line contains an integer N (3 ≤ N ≤ 100), the dimension of the grid. 

Each  of  the  N  following  lines  contains  N  characters  describing  the  grid  –  uppercase  letters  and  the character '.', which marks an empty square.


#### Output:

Output the number of triplets on a single line


#### Example:

!!! question "Test 1"
    ???+ "Input"
        ```
        4
        ...D
        ..C.
        .B..
        A...
        ```
    ???+ "Output"
        ```
        4
        ```

!!! question "Test 2"
    ???+ "Input"
        ```
        5
        ..T..
        A....
        .FE.R
        ....X
        S....
        ```
    ???+ "Output"
        ```
        3
        ```

!!! question "Test 3"
    ???+ "Input"
        ```
        10
        ....AB....
        ..C....D..
        .E......F.
        ...G..H...
        I........J
        K........L
        ...M..N...
        .O......P.
        ..Q....R..
        ....ST....
        ```
    ???+ "Output"
        ```
        0
        ```