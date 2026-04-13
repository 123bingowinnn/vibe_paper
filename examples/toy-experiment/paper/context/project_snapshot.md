# Project Snapshot: toy-experiment

Generated at: 2026-04-13 21:05:49

## What This Snapshot Is For

This file is the default paper-writing context for agents working on the project. Read this file first, then read `paper/main.tex`, and only after that open additional source files or result files as needed.

## Project Overview

# Toy Experiment Project This example project imitates a small computer vision experiment repository. It contains: - source code in `src/` - training configuration in `configs/` - exported metrics in `results/`

## Top-Level Structure

- `configs/`
- `logs/`
- `paper/`
- `README.md`
- `results/`
- `src/`

## Key Code Entry Points

- `src/train.py`

## Key Config Files

- `configs/train_config.yaml`

## Dataset and Experiment Hints

- `README.md`: - training configuration in `configs/`
- `README.md`: - exported metrics in `results/`
- `README.md`: - plain training logs in `logs/`
- `configs/train_config.yaml`: dataset:
- `configs/train_config.yaml`: train_split: train
- `configs/train_config.yaml`: valid_split: valid
- `configs/train_config.yaml`: test_split: test
- `results/summary.json`: "dataset_name": "TinyCampusSet",
- `results/summary.json`: "train_images": 960,
- `results/summary.json`: "valid_images": 240,
- `results/summary.json`: "test_images": 260,

## Result Files and Extracted Metrics

- `logs/train.log` -> epoch=120 loss=0.419 map50=0.872 map50_95=0.503
- `logs/train_metrics.json` -> best_epoch=120, precision=0.821, recall=0.793, map50=0.872, map50_95=0.503
- `results/runtime.csv` -> device=RTX3060Laptop, avg_latency_ms=46.6, fps=21.46
- `results/summary.json` -> dataset_name=TinyCampusSet, train_images=960, valid_images=240, test_images=260, precision=0.821

## Figures and Artifact Paths

- `results/validation_curve.png`

## Large Files Recorded as Metadata Only

- No large artifacts were detected.

## Paper Workspace Status

- `paper/main.tex`: present
- `paper/context/project_snapshot.md`: updated 2026-04-13 18:12:27
- `paper/build/main_preview.pdf`: updated 2026-04-13 18:12:26
- `paper/build/main.log`: updated 2026-04-13 18:12:26

## Agent Workflow Reminder

- Treat the whole project root as the working scope.
- Use `paper/` as the location for LaTeX, references, scripts, and build outputs.
- Preserve claims and numeric results from the project files. Do not invent missing metrics.
- If paper compilation is required, use the unified paper build command rather than editor-specific build actions.
