from gymnasium.envs.registration import register

register(
    id="F1_track/F1Track-v0",
    entry_point="F1_track.envs:F1Track",
    max_episode_steps=15000,
)
