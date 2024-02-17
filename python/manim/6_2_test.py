
from manim import *

class SimpleTriangle(Scene):
    def construct(self):
        # Define the vertices of the triangle
        vertex1 = ORIGIN  # Point to the left
        vertex2 = RIGHT  * 3 # Point to the right
        vertex3 = UP * 4  # Point upwards
        

        sV1 = ORIGIN + ((vertex1 + vertex3) / 2)
        sv2 = (vertex2 + vertex3) / 2 
        sv3 = vertex3 / 2
        # Create the triangle
        triangle = Polygon(vertex1, vertex2, vertex3, stroke_color=BLUE)
        sTriangle = Polygon(sV1, sv2, sv3, stroke_color=RED)
        # Display the triangle
        self.play(Create(triangle))
        
        self.play(Create(sTriangle))
        # Keep the triangle displayed
        self.wait(2)
