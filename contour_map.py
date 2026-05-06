import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

x = np.arange(0, 1.001, 0.01)
y = np.arange(0, 1.001, 0.01)
X, Y = np.meshgrid(x, y)

Z = np.where(Y > X, 1.5 * Y - X, 0.0)

fig, ax = plt.subplots(figsize=(7, 6))

levels = np.linspace(0, Z.max(), 30)
cf = ax.contourf(X, Y, Z, levels=levels, cmap="viridis")
cs = ax.contour(X, Y, Z, levels=levels, colors="white", linewidths=0.4, alpha=0.5)

cbar = fig.colorbar(cf, ax=ax)
cbar.set_label("z", rotation=0, labelpad=10)

# Mark the boundary y = x
ax.plot([0, 1], [0, 1], "r--", linewidth=1.5, label="y = x (boundary)")

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Contour map of z = 1.5y − x (y > x), else 0\n(resolution 0.01)")
ax.legend(loc="upper left")
ax.set_aspect("equal")

plt.tight_layout()
plt.savefig("contour_map.png", dpi=150)
print("Saved contour_map.png")
