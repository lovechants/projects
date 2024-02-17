from manim import * 

class createCircle(Scene):
    def construct(self):
        circle = Circle() # makes a circle
        circle.set_fill(PINK, opacity = .5)
        self.play(Create(circle))
