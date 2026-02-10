from gymnasium.envs.registration import register

register(
    id="F1-track/GridWorld-v0",
    entry_point="F1-track.envs:GridWorldEnv",
)
