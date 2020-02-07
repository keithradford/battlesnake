# Battlesnake Approach

Documenting general strategy and approach.

#### General turn plan
  1. move opposite direction of closest snake (can be any body part)
  2. move direction of closest food (depending on size, will try and stay at optimal size. if good size this is 3 priority)
  3. if colliding with wall and not at center coordinate, move toward center coordinate. (2 priority if good size)
  4. (FINAL FALLBACK, UNLIKELY) if center and nothing else to worry about random direction. Mostly for approaching wall.
  
  *Validate each decision: must check where body is so it doesn't collide with self. Validation may follow same plan.
  
#### Advanced strat
will decide...
