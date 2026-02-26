import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from ..agent.car_agent import CarAgent


# https://gymnasium.farama.org/introduction/create_custom_env/
# https://gymnasium.farama.org/tutorials/gymnasium_basics/environment_creation/
class F1Track(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None, track_name="Austria", simple_mode=True):
        self.agent = CarAgent(track_name)
        self.terminated = False
        self.simple_mode = simple_mode

        self.observation_space = spaces.Dict(
            {
                "x": spaces.Box(low=-np.inf, high=np.inf, dtype=np.float32),
                "y": spaces.Box(low=-np.inf, high=np.inf, dtype=np.float32),
                "vx": spaces.Box(low=0, high=np.inf, dtype=np.float32),
                "vy": spaces.Box(low=-np.inf, high=np.inf, dtype=np.float32),
                "yaw": spaces.Box(low=0, high=2 * np.pi, dtype=np.float32),
                "yaw_rate": spaces.Box(low=-np.inf, high=np.inf, dtype=np.float32),
                "ax": spaces.Box(low=-np.inf, high=np.inf, dtype=np.float32),
                "front_slide": spaces.MultiBinary(1),
                "rear_slide": spaces.MultiBinary(1),
                "dist": spaces.Box(
                    low=0, high=self.agent._track.length, dtype=np.float32
                ),
                # TODO: add more maybe distances at angles
            }
        )

        if simple_mode:
            self.action_space = spaces.Box(
                low=np.array([-1.0, -1.0]),
                high=np.array([1.0, 1.0]),
                dtype=np.float32,
            )
        else:
            self.action_space = spaces.Box(
                low=np.array([0.0, 0.0, -1.0]),
                high=np.array([1.0, 1.0, 1.0]),
                dtype=np.float32,
            )

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window_size = 512  # The size of the PyGame window
        self.window = None
        self.clock = None

    def _get_obs(self):
        # TODO: add more e.g. distance, track limits around him at different angles
        return self.agent.observation | {"dist": self.agent.get_info()["distance"]}

    def _get_info(self):
        return self.agent.get_info()

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        self.agent.reset()
        self.terminated = False

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def _terminated(self):
        if self.agent.last_move is not None:
            if not self.agent._track.valid_move(
                self.agent.last_move.prev, self.agent.last_move.next
            ):
                self.terminated = True
                return True

    def _reward(self):
        if self.terminated:
            return 0
        if self.agent.finished():
            return 1000
        penalty_out_of_track = int(not (self.agent.is_on_track())) * 100
        penalty_slide = 50 * int(self._get_obs()["front_slide"]) + 30 * int(
            self._get_obs()["rear_slide"]
        )
        reward = -penalty_out_of_track - penalty_slide
        reward += self.agent.sector1_finished * 100
        reward += self.agent.sector2_finished * 100
        reward += self._get_info()["percentage"] * 100
        reward += self._get_obs()["vx"]
        reward -= self._get_obs()["yaw_rate"] * 10
        reward -= self._get_info()["time"]
        return reward

    def step(self, throttle, steer, brake=None):
        if self.simple_mode:
            self.agent.simple_step(throttle, steer)
        else:
            if brake is None:
                raise ValueError("Missing brake argument")
            self.agent.step(throttle, brake, steer)

        terminated = self._terminated()
        finished = self.agent.finished()
        observation = self._get_obs()
        info = self._get_info()
        reward = self._reward()

        if self.render_mode == "human":
            self._render_frame()

        # TODO: what should be the 4th value?? [index 3]
        return observation, reward, finished, terminated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels

        # First we draw the target
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                pix_square_size * self._target_location,
                (pix_square_size, pix_square_size),
            ),
        )
        # Now we draw the agent
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self._agent_location + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Finally, add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to
            # keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
