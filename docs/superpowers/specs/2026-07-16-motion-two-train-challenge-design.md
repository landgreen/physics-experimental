# Motion two-train challenge design

## Goal

Add one hard, multi-step `Example:` near the end of the Practice section in
`notes/motion/motion/index.html`. It will give students a one-dimensional,
constant-velocity train-meeting problem that uses only ideas already taught on
that page.

## Learning boundary

The problem will use position, displacement, elapsed time, average velocity,
directions as signs, and unit conversion. It will not require a constant-
acceleration equation, relative-motion notation, or any later-course model.

## Problem design

East is positive. At the same instant, a commuter train is at -18.0 km and
moves east at 72 km/h; a freight train is at 234,000 m and moves west at
15 m/s. Both maintain constant velocity. Students determine when and where
they meet, then calculate the distance each train travels.

The intentionally mixed, compatible units require students to convert every
quantity into SI units before modeling the motion. The values produce an exact
meeting time of 7,200 s (2.00 h), a meeting position of 126,000 m (126 km),
and travel distances of 144,000 m and 108,000 m.

## Solution and placement

The solution will state the sign convention, convert units, write a separate
position expression for each train, set the two positions equal at the meeting
time, and independently check the resulting meeting position with each train.
It will finish with the two travel distances and a brief interpretation.

The markup will match nearby practice cards: a `div.example`, `Example:`
label, and one expandable `solution` block. It will be inserted near the end
of the existing Practice section, before the closing article tag.

## Verification

Check that the addition is inside the motion Practice section, preserves valid
HTML structure, uses one equal sign per display-math line, and independently
recalculate the meeting time, position, and both distances.
