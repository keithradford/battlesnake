# Battlesnake Approach

Documenting general strategy and approach.

#### General turn plan
Check to see if the move is valid, then:
  1. move opposite direction of closest snake (can be any body part)
  2. move direction of closest food (depending on size, will try and stay at optimal size. if good size this is 3 priority)
  3. move away from average coordinate of body depending on head quadrant. (2 priority if good size)
  4. move away from wall (towards centre)
