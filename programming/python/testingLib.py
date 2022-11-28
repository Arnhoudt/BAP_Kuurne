def shortestAngle(a, b):
    """Return the shortest angle between two angles in degrees."""
    return (a - b + 180) % 360 - 180


print(shortestAngle(0, 180))
print(shortestAngle(180, 0))
print(shortestAngle(-180, 179))
print(shortestAngle(90, 0))
print(shortestAngle(0, 270))
print(shortestAngle(270, 0))
print(shortestAngle(0, 360))
print(shortestAngle(360, 0))
print(shortestAngle(0, 0))
print(shortestAngle(0, 1))
print(shortestAngle(1, 0))
print(shortestAngle(0, 359))
print(shortestAngle(359, 0))
print(shortestAngle(0, 358))
print(shortestAngle(358, 0))
print(shortestAngle(0, 2))
print(shortestAngle(2, 0))
print(shortestAngle(0, 358))
