import numpy as np
from typing import Optional
from shapely import Point


class CarDynamics:
    default_dt = 0.01
    default_params = {
        "mass": 800,
        "heigth_com": 0.35,
        "distance_axis_f": 1.6,
        "distance_axis_r": 2.0,
        "wheelbase": 3.6,
        "ltr_stiff_f": 270000,
        "ltr_stiff_r": 270000,
        "friction": 1.8,
        "rolling_friction": 0.01,
        "air_density": 1.225,
        "front_surf": 1.5,
        "drag": 0.9,
        "dwnf_f": 2.0,
        "dwnf_r": 2.5,
        "F_max": 9000,
        "F_brake_max": 20000,
        "brake_bias": 0.6,
    }

    def __init__(self, params: Optional[dict] = None):
        if params is None:
            self.__init__(self.default_params)
            return

        # --- BASIC ---
        self.mass = params["mass"]  # kg
        self.h_com = params["heigth_com"]  # m

        # --- GEOMETRY ---
        #   |<-------------- L -------------->|
        #   |<---- lf ----> COM <---- lr ---->|
        # Front          mass center         Rear
        #
        self.L_f = params["distance_axis_f"]  # meters
        self.L_r = params["distance_axis_r"]  # meters
        self.L = params.get("wheelbase", self.L_f + self.L_r)  # meters
        assert self.L == self.L_f + self.L_r
        self.inertia = self.mass * self.L**2 / 12

        # --- TYRES ---
        self.Ca_f = params["ltr_stiff_f"]  # lateral stiffness front ≈ 7-10e4
        self.Ca_r = params["ltr_stiff_r"]  # lateral stiffness rear ≈ 7-10e4
        self.mu = params[
            "friction"
        ]  # friction coef (generates grip) ≈ 1.6-2.2 for slick
        self.roll_fr = params[
            "rolling_friction"
        ]  # rolling friction coef (slows down the car) ≈ 0.01-0.02

        # --- AERODYNAMICS ---
        self.air_density = params["air_density"]  # air density [kg/m3]
        self.A = params["front_surf"]  # frontal surface [m2]
        self.drag = params["drag"]
        self.dwnf_f = params["dwnf_f"]  # front downforce coef
        self.dwnf_r = params["dwnf_r"]  # rear downforce coef
        assert (self.dwnf_f + self.dwnf_r) / self.drag <= 5
        assert (self.dwnf_f + self.dwnf_r) / self.drag >= 3

        # --- THROTTLE / BRAKING ---
        self.F_max = params["F_max"]  # maximum engine force [N]
        self.F_brake_max = params["F_brake_max"]  # maximum braking force [N]
        self.brake_bias = params["brake_bias"]  # [0,1] - close to 1 means front braking
        assert self.brake_bias <= 1 and self.brake_bias >= 0
        assert self.F_brake_max > self.F_max

        # --- STATE ---
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.vx = 0.0  # potential bugs here may require to treat it as max(vx, 0.1)
        self.vy = 0.0
        self.va = 0.0  # angular velocity (yaw rate)
        self.ax = 0.0
        self.sliding_front = False
        self.sliding_rear = False

        self.g = 9.81

    @property
    def state(self):
        return {
            "x": self.x,
            "y": self.y,
            "vx": self.vx,
            "vy": self.vy,
            "yaw": self.yaw,
            "yaw_rate": self.va,
            "ax": self.ax,
            "front_slide": self.sliding_front,
            "rear_slide": self.sliding_rear,
        }

    def get_position(self) -> "Point":
        return Point(self.x, self.y)

    def set_position(self, x, y, angle):
        self.reset()
        self.x = x
        self.y = y
        self.yaw = np.fmod(angle, 2 * np.pi)

    def step(
        self,
        throttle: float,
        brake: float,
        steer: float,
        dt: Optional[float] = None,
    ) -> dict:
        """Simulates a car move in dt time. Throttle and brakes in [0,1], steer in [-1,1], positive turns left"""
        if (
            throttle < 0
            or throttle > 1
            or brake < 0
            or brake > 1
            or abs(steer) > 1
            or dt <= 0
        ):
            raise ValueError("Input values out of range")
        steer *= 0.45  # limit front axis angle to about 25 degrees (0.45 rad)
        if dt is None:
            dt = CarDynamics.default_dt

        # --- total speed ---
        v = np.sqrt(self.vx**2 + self.vy**2)

        # --- drag ---
        F_drag = 0.5 * self.air_density * self.A * self.drag * v**2

        # --- downforces ---
        F_down_f = 0.5 * self.air_density * self.A * self.dwnf_f * v**2
        F_down_r = 0.5 * self.air_density * self.A * self.dwnf_r * v**2

        # --- moving mass under throttle / braking ---
        # ax is always one step behind because of feedback in model between ax and Fz
        delta_Fz = self.mass * self.ax * self.h_com / self.L

        # --- vertical forces ---
        Fz_f = (self.mass * self.g * self.L_r / self.L) + F_down_f - delta_Fz
        Fz_r = (self.mass * self.g * self.L_f / self.L) + F_down_r + delta_Fz

        # --- axis velocities ---
        vxf = self.vx
        vyf = self.vy + self.L_f * self.va

        vxr = self.vx
        vyr = self.vy - self.L_r * self.va

        # --- slip angles ---
        # --- turning in place correction ---
        v_total = np.sqrt(self.vx**2 + self.vy**2)
        v_eps = 0.01
        if v_total < v_eps:
            alpha_f = 0.0
            alpha_r = 0.0
        else:
            alpha_f = steer - np.arctan2(vyf, vxf)
            alpha_r = -np.arctan2(vyr, vxr)

        # --- lateral forces (linear) ---
        Fy_f = self.Ca_f * alpha_f
        Fy_r = self.Ca_r * alpha_r

        # --- longitudal forces ---
        Fx_r = throttle * self.F_max
        Fx_f = -brake * self.brake_bias * self.F_brake_max
        Fx_r += -brake * (1 - self.brake_bias) * self.F_brake_max

        # --- braking is not throttle backwards correction ---
        v_eps = 0.01
        if abs(self.vx) < v_eps and Fx_f + Fx_r < 0:
            Fx_f = 0.0
            Fx_r = 0.0
            self.vx = 0.0

        # --- front grip limit ---
        Ff_total = np.sqrt(Fx_f**2 + Fy_f**2)
        Ff_limit = self.mu * Fz_f
        if Ff_total > Ff_limit:
            self.sliding_front = True
            scale = Ff_limit / Ff_total
            Fx_f *= scale
            Fy_f *= scale
        else:
            self.sliding_front = False

        # --- rear grip limit ---
        Fr_total = np.sqrt(Fx_r**2 + Fy_r**2)
        Fr_limit = self.mu * Fz_r
        if Fr_total > Fr_limit:
            self.sliding_rear = True
            scale = Fr_limit / Fr_total
            Fx_r *= scale
            Fy_r *= scale
        else:
            self.sliding_rear = False

        # --- rolling friction ---
        F_roll = self.roll_fr * (Fz_f + Fz_r)
        F_roll *= np.sign(self.vx)  # direction change with regard to vx

        # --- motion equations ---
        dvx = (Fx_f + Fx_r - F_drag - F_roll) / self.mass + self.va * self.vy
        dvy = (Fy_f + Fy_r) / self.mass - self.va * self.vx

        dva = (self.L_f * Fy_f - self.L_r * Fy_r) / self.inertia

        # --- integration ---
        self.vx = max(
            self.vx + dvx * dt, 0.0
        )  # limit not to go backwards (may happen during braking and high dt)
        self.vy += dvy * dt
        self.va += dva * dt

        self.yaw = np.fmod(
            self.yaw + self.va * dt + 20 * np.pi, 2 * np.pi
        )  # prevent negative numbers

        dx = self.vx * np.cos(self.yaw) - self.vy * np.sin(self.yaw)
        dy = self.vx * np.sin(self.yaw) + self.vy * np.cos(self.yaw)

        self.x += dx * dt
        self.y += dy * dt

        # longitudal acceleration (always one step behind because of feedback in model between ax and Fz)
        self.ax = (Fx_f + Fx_r - F_drag - F_roll) / self.mass

        return self.state

    def simple_step(
        self, throttle: float, steer: float, dt: Optional[float] = None
    ) -> dict:
        """Disables throttle and braking at once (negative throttle brakes)"""
        if dt is None:
            dt = CarDynamics.default_dt
        if throttle >= 0:
            return self.step(throttle, 0, steer, dt)
        else:
            return self.step(0, -throttle, steer, dt)

    def reset(self) -> dict:
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.va = 0.0
        self.ax = 0.0
        self.sliding_front = False
        self.sliding_rear = False
        return self.state

    @property
    def actions(self):
        return {
            "throttle": float,
            "brake": float,
            "steer": float,
        }

    @property
    def simple_actions(self):
        return {
            "throttle": float,
            "steer": float,
        }

    @property
    def max_speed(self):
        """Returns max speed of a car in m/s"""
        if self.mu * self.dwnf_r >= self.drag + self.roll_fr * (
            self.dwnf_f + self.dwnf_r
        ):
            # normal case scenario - speed limited by engine fighting with drag and friction
            return np.sqrt(
                2
                * (self.F_max - self.roll_fr * self.mass * self.g)
                / (
                    self.air_density
                    * self.A
                    * (self.drag + self.roll_fr * (self.dwnf_f + self.dwnf_r))
                )
            )
        else:
            # special case scenario - engine stronger than grip
            return np.sqrt(
                2
                * self.mass
                * self.g
                * (self.mu * self.L_f / self.L - self.roll_fr)
                / (
                    self.air_density
                    * self.A
                    * (
                        self.drag
                        + self.roll_fr * (self.dwnf_f + self.dwnf_r)
                        - self.mu * self.dwnf_r
                    )
                )
            )

    @property
    def max_speed_kmh(self):
        return self.max_speed * 3.6


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    car = CarDynamics()
    print("max_speed [km/h] =", car.max_speed_kmh)
    xs = []
    ys = []
    vxs = []
    vys = []
    yaws = []
    yaw_rates = []
    f_slips = []
    r_slips = []
    timestep = 0.01

    for _ in range(10):
        car.simple_step(0.3, 0.1, timestep)
        yaws.append(car.state["yaw"] * 10)
        yaw_rates.append(car.state["yaw_rate"])

    # for _ in range(int(350 * 0.05 / timestep)):
    #     car.simple_step(1, 0, timestep)
    #     xs.append(car.state["x"] / 50)
    #     ys.append(car.state["y"] / 50)
    #     vxs.append(car.state["vx"] / 5)
    #     vys.append(car.state["vy"])
    #     yaws.append(car.state["yaw"] * 10)
    #     yaw_rates.append(car.state["yaw_rate"])
    #     f_slips.append(20 * car.state["front_slide"])
    #     r_slips.append(20 * car.state["rear_slide"])
    # for _ in range(int(36 * 0.05 / timestep)):
    #     car.simple_step(-0.1, 0.1, timestep)
    #     xs.append(car.state["x"] / 50)
    #     ys.append(car.state["y"] / 50)
    #     vxs.append(car.state["vx"] / 5)
    #     vys.append(car.state["vy"])
    #     yaws.append(car.state["yaw"] * 10)
    #     yaw_rates.append(car.state["yaw_rate"])
    #     f_slips.append(20 * car.state["front_slide"])
    #     r_slips.append(20 * car.state["rear_slide"])
    # for _ in range(int(200 * 0.05 / timestep)):
    #     car.simple_step(-1, 0, timestep)
    #     xs.append(car.state["x"] / 50)
    #     ys.append(car.state["y"] / 50)
    #     vxs.append(car.state["vx"] / 5)
    #     vys.append(car.state["vy"])
    #     yaws.append(car.state["yaw"] * 10)
    #     yaw_rates.append(car.state["yaw_rate"])
    #     f_slips.append(20 * car.state["front_slide"])
    #     r_slips.append(20 * car.state["rear_slide"])

    # car.simple_step(-1, 0, timestep)
    # t = np.arange(0, 586 * 0.05, timestep) + timestep
    t = np.arange(0, 0.1, timestep) + timestep

    # plt.plot(t, xs, label="x")
    # plt.plot(t, ys, label="y")
    # plt.plot(t, vxs, label="vx")
    # plt.plot(t, vys, label="vy")
    plt.plot(t, yaws, label="yaw")
    plt.plot(t, yaw_rates, label="yaw_rate")
    # plt.plot(t, f_slips, label="f")
    # plt.plot(t, r_slips, label="r")

    # Add labels and title
    plt.xlabel("X Values")
    plt.ylabel("Y Values")
    plt.title("Too high timestep leads to oscillations")

    # Show legend
    plt.legend()

    # Show grid
    plt.grid(True)

    # Display the plot
    plt.savefig("car.png")
    plt.show()
    plt.close()
