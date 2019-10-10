""" FDTD Objects

The objects to place in the grid. Objects define all the regions in the grid
with a modified update equation, such as for example regions with anisotropic
permittivity etc.

Available Objects:
 - Object
 - AnisotropicObject

"""

## Imports

# typing
from .typing import Tensorlike, ListOrSlice

# relative
from .grid import Grid
from .backend import backend as bd


## Object
class Object:
    """ An object to place in the grid [base class] """

    def __init__(self, permittivity: Tensorlike, name: str = None):
        """ Create an object """
        self.grid = None
        self.name = name
        self._permittivity = permittivity

    def _register_grid(
        self, grid: Grid, x: ListOrSlice, y: ListOrSlice, z: ListOrSlice
    ):
        """ Register the object to the grid

        Args:
            grid: the grid to register the object into
            x: the x-location of the object in the grid
            y: the y-location of the object in the grid
            z: the z-location of the object in the grid
        """
        self.grid = grid
        self.grid.objects.append(self)
        if self.name is not None:
            if not hasattr(grid, self.name):
                setattr(grid, self.name, self)
            else:
                raise ValueError(
                    f"The grid already has an attribute with name {self.name}"
                )
        self.x = self._handle_slice(x, max_index=self.grid.Nx)
        self.y = self._handle_slice(y, max_index=self.grid.Ny)
        self.z = self._handle_slice(z, max_index=self.grid.Nz)

        self.Nx = abs(self.x.stop - self.x.start)
        self.Ny = abs(self.y.stop - self.y.start)
        self.Nz = abs(self.z.stop - self.z.start)

        # set the permittivity of the object
        if bd.is_array(self._permittivity) and len(self._permittivity.shape) == 3:
            self._permittivity = self._permittivity[:, :, :, None]
        self.inverse_permittivity = (
            bd.ones((self.Nx, self.Ny, self.Nz, 3)) / self._permittivity
            - self.grid.inverse_permittivity[self.x, self.y, self.z]
        )

        # set the permittivity values of the object at its border to be equal
        # to the grid permittivity. This way, the object is made symmetric.
        if self.Nx > 1:
            self.inverse_permittivity[-1, :, :, 0] = 0
        if self.Ny > 1:
            self.inverse_permittivity[:, -1, :, 1] = 0
        if self.Nz > 1:
            self.inverse_permittivity[:, :, -1, 2] = 0

    def _handle_slice(self, s: ListOrSlice, max_index: int = None) -> slice:
        if isinstance(s, list):
            if len(s) == 1:
                return slice(s[0], s[0] + 1, None)
            raise IndexError(
                "One can only use slices or single indices to index the grid for an Object"
            )
        if isinstance(s, slice):
            start, stop, step = s.start, s.stop, s.step
            if step is not None and step != 1:
                raise IndexError(
                    "Can only use slices with unit step to index the grid for an Object"
                )
            if start is None:
                start = 0
            if stop is None:
                stop = max_index
            return slice(start, stop, None)
        raise ValueError("Invalid grid indexing used for object")

    def update_E(self, curl_H):
        """ custom update equations for inside the object

        Args:
            curl_H: the curl of magnetic field in the grid.

        """
        loc = (self.x, self.y, self.z)
        self.grid.E[loc] += (
            self.grid.courant_number * self.inverse_permittivity * curl_H[loc]
        )

    def update_H(self, curl_E):
        """ custom update equations for inside the object

        Args:
            curl_E: the curl of electric field in the grid.

        """

    def __repr__(self):
        return f"{self.__class__.__name__}(name={repr(self.name)})"

    def __str__(self):
        s = "    " + repr(self) + "\n"

        def _handle_slice(s):
            return (
                str(s)
                .replace("slice(", "")
                .replace(")", "")
                .replace(", ", ":")
                .replace("None", "")
            )

        x = _handle_slice(self.x)
        y = _handle_slice(self.y)
        z = _handle_slice(self.z)
        s += f"        @ x={x}, y={y}, z={z}".replace(":,", ",")
        if s[-1] == ":":
            s = s[:-1]
        return s + "\n"


class AnisotropicObject(Object):
    """ An object with anisotropic permittivity tensor """

    def _register_grid(
        self, grid: Grid, x: slice = None, y: slice = None, z: slice = None
    ):
        """ Register a grid to the object

        Args:
            grid: Grid: the grid to register the object into
            x: slice = None: the x-location of the object in the grid
            y: slice = None: the y-location of the object in the grid
            z: slice = None: the z-location of the object in the grid
        """
        super()._register_grid(grid=grid, x=x, y=y, z=z)
        eye = bd.zeros((self.Nx * self.Ny * self.Nz, 3, 3))
        eye[:, range(3), range(3)] = 1.0
        self.inverse_permittivity = bd.reshape(
            bd.reshape(self.inverse_permittivity, (-1, 1, 3)) * eye,
            (self.Nx, self.Ny, self.Nz, 3, 3),
        )

    def update_E(self, curl_H):
        """ custom update equations for inside the anisotropic object

        Args:
            curl_H: the curl of magnetic field in the grid.

        """
        loc = (self.x, self.y, self.z)
        self.grid.E[loc] += bd.reshape(
            self.grid.courant_number
            * bd.bmm(
                bd.reshape(self.inverse_permittivity, (-1, 3, 3)),
                bd.reshape(curl_H[loc], (-1, 3, 1)),
            ),
            (self.Nx, self.Ny, self.Nz, 3),
        )

    def update_H(self, curl_E):
        """ custom update equations for inside the anisotropic object

        Args:
            curl_E: the curl of electric field in the grid.

        """
