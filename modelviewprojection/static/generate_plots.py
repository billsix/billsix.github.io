# Copyright (c) 2018-2020 William Emerison Six
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import itertools
import imageio

import plotutils.generategridlines as generategridlines
import plotutils.mpltransformations as mplt
from collections import namedtuple

if __name__ != "__main__":
    sys.exit(0)


# TODO, generalize to any number of dimensions
def accumulate_transformation(procedures, backwards=False):
    """Given a pipeline of functions, provide all intermediate results via a function.

    >>> fs = [mplt.translate(5,0),
    ...       mplt.translate(0,10)]
    >>> f = accumulate_transformation(fs)
    >>> f1, isLast = next(f)
    >>> f1((1, 2, 3), (4, 5, 6))
    ((1, 2, 3), (4, 5, 6))
    >>> f2, isLast = next(f)
    >>> f2((1, 2, 3), (4, 5, 6))
    ((6, 7, 8), (4, 5, 6))
    >>> f3, isLast = next(f)
    >>> f3((1, 2, 3), (4, 5, 6))
    ((6, 7, 8), (14, 15, 16))
    """

    def id(x, y):
        return x, y

    yield id, not bool(procedures)

    if not backwards:
        for number_of_fns_to_apply_this_round in [
            x + 1 for x in range(len(procedures))
        ]:

            def process(x, y):
                result_x, result_y = x, y
                for current_fn_index in range(number_of_fns_to_apply_this_round):
                    result_x, result_y = procedures[current_fn_index](result_x, result_y)
                return result_x, result_y

            yield process, True if number_of_fns_to_apply_this_round == len(
                procedures
            ) else False
    else:
        reversed_procs = list(range(len(procedures)))
        reversed_procs.reverse()
        for proc_index in reversed_procs:

            def process(x, y):
                result_x, result_y = x, y
                for current_fn_index in range(proc_index, len(procedures)):
                    result_x, result_y = procedures[current_fn_index](result_x, result_y)
                return result_x, result_y

            yield process, True if proc_index == 0 else False


import doctest

modules = [mplt, sys.modules[__name__]]
for m in modules:
    try:
        doctest.testmod(m, raise_on_error=True)
        print(doctest.testmod(m))
    except Exception:
        print(doctest.testmod(m))
        sys.exit(1)


## Translation Plots


## Translation Plots - reading the transformations forward

### Step 1
graph_bounds = (100, 100)

fig, axes = plt.subplots()
axes.set_xlim([-graph_bounds[0], graph_bounds[0]])
axes.set_ylim([-graph_bounds[1], graph_bounds[1]])

Geometry = namedtuple("Geometry", "points color")

paddle1 = Geometry(
    points=list(
        zip(
            *np.array(
                [
                    [-10.0, -30.0],
                    [10.0, -30.0],
                    [10.0, 30.0],
                    [-10.0, 30.0],
                    [-10.0, -30.0],
                ]
            )
        )
    ),
    color=(0.578123, 0.0, 1.0),
)

paddle2 = Geometry(
    points=list(
        zip(
            *np.array(
                [
                    [-10.0, -30.0],
                    [10.0, -30.0],
                    [10.0, 30.0],
                    [-10.0, 30.0],
                    [-10.0, -30.0],
                ]
            )
        )
    ),
    color=(1.0, 0.0, 0.0, 1.0),
)


def create_graphs(title, filename, geometry, procedures, backwards=False):
    """Creates an animated dif of the geometry, through a sequence of transformations"""

    procs = procedures.copy()
    # when plotting the transformations is backwards order, show the axis
    # at the last step first before plotting the data
    if backwards:
        procs.insert(0, lambda x, y: (x, y))

    # create a single frame of the animated gif
    def create_single_frame(fn, isLast, frame_number):
        fig, axes = plt.subplots()
        axes.set_xlim([-graph_bounds[0], graph_bounds[0]])
        axes.set_ylim([-graph_bounds[1], graph_bounds[1]])

        # plot transformed basis
        for xs, ys, thickness in generategridlines.generategridlines(
            graph_bounds, interval=5
        ):
            transformed_xs, transformed_ys = fn(xs, ys) if backwards else (xs, ys)
            plt.plot(
                transformed_xs,
                transformed_ys,
                "k-",
                lw=thickness,
                color=(0.1, 0.2, 0.5, 0.3),
            )

        # x axis
        transformed_xs, transformed_ys = fn([0.0, 10.0], [0.0, 0.0])
        plt.plot(transformed_xs, transformed_ys, "k-", lw=4.0, color=(0.0, 0.0, 1.0, 1.0))

        # y axis
        transformed_xs, transformed_ys = fn([0.0, 0.0], [0.0, 10.0])
        plt.plot(transformed_xs, transformed_ys, "k-", lw=4.0, color=(1.0, 0.0, 1.0, 1.0))

        # plot the points
        transformed_xs, transformed_ys = fn(*geometry.points)
        plt.title(str.format("{}\nStep {}", title, str(frame_number)))
        if (backwards and isLast) or not backwards:
            plt.plot(transformed_xs, transformed_ys, "k-", lw=2, color=geometry.color)

        # make sure the x and y axis are equally proportional in screen space
        plt.gca().set_aspect("equal", adjustable="box")
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype="uint8")
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close(fig)

        return image

    # create a single frame
    animated_images_list = [
        create_single_frame(fn, isLast, frame_number)
        for (fn, isLast), frame_number in zip(
            accumulate_transformation(procs, backwards), itertools.count(start=1)
        )
    ]

    kwargs_write = {"fps": 1.0, "quantizer": "nq"}
    imageio.mimsave("./" + filename + ".gif", animated_images_list, fps=1)


create_graphs(
    title="Translation",
    filename="translation-forwards",
    geometry=paddle1,
    procedures=[mplt.translate(-90.0, 0.0), mplt.translate(0.0, 20.0)],
)


create_graphs(
    title="Translation",
    filename="translation2-forwards",
    geometry=paddle2,
    procedures=[mplt.translate(90.0, 0.0), mplt.translate(0.0, -40.0)],
)

create_graphs(
    title="Translation",
    filename="translation-backwards",
    geometry=paddle1,
    procedures=[mplt.translate(-90.0, 0.0), mplt.translate(0.0, 20.0)],
    backwards=True,
)


create_graphs(
    title="Translation",
    filename="translation2-backwards",
    geometry=paddle2,
    procedures=[mplt.translate(90.0, 0.0), mplt.translate(0.0, -40.0)],
    backwards=True,
)


create_graphs(
    title="Rotation, Relative to Global Space",
    filename="rotate1-forwards",
    geometry=paddle1,
    procedures=[
        mplt.rotate(math.radians(45.0)),
        mplt.translate(0.0, 20.0),
        mplt.translate(-90.0, 0.0),
    ],
)

create_graphs(
    title="Rotation, Relative to Local Space",
    filename="rotate1-backwards",
    geometry=paddle1,
    procedures=[
        mplt.rotate(math.radians(45.0)),
        mplt.translate(0.0, 20.0),
        mplt.translate(-90.0, 0.0),
    ],
    backwards=True,
)


create_graphs(
    title="Rotation, Global Space",
    filename="rotate2-forwards",
    geometry=paddle2,
    procedures=[
        mplt.rotate(math.radians(-10.0)),
        mplt.translate(90.0, 0.0),
        mplt.translate(0.0, -40.0),
    ],
)

create_graphs(
    title="Rotation, Relative to Local Space",
    filename="rotate2-backwards",
    geometry=paddle2,
    procedures=[
        mplt.rotate(math.radians(-10.0)),
        mplt.translate(90.0, 0.0),
        mplt.translate(0.0, -40.0),
    ],
    backwards=True,
)

square = Geometry(
    points=list(
        zip(
            *np.array(
                [
                    [-10.0, -10.0],
                    [10.0, -10.0],
                    [10.0, 10.0],
                    [-10.0, 10.0],
                    [-10.0, -10.0],
                ]
            )
        )
    ),
    color=(1.0, 0.0, 0.0, 1.0),
)


create_graphs(
    title="Covariance, Relative to Local Space",
    filename="covariance-backwards",
    geometry=square,
    procedures=[
        mplt.rotate(math.radians(-45.0)),
        mplt.scale(scaleX=2.0, scaleY=4.5),
        mplt.rotate(math.radians(45.0)),
    ],
    backwards=True,
)

create_graphs(
    title="Covariance, Relative to Global Space",
    filename="covariance-forwards",
    geometry=square,
    procedures=[
        mplt.rotate(math.radians(-45.0)),
        mplt.scale(scaleX=2.0, scaleY=4.5),
        mplt.rotate(math.radians(45.0)),
    ],
    backwards=False,
)


t = np.linspace(0, np.pi * 2, 100)
circ = [list(np.cos(t) * 10), list(np.sin(t) * 10)]
circle = Geometry(points=circ, color=(0.0, 1.0, 0.0, 1.0))

create_graphs(
    title="Circle, Relative to Local Space",
    filename="circle-backwards",
    geometry=circle,
    procedures=[
        mplt.rotate(math.radians(-45.0)),
        mplt.scale(scaleX=2.0, scaleY=4.5),
        mplt.rotate(math.radians(45.0)),
    ],
    backwards=True,
)

create_graphs(
    title="Circle, Relative to Global Space",
    filename="circle-forwards",
    geometry=circle,
    procedures=[
        mplt.rotate(math.radians(-45.0)),
        mplt.scale(scaleX=2.0, scaleY=4.5),
        mplt.rotate(math.radians(45.0)),
    ],
    backwards=False,
)
