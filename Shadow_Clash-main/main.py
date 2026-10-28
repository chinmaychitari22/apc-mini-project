"""SHADOW CLASH - Master Application Entry Point.

Starts the 2D martial arts fighting game.
"""

from __future__ import annotations
import argparse
import sys
from game.application import Application


def main() -> None:
    parser = argparse.ArgumentParser(description="SHADOW CLASH - 2D Martial Arts Silhouette Fighting Game")
    parser.add_argument("--headless", action="store_true", help="Run without graphical window for automated smoke tests")
    parser.add_argument("--smoke-test", action="store_true", help="Run 120 frames of gameplay simulation then exit cleanly with code 0")
    args = parser.parse_args()

    if args.smoke_test:
        print("[SmokeTest] Starting Shadow Clash headless simulation test...")
        import os
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        app = Application(headless=True)
        # Run 120 frames
        from scenes.combat_scene import CombatScene
        app.scene_mgr.change_scene(CombatScene(app.scene_mgr, stage_id=1))
        for frame in range(120):
            app.input_mgr.begin_frame(frame * (1.0 / 60.0))
            app.scene_mgr.update(1.0 / 60.0)
            app.scene_mgr.render(app.window)
        print("[SmokeTest] Successfully simulated 120 frames of combat! (100% OK)")
        sys.exit(0)

    app = Application(headless=args.headless)
    app.run()


if __name__ == "__main__":
    main()
