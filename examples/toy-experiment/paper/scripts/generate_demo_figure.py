from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "demo_metrics.png"

    labels = ["Baseline", "Improved"]
    accuracy = [0.81, 0.86]
    runtime = [31.2, 28.4]

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.4), dpi=180)

    axes[0].bar(labels, accuracy, color=["#7aa6c2", "#3e7fa6"])
    axes[0].set_ylim(0.0, 1.0)
    axes[0].set_title("Accuracy")
    axes[0].set_ylabel("Value")

    axes[1].bar(labels, runtime, color=["#c6d8e5", "#6d9db8"])
    axes[1].set_title("Runtime")
    axes[1].set_ylabel("Milliseconds")

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    print(f"Saved demo figure to: {out_path}")


if __name__ == "__main__":
    main()
