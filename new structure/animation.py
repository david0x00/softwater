from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Slider, Button


## Create Figure
figure, ax = plt.subplots()

figure.subplots_adjust(left=0.25, bottom=0.25)

## Create Sliders

m1pr_ax = figure.add_axes([0.05, 0.25, 0.0225, 0.30])
m1pr_sl = Slider(
    ax=m1pr_ax,
    label='kPa',
    valmin=99,
    valmax=119,
    valinit=100,
    orientation="vertical"
)

m1pl_ax = figure.add_axes([0.1, 0.25, 0.0225, 0.30])
m1pl_sl = Slider(
    ax=m1pl_ax,
    label='kPa',
    valmin=99,
    valmax=119,
    valinit=100,
    orientation="vertical"
)

## Set Slider Update Functions
def update(val):
    arc_angles = linspace(0 * pi, pi/4, 20)
    arc_xs = r * cos(arc_angles)
    arc_ys = r * sin(arc_angles)
    plt.plot(arc_xs, arc_ys, color = 'red', lw = 3)
    plt.gca().annotate('Arc', xy=(1.5, 0.4), xycoords='data', fontsize=10, rotation = 120)



    line.set_ydata(f(t, amp_slider.val, freq_slider.val))
    fig.canvas.draw_idle()

def draw_arc(m1pl, m1pr, m2pl, m2pr):
    return 1

t = np.linspace(0, 1, 1000)





# register the update function with each slider
m1pl_sl.on_changed(update)
m1pr_sl.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')


def reset(event):
    m1pl_sl.reset()
    m1pr_sl.reset()
button.on_clicked(reset)

# Setting limits for x and y axis
ax.set_xlim(-20,20)
ax.set_ylim(-1, 39)

# # Since plotting a single graph
# line, = ax.plot(0, 0)

# def animation_function(i):
# 	x.append(i * 15)
# 	y.append(i)

# 	line.set_xdata(x)
# 	line.set_ydata(y)
# 	return line,

# animation = FuncAnimation(figure,
# 						func = animation_function,
# 						frames = np.arange(0, 10, 0.1),
# 						interval = 10)
plt.show()
